"""FastAPI route definitions."""
from fastapi import APIRouter, HTTPException, Header, Request
from fastapi.responses import HTMLResponse
from typing import Dict, Optional, Any
import logging
import json

from archie.config import settings
from archie.engine.indexer import CodeIndexer
from archie.engine.visualizer import GraphVisualizer
from archie.engine.ai_provider import create_ai_provider
from archie.incident.listener import IncidentParser
from archie.incident.investigator import IncidentInvestigator
from archie.incident.fix_generator import FixGenerator
from archie.incident.pr_creator import PRCreator

logger = logging.getLogger(__name__)
router = APIRouter()

# Global instances (initialized on startup)
indexer: Optional[CodeIndexer] = None
visualizer: Optional[GraphVisualizer] = None
incident_parser: Optional[IncidentParser] = None
investigator: Optional[IncidentInvestigator] = None
fix_generator: Optional[FixGenerator] = None
pr_creator: Optional[PRCreator] = None


def init_services():
    """Initialize all services."""
    global indexer, visualizer, incident_parser, investigator, fix_generator, pr_creator
    
    logger.info(f"Initializing services with AI provider: {settings.ai_provider}")
    
    # Create AI provider
    ai_provider = create_ai_provider(
        provider=settings.ai_provider,
        openai_key=settings.openai_api_key,
        anthropic_key=settings.anthropic_api_key,
        openai_model=settings.openai_model,
        anthropic_model=settings.anthropic_model
    )
    
    indexer = CodeIndexer(settings.lancedb_path, settings.graph_persist_path)
    
    # Load existing graph if available
    import os
    if os.path.exists(settings.graph_persist_path):
        logger.info(f"Loading existing graph from {settings.graph_persist_path}")
        try:
            indexer.graph.load(settings.graph_persist_path)
            logger.info(f"Graph loaded successfully: {len(indexer.graph.graph.nodes)} nodes, {len(indexer.graph.graph.edges)} edges")
        except Exception as e:
            logger.warning(f"Could not load graph: {e}")
    else:
        logger.warning(f"No existing graph found at {settings.graph_persist_path}")
    
    visualizer = GraphVisualizer(indexer.graph)
    incident_parser = IncidentParser(settings.webhook_secret)
    investigator = IncidentInvestigator(
        indexer.graph,
        indexer.embeddings,
        settings.repo_path,
        ai_provider
    )
    fix_generator = FixGenerator(indexer.graph, ai_provider, settings.repo_path)
    
    # Try to initialize GitHub PR creator, but don't fail if it doesn't work
    try:
        pr_creator = PRCreator(
            settings.github_token,
            settings.github_repo_owner,
            settings.github_repo_name,
            settings.repo_path
        )
        logger.info("GitHub PR creator initialized successfully")
    except Exception as e:
        logger.warning(f"Could not initialize GitHub PR creator: {e}")
        logger.warning("PR creation will not be available, but other features will work")
        pr_creator = None
    
    logger.info("Services initialized successfully")


@router.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}


@router.get("/index/status")
async def index_status() -> Dict[str, Any]:
    """Get indexing status."""
    if indexer is None:
        raise HTTPException(status_code=503, detail="Indexer not initialized")
    
    summary = indexer.get_architecture_summary()
    return summary



@router.post("/index/trigger")
async def trigger_index() -> Dict[str, str]:
    """Manually trigger full re-index."""
    if indexer is None:
        raise HTTPException(status_code=503, detail="Indexer not initialized")
    
    try:
        await indexer.index_repo(settings.repo_path)
        return {"status": "success", "message": "Indexing complete"}
    except Exception as e:
        logger.error(f"Indexing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/graph/summary")
async def graph_summary() -> Dict[str, Any]:
    """Get architecture summary."""
    if indexer is None:
        raise HTTPException(status_code=503, detail="Indexer not initialized")
    
    return indexer.get_architecture_summary()


@router.get("/graph/node/{name}")
async def get_node(name: str) -> Dict[str, Any]:
    """Get node details."""
    if indexer is None:
        raise HTTPException(status_code=503, detail="Indexer not initialized")
    
    node = indexer.graph.get_node(name)
    if node is None:
        raise HTTPException(status_code=404, detail=f"Node not found: {name}")
    
    return node


@router.post("/search")
async def search(query: Dict[str, str]) -> Dict[str, Any]:
    """Semantic search over codebase."""
    if indexer is None:
        raise HTTPException(status_code=503, detail="Indexer not initialized")
    
    query_text = query.get("query", "")
    if not query_text:
        raise HTTPException(status_code=400, detail="Query is required")
    
    results = indexer.embeddings.search(query_text)
    return {"results": results}


@router.post("/webhook/incident")
async def webhook_incident(
    request: Request,
    x_signature: Optional[str] = Header(None)
) -> Dict[str, Any]:
    """Receive incident webhook and trigger investigation."""
    if None in [incident_parser, investigator, fix_generator]:
        raise HTTPException(status_code=503, detail="Services not initialized")
    
    # Get raw body for signature verification
    body = await request.body()
    logger.info(f"Received body length: {len(body)} bytes")
    
    if not body:
        raise HTTPException(status_code=400, detail="Empty request body")
    
    # Decode and log what we received
    body_str = body.decode('utf-8')
    logger.info(f"Body content: {body_str[:200]}")
    
    try:
        payload = json.loads(body_str)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON. Body was: {body_str}")
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {str(e)}")
    
    # Verify signature if provided
    if x_signature and not incident_parser.verify_signature(body, x_signature):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    try:
        # Parse incident
        incident = incident_parser.parse(payload)
        logger.info(f"Received incident: {incident.title}")
        
        # Investigate (async)
        root_cause = await investigator.investigate(incident)
        logger.info(f"Root cause identified: {root_cause.root_cause}")
        
        # Generate fix (async)
        fix = await fix_generator.generate_fix(root_cause)
        logger.info(f"Fix generated with confidence {fix.confidence_score}%")
        
        # Apply fix locally if file exists
        local_fix_applied = False
        import os
        full_file_path = os.path.join(settings.repo_path, root_cause.responsible_file)
        if os.path.exists(full_file_path):
            try:
                # Write the fix to the file
                with open(full_file_path, 'w') as f:
                    f.write(fix.fixed_code)
                logger.info(f"✅ Fix applied locally to {root_cause.responsible_file}")
                local_fix_applied = True
            except Exception as e:
                logger.error(f"Failed to apply fix locally: {e}")
        else:
            logger.warning(f"File not found, cannot apply fix locally: {full_file_path}")
        
        # Create PR (sync git operations, run in executor)
        pr_url = None
        if pr_creator is not None:
            import asyncio
            loop = asyncio.get_event_loop()
            try:
                pr_url = await loop.run_in_executor(
                    None,
                    pr_creator.create_pr,
                    str(hash(incident.title))[:8],
                    incident.title,
                    root_cause,
                    fix
                )
                logger.info(f"PR created: {pr_url}")
            except Exception as e:
                logger.error(f"Failed to create PR: {e}")
                pr_url = f"PR creation failed: {str(e)}"
        else:
            logger.warning("PR creator not available, skipping PR creation")
            pr_url = "PR creation not configured"
        
        return {
            "status": "success",
            "pr_url": pr_url,
            "confidence": root_cause.confidence_score,
            "root_cause": root_cause.root_cause,
            "local_fix_applied": local_fix_applied,
            "analysis": {
                "responsible_file": root_cause.responsible_file,
                "responsible_function": root_cause.responsible_function,
                "responsible_line": root_cause.responsible_line,
                "responsible_commit": root_cause.responsible_commit,
                "affected_services": root_cause.affected_services,
                "reasoning": root_cause.reasoning
            },
            "fix": {
                "fixed_code": fix.fixed_code[:500] + "..." if len(fix.fixed_code) > 500 else fix.fixed_code,
                "change_summary": fix.change_summary,
                "lines_changed": fix.lines_changed,
                "confidence_score": fix.confidence_score,
                "test_suggestion": fix.test_suggestion
            }
        }
        
    except Exception as e:
        logger.error(f"Error processing incident: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))



# Graph Visualization Endpoints

@router.get("/graph/visualize")
async def visualize_graph(max_nodes: Optional[int] = 100) -> Dict:
    """Get graph data for visualization.
    
    Args:
        max_nodes: Maximum number of nodes to return
    
    Returns:
        JSON with nodes and edges for D3.js, Cytoscape, etc.
    """
    if visualizer is None:
        raise HTTPException(status_code=503, detail="Visualizer not initialized")
    
    return visualizer.to_json(max_nodes=max_nodes)


@router.get("/graph/mermaid")
async def get_mermaid_diagram(file_path: Optional[str] = None, depth: int = 2) -> Dict[str, str]:
    """Get Mermaid diagram for graph visualization.
    
    Args:
        file_path: Focus on specific file (None for entire graph)
        depth: How many levels to show
    
    Returns:
        Mermaid diagram syntax
    """
    if visualizer is None:
        raise HTTPException(status_code=503, detail="Visualizer not initialized")
    
    diagram = visualizer.to_mermaid(file_path=file_path, depth=depth)
    return {"mermaid": diagram}


@router.get("/graph/mermaid/view", response_class=HTMLResponse)
async def view_mermaid_diagram(file_path: Optional[str] = None, depth: int = 2):
    """View Mermaid diagram in browser.
    
    Args:
        file_path: Focus on specific file
        depth: How many levels to show
    """
    if visualizer is None:
        raise HTTPException(status_code=503, detail="Visualizer not initialized")
    
    diagram = visualizer.to_mermaid(file_path=file_path, depth=depth)
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Archie Graph Visualization</title>
        <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 20px;
                background: #f5f5f5;
            }}
            .container {{
                background: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            h1 {{
                color: #333;
                margin-bottom: 20px;
            }}
            .mermaid {{
                background: white;
                padding: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 Archie Code Graph</h1>
            <p><strong>File:</strong> {file_path or "Entire Graph"}</p>
            <p><strong>Depth:</strong> {depth}</p>
            <div class="mermaid">
{diagram}
            </div>
        </div>
        <script>
            mermaid.initialize({{ startOnLoad: true, theme: 'default' }});
        </script>
    </body>
    </html>
    """
    return html


@router.get("/graph/file/{file_path:path}/dependencies")
async def get_file_dependencies(file_path: str) -> Dict:
    """Get all dependencies for a specific file.
    
    Args:
        file_path: Path to file
    
    Returns:
        Dict with imports, imported_by, functions, calls, called_by
    """
    if visualizer is None:
        raise HTTPException(status_code=503, detail="Visualizer not initialized")
    
    return visualizer.get_file_dependencies(file_path)


@router.get("/graph/analysis/circular")
async def find_circular_dependencies() -> Dict[str, Any]:
    """Find circular dependencies in the codebase.
    
    Returns:
        List of circular dependency cycles
    """
    if visualizer is None:
        raise HTTPException(status_code=503, detail="Visualizer not initialized")
    
    cycles = visualizer.find_circular_dependencies()
    return {
        "cycles_found": len(cycles),
        "cycles": cycles
    }


@router.get("/graph/analysis/hotspots")
async def get_hotspots(top_n: int = 10) -> Dict[str, Any]:
    """Get the most connected nodes (potential hotspots).
    
    Args:
        top_n: Number of top nodes to return
    
    Returns:
        List of most connected nodes
    """
    if visualizer is None:
        raise HTTPException(status_code=503, detail="Visualizer not initialized")
    
    hotspots = visualizer.get_most_connected_nodes(top_n=top_n)
    return {
        "hotspots": hotspots,
        "message": "These are the most connected nodes in your codebase"
    }



@router.get("/graph/3d", response_class=HTMLResponse)
async def view_3d_graph(max_nodes: int = 200, file_filter: Optional[str] = None):
    """View interactive 3D graph visualization.
    
    Args:
        max_nodes: Maximum number of nodes to display
        file_filter: Filter by file path pattern (e.g., "payment")
    
    Returns:
        Interactive 3D graph using Force-Graph 3D
    """
    if visualizer is None:
        raise HTTPException(status_code=503, detail="Visualizer not initialized")
    
    # Get graph data
    graph_data = visualizer.to_json(max_nodes=max_nodes)
    
    # Filter if requested
    if file_filter:
        graph_data["nodes"] = [
            n for n in graph_data["nodes"] 
            if file_filter.lower() in n.get("file_path", "").lower()
        ]
        node_ids = {n["id"] for n in graph_data["nodes"]}
        graph_data["edges"] = [
            e for e in graph_data["edges"]
            if e["source"] in node_ids and e["target"] in node_ids
        ]
    
    import json
    graph_json = json.dumps(graph_data)
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Archie 3D Graph Visualization</title>
        <style>
            body {{
                margin: 0;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                overflow: hidden;
                background: #0a0a0a;
            }}
            #graph {{
                width: 100vw;
                height: 100vh;
            }}
            .controls {{
                position: absolute;
                top: 20px;
                left: 20px;
                background: rgba(0, 0, 0, 0.8);
                padding: 20px;
                border-radius: 10px;
                color: white;
                max-width: 300px;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.1);
            }}
            .controls h2 {{
                margin: 0 0 15px 0;
                font-size: 20px;
                color: #4fc3f7;
            }}
            .controls p {{
                margin: 5px 0;
                font-size: 14px;
                line-height: 1.5;
            }}
            .legend {{
                margin-top: 15px;
                padding-top: 15px;
                border-top: 1px solid rgba(255, 255, 255, 0.2);
            }}
            .legend-item {{
                display: flex;
                align-items: center;
                margin: 8px 0;
            }}
            .legend-color {{
                width: 20px;
                height: 20px;
                border-radius: 50%;
                margin-right: 10px;
            }}
            .stats {{
                position: absolute;
                bottom: 20px;
                left: 20px;
                background: rgba(0, 0, 0, 0.8);
                padding: 15px;
                border-radius: 10px;
                color: white;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.1);
            }}
            .stats-item {{
                margin: 5px 0;
                font-size: 14px;
            }}
            .info-panel {{
                position: absolute;
                top: 20px;
                right: 20px;
                background: rgba(0, 0, 0, 0.8);
                padding: 20px;
                border-radius: 10px;
                color: white;
                max-width: 350px;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.1);
                display: none;
            }}
            .info-panel.visible {{
                display: block;
            }}
            .info-panel h3 {{
                margin: 0 0 10px 0;
                color: #4fc3f7;
            }}
            .info-panel .detail {{
                margin: 8px 0;
                font-size: 13px;
            }}
            .info-panel .label {{
                color: #888;
                font-weight: bold;
            }}
        </style>
    </head>
    <body>
        <div id="graph"></div>
        
        <div class="controls">
            <h2>🤖 Archie Code Graph</h2>
            <p><strong>Nodes:</strong> {len(graph_data["nodes"])}</p>
            <p><strong>Edges:</strong> {len(graph_data["edges"])}</p>
            <p style="margin-top: 15px; font-size: 12px; color: #aaa;">
                🖱️ Drag to rotate<br>
                🔍 Scroll to zoom<br>
                👆 Click node for details
            </p>
            
            <div class="legend">
                <div class="legend-item">
                    <div class="legend-color" style="background: #4fc3f7;"></div>
                    <span>Files</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: #ffb74d;"></div>
                    <span>Functions</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: #ba68c8;"></div>
                    <span>Classes</span>
                </div>
            </div>
        </div>
        
        <div class="stats">
            <div class="stats-item">📊 <strong>Files:</strong> {graph_data["stats"]["files"]}</div>
            <div class="stats-item">⚡ <strong>Functions:</strong> {graph_data["stats"]["functions"]}</div>
            <div class="stats-item">🎯 <strong>Classes:</strong> {graph_data["stats"]["classes"]}</div>
        </div>
        
        <div class="info-panel" id="infoPanel">
            <h3 id="nodeName">Node Info</h3>
            <div class="detail"><span class="label">Type:</span> <span id="nodeType"></span></div>
            <div class="detail"><span class="label">File:</span> <span id="nodeFile"></span></div>
            <div class="detail"><span class="label">Lines:</span> <span id="nodeLines"></span></div>
            <div class="detail"><span class="label">Connections:</span> <span id="nodeConnections"></span></div>
        </div>
        
        <script src="https://unpkg.com/3d-force-graph"></script>
        <script>
            const graphData = {graph_json};
            
            // Color mapping
            const colorMap = {{
                'file': '#4fc3f7',
                'function': '#ffb74d',
                'class': '#ba68c8',
                'unknown': '#888888'
            }};
            
            // Create 3D force graph
            const Graph = ForceGraph3D()
                (document.getElementById('graph'))
                .graphData(graphData)
                .nodeLabel(node => `${{node.label}} (${{node.type}})`)
                .nodeColor(node => colorMap[node.type] || colorMap['unknown'])
                .nodeVal(node => {{
                    // Size based on type
                    if (node.type === 'file') return 8;
                    if (node.type === 'class') return 6;
                    return 4;
                }})
                .linkColor(link => {{
                    // Color based on edge type
                    if (link.type === 'calls') return '#ff6b6b';
                    if (link.type === 'imports') return '#4ecdc4';
                    if (link.type === 'contains') return '#95e1d3';
                    return '#666666';
                }})
                .linkWidth(link => {{
                    if (link.type === 'calls') return 2;
                    return 1;
                }})
                .linkDirectionalParticles(link => {{
                    // Animated particles for calls
                    if (link.type === 'calls') return 2;
                    return 0;
                }})
                .linkDirectionalParticleWidth(2)
                .linkDirectionalParticleSpeed(0.005)
                .onNodeClick(node => {{
                    // Show info panel
                    const panel = document.getElementById('infoPanel');
                    panel.classList.add('visible');
                    
                    document.getElementById('nodeName').textContent = node.label;
                    document.getElementById('nodeType').textContent = node.type;
                    document.getElementById('nodeFile').textContent = node.file_path || 'N/A';
                    document.getElementById('nodeLines').textContent = 
                        node.line_start && node.line_end 
                        ? `${{node.line_start}}-${{node.line_end}}`
                        : 'N/A';
                    
                    // Count connections
                    const connections = graphData.edges.filter(
                        e => e.source === node.id || e.target === node.id
                    ).length;
                    document.getElementById('nodeConnections').textContent = connections;
                    
                    // Focus camera on node
                    const distance = 200;
                    const distRatio = 1 + distance/Math.hypot(node.x, node.y, node.z);
                    Graph.cameraPosition(
                        {{ x: node.x * distRatio, y: node.y * distRatio, z: node.z * distRatio }},
                        node,
                        1000
                    );
                }})
                .onBackgroundClick(() => {{
                    // Hide info panel
                    document.getElementById('infoPanel').classList.remove('visible');
                }});
            
            // Add some initial camera movement
            Graph.cameraPosition({{ z: 1000 }});
            
            // Auto-rotate
            let angle = 0;
            setInterval(() => {{
                angle += 0.001;
                Graph.cameraPosition({{
                    x: 1000 * Math.sin(angle),
                    z: 1000 * Math.cos(angle)
                }});
            }}, 50);
        </script>
    </body>
    </html>
    """
    return html

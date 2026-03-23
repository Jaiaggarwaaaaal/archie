"""Proper 3D graph visualization route."""

def get_3d_graph_html(graph_data):
    """Generate working 3D graph visualization."""
    import json
    graph_json = json.dumps(graph_data)
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Archie 3D Graph</title>
        <style>
            body {{
                margin: 0;
                overflow: hidden;
                background: #000;
                font-family: Arial, sans-serif;
            }}
            #graph {{
                width: 100vw;
                height: 100vh;
            }}
            .controls {{
                position: absolute;
                top: 20px;
                left: 20px;
                background: rgba(0, 0, 0, 0.9);
                padding: 20px;
                border-radius: 10px;
                color: white;
                max-width: 300px;
                border: 1px solid #4fc3f7;
            }}
            .controls h2 {{
                margin: 0 0 15px 0;
                color: #4fc3f7;
                font-size: 18px;
            }}
            .controls p {{
                margin: 5px 0;
                font-size: 13px;
            }}
            .legend {{
                margin-top: 15px;
                padding-top: 15px;
                border-top: 1px solid #333;
            }}
            .legend-item {{
                display: flex;
                align-items: center;
                margin: 8px 0;
                font-size: 12px;
            }}
            .legend-color {{
                width: 16px;
                height: 16px;
                border-radius: 50%;
                margin-right: 10px;
            }}
            .info {{
                position: absolute;
                top: 20px;
                right: 20px;
                background: rgba(0, 0, 0, 0.9);
                padding: 15px;
                border-radius: 10px;
                color: white;
                max-width: 350px;
                border: 1px solid #4fc3f7;
                display: none;
            }}
            .info.visible {{
                display: block;
            }}
            .info h3 {{
                margin: 0 0 10px 0;
                color: #4fc3f7;
                font-size: 16px;
            }}
            .info p {{
                margin: 5px 0;
                font-size: 12px;
            }}
        </style>
    </head>
    <body>
        <div id="graph"></div>
        
        <div class="controls">
            <h2>🤖 Archie Graph</h2>
            <p><strong>Nodes:</strong> {len(graph_data["nodes"])}</p>
            <p><strong>Edges:</strong> {len(graph_data["edges"])}</p>
            <p style="margin-top: 15px; font-size: 11px; color: #888;">
                🖱️ Click and drag to rotate<br>
                🔍 Scroll to zoom<br>
                👆 Click node for details<br>
                ⏸️ Click background to pause
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
        
        <div class="info" id="info">
            <h3 id="nodeName">Node Info</h3>
            <p><strong>Type:</strong> <span id="nodeType"></span></p>
            <p><strong>File:</strong> <span id="nodeFile"></span></p>
            <p><strong>Lines:</strong> <span id="nodeLines"></span></p>
        </div>
        
        <script src="https://unpkg.com/3d-force-graph"></script>
        <script>
            const data = {graph_json};
            
            // Color mapping
            const colors = {{
                'file': '#4fc3f7',
                'function': '#ffb74d',
                'class': '#ba68c8',
                'unknown': '#666666'
            }};
            
            // Create graph
            const Graph = ForceGraph3D()
                (document.getElementById('graph'))
                .graphData(data)
                .nodeLabel(node => `${{node.label}} (${{node.type}})`)
                .nodeColor(node => colors[node.type] || colors['unknown'])
                .nodeVal(node => {{
                    if (node.type === 'file') return 10;
                    if (node.type === 'class') return 7;
                    if (node.type === 'function') return 5;
                    return 3;
                }})
                .nodeOpacity(0.9)
                .linkColor(() => '#ffffff')
                .linkOpacity(0.3)
                .linkWidth(1)
                .linkDirectionalParticles(link => {{
                    if (link.type === 'calls') return 2;
                    return 0;
                }})
                .linkDirectionalParticleWidth(2)
                .linkDirectionalParticleSpeed(0.003)
                .onNodeClick(node => {{
                    // Show info
                    const info = document.getElementById('info');
                    info.classList.add('visible');
                    
                    document.getElementById('nodeName').textContent = node.label;
                    document.getElementById('nodeType').textContent = node.type;
                    document.getElementById('nodeFile').textContent = node.file_path || 'N/A';
                    document.getElementById('nodeLines').textContent = 
                        node.line_start ? `${{node.line_start}}-${{node.line_end}}` : 'N/A';
                    
                    // Focus camera
                    const distance = 200;
                    const distRatio = 1 + distance/Math.hypot(node.x, node.y, node.z);
                    Graph.cameraPosition(
                        {{ x: node.x * distRatio, y: node.y * distRatio, z: node.z * distRatio }},
                        node,
                        1000
                    );
                }})
                .onBackgroundClick(() => {{
                    document.getElementById('info').classList.remove('visible');
                }})
                .d3Force('charge').strength(-120)
                .d3Force('link').distance(50);
            
            // Better initial camera position
            Graph.cameraPosition({{ z: 800 }});
            
            // Slow rotation
            let angle = 0;
            const rotationSpeed = 0.0005;
            
            function animate() {{
                angle += rotationSpeed;
                const distance = 800;
                Graph.cameraPosition({{
                    x: distance * Math.sin(angle),
                    z: distance * Math.cos(angle),
                    y: 100
                }});
                requestAnimationFrame(animate);
            }}
            
            // Start animation after 2 seconds
            setTimeout(() => animate(), 2000);
            
            console.log('Graph loaded with', data.nodes.length, 'nodes and', data.edges.length, 'edges');
        </script>
    </body>
    </html>
    """

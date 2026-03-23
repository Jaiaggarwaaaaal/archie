# Priority Improvements for Archie

## Status: 3 Critical Features Needed

### 1. ✅ FASTER INDEXING (DONE)
**Status:** Implemented - parallel processing
**Speed:** 5-10x faster (1-2 min instead of 7-8 min)
**Next run:** Will automatically use parallel processing

---

### 2. 🔴 PROPER GRAPH VISUALIZATION (IN PROGRESS)

**Current Problem:**
- Nodes render but are invisible/too far apart
- No visible connections between nodes
- Can't see the graph structure

**Target:** Graph like the images shown
- Visible colored nodes (files, functions, classes)
- Clear connection lines between nodes
- Interactive (click, zoom, search)
- Proper force-directed layout

**Implementation Plan:**

#### Option A: Use React Flow (Recommended)
- Modern, fast, interactive
- 2D graph with proper layout
- Easy to customize
- Works in browser

#### Option B: Use Cytoscape.js
- Powerful graph library
- Good for large graphs
- More complex setup

#### Option C: Use D3.js Force Graph
- Most flexible
- Requires more code
- Best for custom layouts

**Recommendation:** Use **React Flow** - it's the easiest and most modern.

**Steps:**
1. Create a separate React app for visualization
2. Fetch data from `/graph/visualize` endpoint
3. Render with React Flow
4. Add search, filters, zoom controls

**Time Estimate:** 2-3 hours

---

### 3. 🔴 AUTOMATIC CODE CHANGES (CRITICAL)

**Current Problem:**
- AI generates fix but doesn't apply it
- File path mismatch (says `report_generator.py` but actual is `logging_celery/logging_report.py`)
- No actual code modification

**What's Needed:**
1. **Better file path resolution**
   - Use fuzzy matching to find actual files
   - Search by filename, not full path
   - Handle multiple matches

2. **Actual code modification**
   - Parse the existing file
   - Apply the AI-generated changes
   - Preserve formatting and structure

3. **Git integration**
   - Create a branch
   - Commit the changes
   - Push to GitHub
   - Create PR automatically

**Implementation Plan:**

#### Step 1: Fuzzy File Matching
```python
def find_actual_file(filename: str, repo_path: str) -> str:
    """Find actual file path using fuzzy matching."""
    # Search for files with similar names
    # Return best match
```

#### Step 2: Smart Code Application
```python
def apply_fix_to_file(file_path: str, fix: CodeFix) -> bool:
    """Apply AI-generated fix to actual file."""
    # Read current file
    # Parse with AST
    # Apply changes intelligently
    # Write back with proper formatting
```

#### Step 3: Automatic PR Creation
```python
def create_fix_pr(incident: Incident, fix: CodeFix) -> str:
    """Create PR with the fix."""
    # Create branch: fix/inc-207-report-truncation
    # Apply changes
    # Commit with detailed message
    # Push to GitHub
    # Create PR with description
    # Return PR URL
```

**Time Estimate:** 3-4 hours

---

## Implementation Priority:

### Phase 1: Critical (Do Now)
1. ✅ Faster indexing (DONE)
2. 🔴 Automatic code changes (CRITICAL - users need this)
3. 🔴 Better file path resolution

### Phase 2: Important (Do Next)
4. Proper graph visualization
5. Search and filter in graph
6. Click node to see code

### Phase 3: Nice to Have
7. Real-time updates
8. Multiple repo support
9. Incident history tracking

---

## Next Steps:

1. **Implement fuzzy file matching** (30 min)
2. **Implement smart code application** (2 hours)
3. **Test with INC-207** (30 min)
4. **Create actual PR** (1 hour)

Total time: ~4 hours to have fully working automatic fixes

---

## For Graph Visualization:

**Quick Win:** Use an existing graph visualization service
- Upload graph data to https://cosmograph.app/
- Or use https://gephi.org/
- Or build custom React Flow app

**Long-term:** Build integrated visualization in Archie

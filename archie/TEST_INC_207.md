# Testing Archie with INC-207

## Incident Details

**Title:** INC-207: No images in test report for thread yCmxs

**Problem:** 
- Test report shows no images
- `test_logs` array truncated to steps 0-2
- Missing 151 steps including healing screenshots
- 20 healing screenshots not rendered in UI

**Affected Files:**
- `enricher/report_generator.py` (PRIMARY)
- `frontend/report_ui.js`
- `enricher/step_logger.py`
- `enricher/healing_session.py`

**Root Cause:**
- Step 18: LLM tapped wrong element (container instead of text input)
- Step 19: Failed (UNDOABLE)
- Healing session: EXEC_FAILED
- Report generation pipeline: Truncated test_logs

## Testing Steps

### 1. Prepare Your Environment

```bash
# Make sure your codebase path is correct
cd /Users/jaiaggarwal/your-project

# Verify these files exist:
ls -la enricher/report_generator.py
ls -la enricher/step_logger.py
ls -la enricher/healing_session.py
ls -la frontend/report_ui.js
```

### 2. Configure Archie

Edit `archie/.env`:

```env
# Point to YOUR codebase
REPO_PATH=/Users/jaiaggarwal/your-project

# Use your OpenAI key
AI_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here

# GitHub settings (for PR creation)
GITHUB_TOKEN=ghp_your-token
GITHUB_REPO_OWNER=your-username
GITHUB_REPO_NAME=your-repo-name
```

### 3. Start Archie and Index

```bash
# Terminal 1: Start Archie
cd archie
python -m archie.main

# Terminal 2: Index your codebase
curl -X POST http://localhost:8000/index/trigger

# Wait 30-60 seconds
sleep 60

# Check status
curl http://localhost:8000/index/status
```

### 4. Explore the Affected Code

Before sending the incident, let's explore:

#### A. View report_generator.py in graph

```bash
curl http://localhost:8000/graph/node/report_generator.py
```

Expected output:
```json
{
  "name": "report_generator.py",
  "type": "file",
  "functions": ["generate_report", "format_test_logs", "..."],
  "imports": ["step_logger", "healing_session"],
  "imported_by": ["api.py", "..."]
}
```

#### B. Search for report generation logic

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "test report generation logs screenshots"}'
```

This should find relevant functions in `report_generator.py`.

#### C. View dependencies

```bash
curl http://localhost:8000/graph/file/enricher/report_generator.py/dependencies
```

This shows what `report_generator.py` depends on and what depends on it.

#### D. Visual exploration

```bash
# Open 3D graph filtered to enricher module
open "http://localhost:8000/graph/3d?file_filter=enricher"
```

Look for:
- Blue nodes: Files (report_generator.py, step_logger.py, etc.)
- Orange nodes: Functions (generate_report, format_logs, etc.)
- Connections: How they call each other

### 5. Send the Incident

```bash
curl -X POST http://localhost:8000/webhook/incident \
  -H "Content-Type: application/json" \
  -d @example_incident.json \
  | python -m json.tool > incident_response.json

# View the response
cat incident_response.json
```

### 6. Analyze Archie's Response

The response should contain:

#### A. Investigation Results

```json
{
  "investigation": {
    "root_cause": "...",
    "confidence": 0.85,
    "affected_files": [
      "enricher/report_generator.py",
      "enricher/step_logger.py"
    ],
    "analysis": "..."
  }
}
```

**Check:**
- ✅ Did Archie identify `report_generator.py` as the main issue?
- ✅ Did it understand the truncation problem?
- ✅ Did it mention the healing screenshots issue?
- ✅ Is the confidence score reasonable (70-90%)?

#### B. Generated Fix

```json
{
  "fix": {
    "file": "enricher/report_generator.py",
    "changes": "...",
    "explanation": "...",
    "validation": {
      "syntax_valid": true,
      "signature_preserved": true
    }
  }
}
```

**Check:**
- ✅ Does the fix address test_logs truncation?
- ✅ Does it handle healing screenshots?
- ✅ Is the code syntactically correct?
- ✅ Does it preserve existing function signatures?

#### C. Pull Request

```json
{
  "pr_url": "https://github.com/your-username/your-repo/pull/123",
  "pr_title": "Fix: INC-207 - No images in test report",
  "pr_body": "..."
}
```

**Check:**
- ✅ Was PR created successfully?
- ✅ Does PR description explain the issue?
- ✅ Does it include confidence score?
- ✅ Does it suggest tests?

### 7. Review the PR

Go to the GitHub PR URL and review:

1. **Code Changes**
   - Are they minimal?
   - Do they address the root cause?
   - Are there any side effects?

2. **Explanation**
   - Does it explain what was wrong?
   - Does it explain the fix?
   - Is it clear and concise?

3. **Tests**
   - Does it suggest tests?
   - Are the test suggestions relevant?

### 8. Measure Performance

#### Time Comparison

**Manual Investigation (estimated):**
- Read incident: 5 min
- Find affected files: 20 min
- Understand report generation flow: 30 min
- Trace through step_logger and healing_session: 30 min
- Identify truncation logic: 30 min
- Write fix: 20 min
- Test fix: 15 min
- **Total: 2 hours 30 minutes**

**With Archie:**
- Archie investigates: 15 seconds
- Review investigation: 5 min
- Review PR: 10 min
- **Total: 15 minutes**

**Time Saved: 2 hours 15 minutes**

#### Accuracy Assessment

Rate Archie's performance:

| Aspect | Score (1-10) | Notes |
|--------|--------------|-------|
| Root cause identification | ? | Did it find the truncation issue? |
| Fix correctness | ? | Is the fix appropriate? |
| Code quality | ? | Is the code clean and maintainable? |
| Explanation clarity | ? | Is the PR description clear? |
| Test suggestions | ? | Are test suggestions helpful? |
| **Overall** | ? | Would you merge this PR? |

### 9. Expected Results

Based on the incident details, Archie should:

#### ✅ Identify Root Causes

1. **Primary:** `report_generator.py` truncates `test_logs` array
2. **Secondary:** Healing screenshots not included in report JSON
3. **Tertiary:** UI doesn't render `healing.screens` array

#### ✅ Generate Fixes

**Fix 1: report_generator.py**
```python
# Before (truncated)
test_logs = test_data.get('test_logs', [])[:3]

# After (full logs)
test_logs = test_data.get('test_logs', [])
```

**Fix 2: Include healing screenshots**
```python
# Add healing screenshots to report
report_data['healing_screenshots'] = healing_session.get('screens', [])
```

#### ✅ Suggest Improvements

1. Add `command_verifier` to search field tap steps
2. Improve LLM element selection for search fields
3. Add tests for report generation with large test_logs
4. Add tests for healing screenshot rendering

### 10. What If Results Are Not Perfect?

This is EXPECTED for complex issues. Here's what to do:

#### Scenario A: Archie finds the right file but wrong fix

**Action:** Use Archie's investigation as a starting point
- Review the dependency graph it built
- Use the semantic search results
- Write the fix yourself with better context

**Value:** Still saved 1+ hour on investigation

#### Scenario B: Archie misses some files

**Action:** Check the graph visualization
- Look at `report_generator.py` dependencies
- See what it calls and what calls it
- Manually review those files

**Value:** Visual graph helps understand relationships

#### Scenario C: Fix is partially correct

**Action:** Iterate on the fix
- Take Archie's fix as v1
- Refine it based on your knowledge
- Add edge cases Archie missed

**Value:** Faster than starting from scratch

## 🎯 Success Criteria

After testing INC-207, you should be able to answer:

1. **Time Savings**
   - How much time did Archie save? (Target: 1+ hour)

2. **Accuracy**
   - Did Archie identify the correct root cause? (Target: 70%+)
   - Is the fix correct or close? (Target: 70%+)

3. **Usability**
   - Was the 3D graph helpful? (Target: Yes)
   - Was the investigation clear? (Target: Yes)
   - Would you use this for future incidents? (Target: Yes)

4. **ROI**
   - If you have 10 incidents/month, how much time saved? (Target: 10+ hours)
   - What's the value of that time? (Target: $1000+)

## 📊 Next Steps Based on Results

### If Accuracy > 80%

**You're ready to deploy!**

1. Set up webhooks from your monitoring tools
2. Enable auto-PR creation
3. Roll out to your team
4. Measure ROI over 1 month

### If Accuracy 60-80%

**Use in assistant mode:**

1. Let Archie investigate
2. Review its findings
3. Write fix yourself with better context
4. Still saves 50%+ time

### If Accuracy < 60%

**Improve the system:**

1. Add more context to code (comments, docs)
2. Fine-tune prompts for your domain
3. Use for code exploration only (3D graph, search)
4. Re-test after improvements

## 💡 Pro Tips for INC-207

1. **Before testing:** Add comments to `report_generator.py` explaining the report generation flow

2. **During testing:** Watch Archie's logs to see its reasoning process

3. **After testing:** Compare Archie's fix to what you would have written

4. **Bonus:** Try searching for "report generation" and "healing screenshots" to see what Archie finds

## 🚀 Ready to Test?

```bash
# Quick test command
cd archie
python -m archie.main &
sleep 5
curl -X POST http://localhost:8000/index/trigger
sleep 60
curl -X POST http://localhost:8000/webhook/incident \
  -H "Content-Type: application/json" \
  -d @example_incident.json
```

Then check your GitHub for the PR!

---

**Good luck! Let's see how Archie handles your real-world incident.** 🎯

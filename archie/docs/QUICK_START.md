# Quick Start Guide - Test Archie with Your Codebase

## 🚀 Get Archie Running in 5 Minutes

### Step 1: Install Dependencies

```bash
cd archie
pip install -r requirements.txt
```

### Step 2: Configure Environment

```bash
# Copy example config
cp .env.example .env

# Edit .env with your details
nano .env  # or use your favorite editor
```

**Minimum required configuration:**

```env
# AI Provider (choose one)
AI_PROVIDER=openai
OPENAI_API_KEY=sk-your-openai-key-here

# OR use Anthropic
# AI_PROVIDER=anthropic
# ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here

# GitHub (for creating PRs)
GITHUB_TOKEN=ghp_your-github-token-here
GITHUB_REPO_OWNER=your-username
GITHUB_REPO_NAME=your-repo-name

# Path to YOUR codebase (absolute path)
REPO_PATH=/Users/jaiaggarwal/your-project

# Webhook secret (any random string)
WEBHOOK_SECRET=my-secret-123
```

### Step 3: Start Archie

```bash
python -m archie.main
```

You should see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Archie starting up...
INFO:     Services initialized
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 4: Index Your Codebase

Open a new terminal:

```bash
# Trigger indexing
curl -X POST http://localhost:8000/index/trigger

# Wait 30-60 seconds, then check status
curl http://localhost:8000/index/status
```

You should see something like:
```json
{
  "status": "ready",
  "files_indexed": 42,
  "functions_found": 156,
  "classes_found": 23,
  "total_nodes": 221,
  "total_edges": 387
}
```

### Step 5: Explore Your Code

#### A. View 3D Interactive Graph

```bash
open http://localhost:8000/graph/3d
```

- Drag to rotate
- Scroll to zoom
- Click nodes for details
- Blue = Files, Orange = Functions, Purple = Classes

#### B. Search Your Code

```bash
# Find error handling code
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "error handling exception"}'

# Find payment processing
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "payment processing validation"}'
```

#### C. Find Hotspots (High-Risk Code)

```bash
curl http://localhost:8000/graph/analysis/hotspots
```

#### D. Find Circular Dependencies

```bash
curl http://localhost:8000/graph/analysis/circular
```

### Step 6: Test Incident Response

Now let's test with your REAL incident (INC-207):

```bash
# Send the incident to Archie
curl -X POST http://localhost:8000/webhook/incident \
  -H "Content-Type: application/json" \
  -d @example_incident.json
```

**What happens next:**

1. Archie analyzes the incident (10-20 seconds)
2. Searches for affected files: `enricher/report_generator.py`
3. Builds dependency graph
4. Uses AI to identify root cause
5. Generates code fix
6. Creates GitHub PR

**Check the response:**

```json
{
  "status": "success",
  "investigation": {
    "root_cause": "...",
    "confidence": 0.85,
    "affected_files": ["enricher/report_generator.py"]
  },
  "fix": {
    "file": "enricher/report_generator.py",
    "changes": "...",
    "explanation": "..."
  },
  "pr_url": "https://github.com/your-username/your-repo/pull/123"
}
```

## 📊 Measuring Results

### Time Savings

**Without Archie:**
- Read incident: 5 min
- Search codebase: 30 min
- Understand dependencies: 30 min
- Identify root cause: 60 min
- Write fix: 30 min
- **Total: 2.5 hours**

**With Archie:**
- Archie investigates: 15 seconds
- Review PR: 10 min
- **Total: 10 minutes**

**Savings: 2 hours 20 minutes per incident**

### Accuracy Check

Review Archie's PR:
- ✅ Did it identify the correct file?
- ✅ Did it understand the root cause?
- ✅ Is the fix correct?
- ✅ Are there any side effects?

### Confidence Score

Archie provides a confidence score (0-100%):
- **90-100%**: High confidence, likely correct
- **70-89%**: Medium confidence, review carefully
- **Below 70%**: Low confidence, use as starting point

## 🎯 Real-World Testing Checklist

### Test 1: Code Understanding
- [ ] View 3D graph of your codebase
- [ ] Search for specific functionality
- [ ] Check hotspot analysis
- [ ] Verify dependency detection

### Test 2: Incident Response
- [ ] Send real incident (INC-207)
- [ ] Review investigation results
- [ ] Check generated fix
- [ ] Verify PR quality

### Test 3: Time Measurement
- [ ] Note time Archie takes
- [ ] Compare to manual investigation
- [ ] Calculate time savings
- [ ] Estimate monthly ROI

### Test 4: Accuracy Assessment
- [ ] Is root cause correct?
- [ ] Is fix appropriate?
- [ ] Are dependencies understood?
- [ ] Would you merge the PR?

## 🔧 Troubleshooting

### Issue: "Connection refused"
**Solution:** Make sure Archie is running (`python -m archie.main`)

### Issue: "No files indexed"
**Solution:** Check `REPO_PATH` in `.env` points to correct directory

### Issue: "API key invalid"
**Solution:** Verify your OpenAI/Anthropic API key in `.env`

### Issue: "GitHub PR failed"
**Solution:** Check `GITHUB_TOKEN` has repo write permissions

### Issue: "Indexing takes too long"
**Solution:** Normal for large codebases (1000+ files). Wait 2-3 minutes.

### Issue: "Fix is incorrect"
**Solution:** This is expected for complex issues. Use Archie as assistant, not autopilot.

## 📈 Next Steps After Testing

### If Results Are Good (80%+ accuracy):

1. **Integrate with Monitoring**
   - Set up webhooks from Sentry/PagerDuty
   - Configure Slack notifications
   - Enable auto-PR creation

2. **Expand Coverage**
   - Index more repositories
   - Add more languages (Java, Go, etc.)
   - Train on your specific patterns

3. **Team Rollout**
   - Share 3D graph with team
   - Use for code reviews
   - Use for onboarding new engineers

4. **Measure ROI**
   - Track incidents handled
   - Calculate time saved
   - Measure downtime reduced

### If Results Need Improvement:

1. **Provide More Context**
   - Add comments to complex code
   - Document business logic
   - Include architecture diagrams

2. **Fine-tune Prompts**
   - Customize investigation prompts
   - Add domain-specific knowledge
   - Adjust confidence thresholds

3. **Hybrid Approach**
   - Use Archie for investigation
   - Human writes the fix
   - Archie validates the fix

## 💡 Pro Tips

1. **Use 3D Graph Daily**
   - Great for code reviews
   - Helps understand new code
   - Identifies refactoring opportunities

2. **Search Before Writing**
   - Check if functionality exists
   - Find similar patterns
   - Avoid duplicates

3. **Monitor Hotspots**
   - High-risk code needs more tests
   - Consider refactoring
   - Extra careful in code reviews

4. **Trust the Confidence Score**
   - 90%+ → Usually safe to merge
   - 70-89% → Review carefully
   - <70% → Use as starting point

## 📞 Support

If you encounter issues:
1. Check logs: `tail -f archie.log`
2. Review documentation: `archie/DOCUMENTATION_INDEX.md`
3. Check troubleshooting: `archie/TROUBLESHOOTING.md`

## 🎉 Success Metrics

After 1 week of testing, you should see:
- ✅ 50%+ reduction in incident response time
- ✅ Faster code understanding for new engineers
- ✅ Better code review quality
- ✅ Fewer production incidents (proactive detection)

**Archie is ready to save you time. Let's get started!** 🚀

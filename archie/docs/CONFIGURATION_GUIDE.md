# Configuration Guide - Step by Step

## Overview

This guide explains every configuration setting in `.env` and how to get the values.

## Configuration Settings Explained

### 1. REPO_PATH - Your Codebase Location

**What it is:** The absolute path to the codebase you want Archie to analyze.

**How to find it:**

```bash
# Go to your project directory
cd /Users/jaiaggarwal/your-project

# Get the full path
pwd
```

**Example:**
```env
REPO_PATH=/Users/jaiaggarwal/atom/your-project
REPO_PATH=/Users/jaiaggarwal/Documents/my-company/backend
```

**Important:**
- Must be an ABSOLUTE path (starts with `/`)
- Must be a directory that exists
- Archie will read all Python/JavaScript/TypeScript files in this directory

**For testing INC-207:**
```env
# If your enricher code is at:
# /Users/jaiaggarwal/atom/enricher-project
REPO_PATH=/Users/jaiaggarwal/atom/enricher-project
```

---

### 2. WEBHOOK_SECRET - Security Token

**What it is:** A random secret string to verify webhook requests are legitimate.

**How to generate:**

```bash
# Option 1: Use openssl (recommended)
openssl rand -hex 32

# Option 2: Use Python
python3 -c "import secrets; print(secrets.token_hex(32))"

# Option 3: Just make up a long random string
# Example: my-super-secret-webhook-key-12345
```

**Example:**
```env
WEBHOOK_SECRET=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
WEBHOOK_SECRET=my-random-secret-key-for-webhooks-2024
```

**Important:**
- Keep it secret (don't share publicly)
- Use at least 20 characters
- Can be any random string
- Used to verify webhook requests from Sentry/PagerDuty

**For testing:**
```env
# Any random string works for local testing
WEBHOOK_SECRET=test-secret-123
```

---

### 3. GITHUB_TOKEN - GitHub Personal Access Token

**What it is:** A token that allows Archie to create Pull Requests on your behalf.

**How to get it:**

#### Step 1: Go to GitHub Settings
1. Go to https://github.com
2. Click your profile picture (top right)
3. Click "Settings"
4. Scroll down to "Developer settings" (bottom left)
5. Click "Personal access tokens"
6. Click "Tokens (classic)"

#### Step 2: Generate New Token
1. Click "Generate new token" → "Generate new token (classic)"
2. Give it a name: "Archie AI Agent"
3. Set expiration: 90 days (or "No expiration" for testing)
4. Select scopes (permissions):
   - ✅ `repo` (Full control of private repositories)
     - This includes: repo:status, repo_deployment, public_repo, repo:invite, security_events
   - ✅ `workflow` (Update GitHub Action workflows)
5. Click "Generate token"
6. **COPY THE TOKEN NOW** (you won't see it again!)

#### Step 3: Use the Token
```env
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Example:**
```env
GITHUB_TOKEN=ghp_1234567890abcdefghijklmnopqrstuvwxyz123456
```

**Important:**
- Starts with `ghp_`
- Keep it secret (don't commit to git)
- If you lose it, generate a new one
- Needed for creating PRs

**For testing without PRs:**
```env
# You can use a dummy value if you just want to test indexing/search
GITHUB_TOKEN=dummy-token-for-testing
# But PR creation will fail
```

---

### 4. GITHUB_REPO_OWNER - Your GitHub Username

**What it is:** Your GitHub username or organization name.

**How to find it:**

#### Option 1: From GitHub URL
If your repo is at: `https://github.com/jaiaggarwal/my-project`
- Owner: `jaiaggarwal`

#### Option 2: From GitHub Profile
1. Go to https://github.com
2. Click your profile picture
3. Your username is shown there

#### Option 3: From Command Line
```bash
# If you have a git repo
cd /Users/jaiaggarwal/your-project
git remote -v
# Look at the URL: git@github.com:USERNAME/repo.git
```

**Example:**
```env
GITHUB_REPO_OWNER=jaiaggarwal
GITHUB_REPO_OWNER=your-company
GITHUB_REPO_OWNER=myorganization
```

**Important:**
- Case-sensitive
- No spaces
- Just the username, not the full URL

---

### 5. GITHUB_REPO_NAME - Your Repository Name

**What it is:** The name of your GitHub repository.

**How to find it:**

#### Option 1: From GitHub URL
If your repo is at: `https://github.com/jaiaggarwal/my-project`
- Repo name: `my-project`

#### Option 2: From Command Line
```bash
cd /Users/jaiaggarwal/your-project
git remote -v
# Look at the URL: git@github.com:username/REPONAME.git
```

**Example:**
```env
GITHUB_REPO_NAME=my-project
GITHUB_REPO_NAME=backend-api
GITHUB_REPO_NAME=enricher
```

**Important:**
- Case-sensitive
- No spaces
- Just the repo name, not the full URL
- Must match exactly with GitHub

---

## Complete Example Configuration

### Example 1: Testing with Your Enricher Project

```env
# AI Provider
AI_PROVIDER=openai
OPENAI_API_KEY=sk-proj-your-actual-openai-key-here

# Your codebase (where enricher/report_generator.py is)
REPO_PATH=/Users/jaiaggarwal/atom/enricher-project

# GitHub (for creating PRs)
GITHUB_TOKEN=ghp_your-actual-github-token-here
GITHUB_REPO_OWNER=jaiaggarwal
GITHUB_REPO_NAME=enricher-project

# Security (any random string)
WEBHOOK_SECRET=my-test-secret-123

# Optional (defaults are fine)
OPENAI_MODEL=gpt-4o
EMBEDDINGS_MODEL=all-MiniLM-L6-v2
LANCEDB_PATH=./.lancedb
GRAPH_PERSIST_PATH=./.graph.pkl
LOG_LEVEL=INFO
```

### Example 2: Testing Without GitHub PRs

If you just want to test indexing and investigation (no PR creation):

```env
# AI Provider
AI_PROVIDER=openai
OPENAI_API_KEY=sk-proj-your-actual-openai-key-here

# Your codebase
REPO_PATH=/Users/jaiaggarwal/atom/your-project

# Dummy GitHub values (PRs will fail but everything else works)
GITHUB_TOKEN=dummy-token
GITHUB_REPO_OWNER=dummy-owner
GITHUB_REPO_NAME=dummy-repo

# Security
WEBHOOK_SECRET=test-secret-123
```

---

## Step-by-Step Setup

### Step 1: Find Your Repository Path

```bash
# Go to your project
cd ~/atom/your-project  # or wherever your code is

# Get the full path
pwd
# Copy this output
```

### Step 2: Generate Webhook Secret

```bash
# Generate a random secret
openssl rand -hex 32
# Copy this output
```

### Step 3: Get GitHub Token

1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Name: "Archie AI"
4. Select: `repo` scope
5. Click "Generate token"
6. Copy the token (starts with `ghp_`)

### Step 4: Find GitHub Info

```bash
# If you have a git repo
cd /Users/jaiaggarwal/your-project
git remote -v

# Output will look like:
# origin  git@github.com:jaiaggarwal/my-project.git
#                        ^^^^^^^^^^^  ^^^^^^^^^^
#                        OWNER        REPO_NAME
```

### Step 5: Edit .env File

```bash
cd archie
cp .env.example .env
nano .env  # or use your favorite editor
```

Paste your values:
```env
OPENAI_API_KEY=sk-proj-YOUR-KEY-HERE
REPO_PATH=/Users/jaiaggarwal/atom/YOUR-PROJECT
GITHUB_TOKEN=ghp_YOUR-TOKEN-HERE
GITHUB_REPO_OWNER=YOUR-USERNAME
GITHUB_REPO_NAME=YOUR-REPO-NAME
WEBHOOK_SECRET=YOUR-RANDOM-SECRET
```

Save and exit (Ctrl+X, then Y, then Enter in nano).

---

## Verification

### Test Your Configuration

```bash
# 1. Check if repo path exists
ls -la $REPO_PATH

# 2. Check if .env is loaded
cd archie
python3 -c "from archie.config import settings; print(f'Repo: {settings.repo_path}')"

# 3. Start Archie
python -m archie.main
```

If it starts without errors, your configuration is correct!

---

## Troubleshooting

### Error: "REPO_PATH does not exist"

**Problem:** Path is wrong or doesn't exist

**Solution:**
```bash
# Find the correct path
cd /Users/jaiaggarwal
find . -name "report_generator.py" -type f
# Use the directory containing this file
```

### Error: "GitHub authentication failed"

**Problem:** GitHub token is invalid or expired

**Solution:**
1. Go to https://github.com/settings/tokens
2. Check if token exists and is not expired
3. Generate a new token if needed
4. Make sure `repo` scope is selected

### Error: "Invalid API key"

**Problem:** OpenAI API key is wrong

**Solution:**
1. Go to https://platform.openai.com/api-keys
2. Check if key exists
3. Generate a new key if needed
4. Make sure it starts with `sk-proj-` or `sk-`

### Error: "Repository not found"

**Problem:** GITHUB_REPO_OWNER or GITHUB_REPO_NAME is wrong

**Solution:**
```bash
# Check your GitHub URL
# If repo is at: https://github.com/jaiaggarwal/my-project
# Then:
GITHUB_REPO_OWNER=jaiaggarwal
GITHUB_REPO_NAME=my-project
```

---

## Quick Reference

| Setting | What It Is | How to Get It | Example |
|---------|-----------|---------------|---------|
| `REPO_PATH` | Your code location | `pwd` in your project | `/Users/jaiaggarwal/atom/project` |
| `WEBHOOK_SECRET` | Random security string | `openssl rand -hex 32` | `a1b2c3d4e5f6...` |
| `GITHUB_TOKEN` | GitHub access token | github.com/settings/tokens | `ghp_xxxx...` |
| `GITHUB_REPO_OWNER` | Your GitHub username | Your GitHub profile | `jaiaggarwal` |
| `GITHUB_REPO_NAME` | Your repo name | From GitHub URL | `my-project` |

---

## Minimal Configuration for Testing

If you just want to test Archie quickly:

```env
# Required
AI_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
REPO_PATH=/Users/jaiaggarwal/atom/your-project

# Optional (use dummy values)
GITHUB_TOKEN=test
GITHUB_REPO_OWNER=test
GITHUB_REPO_NAME=test
WEBHOOK_SECRET=test-secret
```

This will let you:
- ✅ Index your codebase
- ✅ View 3D graph
- ✅ Search semantically
- ✅ Investigate incidents
- ❌ Create PRs (will fail)

---

## Security Best Practices

1. **Never commit .env to git**
   ```bash
   # .env is already in .gitignore
   git status  # Should NOT show .env
   ```

2. **Use environment-specific tokens**
   - Development: Short-lived tokens
   - Production: Rotate every 90 days

3. **Limit token permissions**
   - Only select `repo` scope
   - Don't give admin access

4. **Keep secrets secret**
   - Don't share in Slack/email
   - Don't paste in public forums
   - Use password manager

---

## Next Steps

After configuration:

```bash
# 1. Verify configuration
cd archie
python3 -c "from archie.config import settings; print('Config OK')"

# 2. Start Archie
python -m archie.main

# 3. Test indexing
curl -X POST http://localhost:8000/index/trigger

# 4. Check status
curl http://localhost:8000/index/status
```

**See:** `QUICK_START.md` for next steps

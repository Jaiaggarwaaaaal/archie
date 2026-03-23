# Installation Guide - Quick Fix

## The Problem

You're getting `ModuleNotFoundError: No module named 'archie'` because:
1. Python dependencies are not installed yet
2. You need to run commands from the correct directory

## Quick Fix (5 minutes)

### Step 1: Install Dependencies

```bash
# Make sure you're in the archie directory
cd /Users/jaiaggarwal/atom/archie

# Install all required packages
pip3 install -r requirements.txt
```

This will install:
- FastAPI (web server)
- OpenAI/Anthropic (AI providers)
- LanceDB (vector database)
- Tree-sitter (code parser)
- And all other dependencies

**Expected output:**
```
Successfully installed fastapi-0.109.0 anthropic-0.18.0 openai-1.12.0 ...
```

### Step 2: Verify Installation

```bash
# Check if packages are installed
pip3 list | grep fastapi
pip3 list | grep openai
```

You should see the packages listed.

### Step 3: Test Configuration

```bash
# Go to PARENT directory (not inside archie/)
cd /Users/jaiaggarwal/atom

# Now test the config
python3 -c "from archie.config import settings; print('Config OK')"
```

**Important:** Run this from `/Users/jaiaggarwal/atom` (parent directory), NOT from `/Users/jaiaggarwal/atom/archie`

### Step 4: Start Archie

```bash
# From the parent directory
cd /Users/jaiaggarwal/atom

# Start Archie
python3 -m archie.main
```

## Why This Happens

Python needs to find the `archie` module. The directory structure is:

```
/Users/jaiaggarwal/atom/
├── archie/              ← This is the Python package
│   ├── __init__.py
│   ├── config.py
│   ├── main.py
│   ├── api/
│   ├── engine/
│   └── incident/
```

When you run `python3 -c "from archie.config import settings"`:
- Python looks for a folder named `archie` in the current directory
- If you're INSIDE `archie/`, it can't find itself
- You need to be in the PARENT directory (`/Users/jaiaggarwal/atom`)

## Complete Installation Steps

### 1. Install Python Dependencies

```bash
cd /Users/jaiaggarwal/atom/archie
pip3 install -r requirements.txt
```

**If you get permission errors:**
```bash
pip3 install --user -r requirements.txt
```

**If you want to use a virtual environment (recommended):**
```bash
cd /Users/jaiaggarwal/atom/archie
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cd /Users/jaiaggarwal/atom/archie

# Option A: Interactive setup (recommended)
chmod +x setup_config.sh
./setup_config.sh

# Option B: Manual setup
cp .env.example .env
nano .env  # Edit with your values
```

**Minimum required in .env:**
```env
AI_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
REPO_PATH=/Users/jaiaggarwal/atom/your-project
GITHUB_TOKEN=dummy-token
GITHUB_REPO_OWNER=dummy
GITHUB_REPO_NAME=dummy
WEBHOOK_SECRET=test-secret
```

### 3. Verify Everything Works

```bash
# Go to parent directory
cd /Users/jaiaggarwal/atom

# Test import
python3 -c "from archie.config import settings; print(f'Repo: {settings.repo_path}')"

# Start Archie
python3 -m archie.main
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

### 4. Test in Browser

Open: http://localhost:8000/health

You should see:
```json
{"status": "healthy"}
```

## Troubleshooting

### Error: "pip3: command not found"

**Solution:**
```bash
# Install pip
python3 -m ensurepip --upgrade

# Or use easy_install
sudo easy_install pip
```

### Error: "Permission denied"

**Solution:**
```bash
# Install for user only
pip3 install --user -r requirements.txt

# Or use virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Error: "No module named 'archie'" (after installing)

**Solution:**
```bash
# Make sure you're in the PARENT directory
cd /Users/jaiaggarwal/atom  # NOT /Users/jaiaggarwal/atom/archie

# Then run
python3 -m archie.main
```

### Error: "tree-sitter build failed"

**Solution:**
```bash
# Install build tools on macOS
xcode-select --install

# Then retry
pip3 install -r requirements.txt
```

### Error: "Port 8000 already in use"

**Solution:**
```bash
# Find what's using port 8000
lsof -i :8000

# Kill it
kill -9 <PID>

# Or use a different port
python3 -m archie.main --port 8001
```

## Quick Commands Reference

```bash
# Install dependencies
cd /Users/jaiaggarwal/atom/archie
pip3 install -r requirements.txt

# Configure
./setup_config.sh

# Start Archie (from parent directory)
cd /Users/jaiaggarwal/atom
python3 -m archie.main

# Test in another terminal
curl http://localhost:8000/health
curl -X POST http://localhost:8000/index/trigger
```

## Using Virtual Environment (Recommended)

Virtual environments keep dependencies isolated:

```bash
# Create virtual environment
cd /Users/jaiaggarwal/atom/archie
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Now run Archie (from parent directory)
cd /Users/jaiaggarwal/atom
python -m archie.main

# When done, deactivate
deactivate
```

## Next Steps

After installation:

1. **Configure:** Edit `.env` with your API keys
2. **Start:** `python3 -m archie.main`
3. **Test:** Follow `QUICK_START.md`
4. **Index:** `curl -X POST http://localhost:8000/index/trigger`
5. **Explore:** Open http://localhost:8000/graph/3d

## Need Help?

- Configuration help: `CONFIGURATION_GUIDE.md`
- Quick start: `QUICK_START.md`
- Troubleshooting: `TROUBLESHOOTING.md`
- All docs: `DOCUMENTATION_INDEX.md`

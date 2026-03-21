#!/bin/bash
# Interactive configuration setup for Archie

echo "🤖 Archie Configuration Setup"
echo "=============================="
echo ""

# Check if .env already exists
if [ -f .env ]; then
    echo "⚠️  .env file already exists!"
    read -p "Do you want to overwrite it? (y/n): " overwrite
    if [ "$overwrite" != "y" ]; then
        echo "Exiting without changes."
        exit 0
    fi
fi

# Copy example
cp .env.example .env

echo "Let's configure Archie step by step..."
echo ""

# 1. AI Provider
echo "1️⃣  AI Provider"
echo "   Which AI provider do you want to use?"
echo "   a) OpenAI (default, recommended)"
echo "   b) Anthropic Claude"
read -p "   Choice (a/b): " ai_choice

if [ "$ai_choice" = "b" ]; then
    AI_PROVIDER="anthropic"
    echo ""
    read -p "   Enter your Anthropic API key (starts with sk-ant-): " ANTHROPIC_KEY
    sed -i.bak "s/AI_PROVIDER=openai/AI_PROVIDER=anthropic/" .env
    sed -i.bak "s/ANTHROPIC_API_KEY=/ANTHROPIC_API_KEY=$ANTHROPIC_KEY/" .env
else
    echo ""
    read -p "   Enter your OpenAI API key (starts with sk-): " OPENAI_KEY
    sed -i.bak "s/OPENAI_API_KEY=/OPENAI_API_KEY=$OPENAI_KEY/" .env
fi

echo "   ✅ AI provider configured"
echo ""

# 2. Repository Path
echo "2️⃣  Repository Path"
echo "   Where is your codebase located?"
echo "   Current directory: $(pwd)"
echo ""
read -p "   Enter full path to your project (or press Enter to browse): " REPO_PATH

if [ -z "$REPO_PATH" ]; then
    echo "   Common locations:"
    echo "   - ~/atom/"
    echo "   - ~/Documents/"
    echo "   - ~/Projects/"
    ls -d ~/atom/* 2>/dev/null | head -5
    echo ""
    read -p "   Enter full path: " REPO_PATH
fi

# Expand ~ to full path
REPO_PATH="${REPO_PATH/#\~/$HOME}"

# Verify path exists
if [ ! -d "$REPO_PATH" ]; then
    echo "   ⚠️  Warning: Directory does not exist: $REPO_PATH"
    read -p "   Continue anyway? (y/n): " continue
    if [ "$continue" != "y" ]; then
        echo "   Please create the directory first or provide correct path."
        exit 1
    fi
fi

sed -i.bak "s|REPO_PATH=|REPO_PATH=$REPO_PATH|" .env
echo "   ✅ Repository path set to: $REPO_PATH"
echo ""

# 3. Webhook Secret
echo "3️⃣  Webhook Secret"
echo "   Generating random secret..."
WEBHOOK_SECRET=$(openssl rand -hex 32 2>/dev/null || python3 -c "import secrets; print(secrets.token_hex(32))" 2>/dev/null || echo "random-secret-$(date +%s)")
sed -i.bak "s/WEBHOOK_SECRET=/WEBHOOK_SECRET=$WEBHOOK_SECRET/" .env
echo "   ✅ Webhook secret generated"
echo ""

# 4. GitHub Configuration
echo "4️⃣  GitHub Configuration"
echo "   Do you want to enable GitHub PR creation?"
read -p "   (y/n): " enable_github

if [ "$enable_github" = "y" ]; then
    echo ""
    echo "   📝 To get a GitHub token:"
    echo "   1. Go to: https://github.com/settings/tokens"
    echo "   2. Click 'Generate new token (classic)'"
    echo "   3. Select 'repo' scope"
    echo "   4. Copy the token (starts with ghp_)"
    echo ""
    read -p "   Enter GitHub token: " GITHUB_TOKEN
    
    echo ""
    echo "   📝 GitHub repository info:"
    echo "   If your repo is at: https://github.com/username/repo-name"
    echo "   Then owner=username, name=repo-name"
    echo ""
    read -p "   Enter GitHub username/organization: " GITHUB_OWNER
    read -p "   Enter repository name: " GITHUB_REPO
    
    sed -i.bak "s/GITHUB_TOKEN=/GITHUB_TOKEN=$GITHUB_TOKEN/" .env
    sed -i.bak "s/GITHUB_REPO_OWNER=/GITHUB_REPO_OWNER=$GITHUB_OWNER/" .env
    sed -i.bak "s/GITHUB_REPO_NAME=/GITHUB_REPO_NAME=$GITHUB_REPO/" .env
    
    echo "   ✅ GitHub configured"
else
    echo "   ⚠️  Skipping GitHub configuration (PR creation will not work)"
    sed -i.bak "s/GITHUB_TOKEN=/GITHUB_TOKEN=dummy-token/" .env
    sed -i.bak "s/GITHUB_REPO_OWNER=/GITHUB_REPO_OWNER=dummy-owner/" .env
    sed -i.bak "s/GITHUB_REPO_NAME=/GITHUB_REPO_NAME=dummy-repo/" .env
fi

echo ""

# Clean up backup files
rm -f .env.bak

# Summary
echo "=============================="
echo "✅ Configuration Complete!"
echo "=============================="
echo ""
echo "Configuration saved to: .env"
echo ""
echo "Summary:"
echo "--------"
if [ "$ai_choice" = "b" ]; then
    echo "AI Provider: Anthropic Claude"
else
    echo "AI Provider: OpenAI"
fi
echo "Repository: $REPO_PATH"
if [ "$enable_github" = "y" ]; then
    echo "GitHub: Enabled ($GITHUB_OWNER/$GITHUB_REPO)"
else
    echo "GitHub: Disabled"
fi
echo ""
echo "Next steps:"
echo "1. Verify configuration: cat .env"
echo "2. Start Archie: python -m archie.main"
echo "3. Test indexing: curl -X POST http://localhost:8000/index/trigger"
echo ""
echo "For detailed help, see: CONFIGURATION_GUIDE.md"
echo ""

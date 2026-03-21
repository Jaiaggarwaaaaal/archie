#!/bin/bash
# One-command installer for Archie

echo "🤖 Installing Archie..."
echo "======================"
echo ""

# Check Python version
echo "1. Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "   Found: Python $PYTHON_VERSION"

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "   ❌ Error: requirements.txt not found"
    echo "   Please run this script from the archie directory"
    exit 1
fi

# Install dependencies
echo ""
echo "2. Installing Python dependencies..."
echo "   This may take 2-3 minutes..."
pip3 install -r requirements.txt --quiet

if [ $? -eq 0 ]; then
    echo "   ✅ Dependencies installed successfully"
else
    echo "   ⚠️  Some packages failed to install"
    echo "   Trying with --user flag..."
    pip3 install --user -r requirements.txt --quiet
fi

# Verify installation
echo ""
echo "3. Verifying installation..."
python3 -c "import fastapi, anthropic, openai, lancedb" 2>/dev/null

if [ $? -eq 0 ]; then
    echo "   ✅ All packages verified"
else
    echo "   ⚠️  Some packages missing, but continuing..."
fi

# Check if .env exists
echo ""
echo "4. Checking configuration..."
if [ -f ".env" ]; then
    echo "   ✅ .env file exists"
else
    echo "   ⚠️  .env file not found"
    echo "   Creating from template..."
    cp .env.example .env
    echo "   ✅ Created .env file"
    echo ""
    echo "   ⚠️  IMPORTANT: Edit .env with your API keys!"
    echo "   Run: nano .env"
fi

# Summary
echo ""
echo "======================"
echo "✅ Installation Complete!"
echo "======================"
echo ""
echo "Next steps:"
echo "1. Configure: nano .env (add your API keys)"
echo "2. Go to parent directory: cd .."
echo "3. Start Archie: python3 -m archie.main"
echo "4. Test: curl http://localhost:8000/health"
echo ""
echo "For detailed help, see: INSTALL.md"
echo ""

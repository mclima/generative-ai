#!/bin/bash

echo "🧞 NewsGenie Setup Script"
echo "=========================="
echo ""

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"
echo ""

echo "📦 Creating virtual environment..."
python3 -m venv venv

echo "✅ Virtual environment created"
echo ""

echo "🔧 Activating virtual environment..."
source venv/bin/activate

echo "✅ Virtual environment activated"
echo ""

echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Dependencies installed"
echo ""

if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env and add your API keys:"
    echo "   - OPENAI_API_KEY"
    echo "   - GNEWS_API_KEY"
    echo "   - TAVILY_API_KEY"
    echo ""
else
    echo "ℹ️  .env file already exists"
    echo ""
fi

echo "🎉 Setup complete!"
echo ""
echo "📚 Next steps:"
echo "   1. Edit .env and add your API keys"
echo "   2. Activate virtual environment: source venv/bin/activate"
echo "   3. Run the app: streamlit run app.py"
echo ""
echo "🔗 Get API keys from:"
echo "   - OpenAI: https://platform.openai.com/api-keys"
echo "   - GNews: https://gnews.io/"
echo "   - Tavily: https://tavily.com/"
echo ""

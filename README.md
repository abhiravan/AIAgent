# 🚀 Fetch and Fix Agent - AI-Powered Issue Analysis

**Intelligent Jira issue analysis with Azure OpenAI and GitHub integration for the MEBP pricing pipeline.**

## ⚡ Quick Start

```bash
# 1. Install dependencies
pip install flask requests python-dotenv

# 2. Configure environment (see docs/configuration.md)
cp .env.example .env
# Edit .env with your API keys

# 3. Run the application
python fetch_and_fix_agent.py

# 4. Open browser
# http://127.0.0.1:5000
```

## 🎯 Features

- **🤖 AI-Powered Analysis**: Azure OpenAI analyzes issues with project context
- **🐙 GitHub Integration**: Repository-aware insights and file identification  
- **🎫 Jira Integration**: Seamless issue fetching and processing
- **🌐 Web Interface**: Modern, responsive Bootstrap UI
- **🔧 MEBP-Specific**: Trained on Databricks, PySpark, and MongoDB patterns

## 📁 Project Structure

```
📦 AIAgent/
├── 🌐 fetch_and_fix_agent.py       # Main Flask application
├── 📁 services/                    # External API integrations
│   ├── jira_service.py            # Jira API client
│   ├── ai_service.py              # Azure OpenAI integration
│   └── github_service.py          # GitHub API client
├── 📁 tests/                       # Testing & utilities
├── 📁 templates/                   # Web interface
├── 📁 docs/                        # 📚 Documentation
└── 📁 .github/                     # GitHub configuration
```

## 📚 Documentation

Comprehensive documentation is available in the [`docs/`](./docs/) folder:

- **[📖 Quick Start Guide](./docs/QUICK_START.md)** - Get up and running fast
- **[🏗️ Project Structure](./docs/PROJECT_STRUCTURE.md)** - Detailed architecture overview  
- **[🤖 AI Integration Guide](./docs/README_AI_Integration.md)** - AI setup and configuration
- **[🎯 Success Summary](./docs/SUCCESS_SUMMARY.md)** - Implementation achievements
- **[🔧 Fetch and Fix Setup](./docs/README_FetchAndFix.md)** - Original setup guide

## 🚀 Usage

1. **Fetch Jira Issue**: Enter issue key (e.g., `MEBP-123`)
2. **Analyze with AI**: Click "Analyze Issue" for intelligent insights
3. **Review Results**: Get root cause, affected files, and fix strategy
4. **Generate Fixes**: Use traditional fix suggestions alongside AI analysis

## 🔧 Configuration Required

- **Jira API**: Base URL, email, and API token
- **Azure OpenAI**: Endpoint, API key, and deployment name
- **GitHub**: Repository URL, username, and personal access token

See [AI Integration Guide](./docs/README_AI_Integration.md) for detailed setup instructions.

## 🎯 AI Analysis Capabilities

The AI provides:
- **Root Cause Analysis**: Intelligent issue diagnosis
- **File Identification**: Specific files needing investigation
- **Fix Strategy**: Step-by-step resolution approach
- **Priority Assessment**: Urgency and effort estimation
- **Testing Plan**: Comprehensive validation recommendations

## 🏢 MEBP Project Context

Specifically designed for the **MEBP Pricing Data Pipeline**:
- Understands Databricks notebook patterns
- Recognizes PySpark DataFrame transformations
- Knows MongoDB collection structures
- Applies pricing pipeline best practices

## 🛠️ Development

```bash
# Run tests
python tests/test_ai_integration.py

# Demo AI analysis
python tests/demo_ai_analysis.py

# Validate syntax
python tests/check_syntax.py

# Configure APIs
python tests/configure_ai.py
```

## 📄 License

Internal Safeway project for MEBP pricing pipeline analysis and troubleshooting.

---

**🎉 Ready to revolutionize your issue analysis workflow!** Start by reading the [Quick Start Guide](./docs/QUICK_START.md).
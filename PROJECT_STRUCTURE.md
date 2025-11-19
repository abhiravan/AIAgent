# 📁 Project Structure - Fetch and Fix Agent

## 🏗️ **Organized Project Layout**

```
AIAgent/
├── 📄 fetch_and_fix_agent.py          # Main Flask application
├── 📄 .env                            # Environment configuration (not in Git)
├── 📄 .env.example                    # Environment template
├── 📄 .gitignore                      # Git ignore rules
├── 📄 requirements.txt                # Python dependencies
├── 📄 README_*.md                     # Documentation files
├── 
├── 📁 services/                       # 🔧 Service Layer
│   ├── __init__.py                    # Package initialization
│   ├── jira_service.py               # Jira API integration
│   ├── ai_service.py                 # Azure OpenAI integration  
│   └── github_service.py             # GitHub API integration
├── 
├── 📁 tests/                          # 🧪 Testing & Utilities
│   ├── __init__.py                    # Package initialization
│   ├── test_ai_integration.py        # Comprehensive integration tests
│   ├── demo_ai_analysis.py           # AI analysis demonstration
│   ├── configure_ai.py               # Configuration setup utility
│   └── check_syntax.py               # Syntax validation utility
├── 
├── 📁 templates/                      # 🌐 Web Templates
│   └── index.html                     # Main web interface
├── 
├── 📁 .github/                        # 🤖 GitHub Configuration
│   └── copilot-instructions.md       # AI coding guidelines
└── 
└── 📁 [Original Files]/               # 📊 Original MEBP Files
    ├── nt_msp_priceArea_load.py      # Databricks notebook
    ├── nt_msp_priceArea_query.py     # SQL queries
    ├── nt_pchg_audit.py              # Audit processing
    ├── complex_promo.sql             # Complex promotion queries
    └── price_load.py                  # Price loading utilities
```

## 🎯 **Benefits of This Structure**

### **🔧 Services Package (`/services/`)**
- **Centralized**: All external API integrations in one place
- **Modular**: Each service handles one responsibility (Jira, AI, GitHub)
- **Reusable**: Services can be imported and used across the application
- **Testable**: Easy to mock and test individual services
- **Maintainable**: Changes to APIs are isolated to specific files

### **🧪 Tests Package (`/tests/`)**
- **Organized**: All testing, demo, and utility scripts together
- **Isolated**: Testing code separated from production code
- **Comprehensive**: Integration tests, demos, and configuration tools
- **Development**: Helper scripts for setup and validation

### **🌐 Templates Folder**
- **Web Assets**: HTML templates for the Flask application
- **UI Components**: Centralized location for all frontend code

## 📋 **Import Structure**

### **Main Application**
```python
# fetch_and_fix_agent.py
from services.jira_service import JiraService
from services.ai_service import AIService
from services.github_service import GitHubService
```

### **Testing Files**
```python
# tests/test_ai_integration.py
from services.ai_service import AIService
from services.github_service import GitHubService
```

### **Package Initialization**
```python
# services/__init__.py
from .jira_service import JiraService
from .ai_service import AIService
from .github_service import GitHubService
```

## 🚀 **Running the Application**

### **Main Application**
```bash
# From project root
python fetch_and_fix_agent.py
```

### **Tests and Utilities**
```bash
# Integration tests
python tests/test_ai_integration.py

# AI Demo
python tests/demo_ai_analysis.py

# Configuration setup
python tests/configure_ai.py

# Syntax validation
python tests/check_syntax.py
```

## 🎯 **File Responsibilities**

### **Core Application**
- `fetch_and_fix_agent.py` - Flask app with routes and main logic
- `.env` - Environment configuration (secrets, API keys)
- `requirements.txt` - Python package dependencies

### **Services Layer** 
- `jira_service.py` - Jira API client (fetch issues, test connection)
- `ai_service.py` - Azure OpenAI integration (issue analysis, prompt engineering)
- `github_service.py` - GitHub API client (repository files, code search)

### **Testing & Utilities**
- `test_ai_integration.py` - Complete system testing suite  
- `demo_ai_analysis.py` - Interactive demonstration of AI capabilities
- `configure_ai.py` - Guided setup for API keys and configuration
- `check_syntax.py` - Python syntax validation across all files

### **Web Interface**
- `templates/index.html` - Responsive Bootstrap UI with AI analysis features

This structure provides clear separation of concerns, making the codebase more maintainable, testable, and scalable! 🎉
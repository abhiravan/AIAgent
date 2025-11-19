"""
Configuration helper for Azure OpenAI and GitHub integration
This script helps set up the required environment variables
"""

import os
import json
from pathlib import Path

def setup_azure_openai():
    """Guide through Azure OpenAI setup"""
    print("🔧 Azure OpenAI Configuration Setup")
    print("=" * 40)
    
    print("\n📋 You need to provide the following information:")
    print("1. Azure OpenAI Endpoint URL")
    print("2. Azure OpenAI API Key")
    print("3. API Version (usually 2023-07-01-preview)")
    print("4. Deployment Name for your GPT model")
    
    print(f"\n✅ Current endpoint: https://mestk-eus-ai-01.openai.azure.com/")
    print(f"✅ Current API version: 2023-07-01-preview")
    print(f"✅ Current deployment: mestk-gpt-35-deployment")
    
    print(f"\n⚠️ You need to provide your actual Azure OpenAI API key")
    print("To get your API key:")
    print("1. Go to Azure Portal (https://portal.azure.com)")
    print("2. Navigate to your Azure OpenAI resource 'mestk-eus-ai-01'")
    print("3. Click on 'Keys and Endpoint' in the left sidebar")
    print("4. Copy 'KEY 1' or 'KEY 2'")
    
    api_key = input("\n🔑 Enter your Azure OpenAI API Key: ").strip()
    
    if api_key:
        return {
            'AZURE_OPENAI_ENDPOINT': 'https://mestk-eus-ai-01.openai.azure.com/',
            'AZURE_OPENAI_API_KEY': api_key,
            'AZURE_OPENAI_API_VERSION': '2023-07-01-preview',
            'AZURE_OPENAI_DEPLOYMENT_NAME': 'mestk-gpt-35-deployment'
        }
    else:
        print("❌ API key is required for Azure OpenAI integration")
        return None

def setup_github():
    """Guide through GitHub setup"""
    print("\n🐙 GitHub Configuration Setup")
    print("=" * 40)
    
    print("\n📋 You need to provide:")
    print("1. Your GitHub repository URL")
    print("2. Your GitHub username")
    print("3. GitHub Personal Access Token")
    
    repo_url = input("\n📁 Enter repository URL (e.g., https://github.com/owner/repo): ").strip()
    if not repo_url:
        repo_url = "https://github.com/abhiravan/AIAgent"  # Default to current repo
        print(f"Using default: {repo_url}")
    
    username = input("👤 Enter your GitHub username: ").strip()
    
    print("\n🔑 To create a GitHub Personal Access Token:")
    print("1. Go to GitHub Settings → Developer settings → Personal access tokens")
    print("2. Click 'Generate new token (classic)'")
    print("3. Select scopes: 'repo' (Full control of private repositories)")
    print("4. Copy the generated token")
    
    token = input("\n🎫 Enter your GitHub Personal Access Token: ").strip()
    
    if repo_url and username and token:
        return {
            'GITHUB_REPO_URL': repo_url,
            'GITHUB_USERNAME': username,
            'GITHUB_TOKEN': token
        }
    else:
        print("❌ All GitHub fields are required")
        return None

def update_env_file(config):
    """Update the .env file with new configuration"""
    env_file = Path('.env')
    
    # Read current .env file
    current_config = {}
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    current_config[key] = value
    
    # Update with new config
    current_config.update(config)
    
    # Write back to .env file
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write("# Environment variables for Fetch and Fix Agent\n")
        f.write("# AI-Powered Issue Analysis Configuration\n\n")
        
        # Flask config
        f.write("# Flask configuration\n")
        f.write(f"FLASK_SECRET_KEY={current_config.get('FLASK_SECRET_KEY', 'your-secret-key-here')}\n")
        f.write(f"FLASK_ENV={current_config.get('FLASK_ENV', 'development')}\n\n")
        
        # Jira config
        f.write("# Jira configuration\n")
        f.write(f"JIRA_BASE_URL={current_config.get('JIRA_BASE_URL', 'https://your-company.atlassian.net')}\n")
        f.write(f"JIRA_EMAIL={current_config.get('JIRA_EMAIL', 'your-email@company.com')}\n")
        f.write(f"JIRA_TOKEN={current_config.get('JIRA_TOKEN', 'your-jira-api-token')}\n\n")
        
        # Azure OpenAI config
        f.write("# Azure OpenAI Configuration\n")
        f.write(f"AZURE_OPENAI_ENDPOINT={current_config.get('AZURE_OPENAI_ENDPOINT', 'https://mestk-eus-ai-01.openai.azure.com/')}\n")
        f.write(f"AZURE_OPENAI_API_KEY={current_config.get('AZURE_OPENAI_API_KEY', 'your-azure-openai-api-key-here')}\n")
        f.write(f"AZURE_OPENAI_API_VERSION={current_config.get('AZURE_OPENAI_API_VERSION', '2023-07-01-preview')}\n")
        f.write(f"AZURE_OPENAI_DEPLOYMENT_NAME={current_config.get('AZURE_OPENAI_DEPLOYMENT_NAME', 'mestk-gpt-35-deployment')}\n\n")
        
        # GitHub config
        f.write("# GitHub Configuration\n")
        f.write(f"GITHUB_REPO_URL={current_config.get('GITHUB_REPO_URL', 'https://github.com/owner/repo')}\n")
        f.write(f"GITHUB_USERNAME={current_config.get('GITHUB_USERNAME', 'your-github-username')}\n")
        f.write(f"GITHUB_TOKEN={current_config.get('GITHUB_TOKEN', 'your-github-token')}\n\n")
        
        # Security note
        f.write("# SECURITY NOTE:\n")
        f.write("# - Never commit the .env file to version control\n")
        f.write("# - The .env file is already added to .gitignore for safety\n")
        f.write("# - Rotate tokens and keys regularly for security\n")
    
    print(f"✅ Configuration saved to {env_file}")

def test_configuration():
    """Test the configuration"""
    print("\n🧪 Testing configuration...")
    
    try:
        # Test environment loading
        from dotenv import load_dotenv
        load_dotenv()
        
        # Check Azure OpenAI config
        azure_config = [
            os.getenv('AZURE_OPENAI_ENDPOINT'),
            os.getenv('AZURE_OPENAI_API_KEY'),
            os.getenv('AZURE_OPENAI_API_VERSION'),
            os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME')
        ]
        
        if all(azure_config) and azure_config[1] != 'your-azure-openai-api-key-here':
            print("✅ Azure OpenAI configuration looks good")
            azure_ok = True
        else:
            print("❌ Azure OpenAI configuration incomplete")
            azure_ok = False
        
        # Check GitHub config
        github_config = [
            os.getenv('GITHUB_REPO_URL'),
            os.getenv('GITHUB_USERNAME'),
            os.getenv('GITHUB_TOKEN')
        ]
        
        if all(github_config) and github_config[2] != 'your-github-token':
            print("✅ GitHub configuration looks good")
            github_ok = True
        else:
            print("❌ GitHub configuration incomplete")
            github_ok = False
        
        return azure_ok and github_ok
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def main():
    """Main configuration setup"""
    print("🚀 AI-Powered Issue Analysis - Configuration Setup")
    print("=" * 55)
    
    print("\nThis script will help you configure:")
    print("• Azure OpenAI for intelligent issue analysis")
    print("• GitHub integration for repository context")
    
    proceed = input("\n❓ Do you want to proceed with configuration? (y/N): ").strip().lower()
    
    if proceed != 'y':
        print("Configuration cancelled.")
        return
    
    config_updates = {}
    
    # Setup Azure OpenAI
    azure_config = setup_azure_openai()
    if azure_config:
        config_updates.update(azure_config)
    else:
        print("Skipping Azure OpenAI configuration...")
    
    # Setup GitHub
    setup_github_option = input("\n❓ Do you want to configure GitHub integration? (Y/n): ").strip().lower()
    if setup_github_option != 'n':
        github_config = setup_github()
        if github_config:
            config_updates.update(github_config)
    
    if config_updates:
        # Update .env file
        update_env_file(config_updates)
        
        # Test configuration
        if test_configuration():
            print("\n🎉 Configuration completed successfully!")
            print("\n🚀 Next steps:")
            print("1. Run: python test_ai_integration.py")
            print("2. If tests pass, run: python fetch_and_fix_agent.py")
            print("3. Open: http://127.0.0.1:5000")
        else:
            print("\n⚠️ Configuration saved but some issues detected.")
            print("Please run: python test_ai_integration.py")
    else:
        print("\n❌ No configuration updates made.")

if __name__ == "__main__":
    main()
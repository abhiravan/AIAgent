"""
Test script for Azure OpenAI and GitHub integration
This script verifies that the AI service can analyze issues and identify relevant files
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_ai_service():
    """Test the AI service functionality"""
    try:
        from ai_service import AIService
        
        print("🧪 Testing AI Service...")
        ai_service = AIService()
        print("✅ AI Service initialized successfully")
        
        # Test with a sample Jira issue
        sample_issue = {
            'key': 'TEST-123',
            'summary': 'PySpark DataFrame transformation failing in price area processing',
            'description': 'The nt_msp_priceArea_load.py notebook is throwing errors when processing MongoDB collections. The _id field creation and nested JSON transformation are not working correctly. Data from BigQuery is being extracted successfully but the transformation step fails.',
            'issue_type': 'Bug',
            'priority': 'High',
            'status': 'Open',
            'assignee': 'test.user@company.com',
            'reporter': 'jira.user@company.com'
        }
        
        # Sample repository files (simulating GitHub response)
        sample_repo_files = [
            {'name': 'nt_msp_priceArea_load.py', 'type': 'file', 'path': 'nt_msp_priceArea_load.py', 'relevance': 'high'},
            {'name': 'nt_msp_priceArea_query.py', 'type': 'file', 'path': 'nt_msp_priceArea_query.py', 'relevance': 'high'},
            {'name': 'nt_user_defined_methods.py', 'type': 'file', 'path': 'General/nt_user_defined_methods.py', 'relevance': 'medium'},
            {'name': 'complex_promo.sql', 'type': 'file', 'path': 'complex_promo.sql', 'relevance': 'medium'},
            {'name': 'nt_pchg_audit.py', 'type': 'file', 'path': 'nt_pchg_audit.py', 'relevance': 'high'},
        ]
        
        print("🔍 Running AI analysis on sample issue...")
        result = ai_service.analyze_issue_with_context(sample_issue, sample_repo_files)
        
        if result.get('success', True) and not result.get('error'):
            print("✅ AI Analysis completed successfully!")
            print(f"🎯 Root Cause: {result.get('root_cause', 'N/A')[:100]}...")
            print(f"📁 Files Identified: {result.get('affected_files', [])}")
            print(f"⚡ Priority: {result.get('priority_level', 'N/A')}")
            print(f"⏱️ Estimated Effort: {result.get('estimated_effort', 'N/A')}")
            return True
        else:
            print(f"❌ AI Analysis failed: {result.get('error', 'Unknown error')}")
            return False
            
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("Make sure ai_service.py is in the current directory")
        return False
    except Exception as e:
        print(f"❌ AI Service Error: {e}")
        return False

def test_github_service():
    """Test the GitHub service functionality"""
    try:
        from github_service import GitHubService
        
        print("\n🐙 Testing GitHub Service...")
        github_service = GitHubService()
        print("✅ GitHub Service initialized successfully")
        
        # Test connection
        print("🔗 Testing GitHub connection...")
        connection_result = github_service.test_connection()
        
        if connection_result.get('success'):
            print(f"✅ Connected to repository: {connection_result.get('repository')}")
            print(f"📝 Description: {connection_result.get('description', 'N/A')}")
            print(f"💻 Language: {connection_result.get('language', 'N/A')}")
            
            # Test file listing
            print("📁 Fetching repository files...")
            files = github_service.get_repository_files()
            
            if files and not files[0].get('error'):
                print(f"✅ Found {len(files)} files")
                print("📄 Top files:")
                for file in files[:5]:
                    print(f"   - {file['name']} ({file['type']}) - {file.get('relevance', 'unknown')} relevance")
                return True
            else:
                print(f"❌ File listing failed: {files[0].get('error') if files else 'No files returned'}")
                return False
        else:
            print(f"❌ GitHub connection failed: {connection_result.get('error')}")
            return False
            
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("Make sure github_service.py is in the current directory")
        return False
    except Exception as e:
        print(f"❌ GitHub Service Error: {e}")
        return False

def test_environment_config():
    """Test environment configuration"""
    print("⚙️ Testing Environment Configuration...")
    
    required_vars = {
        'Azure OpenAI': ['AZURE_OPENAI_ENDPOINT', 'AZURE_OPENAI_API_KEY', 'AZURE_OPENAI_API_VERSION', 'AZURE_OPENAI_DEPLOYMENT_NAME'],
        'GitHub': ['GITHUB_REPO_URL', 'GITHUB_USERNAME', 'GITHUB_TOKEN'],
        'Jira': ['JIRA_BASE_URL', 'JIRA_EMAIL', 'JIRA_TOKEN']
    }
    
    all_configured = True
    
    for service, vars_list in required_vars.items():
        print(f"\n🔧 {service} Configuration:")
        service_configured = True
        
        for var in vars_list:
            value = os.getenv(var)
            if value and value != f"your-{var.lower().replace('_', '-')}-here":
                print(f"  ✅ {var}: {'*' * min(len(value), 20)}...")
            else:
                print(f"  ❌ {var}: Not configured")
                service_configured = False
                all_configured = False
        
        if service_configured:
            print(f"  🎉 {service} is fully configured!")
        else:
            print(f"  ⚠️ {service} needs configuration")
    
    return all_configured

def test_flask_integration():
    """Test Flask application endpoints"""
    print("\n🌐 Testing Flask Integration...")
    
    try:
        import requests
        import json
        import subprocess
        import time
        
        # Start Flask app in background
        print("🚀 Starting Flask application...")
        
        # Test if Flask is already running
        try:
            response = requests.get('http://127.0.0.1:5000/', timeout=2)
            print("✅ Flask app is already running")
            app_running = True
        except:
            print("⚠️ Flask app not running. Please start it manually with: python fetch_and_fix_agent.py")
            app_running = False
        
        if app_running:
            # Test main page
            try:
                response = requests.get('http://127.0.0.1:5000/')
                if response.status_code == 200:
                    print("✅ Main page accessible")
                else:
                    print(f"❌ Main page returned status: {response.status_code}")
            except Exception as e:
                print(f"❌ Main page test failed: {e}")
            
            # Test GitHub connection endpoint
            try:
                response = requests.get('http://127.0.0.1:5000/test_github', timeout=10)
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success'):
                        print(f"✅ GitHub test endpoint working: {result.get('repository', 'Unknown repo')}")
                    else:
                        print(f"⚠️ GitHub test returned: {result.get('error', 'Unknown error')}")
                else:
                    print(f"❌ GitHub test endpoint returned status: {response.status_code}")
            except Exception as e:
                print(f"❌ GitHub test endpoint failed: {e}")
        
        return app_running
        
    except ImportError:
        print("❌ requests library not available for Flask testing")
        return False
    except Exception as e:
        print(f"❌ Flask integration test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 AI-Powered Issue Analysis - Integration Test")
    print("=" * 50)
    
    # Test environment configuration
    env_ok = test_environment_config()
    
    if not env_ok:
        print("\n⚠️ Some environment variables are not configured.")
        print("Please update your .env file with the correct values.")
        print("See .env.example for the required format.")
    
    print("\n" + "=" * 50)
    
    # Test individual services
    ai_ok = test_ai_service()
    github_ok = test_github_service()
    flask_ok = test_flask_integration()
    
    print("\n" + "=" * 50)
    print("📋 Test Summary:")
    print(f"  Environment Config: {'✅ Pass' if env_ok else '❌ Fail'}")
    print(f"  AI Service: {'✅ Pass' if ai_ok else '❌ Fail'}")
    print(f"  GitHub Service: {'✅ Pass' if github_ok else '❌ Fail'}")
    print(f"  Flask Integration: {'✅ Pass' if flask_ok else '❌ Fail'}")
    
    if all([env_ok, ai_ok, github_ok, flask_ok]):
        print("\n🎉 All tests passed! The AI integration is ready to use.")
        print("\n🚀 Next steps:")
        print("  1. Run: python fetch_and_fix_agent.py")
        print("  2. Open: http://127.0.0.1:5000")
        print("  3. Fetch a Jira issue and click 'Analyze Issue'")
    else:
        print("\n⚠️ Some tests failed. Please check the configuration and try again.")
        
        if not env_ok:
            print("  - Update .env file with correct API keys and tokens")
        if not ai_ok:
            print("  - Verify Azure OpenAI credentials and endpoint")
        if not github_ok:
            print("  - Check GitHub repository URL and token permissions")
        if not flask_ok:
            print("  - Ensure Flask dependencies are installed")

if __name__ == "__main__":
    main()
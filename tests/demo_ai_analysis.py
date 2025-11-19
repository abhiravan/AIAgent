"""
Demo script showing AI-powered issue analysis in action
This demonstrates how the AI analyzes issues and identifies relevant files
"""

import requests
import json

def demo_ai_analysis():
    """Demonstrate AI analysis with a sample MEBP-related issue"""
    
    print("🎯 AI-Powered Issue Analysis Demo")
    print("=" * 45)
    
    # Sample Jira issue data (similar to MEBP pricing pipeline issues)
    sample_issue = {
        "key": "MEBP-456",
        "summary": "MongoDB collection write failing in priceArea pipeline",
        "description": """
        The nt_msp_priceArea_load.py notebook is encountering errors when writing 
        transformed data to MongoDB collections. The PySpark DataFrame processing 
        completes successfully, but the mongodb_Write_with_df function fails during 
        the final write operation.
        
        Error details:
        - BigQuery extraction works fine
        - DataFrame transformations complete without errors  
        - Nested JSON structure creation appears correct
        - MongoDB write operation times out or fails
        - Issue occurs specifically with priceArea collection
        
        Stack trace shows connection timeout to MongoDB cluster. Need to investigate:
        1. Connection string configuration
        2. Network connectivity issues
        3. MongoDB collection permissions
        4. Data volume impact on write performance
        """,
        "issue_type": "Bug",
        "priority": "High", 
        "status": "Open",
        "assignee": "data.engineer@safeway.com",
        "reporter": "product.owner@safeway.com",
        "created": "2025-11-18T10:30:00Z",
        "updated": "2025-11-18T14:15:00Z"
    }
    
    print("📋 Sample Issue Details:")
    print(f"  🎫 Key: {sample_issue['key']}")
    print(f"  📝 Summary: {sample_issue['summary']}")
    print(f"  ⚡ Priority: {sample_issue['priority']}")
    print(f"  📊 Type: {sample_issue['issue_type']}")
    
    print(f"\n📄 Description Preview:")
    desc_preview = sample_issue['description'][:200].replace('\n', ' ').strip()
    print(f"  {desc_preview}...")
    
    # Test the analyze endpoint
    try:
        print(f"\n🤖 Sending to AI for analysis...")
        
        url = "http://127.0.0.1:5000/analyze_issue"
        payload = {"issue_data": sample_issue}
        
        response = requests.post(url, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('success'):
                analysis = result['analysis']
                
                print("✅ AI Analysis Results:")
                print("=" * 25)
                
                print(f"\n🔍 Root Cause Analysis:")
                print(f"   {analysis.get('root_cause', 'Not provided')}")
                
                print(f"\n📁 Files to Investigate:")
                files = analysis.get('affected_files', [])
                for i, file in enumerate(files, 1):
                    print(f"   {i}. {file}")
                
                print(f"\n⚡ Priority Level: {analysis.get('priority_level', 'Not specified')}")
                print(f"⏱️ Estimated Effort: {analysis.get('estimated_effort', 'Not specified')}")
                
                fix_strategy = analysis.get('fix_strategy', [])
                if fix_strategy:
                    print(f"\n🛠️ Fix Strategy:")
                    for i, step in enumerate(fix_strategy, 1):
                        print(f"   {i}. {step}")
                
                testing_plan = analysis.get('testing_plan', [])
                if testing_plan:
                    print(f"\n✅ Testing Plan:")
                    for i, test in enumerate(testing_plan, 1):
                        print(f"   {i}. {test}")
                
                print(f"\n🎯 Summary:")
                print(f"   The AI has successfully analyzed the MongoDB write issue")
                print(f"   and identified {len(files)} relevant files for investigation.")
                print(f"   Priority: {analysis.get('priority_level', 'TBD')}")
                print(f"   Effort: {analysis.get('estimated_effort', 'TBD')}")
                
            else:
                print(f"❌ Analysis failed: {result.get('error', 'Unknown error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏱️ Request timed out - AI analysis may take longer for complex issues")
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - make sure Flask app is running on http://127.0.0.1:5000")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_github_context():
    """Test GitHub context retrieval"""
    print(f"\n🐙 Testing GitHub Context Retrieval")
    print("=" * 35)
    
    try:
        url = "http://127.0.0.1:5000/test_github"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('success'):
                print("✅ GitHub Integration Working:")
                print(f"   📁 Repository: {result.get('repository')}")
                print(f"   💻 Language: {result.get('language')}")
                print(f"   🔒 Private: {result.get('private')}")
                print(f"   📅 Last Updated: {result.get('last_updated', 'N/A')}")
            else:
                print(f"❌ GitHub test failed: {result.get('error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ GitHub test error: {e}")

def main():
    """Run the demo"""
    print("🚀 Welcome to the AI-Powered Issue Analysis Demo!")
    print("\nThis demo shows how the AI analyzes MEBP pricing pipeline issues")
    print("and provides intelligent insights for troubleshooting.")
    
    # Test GitHub context first
    test_github_context()
    
    # Run AI analysis demo
    demo_ai_analysis()
    
    print(f"\n" + "=" * 50)
    print("🎉 Demo Complete!")
    print(f"\n💡 How to use this in the web interface:")
    print("  1. Open: http://127.0.0.1:5000")
    print("  2. Enter a Jira issue key (e.g., MEBP-123)")
    print("  3. Click 'Fetch' to get issue details")
    print("  4. Click 'Analyze Issue' for AI-powered insights")
    print("  5. Review the detailed analysis and recommendations")
    
    print(f"\n🔧 The AI considers:")
    print("  • Project context from copilot-instructions.md")
    print("  • Repository files and structure")
    print("  • Issue description and metadata")
    print("  • MEBP-specific patterns (Databricks, PySpark, MongoDB)")

if __name__ == "__main__":
    main()
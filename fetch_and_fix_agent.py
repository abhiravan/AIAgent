"""
Fetch and Fix Agent - A web UI for fetching Jira issues and generating fixes
"""

import os
from flask import Flask, render_template, request, jsonify
from jira_service import JiraService
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("python-dotenv not installed. Using system environment variables only.")

# Initialize Jira service
try:
    jira_service = JiraService()
    print("✅ Jira service initialized successfully")
except ValueError as e:
    print(f"❌ ERROR: {e}")
    print("Please set these environment variables:")
    print("  JIRA_BASE_URL=https://your-domain.atlassian.net")
    print("  JIRA_EMAIL=your-email@example.com")
    print("  JIRA_TOKEN=your-jira-api-token")
    print("Or create a .env file with these variables.")
    exit(1)

@app.route('/')
def index():
    """Main page with the Fetch and Fix Agent interface"""
    return render_template('index.html')

@app.route('/test_connection', methods=['GET'])
def test_connection():
    """Test Jira connection"""
    result = jira_service.test_connection()
    return jsonify(result)

@app.route('/fetch_issue', methods=['POST'])
def fetch_issue():
    """Fetch issue details from Jira"""
    data = request.get_json()
    issue_key = data.get('issue_key', '').strip().upper()
    
    if not issue_key:
        return jsonify({'success': False, 'error': 'Please provide a Jira issue key'})
    
    result = jira_service.get_issue(issue_key)
    return jsonify(result)

@app.route('/fix_issue', methods=['POST'])
def fix_issue():
    """Generate a fix suggestion for the issue"""
    data = request.get_json()
    issue_data = data.get('issue_data')
    
    if not issue_data:
        return jsonify({'success': False, 'error': 'No issue data provided'})
    
    # Generate fix suggestions based on the issue
    fix_suggestions = generate_fix_suggestions(issue_data)
    
    return jsonify({
        'success': True,
        'fix_suggestions': fix_suggestions
    })

def generate_fix_suggestions(issue_data):
    """Generate fix suggestions based on issue content"""
    summary = issue_data.get('summary', '').lower()
    description = issue_data.get('description', '').lower()
    
    suggestions = []
    
    # Common patterns and their suggestions
    if any(keyword in summary or keyword in description for keyword in ['bug', 'error', 'exception', 'crash']):
        suggestions.append({
            'type': 'Bug Fix',
            'priority': 'High',
            'suggestions': [
                '1. Review error logs and stack traces',
                '2. Add try-catch blocks for error handling',
                '3. Implement proper logging for debugging',
                '4. Add unit tests to reproduce the issue',
                '5. Consider edge cases and input validation'
            ]
        })
    
    if any(keyword in summary or keyword in description for keyword in ['performance', 'slow', 'timeout', 'optimization']):
        suggestions.append({
            'type': 'Performance Optimization',
            'priority': 'Medium',
            'suggestions': [
                '1. Profile the application to identify bottlenecks',
                '2. Optimize database queries and indexes',
                '3. Implement caching strategies',
                '4. Review memory usage and garbage collection',
                '5. Consider async processing for heavy operations'
            ]
        })
    
    if any(keyword in summary or keyword in description for keyword in ['security', 'vulnerability', 'auth', 'permission']):
        suggestions.append({
            'type': 'Security Fix',
            'priority': 'Critical',
            'suggestions': [
                '1. Review authentication and authorization logic',
                '2. Validate and sanitize all user inputs',
                '3. Implement proper session management',
                '4. Use parameterized queries to prevent SQL injection',
                '5. Apply principle of least privilege'
            ]
        })
    
    if any(keyword in summary or keyword in description for keyword in ['ui', 'interface', 'frontend', 'display']):
        suggestions.append({
            'type': 'UI/UX Fix',
            'priority': 'Medium',
            'suggestions': [
                '1. Review responsive design and cross-browser compatibility',
                '2. Improve accessibility (ARIA labels, keyboard navigation)',
                '3. Optimize CSS and JavaScript loading',
                '4. Implement user feedback mechanisms',
                '5. Test on different devices and screen sizes'
            ]
        })
    
    if any(keyword in summary or keyword in description for keyword in ['data', 'database', 'migration', 'schema']):
        suggestions.append({
            'type': 'Data Fix',
            'priority': 'High',
            'suggestions': [
                '1. Backup existing data before making changes',
                '2. Create database migration scripts',
                '3. Validate data integrity and constraints',
                '4. Test rollback procedures',
                '5. Monitor data consistency after changes'
            ]
        })
    
    # Default suggestions if no specific patterns match
    if not suggestions:
        suggestions.append({
            'type': 'General Investigation',
            'priority': 'Medium',
            'suggestions': [
                '1. Analyze the issue requirements and acceptance criteria',
                '2. Review related code and documentation',
                '3. Identify root cause through systematic debugging',
                '4. Plan the fix with minimal impact',
                '5. Implement comprehensive testing strategy'
            ]
        })
    
    return suggestions

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=5000)
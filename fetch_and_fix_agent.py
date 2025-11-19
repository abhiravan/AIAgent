"""
Fetch and Fix Agent - A web UI for fetching Jira issues and generating fixes
"""

import os
from flask import Flask, render_template, request, jsonify
from services.jira_service import JiraService
from datetime import datetime
import subprocess
import tempfile
import shlex
import requests

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


@app.route('/generate_fix_patch', methods=['POST'])
def generate_fix_patch():
    """Ask the AI to produce an apply_patch-style patch for the issue."""
    try:
        from services.ai_service import AIService
        from services.github_service import GitHubService

        data = request.get_json()
        issue_data = data.get('issue_data')

        if not issue_data:
            return jsonify({'success': False, 'error': 'No issue data provided'})

        ai_service = AIService()
        github_service = GitHubService()

        repo_files = github_service.get_repository_files()

        result = ai_service.generate_fix_patch(issue_data=issue_data, repo_files=repo_files)

        return jsonify({'success': True, 'result': result})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/apply_patch', methods=['POST'])
def apply_patch_route():
    """Apply an apply_patch-style diff locally, commit and push, and optionally create a PR."""
    try:
        data = request.get_json()
        patch_text = data.get('patch')
        commit_message = data.get('commit_message', 'chore: apply LLM patch')
        issue_data = data.get('issue_data', {})
        pr_title = data.get('pr_title')
        pr_body = data.get('pr_body')

        if not patch_text:
            return jsonify({'success': False, 'error': 'No patch provided'})

        # Safety: quick check patch size and forbidden patterns
        if patch_text.count('\n*** Update File:') > 5:
            return jsonify({'success': False, 'error': 'Patch touches too many files; aborting for safety.'})

        forbidden = ['API_KEY', 'SECRET', 'TOKEN', 'PASSWORD']
        for token in forbidden:
            if token in patch_text.upper():
                return jsonify({'success': False, 'error': 'Patch contains forbidden tokens; aborting.'})

        # Determine branch name based on issue key, per Agents.md
        jira_key = None
        if issue_data and isinstance(issue_data, dict):
            jira_key = issue_data.get('key')

        if jira_key:
            branch_name = f'fb_{jira_key}'
        else:
            # fallback branch name
            branch_name = f'fb_auto_fix_{datetime.utcnow().strftime("%Y%m%d%H%M%S")}'

        # Create and switch to the new branch
        subprocess.run(f'git checkout -b {branch_name}', shell=True, cwd=os.getcwd())

        # Parse and apply MCP-style patch blocks (*** Begin Patch / *** Update File: ...)
        def apply_mcp_patch(patch: str):
            """Apply an MCP-style patch to the local filesystem.

            Returns (success, message, list_of_changed_files)
            """
            changed_files = []
            try:
                lines = patch.splitlines()
                i = 0
                while i < len(lines):
                    line = lines[i]
                    if line.startswith('*** Update File:') or line.startswith('*** Add File:'):
                        mode = 'update' if 'Update' in line else 'add'
                        # extract path
                        parts = line.split(':', 1)
                        if len(parts) < 2:
                            return False, f'Malformed patch header: {line}', []
                        file_path = parts[1].strip()
                        i += 1

                        # skip optional @@ headers until we hit diff content or next block
                        hunk_lines = []
                        while i < len(lines) and not lines[i].startswith('***'):
                            hunk_lines.append(lines[i])
                            i += 1

                        # If adding file, write the content from hunk_lines (strip leading +/- if present)
                        if mode == 'add':
                            content_lines = []
                            for hl in hunk_lines:
                                if hl.startswith('+'):
                                    content_lines.append(hl[1:])
                                elif not hl.startswith('-'):
                                    content_lines.append(hl)
                            # ensure directory exists
                            os.makedirs(os.path.dirname(file_path) or '.', exist_ok=True)
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write('\n'.join(content_lines) + ('\n' if content_lines and not content_lines[-1].endswith('\n') else ''))
                            changed_files.append(file_path)
                            continue

                        # For update, apply a simple patch: read original, then process hunk lines
                        if not os.path.exists(file_path):
                            orig_lines = []
                        else:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                orig_lines = f.read().splitlines()

                        out_lines = []
                        orig_idx = 0

                        for hl in hunk_lines:
                            if hl.startswith('@@'):
                                # hunk header, skip
                                continue
                            if hl.startswith('-'):
                                # remove line from original: advance orig_idx by 1
                                orig_idx += 1
                            elif hl.startswith('+'):
                                out_lines.append(hl[1:])
                            else:
                                # context line: keep and advance original
                                out_lines.append(hl)
                                orig_idx += 1

                        # If nothing in out_lines but we have orig_lines, fallback to original
                        if not out_lines and orig_lines:
                            new_content = '\n'.join(orig_lines)
                        else:
                            new_content = '\n'.join(out_lines)

                        # Write back
                        os.makedirs(os.path.dirname(file_path) or '.', exist_ok=True)
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(new_content + ('\n' if new_content and not new_content.endswith('\n') else ''))
                        changed_files.append(file_path)
                    else:
                        i += 1

                return True, 'Patch applied', changed_files
            except Exception as e:
                return False, str(e), []

        success, msg, changed_files = apply_mcp_patch(patch_text)
        if not success:
            return jsonify({'success': False, 'error': 'Patch application failed: ' + msg})

        # Stage and commit changed files
        if changed_files:
            subprocess.run('git add ' + ' '.join([shlex.quote(f) for f in changed_files]), shell=True, cwd=os.getcwd())
            subprocess.run(f'git commit -m "{commit_message}"', shell=True, cwd=os.getcwd())
        else:
            # Nothing changed
            return jsonify({'success': False, 'error': 'No files were changed by the patch.'})

        # Push branch
        push_res = subprocess.run(f'git push -u origin {branch_name}', shell=True, cwd=os.getcwd(), capture_output=True, text=True)

        pr_url = None
        github_token = os.getenv('GITHUB_TOKEN')
        repo_url = os.getenv('GITHUB_REPO_URL')

        if github_token and repo_url:
            # Create PR via GitHub API
            try:
                # derive owner/repo
                owner_repo = repo_url.replace('https://github.com/', '').strip('/')
                api_url = f'https://api.github.com/repos/{owner_repo}/pulls'
                headers = {
                    'Authorization': f'token {github_token}',
                    'Accept': 'application/vnd.github.v3+json'
                }
                pr_payload = {
                    'title': pr_title or commit_message,
                    'head': branch_name,
                    'base': 'main',
                    'body': pr_body or f'Automated patch generated by LLM for {jira_key or "auto-fix"}'
                }
                resp = requests.post(api_url, headers=headers, json=pr_payload, timeout=15)
                if resp.status_code in (200, 201):
                    pr_data = resp.json()
                    pr_url = pr_data.get('html_url')
                else:
                    pr_url = f'https://github.com/{owner_repo}/pull/new/{branch_name}'
            except Exception:
                pr_url = f'https://github.com/{owner_repo}/pull/new/{branch_name}'
        else:
            # Fallback: return manual PR URL
            pr_url = f'https://github.com/{os.getenv("GITHUB_REPO_URL", "<owner/repo>").replace("https://github.com/", "")}/pull/new/{branch_name}'

        return jsonify({'success': True, 'push_stdout': push_res.stdout, 'pr_url': pr_url, 'branch': branch_name})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/analyze_issue', methods=['POST'])
def analyze_issue():
    """Analyze issue using AI and GitHub context"""
    try:
        from services.ai_service import AIService
        from services.github_service import GitHubService
        
        data = request.get_json()
        issue_data = data.get('issue_data')
        
        if not issue_data:
            return jsonify({'success': False, 'error': 'No issue data provided'})
        
        # Initialize services
        ai_service = AIService()
        github_service = GitHubService()
        
        # Get repository files for context
        repo_files = github_service.get_repository_files()
        
        # Analyze issue with AI
        analysis_result = ai_service.analyze_issue_with_context(
            issue_data=issue_data,
            repo_files=repo_files
        )
        
        return jsonify({
            'success': True,
            'analysis': analysis_result
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/test_github', methods=['GET'])
def test_github():
    """Test GitHub connection"""
    try:
        from services.github_service import GitHubService
        github_service = GitHubService()
        result = github_service.test_connection()
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

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
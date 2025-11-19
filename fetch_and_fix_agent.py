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

        def convert_mcp_to_unified(patch: str) -> str:
            """Convert MCP-style patch blocks to a unified diff suitable for git apply.

            MCP blocks look like:
            *** Begin Patch
            *** Update File: path/to/file.py
            @@
            -old
            +new
            *** End Patch
            """
            out_chunks = []
            lines = patch.splitlines()
            i = 0
            while i < len(lines):
                line = lines[i]
                if line.startswith('*** Update File:') or line.startswith('*** Add File:') or line.startswith('*** Delete File:'):
                    op = 'update'
                    if 'Add File' in line:
                        op = 'add'
                    if 'Delete File' in line:
                        op = 'delete'
                    parts = line.split(':', 1)
                    file_path = parts[1].strip() if len(parts) > 1 else None
                    i += 1
                    # collect hunk lines until next *** block or end
                    hunk = []
                    while i < len(lines) and not lines[i].startswith('***'):
                        hunk.append(lines[i])
                        i += 1

                    if not file_path:
                        continue

                    if op == 'delete':
                        # create a minimal delete diff
                        header = f"diff --git a/{file_path} b/{file_path}\nindex e69de29..0000000 100644\n--- a/{file_path}\n+++ /dev/null\n"
                        out_chunks.append(header + '\n'.join(hunk))
                        continue

                    # Ensure hunk contains @@ headers; if not, convert +/- block into a single hunk
                    hunk_text = '\n'.join(hunk)
                    if '@@' not in hunk_text:
                        # add a simple hunk header covering full file
                        header_hunk = '@@ -1,0 +1,0 @@\n'
                        # Build unified diff body from +/- lines
                        body = ''
                        for hl in hunk:
                            if hl.startswith('+') or hl.startswith('-') or not hl.startswith(' '):
                                body += hl + '\n'
                            else:
                                body += ' ' + hl + '\n'
                        unified = header_hunk + body
                    else:
                        unified = hunk_text

                    header = f"diff --git a/{file_path} b/{file_path}\n--- a/{file_path}\n+++ b/{file_path}\n"
                    out_chunks.append(header + unified)
                else:
                    i += 1

            return '\n'.join(out_chunks)

        unified = None
        # If patch already contains a unified diff, use it directly
        if 'diff --git' in patch_text or patch_text.strip().startswith('diff --git'):
            unified = patch_text
        elif '*** Begin Patch' in patch_text:
            # Extract inner content
            # remove Begin/End markers if present
            inner = patch_text
            inner = inner.replace('*** Begin Patch', '')
            inner = inner.replace('*** End Patch', '')
            unified = convert_mcp_to_unified(inner)

        if unified:
            # Try to apply using git apply
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.diff') as tf:
                tf.write(unified)
                tf.flush()
                diff_path = tf.name

            apply_cmd = f'git apply --index "{diff_path}"'
            res = subprocess.run(apply_cmd, shell=True, cwd=os.getcwd(), capture_output=True, text=True)
            if res.returncode != 0:
                # fallback to direct write if git apply fails
                pass
            else:
                # Stage and commit all changes applied by git
                subprocess.run('git add -A', shell=True, cwd=os.getcwd())
                commit = subprocess.run(f'git commit -m "{commit_message}"', shell=True, cwd=os.getcwd(), capture_output=True, text=True)
                if commit.returncode != 0:
                    return jsonify({'success': False, 'error': f'git commit failed: {commit.stderr}'})
                changed_files = []
                # get list of changed files in this commit
                diff_names = subprocess.run('git diff --name-only HEAD~1..HEAD', shell=True, cwd=os.getcwd(), capture_output=True, text=True)
                if diff_names.returncode == 0:
                    changed_files = [n for n in diff_names.stdout.splitlines() if n.strip()]
                else:
                    changed_files = []
        else:
            # No unified diff could be generated; try naive MCP apply (previous approach)
            def naive_apply(patch: str):
                changed = []
                lines = patch.splitlines()
                i = 0
                while i < len(lines):
                    if lines[i].startswith('*** Update File:') or lines[i].startswith('*** Add File:'):
                        parts = lines[i].split(':', 1)
                        file_path = parts[1].strip()
                        i += 1
                        content = []
                        while i < len(lines) and not lines[i].startswith('***'):
                            l = lines[i]
                            if l.startswith('+'):
                                content.append(l[1:])
                            elif not l.startswith('-'):
                                content.append(l)
                            i += 1
                        os.makedirs(os.path.dirname(file_path) or '.', exist_ok=True)
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write('\n'.join(content) + ('\n' if content and not content[-1].endswith('\n') else ''))
                        changed.append(file_path)
                    else:
                        i += 1
                return changed

            changed_files = naive_apply(patch_text)

            # Stage and commit the naive-applied files
            if changed_files:
                subprocess.run('git add ' + ' '.join([shlex.quote(f) for f in changed_files]), shell=True, cwd=os.getcwd())
                commit = subprocess.run(f'git commit -m "{commit_message}"', shell=True, cwd=os.getcwd(), capture_output=True, text=True)
                if commit.returncode != 0:
                    return jsonify({'success': False, 'error': f'git commit failed for naive apply: {commit.stderr}'})

        if not changed_files:
            return jsonify({'success': False, 'error': 'No files were changed by the patch or git apply failed.'})

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
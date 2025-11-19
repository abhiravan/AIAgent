"""
GitHub Service for repository integration
"""
import os
import requests
import base64
from typing import List, Dict, Any


class GitHubService:
    def __init__(self):
        self.repo_url = os.getenv('GITHUB_REPO_URL')
        self.username = os.getenv('GITHUB_USERNAME')
        self.token = os.getenv('GITHUB_TOKEN')
        
        if not all([self.repo_url, self.username, self.token]):
            raise ValueError("Missing required GitHub configuration variables")
        
        # Extract owner and repo from URL
        # Format: https://github.com/owner/repo
        parts = self.repo_url.rstrip('/').split('/')
        self.owner = parts[-2]
        self.repo = parts[-1]
        
        self.api_base = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    def get_repository_files(self, path: str = "", max_files: int = 50) -> List[Dict[str, Any]]:
        """
        Get repository files and directories
        """
        try:
            url = f"{self.api_base}/repos/{self.owner}/{self.repo}/contents/{path}"
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            contents = response.json()
            files = []
            
            for item in contents[:max_files]:
                file_info = {
                    'name': item['name'],
                    'path': item['path'],
                    'type': item['type'],
                    'size': item.get('size', 0),
                    'download_url': item.get('download_url')
                }
                
                # Add relevance scoring for Python files
                if item['name'].endswith('.py'):
                    file_info['relevance'] = 'high'
                elif item['name'].endswith(('.sql', '.md', '.json', '.txt')):
                    file_info['relevance'] = 'medium'
                else:
                    file_info['relevance'] = 'low'
                
                files.append(file_info)
            
            # Sort by relevance and name
            files.sort(key=lambda x: (x['relevance'] == 'high', x['relevance'] == 'medium', x['name']))
            return files
            
        except Exception as e:
            return [{'error': f"Failed to fetch repository files: {str(e)}"}]
    
    def get_file_content(self, file_path: str) -> Dict[str, Any]:
        """
        Get content of a specific file
        """
        try:
            url = f"{self.api_base}/repos/{self.owner}/{self.repo}/contents/{file_path}"
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            file_data = response.json()
            
            # Decode base64 content
            if file_data.get('encoding') == 'base64':
                content = base64.b64decode(file_data['content']).decode('utf-8')
            else:
                content = file_data.get('content', '')
            
            return {
                'success': True,
                'path': file_path,
                'content': content,
                'size': file_data.get('size', 0),
                'sha': file_data.get('sha')
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to fetch file content: {str(e)}"
            }
    
    def search_code(self, query: str, max_results: int = 20) -> List[Dict[str, Any]]:
        """
        Search for code in the repository
        """
        try:
            # GitHub code search API
            search_query = f"{query} repo:{self.owner}/{self.repo}"
            url = f"{self.api_base}/search/code"
            params = {
                'q': search_query,
                'per_page': max_results
            }
            
            response = requests.get(url, headers=self.headers, params=params, timeout=15)
            response.raise_for_status()
            
            results = response.json()
            
            search_results = []
            for item in results.get('items', []):
                result = {
                    'name': item['name'],
                    'path': item['path'],
                    'repository': item['repository']['full_name'],
                    'score': item['score'],
                    'html_url': item['html_url']
                }
                search_results.append(result)
            
            return search_results
            
        except Exception as e:
            return [{'error': f"Code search failed: {str(e)}"}]
    
    def get_recent_commits(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent commits to understand recent changes
        """
        try:
            url = f"{self.api_base}/repos/{self.owner}/{self.repo}/commits"
            params = {'per_page': limit}
            
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            
            commits = response.json()
            
            commit_info = []
            for commit in commits:
                info = {
                    'sha': commit['sha'][:8],
                    'message': commit['commit']['message'],
                    'author': commit['commit']['author']['name'],
                    'date': commit['commit']['author']['date'],
                    'files_changed': len(commit.get('files', []))
                }
                commit_info.append(info)
            
            return commit_info
            
        except Exception as e:
            return [{'error': f"Failed to fetch commits: {str(e)}"}]
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test GitHub API connection
        """
        try:
            url = f"{self.api_base}/repos/{self.owner}/{self.repo}"
            response = requests.get(url, headers=self.headers, timeout=5)
            response.raise_for_status()
            
            repo_info = response.json()
            
            return {
                'success': True,
                'repository': repo_info['full_name'],
                'description': repo_info.get('description', 'No description'),
                'language': repo_info.get('language', 'Unknown'),
                'private': repo_info['private'],
                'last_updated': repo_info['updated_at']
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"GitHub connection failed: {str(e)}"
            }
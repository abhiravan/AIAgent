"""
Jira Service Module
Handles all Jira API interactions for the Fetch and Fix Agent
"""

import os
import requests
import base64
from typing import Dict, Any, Optional

class JiraService:
    """Service class for Jira API operations"""
    
    def __init__(self, base_url: str = None, email: str = None, token: str = None):
        """
        Initialize Jira service with credentials
        
        Args:
            base_url: Jira instance URL (defaults to environment variable)
            email: Jira user email (defaults to environment variable)
            token: Jira API token (defaults to environment variable)
        """
        self.base_url = (base_url or os.environ.get('JIRA_BASE_URL', '')).rstrip('/')
        self.email = email or os.environ.get('JIRA_EMAIL', '')
        self.token = token or os.environ.get('JIRA_TOKEN', '')
        
        if not all([self.base_url, self.email, self.token]):
            raise ValueError("Missing required Jira credentials. Set JIRA_BASE_URL, JIRA_EMAIL, and JIRA_TOKEN environment variables.")
        
        self.auth_header = self._create_auth_header()
    
    def _create_auth_header(self) -> str:
        """Create Basic Auth header for Jira API"""
        auth_string = f"{self.email}:{self.token}"
        auth_bytes = auth_string.encode('ascii')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
        return f"Basic {auth_b64}"
    
    def _make_request(self, endpoint: str, method: str = 'GET', timeout: int = 30) -> Dict[str, Any]:
        """
        Make HTTP request to Jira API
        
        Args:
            endpoint: API endpoint (without base URL)
            method: HTTP method
            timeout: Request timeout in seconds
            
        Returns:
            Dictionary with success status and data/error
        """
        try:
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            headers = {
                'Authorization': self.auth_header,
                'Accept': 'application/json'
            }
            
            response = requests.request(method, url, headers=headers, timeout=timeout)
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'data': response.json(),
                    'status_code': response.status_code
                }
            elif response.status_code == 404:
                return {
                    'success': False,
                    'error': 'Resource not found',
                    'status_code': response.status_code
                }
            elif response.status_code == 401:
                return {
                    'success': False,
                    'error': 'Authentication failed. Check your credentials.',
                    'status_code': response.status_code
                }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}: {response.reason}',
                    'status_code': response.status_code
                }
                
        except requests.exceptions.Timeout:
            return {'success': False, 'error': 'Request timeout'}
        except requests.exceptions.ConnectionError:
            return {'success': False, 'error': 'Connection failed. Check your network or Jira URL.'}
        except requests.exceptions.RequestException as e:
            return {'success': False, 'error': f'Request failed: {str(e)}'}
        except Exception as e:
            return {'success': False, 'error': f'Unexpected error: {str(e)}'}
    
    def get_issue(self, issue_key: str) -> Dict[str, Any]:
        """
        Fetch issue details from Jira
        
        Args:
            issue_key: Jira issue key (e.g., "PROJ-123")
            
        Returns:
            Dictionary with success status and issue data or error
        """
        if not issue_key or not issue_key.strip():
            return {'success': False, 'error': 'Issue key cannot be empty'}
        
        issue_key = issue_key.strip().upper()
        endpoint = f"rest/api/3/issue/{issue_key}"
        
        result = self._make_request(endpoint)
        
        if not result['success']:
            if result.get('status_code') == 404:
                result['error'] = f'Issue {issue_key} not found'
            return result
        
        # Parse and format issue data
        try:
            issue_data = result['data']
            formatted_issue = self._format_issue_data(issue_data)
            return {
                'success': True,
                'data': formatted_issue
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to parse issue data: {str(e)}'
            }
    
    def _format_issue_data(self, issue_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format raw Jira issue data into a clean structure
        
        Args:
            issue_data: Raw issue data from Jira API
            
        Returns:
            Formatted issue data dictionary
        """
        fields = issue_data.get('fields', {})
        
        # Extract description text from ADF (Atlassian Document Format)
        description = self._extract_description(fields.get('description'))
        
        return {
            'key': issue_data.get('key', ''),
            'summary': fields.get('summary', ''),
            'description': description,
            'status': fields.get('status', {}).get('name', 'Unknown'),
            'assignee': fields.get('assignee', {}).get('displayName', 'Unassigned') if fields.get('assignee') else 'Unassigned',
            'priority': fields.get('priority', {}).get('name', 'None') if fields.get('priority') else 'None',
            'issue_type': fields.get('issuetype', {}).get('name', 'Unknown'),
            'created': fields.get('created', ''),
            'updated': fields.get('updated', ''),
            'reporter': fields.get('reporter', {}).get('displayName', 'Unknown') if fields.get('reporter') else 'Unknown',
            'project': fields.get('project', {}).get('name', 'Unknown') if fields.get('project') else 'Unknown'
        }
    
    def _extract_description(self, description_obj: Optional[Dict[str, Any]]) -> str:
        """
        Extract plain text from Jira ADF (Atlassian Document Format) description
        
        Args:
            description_obj: Description object from Jira API
            
        Returns:
            Plain text description
        """
        if not description_obj:
            return 'No description available'
        
        try:
            # Handle ADF format
            content = description_obj.get('content', [])
            if not content:
                return 'No description available'
            
            text_parts = []
            for block in content:
                if block.get('type') == 'paragraph':
                    paragraph_content = block.get('content', [])
                    for item in paragraph_content:
                        if item.get('type') == 'text':
                            text_parts.append(item.get('text', ''))
                elif block.get('type') == 'text':
                    text_parts.append(block.get('text', ''))
            
            result = ' '.join(text_parts).strip()
            return result if result else 'No description available'
            
        except Exception:
            # Fallback for different description formats
            if isinstance(description_obj, str):
                return description_obj
            return 'No description available'
    
    def search_issues(self, jql: str, max_results: int = 50) -> Dict[str, Any]:
        """
        Search for issues using JQL
        
        Args:
            jql: JQL (Jira Query Language) string
            max_results: Maximum number of results to return
            
        Returns:
            Dictionary with success status and search results
        """
        endpoint = "rest/api/3/search"
        
        # For search, we'd need to make a POST request with JQL
        # This is a placeholder for potential future functionality
        return {
            'success': False,
            'error': 'Search functionality not implemented yet'
        }
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test the Jira connection
        
        Returns:
            Dictionary with connection test results
        """
        endpoint = "rest/api/3/myself"
        result = self._make_request(endpoint)
        
        if result['success']:
            user_data = result['data']
            return {
                'success': True,
                'message': f"Connected as {user_data.get('displayName', 'Unknown User')}",
                'user': user_data.get('displayName', 'Unknown User'),
                'email': user_data.get('emailAddress', 'Unknown Email')
            }
        else:
            return {
                'success': False,
                'error': f"Connection test failed: {result['error']}"
            }


# Convenience function for quick issue fetching
def fetch_jira_issue(issue_key: str, base_url: str = None, email: str = None, token: str = None) -> Dict[str, Any]:
    """
    Convenience function to fetch a single Jira issue
    
    Args:
        issue_key: Jira issue key
        base_url: Optional Jira URL (uses env var if not provided)
        email: Optional email (uses env var if not provided)
        token: Optional token (uses env var if not provided)
        
    Returns:
        Issue data dictionary
    """
    try:
        jira_service = JiraService(base_url, email, token)
        return jira_service.get_issue(issue_key)
    except ValueError as e:
        return {'success': False, 'error': str(e)}
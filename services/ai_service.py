"""
AI Service for intelligent issue analysis using Azure OpenAI
"""
import os
import json
import requests
from typing import Dict, List, Any


class AIService:
    def __init__(self):
        self.endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
        self.api_key = os.getenv('AZURE_OPENAI_API_KEY')
        self.api_version = os.getenv('AZURE_OPENAI_API_VERSION')
        self.deployment_name = os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME')
        
        if not all([self.endpoint, self.api_key, self.api_version, self.deployment_name]):
            raise ValueError("Missing required Azure OpenAI configuration variables")
    
    def analyze_issue_with_context(self, issue_data: Dict, repo_files: List[Dict]) -> Dict[str, Any]:
        """
        Analyze Jira issue using AI with repository context and copilot instructions
        """
        try:
            # Read copilot instructions for context
            copilot_instructions = self._read_copilot_instructions()
            
            # Prepare the analysis prompt
            prompt = self._build_analysis_prompt(issue_data, repo_files, copilot_instructions)
            
            # Call Azure OpenAI
            response = self._call_azure_openai(prompt)
            
            # Parse and structure the response
            analysis = self._parse_analysis_response(response)
            
            return analysis
            
        except Exception as e:
            return {
                'error': f"Analysis failed: {str(e)}",
                'success': False
            }
    
    def _read_copilot_instructions(self) -> str:
        """Read the copilot instructions for context"""
        try:
            instructions_path = os.path.join(os.path.dirname(__file__), '.github', 'copilot-instructions.md')
            with open(instructions_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception:
            return "No copilot instructions available"
    
    def _build_analysis_prompt(self, issue_data: Dict, repo_files: List[Dict], copilot_instructions: str) -> str:
        """Build the analysis prompt for Azure OpenAI"""
        
        prompt = f"""
You are an expert AI coding assistant analyzing a Jira issue for the MEBP Pricing Data Pipeline project. 

**Project Context (from Copilot Instructions):**
{copilot_instructions[:2000]}...  # Truncated for token limits

**Jira Issue Details:**
- Key: {issue_data.get('key', 'Unknown')}
- Summary: {issue_data.get('summary', 'No summary')}
- Type: {issue_data.get('issue_type', 'Unknown')}
- Priority: {issue_data.get('priority', 'Unknown')}
- Status: {issue_data.get('status', 'Unknown')}
- Description: {issue_data.get('description', 'No description')}

**Repository Files Available:**
{json.dumps([f['name'] for f in repo_files[:20]], indent=2)}  # Show first 20 files

**Analysis Task:**
Based on the issue description and the codebase context, provide a detailed analysis including:

1. **Root Cause Analysis**: What is likely causing this issue?
2. **Files to Investigate**: Which specific files need to be examined/modified?
3. **Fix Strategy**: Step-by-step approach to resolve the issue
4. **Priority Assessment**: How critical is this fix?
5. **Testing Recommendations**: What should be tested after the fix?

**Response Format:**
Please provide your analysis in JSON format with the following structure:
{{
    "root_cause": "Detailed explanation of what's causing the issue",
    "affected_files": ["file1.py", "file2.sql", "..."],
    "fix_strategy": [
        "Step 1: Description",
        "Step 2: Description",
        "..."
    ],
    "priority_level": "Critical|High|Medium|Low",
    "testing_plan": [
        "Test 1: Description",
        "Test 2: Description"
    ],
    "estimated_effort": "X hours/days",
    "dependencies": ["Any dependencies or prerequisites"],
    "risks": ["Potential risks of the fix"]
}}
"""
        return prompt
    
    def _call_azure_openai(self, prompt: str) -> str:
        """Make API call to Azure OpenAI"""
        url = f"{self.endpoint}openai/deployments/{self.deployment_name}/chat/completions?api-version={self.api_version}"
        
        headers = {
            "Content-Type": "application/json",
            "api-key": self.api_key
        }
        
        payload = {
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert software engineer specializing in data pipelines, PySpark, and MongoDB. Analyze issues methodically and provide actionable solutions."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            "max_tokens": 2000,
            "temperature": 0.1,
            "top_p": 0.95
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        return result['choices'][0]['message']['content']
    
    def _parse_analysis_response(self, response: str) -> Dict[str, Any]:
        """Parse and validate the AI response"""
        try:
            # Try to extract JSON from the response
            response = response.strip()
            
            # Find JSON content between ```json markers or direct JSON
            if '```json' in response:
                start = response.find('```json') + 7
                end = response.find('```', start)
                json_content = response[start:end].strip()
            elif response.startswith('{'):
                json_content = response
            else:
                # Fallback: create structured response from text
                return self._create_fallback_analysis(response)
            
            analysis = json.loads(json_content)
            
            # Validate required fields
            required_fields = ['root_cause', 'affected_files', 'fix_strategy', 'priority_level']
            for field in required_fields:
                if field not in analysis:
                    analysis[field] = f"Missing {field} information"
            
            analysis['success'] = True
            return analysis
            
        except Exception as e:
            return self._create_fallback_analysis(response, str(e))
    
    def _create_fallback_analysis(self, raw_response: str, error: str = None) -> Dict[str, Any]:
        """Create a fallback analysis structure when JSON parsing fails"""
        return {
            'success': True,
            'root_cause': 'AI analysis completed but response format needs manual review',
            'affected_files': ['Please review manually based on issue description'],
            'fix_strategy': [
                'Review the detailed analysis below',
                'Identify specific files mentioned in the analysis',
                'Follow the recommended approach step by step'
            ],
            'priority_level': 'Medium',
            'testing_plan': ['Manual testing required based on changes made'],
            'estimated_effort': 'To be determined',
            'raw_analysis': raw_response,
            'parsing_error': error,
            'note': 'This is a fallback analysis. Please review the raw_analysis field for detailed insights.'
        }
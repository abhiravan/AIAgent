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

    def generate_fix_patch(self, issue_data: Dict, repo_files: List[Dict]) -> Dict[str, Any]:
        """Request the LLM to generate an apply_patch-style patch for a minimal fix.

        Returns a dict with keys: success, patch, candidates, rationale, validation
        """
        try:
            copilot_instructions = self._read_copilot_instructions()
            prompt = self._build_patch_generation_prompt(issue_data, repo_files, copilot_instructions)
            response = self._call_azure_openai(prompt)

            # Expecting JSON + patch block; try to extract JSON first
            # Look for an apply_patch block
            patch = None
            if '*** Begin Patch' in response:
                patch_start = response.find('*** Begin Patch')
                patch = response[patch_start:].strip()
                json_part = response[:patch_start].strip()
            else:
                # Try to parse JSON from the response
                json_part = response.strip()

            try:
                parsed = json.loads(json_part)
            except Exception:
                parsed = {'note': 'Could not parse JSON header from LLM response', 'raw': response}

            return {
                'success': True,
                'patch': patch,
                'meta': parsed
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _build_patch_generation_prompt(self, issue_data: Dict, repo_files: List[Dict], copilot_instructions: str) -> str:
        """Build a conservative patch generation prompt following the repo's LLM strategy."""
        files_list = json.dumps([f['path'] for f in repo_files[:50]], indent=2)

        prompt = f'''
You are a conservative, safety-first code repair agent. Follow these rules exactly:

- Analyze the Jira issue below and the repository file list. Identify up to 3 candidate files to modify, with a confidence score (0.0-1.0) and brief reason for each.
- If confidence for a chosen file is < 0.75, respond with action: request_more_info and list the required clarifications.
- When producing a patch, make the minimal change needed to fix the issue. Modify at most 2 files if possible.
- NEVER include secrets, tokens, credentials, or any values that look like API keys in the patch.
- Output MUST be: a JSON header (with keys: candidates, chosen_file, rationale, validation, safety_checks) followed by an apply_patch-style block starting with '*** Begin Patch' and ending with '*** End Patch'.

Jira Issue:
- Key: {issue_data.get('key')}
- Summary: {issue_data.get('summary')}
- Description: {issue_data.get('description')}

Repository files (top 50):
{files_list}

Copilot Instructions (truncated):
{copilot_instructions[:2000]}

Produce the JSON header and the patch. Keep changes minimal and focused. If multiple candidate fixes are plausible, provide them in 'candidates' but only include a patch for one 'chosen_file'.
'''
        return prompt
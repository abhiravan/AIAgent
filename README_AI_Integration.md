# AI-Powered Issue Analysis Setup

## Overview

The Fetch and Fix Agent now includes AI-powered issue analysis using Azure OpenAI and GitHub integration. The AI analyzes Jira issues in the context of your codebase and provides intelligent insights for troubleshooting.

## Features

### 🤖 AI Analysis
- **Root Cause Analysis**: AI identifies potential causes based on issue description and codebase context
- **File Identification**: Suggests specific files that may need investigation or modification
- **Fix Strategy**: Provides step-by-step approach to resolve the issue
- **Priority Assessment**: Evaluates the criticality of the fix
- **Testing Recommendations**: Suggests appropriate testing strategies

### 🔗 GitHub Integration
- Repository file analysis
- Code search capabilities
- Recent commit history for context
- File content retrieval for detailed analysis

## Configuration

### 1. Azure OpenAI Setup

Add the following variables to your `.env` file:

```env
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://mestk-eus-ai-01.openai.azure.com/
AZURE_OPENAI_API_KEY=your-azure-openai-api-key-here
AZURE_OPENAI_API_VERSION=2023-07-01-preview
AZURE_OPENAI_DEPLOYMENT_NAME=mestk-gpt-35-deployment
```

#### Getting Azure OpenAI Credentials:
1. Log into Azure Portal
2. Navigate to your Azure OpenAI resource
3. Go to "Keys and Endpoint" section
4. Copy the endpoint URL and API key
5. Note your deployment name (model deployment)

### 2. GitHub Configuration

Add these variables to your `.env` file:

```env
# GitHub Configuration
GITHUB_REPO_URL=https://github.com/owner/repo
GITHUB_USERNAME=your-github-username
GITHUB_TOKEN=your-github-token
```

#### Creating a GitHub Personal Access Token:
1. Go to GitHub Settings > Developer settings > Personal access tokens
2. Generate new token with the following permissions:
   - `repo` (Full repository access)
   - `read:user` (Read user profile)
3. Copy the token to your `.env` file

### 3. Security Best Practices

⚠️ **IMPORTANT**: Never commit `.env` files to version control!

- The `.env` file is already in `.gitignore`
- Use `.env.example` as a template
- Rotate tokens regularly
- Use least-privilege access for tokens

## Usage

### 1. Fetch Jira Issue
1. Enter a Jira issue key (e.g., `PROJ-123`)
2. Click "Fetch" to retrieve issue details

### 2. AI Analysis
1. After fetching an issue, click "Analyze Issue"
2. The AI will:
   - Read the copilot instructions for project context
   - Analyze the repository structure
   - Examine the issue description
   - Generate comprehensive analysis

### 3. Analysis Results
The AI analysis provides:

- **Root Cause**: Potential reasons for the issue
- **Files to Investigate**: Specific files that may need changes
- **Fix Strategy**: Step-by-step resolution approach
- **Priority & Effort**: Assessment of urgency and time requirements
- **Testing Plan**: Recommended testing procedures

## API Endpoints

### `/analyze_issue`
- **Method**: POST
- **Body**: `{"issue_data": {...}}`
- **Response**: Comprehensive AI analysis

### `/test_github`
- **Method**: GET
- **Response**: GitHub connection status

## Troubleshooting

### Common Issues

1. **"Missing required Azure OpenAI configuration"**
   - Verify all Azure OpenAI variables are set in `.env`
   - Check endpoint URL format (should end with `/`)

2. **"Missing required GitHub configuration"**
   - Ensure GitHub URL, username, and token are configured
   - Verify token has correct permissions

3. **"Analysis failed: timeout"**
   - Azure OpenAI service may be unavailable
   - Try again after a few minutes

4. **"GitHub connection failed"**
   - Check if repository URL is correct
   - Verify GitHub token is valid and has repo access
   - Ensure repository is accessible with the token

### Debug Mode

To debug API calls, check the browser console for detailed error messages. The application includes comprehensive error handling and logging.

## Architecture

```
┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐
│   Jira Issue    │───▶│ AI Service   │───▶│ Azure OpenAI    │
│   Description   │    │              │    │   Analysis      │
└─────────────────┘    └──────┬───────┘    └─────────────────┘
                              │
┌─────────────────┐           │
│ GitHub Service  │───────────┘
│ - File Context  │
│ - Repo Analysis │
└─────────────────┘
```

## AI Prompt Engineering

The AI service uses carefully crafted prompts that include:
- Project-specific context from copilot instructions
- Repository structure and file information
- Issue details and metadata
- Structured response formatting

The AI is trained to provide actionable, technical insights specific to the Databricks/PySpark/MongoDB architecture of the MEBP project.

## Limitations

- AI analysis is based on available context and may not catch all edge cases
- Repository analysis is limited to file structure and names (not full content for large repos)
- Azure OpenAI has token limits that may affect analysis of very large issues
- GitHub API rate limits may affect repository analysis for frequent requests

## Future Enhancements

- Code diff analysis for recent changes
- Integration with Databricks notebooks
- Historical issue pattern recognition
- Automated fix suggestion validation
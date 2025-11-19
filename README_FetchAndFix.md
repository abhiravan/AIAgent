# Fetch and Fix Agent

A web-based tool for fetching Jira issues and generating intelligent fix suggestions.

## Features

- **Fetch Jira Issues**: Enter a Jira issue key to retrieve detailed issue information
- **Smart Analysis**: Display comprehensive issue details including summary, description, status, and metadata
- **Fix Suggestions**: Generate intelligent fix recommendations based on issue content and patterns
- **Secure Token Handling**: Environment variable-based configuration for sensitive data

## Installation

1. Install required dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables (choose one method):

**Option A: Create .env file**
```bash
# Create .env file with your Jira credentials
echo JIRA_BASE_URL=https://your-domain.atlassian.net > .env
echo JIRA_EMAIL=your-email@example.com >> .env  
echo JIRA_TOKEN=your-jira-api-token >> .env
```

**Option B: Set system environment variables**
```bash
set JIRA_BASE_URL=https://your-domain.atlassian.net
set JIRA_EMAIL=your-email@example.com
set JIRA_TOKEN=your-jira-api-token
```

3. Run the application:
```bash
python fetch_and_fix_agent.py
```

4. Open your browser and navigate to `http://localhost:5000`

## Usage

1. **Fetch Issue**: Enter a Jira issue key (e.g., "PROJ-123") and click "Fetch Issue"
2. **View Details**: Review the comprehensive issue information displayed
3. **Generate Fixes**: Click "Generate Fix Suggestions" to get intelligent recommendations
4. **Apply Solutions**: Use the suggested fixes as a starting point for issue resolution

## Security 🔐

- ✅ **No Hardcoded Secrets**: Jira credentials stored as environment variables
- ✅ **Git Safe**: `.env` file automatically excluded from version control  
- ✅ **API Tokens**: Uses secure API tokens instead of passwords
- ✅ **Environment Validation**: Application validates all required variables on startup
- ✅ **Flexible Configuration**: Supports both `.env` file and system environment variables

### Security Verification
```bash
# Verify .env is not tracked by git
git status  # .env should NOT appear in the output

# Check .gitignore protects .env
findstr "\.env" .gitignore  # Should show .env is excluded
```

## Fix Suggestion Categories

The tool provides targeted suggestions for:
- **Bug Fixes**: Error handling, logging, and debugging strategies
- **Performance**: Optimization techniques and bottleneck identification
- **Security**: Authentication, validation, and security best practices
- **UI/UX**: Frontend improvements and accessibility enhancements
- **Data Issues**: Database operations and data integrity checks

## Configuration

Key environment variables:
- `JIRA_BASE_URL`: Your Atlassian domain URL
- `JIRA_EMAIL`: Your Jira account email
- `JIRA_TOKEN`: API token from Jira (not your password)
- `FLASK_SECRET_KEY`: Secret key for Flask sessions

## Development

To run in development mode:
```bash
set FLASK_ENV=development
python fetch_and_fix_agent.py
```

The application will run with debug mode enabled and auto-reload on file changes.
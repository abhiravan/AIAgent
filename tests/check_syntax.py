"""
Syntax checker for all Python files in the project
"""

import os
import py_compile
import sys

def check_syntax(file_path):
    """Check syntax of a Python file"""
    try:
        py_compile.compile(file_path, doraise=True)
        return True, "OK"
    except py_compile.PyCompileError as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)

def main():
    """Check all Python files for syntax errors"""
    print("🔍 Checking Python file syntax...")
    print("=" * 40)
    
    python_files = [
        'fetch_and_fix_agent.py',
        'services/jira_service.py', 
        'services/ai_service.py',
        'services/github_service.py',
        'tests/test_ai_integration.py',
        'tests/configure_ai.py',
        'tests/demo_ai_analysis.py'
    ]
    
    all_ok = True
    
    for file in python_files:
        if os.path.exists(file):
            is_ok, message = check_syntax(file)
            status = "✅" if is_ok else "❌"
            print(f"{status} {file}: {message}")
            if not is_ok:
                all_ok = False
        else:
            print(f"⚠️  {file}: File not found")
    
    print("\n" + "=" * 40)
    if all_ok:
        print("🎉 All Python files have correct syntax!")
    else:
        print("❌ Some files have syntax errors")
    
    return all_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
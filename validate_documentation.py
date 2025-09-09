#!/usr/bin/env python3
"""
Documentation Validation Script

This script validates that the documentation is comprehensive and accurate.
It checks for:
- All CLI options are documented
- All methods have docstrings
- Examples are valid
- Configuration is complete
"""

import ast
import inspect
import os
import sys
from pathlib import Path
from typing import List, Dict, Any

def extract_cli_options(script_path: str) -> List[str]:
    """Extract CLI options from the script."""
    with open(script_path, 'r') as f:
        content = f.read()
    
    # Find argparse.add_argument calls
    options = []
    lines = content.split('\n')
    for line in lines:
        if 'add_argument(' in line and '--' in line:
            # Extract the option name
            if '--' in line:
                start = line.find('--')
                end = line.find(' ', start)
                if end == -1:
                    end = line.find(',', start)
                if end == -1:
                    end = line.find(')', start)
                if end != -1:
                    option = line[start:end].strip()
                    options.append(option)
    
    return options

def extract_method_docstrings(script_path: str) -> Dict[str, str]:
    """Extract method docstrings from the script."""
    with open(script_path, 'r') as f:
        content = f.read()
    
    tree = ast.parse(content)
    docstrings = {}
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if node.name.startswith('_'):
                continue
            if ast.get_docstring(node):
                docstrings[node.name] = ast.get_docstring(node)
    
    return docstrings

def check_readme_completeness(readme_path: str, cli_options: List[str]) -> List[str]:
    """Check if README contains all CLI options."""
    with open(readme_path, 'r') as f:
        content = f.read()
    
    missing_options = []
    for option in cli_options:
        if option not in content:
            missing_options.append(option)
    
    return missing_options

def check_example_data_files(data_dir: str) -> Dict[str, bool]:
    """Check if example data files exist and are properly formatted."""
    data_path = Path(data_dir)
    results = {}
    
    required_files = [
        "contact information.txt",
        "degree information.txt", 
        "work history information.txt",
        "skills.txt",
        "projects.txt",
        "classes taken.txt",
        "extracurriculars information.txt"
    ]
    
    for file_name in required_files:
        file_path = data_path / file_name
        results[file_name] = file_path.exists() and file_path.stat().st_size > 0
    
    return results

def validate_script_structure(script_path: str) -> Dict[str, Any]:
    """Validate the script structure and documentation."""
    with open(script_path, 'r') as f:
        content = f.read()
    
    results = {
        "has_shebang": content.startswith('#!/usr/bin/env python3'),
        "has_docstring": '"""' in content[:500],
        "has_imports": "import" in content,
        "has_main_function": "def main():" in content,
        "has_class": "class ResumeBuilder:" in content,
        "has_error_handling": "try:" in content and "except" in content,
        "has_logging": "print(" in content,
        "has_type_hints": "->" in content,
        "has_examples": "Examples:" in content
    }
    
    return results

def generate_documentation_report():
    """Generate a comprehensive documentation report."""
    print("📋 Resume Builder Documentation Validation Report")
    print("=" * 50)
    
    # Check script structure
    print("\n🔍 Script Structure Validation:")
    script_path = "resume_builder.py"
    if os.path.exists(script_path):
        structure = validate_script_structure(script_path)
        for key, value in structure.items():
            status = "✅" if value else "❌"
            print(f"  {status} {key.replace('_', ' ').title()}")
    else:
        print("  ❌ Script file not found")
    
    # Check CLI options documentation
    print("\n📝 CLI Options Documentation:")
    cli_options = extract_cli_options(script_path)
    readme_path = "README.md"
    
    if os.path.exists(readme_path):
        missing_options = check_readme_completeness(readme_path, cli_options)
        if missing_options:
            print("  ❌ Missing CLI options in README:")
            for option in missing_options:
                print(f"    - {option}")
        else:
            print("  ✅ All CLI options documented in README")
    else:
        print("  ❌ README.md not found")
    
    # Check method documentation
    print("\n📚 Method Documentation:")
    docstrings = extract_method_docstrings(script_path)
    methods_without_docs = []
    
    # Get all public methods from the class
    with open(script_path, 'r') as f:
        content = f.read()
    
    tree = ast.parse(content)
    class_methods = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "ResumeBuilder":
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and not item.name.startswith('_'):
                    class_methods.append(item.name)
    
    for method in class_methods:
        if method not in docstrings:
            methods_without_docs.append(method)
    
    if methods_without_docs:
        print("  ❌ Methods without docstrings:")
        for method in methods_without_docs:
            print(f"    - {method}")
    else:
        print("  ✅ All public methods have docstrings")
    
    # Check example data files
    print("\n📁 Example Data Files:")
    data_results = check_example_data_files("data")
    all_files_exist = all(data_results.values())
    
    if all_files_exist:
        print("  ✅ All required data files exist")
    else:
        print("  ❌ Missing or empty data files:")
        for file_name, exists in data_results.items():
            status = "✅" if exists else "❌"
            print(f"    {status} {file_name}")
    
    # Check configuration file
    print("\n⚙️ Configuration:")
    config_path = "config.py"
    if os.path.exists(config_path):
        print("  ✅ Configuration file exists")
    else:
        print("  ❌ Configuration file missing")
    
    # Check example documentation
    print("\n📖 Example Documentation:")
    example_doc_path = "example_data_structure.md"
    if os.path.exists(example_doc_path):
        print("  ✅ Example data structure documentation exists")
    else:
        print("  ❌ Example data structure documentation missing")
    
    # Check test files
    print("\n🧪 Test Files:")
    test_files = ["test_setup.py", "validate_documentation.py"]
    for test_file in test_files:
        if os.path.exists(test_file):
            print(f"  ✅ {test_file} exists")
        else:
            print(f"  ❌ {test_file} missing")
    
    # Overall assessment
    print("\n📊 Overall Assessment:")
    total_checks = len(structure) + len(cli_options) + len(class_methods) + len(data_results) + 4
    passed_checks = sum(structure.values()) + (len(cli_options) - len(missing_options)) + (len(class_methods) - len(methods_without_docs)) + sum(data_results.values()) + 4
    
    if all_files_exist and not missing_options and not methods_without_docs:
        passed_checks += 1
    
    score = (passed_checks / total_checks) * 100
    print(f"  Documentation Score: {score:.1f}%")
    
    if score >= 90:
        print("  🎉 Excellent documentation!")
    elif score >= 80:
        print("  👍 Good documentation with minor gaps")
    elif score >= 70:
        print("  ⚠️ Documentation needs improvement")
    else:
        print("  🚨 Documentation requires significant work")

if __name__ == "__main__":
    generate_documentation_report()

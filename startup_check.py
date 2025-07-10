#!/usr/bin/env python3
"""
Startup Check Script
Verifies system requirements and dependencies before running
"""

import sys
import subprocess
import importlib
from pathlib import Path

def check_python_version():
    """Check Python version compatibility"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} detected")
        print("⚠️  Python 3.8+ is required")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
    return True

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'gradio',
        'aiohttp', 
        'feedparser',
        'pandas',
        'numpy',
        'scikit-learn',
        'plotly',
        'cryptography',
        'psutil',
        'geopy',
        'schedule',
        'watchdog'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - Missing")
            missing_packages.append(package)
    
    return missing_packages

def check_files():
    """Check if required files exist"""
    required_files = [
        'app.py',
        'interactive_mcp_server.py',
        'dynamic_tool_manager.py',
        'api_tools_module.py',
        'api_integrations.py',
        'requirements.txt'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - Missing")
            missing_files.append(file_path)
    
    return missing_files

def install_missing_packages(packages):
    """Install missing packages"""
    if not packages:
        return True
    
    print(f"\n📦 Installing {len(packages)} missing packages...")
    
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install"
        ] + packages, check=True)
        
        print("✅ All packages installed successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Installation failed: {e}")
        return False

def main():
    """Run startup checks"""
    print("🔍 MCP Tools - Startup Check")
    print("=" * 40)
    
    # Check Python version
    print("\n🐍 Checking Python version...")
    if not check_python_version():
        print("\n❌ Python version check failed")
        sys.exit(1)
    
    # Check files
    print("\n📁 Checking required files...")
    missing_files = check_files()
    if missing_files:
        print(f"\n❌ Missing files: {', '.join(missing_files)}")
        print("Please ensure all project files are present")
        sys.exit(1)
    
    # Check dependencies
    print("\n📦 Checking dependencies...")
    missing_packages = check_dependencies()
    
    if missing_packages:
        print(f"\n⚠️  Found {len(missing_packages)} missing packages")
        
        response = input("Install missing packages? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            if install_missing_packages(missing_packages):
                print("\n✅ All dependencies satisfied!")
            else:
                print("\n❌ Dependency installation failed")
                sys.exit(1)
        else:
            print("\n❌ Cannot proceed without required dependencies")
            print("Install manually with: pip install -r requirements.txt")
            sys.exit(1)
    else:
        print("\n✅ All dependencies satisfied!")
    
    # Test basic imports
    print("\n🧪 Testing core imports...")
    try:
        import gradio
        import aiohttp
        import pandas
        print("✅ Core imports successful")
    except ImportError as e:
        print(f"❌ Import test failed: {e}")
        sys.exit(1)
    
    print("\n🚀 System ready! You can now run:")
    print("   python app.py")
    print("\n" + "=" * 40)

if __name__ == "__main__":
    main()
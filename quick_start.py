#!/usr/bin/env python3
"""
Quick Start Script for MCP Tools
Provides easy commands to run different modes of the system
"""

import subprocess
import sys
import argparse
from pathlib import Path

def run_web_interface():
    """Run the web interface (default mode)"""
    print("🌐 Starting web interface...")
    subprocess.run([sys.executable, "app.py"])

def run_mcp_server():
    """Run MCP server only"""
    print("🔧 Starting MCP server...")
    subprocess.run([sys.executable, "main.py", "--mode", "mcp"])

def run_api_tests():
    """Run API connectivity tests"""
    print("🔍 Testing API connections...")
    subprocess.run([sys.executable, "examples/api_usage_examples.py"])

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

def main():
    parser = argparse.ArgumentParser(description="Quick Start for MCP Tools")
    parser.add_argument(
        "command",
        choices=["web", "mcp", "test", "install"],
        help="Command to run: web (default interface), mcp (server only), test (API tests), install (dependencies)"
    )
    
    args = parser.parse_args()
    
    if args.command == "web":
        run_web_interface()
    elif args.command == "mcp":
        run_mcp_server()
    elif args.command == "test":
        run_api_tests()
    elif args.command == "install":
        install_dependencies()

if __name__ == "__main__":
    if len(sys.argv) == 1:
        # No arguments provided, run web interface by default
        run_web_interface()
    else:
        main()
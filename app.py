#!/usr/bin/env python3
"""
Interactive MCP Tools System - Main Application
Dynamic tool management with real-time requirement detection and free API integrations.
Just run: python app.py
"""

import asyncio
import logging
import sys
import threading
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('mcp_tools.log')
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Main entry point - starts the interactive system"""
    
    print("🚀 Starting Interactive MCP Tools System with Free API Integrations")
    print("=" * 70)
    
    try:
        # Import here to handle any import errors gracefully
        from interactive_mcp_server import interactive_server
        
        # Test API connections on startup
        logger.info("🔍 Testing API connections...")
        try:
            from api_tools_module import APIToolsModule
            api_module = APIToolsModule()
            test_results = api_module.test_api_connectivity_sync()
            success_rate = test_results.get('success_rate', 'N/A')
            available_apis = test_results.get('available_apis', 0)
            total_apis = test_results.get('total_apis', 0)
            
            print(f"📡 API Status: {available_apis}/{total_apis} APIs available ({success_rate} success rate)")
            
            if available_apis > 0:
                print("✅ System ready with API integrations!")
            else:
                print("⚠️  No APIs available, but core tools will still work")
                
        except Exception as e:
            print(f"⚠️  API test failed: {e}")
            print("Core tools will still be available")
        
        # Start the system
        print("\n🌐 Starting web interface...")
        print("📍 Open your browser to: http://localhost:7860")
        print("💡 The system will automatically detect your needs and load the right tools!")
        print("\n" + "=" * 70)
        
        # Launch Gradio interface
        interactive_server.launch_gradio(
            server_name="127.0.0.1",
            server_port=7860,
            share=False,
            show_error=True,
            quiet=False
        )
        
    except ImportError as e:
        print(f"❌ Import Error: {str(e)}")
        print("\n🔧 Please install required dependencies:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
        
    except KeyboardInterrupt:
        print("\n👋 Shutting down gracefully...")
        try:
            interactive_server.shutdown()
        except:
            pass
        
    except Exception as e:
        print(f"❌ Startup Error: {str(e)}")
        print("\n🔧 Troubleshooting:")
        print("1. Ensure all dependencies are installed: pip install -r requirements.txt")
        print("2. Check network connectivity for API access")
        print("3. Verify Python version compatibility (3.8+)")
        print("4. Check the log file: mcp_tools.log")
        sys.exit(1)

if __name__ == "__main__":
    main()
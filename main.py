#!/usr/bin/env python3
"""
Interactive MCP Tools System
Dynamic tool management with real-time requirement detection and automatic module loading.
Includes free API integrations for research, development, and information gathering.
"""

import asyncio
import logging
import argparse
import sys
from pathlib import Path

from interactive_mcp_server import interactive_server

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
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Interactive MCP Tools System with Free API Integrations")
    parser.add_argument(
        "--mode", 
        choices=["gradio", "mcp", "both"], 
        default="gradio",
        help="Run mode: gradio (web interface), mcp (MCP server), or both"
    )
    parser.add_argument(
        "--host", 
        default="127.0.0.1",
        help="Host for Gradio interface"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=7860,
        help="Port for Gradio interface"
    )
    parser.add_argument(
        "--share", 
        action="store_true",
        help="Create public Gradio link"
    )
    parser.add_argument(
        "--debug", 
        action="store_true",
        help="Enable debug logging"
    )
    parser.add_argument(
        "--test-apis",
        action="store_true",
        help="Test all API connections on startup"
    )
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    logger.info("🚀 Starting Interactive MCP Tools System with API Integrations")
    
    try:
        if args.test_apis:
            logger.info("🔍 Testing API connections...")
            # Test API connections
            from api_tools_module import APIToolsModule
            api_module = APIToolsModule()
            test_results = api_module.test_api_connectivity_sync()
            logger.info(f"API Test Results: {test_results.get('success_rate', 'N/A')} success rate")
        
        if args.mode == "gradio":
            logger.info("Starting Gradio interface...")
            interactive_server.launch_gradio(
                server_name=args.host,
                server_port=args.port,
                share=args.share,
                show_error=True
            )
        elif args.mode == "mcp":
            logger.info("Starting MCP server...")
            asyncio.run(interactive_server.run_server())
        elif args.mode == "both":
            logger.info("Starting both Gradio and MCP server...")
            # Run both in parallel
            async def run_both():
                await asyncio.gather(
                    interactive_server.run_server(),
                    # Note: Gradio needs to run in main thread, so this is simplified
                )
            
            # Start Gradio in background thread and MCP in main
            import threading
            gradio_thread = threading.Thread(
                target=lambda: interactive_server.launch_gradio(
                    server_name=args.host,
                    server_port=args.port,
                    share=args.share
                )
            )
            gradio_thread.daemon = True
            gradio_thread.start()
            
            # Run MCP server
            asyncio.run(interactive_server.run_server())
            
    except KeyboardInterrupt:
        logger.info("👋 Shutting down...")
        interactive_server.shutdown()
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
        print(f"❌ Startup failed: {str(e)}")
        print("Please check the following:")
        print("1. Ensure all dependencies are installed: pip install -r requirements.txt")
        print("2. Check network connectivity for API access")
        print("3. Verify Python version compatibility (3.8+)")
        sys.exit(1)

if __name__ == "__main__":
    main()
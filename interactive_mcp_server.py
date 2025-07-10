import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import gradio as gr
from mcp.server import Server
from mcp.types import (
    TextContent, 
    Tool, 
    CallToolResult, 
    ListToolsResult,
    GetPromptResult,
    ListPromptsResult,
    Prompt,
    PromptArgument
)

from dynamic_tool_manager import DynamicToolManager

logger = logging.getLogger(__name__)

class InteractiveMCPServer:
    """Interactive MCP Server with dynamic tool management"""
    
    def __init__(self):
        self.tool_manager = DynamicToolManager()
        self.server = Server("interactive-mcp-tools")
        self.chat_history = []
        self.setup_server_handlers()
        
        # Load initial modules
        self._load_initial_modules()
    
    def _load_initial_modules(self):
        """Load initial set of modules"""
        initial_modules = [
            "task_automation",
            "data_reports", 
            "financial_compliance",
            "health_focus",
            "security_privacy"
        ]
        
        for module in initial_modules:
            self.tool_manager.load_module(module)
    
    def setup_server_handlers(self):
        """Setup MCP server handlers"""
        
        @self.server.list_tools()
        async def list_tools() -> ListToolsResult:
            """List all available tools dynamically"""
            tools = []
            available_tools = self.tool_manager.get_available_tools()
            
            for tool_info in available_tools:
                # Convert to MCP Tool format
                input_schema = {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
                
                for param in tool_info["parameters"]:
                    input_schema["properties"][param["name"]] = {
                        "type": "string",  # Simplified for now
                        "description": f"Parameter: {param['name']}"
                    }
                    if param["required"]:
                        input_schema["required"].append(param["name"])
                
                tool = Tool(
                    name=tool_info["name"],
                    description=tool_info["description"],
                    inputSchema=input_schema
                )
                tools.append(tool)
            
            return ListToolsResult(tools=tools)
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
            """Execute a tool dynamically"""
            result = await self.tool_manager.execute_tool(name, **arguments)
            
            if result.get("success", False):
                content = json.dumps(result["result"], indent=2, default=str)
            else:
                content = f"Error: {result.get('error', 'Unknown error')}"
            
            return CallToolResult(
                content=[TextContent(type="text", text=content)]
            )
        
        @self.server.list_prompts()
        async def list_prompts() -> ListPromptsResult:
            """List available prompts"""
            prompts = [
                Prompt(
                    name="analyze_requirements",
                    description="Analyze user requirements and suggest tools",
                    arguments=[
                        PromptArgument(name="user_input", description="User's request or requirement", required=True)
                    ]
                ),
                Prompt(
                    name="tool_status",
                    description="Get status of all loaded tools and modules",
                    arguments=[]
                ),
                Prompt(
                    name="usage_analytics", 
                    description="Get tool usage analytics and recommendations",
                    arguments=[]
                )
            ]
            return ListPromptsResult(prompts=prompts)
        
        @self.server.get_prompt()
        async def get_prompt(name: str, arguments: Dict[str, str]) -> GetPromptResult:
            """Get dynamic prompts based on current system state"""
            
            if name == "analyze_requirements":
                user_input = arguments.get("user_input", "")
                analysis = self.tool_manager.detect_and_load_requirements(user_input)
                
                prompt_content = f"""
Based on your request: "{user_input}"

I've analyzed your requirements and here's what I found:

**Detected Requirements:**
{json.dumps(analysis['detected_requirements'], indent=2)}

**Loaded Modules:**
{', '.join(analysis['loaded_modules']) if analysis['loaded_modules'] else 'None'}

**Failed Modules:**
{', '.join(analysis['failed_modules']) if analysis['failed_modules'] else 'None'}

**Installed Dependencies:**
{', '.join(analysis['installed_dependencies']) if analysis['installed_dependencies'] else 'None'}

**Available Tools:**
{self._format_available_tools()}

How would you like to proceed with these tools?
"""
            
            elif name == "tool_status":
                module_status = self.tool_manager.get_module_status()
                available_tools = self.tool_manager.get_available_tools()
                
                prompt_content = f"""
**System Status Report**
Generated at: {datetime.now().isoformat()}

**Module Status:**
{json.dumps(module_status, indent=2, default=str)}

**Available Tools:** {len(available_tools)}
{self._format_available_tools()}

**System Health:** {'✅ Good' if all(m.get('loaded', False) for m in module_status.values()) else '⚠️ Some issues detected'}
"""
            
            elif name == "usage_analytics":
                analytics = self.tool_manager.get_usage_analytics()
                
                prompt_content = f"""
**Tool Usage Analytics**
Generated at: {datetime.now().isoformat()}

{json.dumps(analytics, indent=2, default=str)}

**Recommendations:**
- Most used tool: {analytics.get('most_used_tool', 'N/A')}
- Average success rate: {analytics.get('average_success_rate', 0):.2%}
- Consider optimizing frequently used tools
- Monitor tools with low success rates
"""
            
            else:
                prompt_content = f"Unknown prompt: {name}"
            
            return GetPromptResult(
                description=f"Dynamic prompt for {name}",
                messages=[
                    {"role": "system", "content": prompt_content}
                ]
            )
    
    def _format_available_tools(self) -> str:
        """Format available tools for display"""
        tools = self.tool_manager.get_available_tools()
        if not tools:
            return "No tools currently available"
        
        formatted = []
        for tool in tools:
            formatted.append(f"- **{tool['name']}**: {tool['description']} (Module: {tool['module']})")
        
        return '\n'.join(formatted)
    
    def create_gradio_interface(self) -> gr.Interface:
        """Create Gradio interface for interactive tool management"""
        
        def process_user_input(user_input: str, chat_history: List[List[str]]) -> tuple:
            """Process user input and return response"""
            try:
                # Detect and load requirements
                analysis = self.tool_manager.detect_and_load_requirements(user_input)
                
                response = f"""
🔍 **Requirement Analysis Complete**

**Detected Requirements:** {len(analysis['detected_requirements'])}
{', '.join([req['category'] for req in analysis['detected_requirements']])}

**Loaded Modules:** {', '.join(analysis['loaded_modules']) if analysis['loaded_modules'] else 'None'}

**Available Tools:** {len(self.tool_manager.get_available_tools())}

**Next Steps:**
1. Use the tools listed below for your tasks
2. Ask for specific tool execution
3. Request analytics or status updates

**Available Tools:**
{self._format_available_tools()}
"""
                
                # Update chat history
                chat_history.append([user_input, response])
                
                return "", chat_history
                
            except Exception as e:
                error_response = f"❌ Error processing request: {str(e)}"
                chat_history.append([user_input, error_response])
                return "", chat_history
        
        def execute_tool_interface(tool_name: str, parameters: str) -> str:
            """Execute tool through interface"""
            try:
                # Parse parameters
                if parameters.strip():
                    params = json.loads(parameters)
                else:
                    params = {}
                
                # Execute tool synchronously for Gradio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(
                    self.tool_manager.execute_tool(tool_name, **params)
                )
                loop.close()
                
                if result.get("success", False):
                    return f"✅ **Success**\n\n```json\n{json.dumps(result['result'], indent=2, default=str)}\n```"
                else:
                    return f"❌ **Error**\n\n{result.get('error', 'Unknown error')}"
                    
            except json.JSONDecodeError:
                return "❌ **Error**: Invalid JSON parameters"
            except Exception as e:
                return f"❌ **Error**: {str(e)}"
        
        def get_system_status() -> str:
            """Get current system status"""
            try:
                module_status = self.tool_manager.get_module_status()
                analytics = self.tool_manager.get_usage_analytics()
                
                status_report = f"""
# 📊 System Status Report
*Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

## 🔧 Module Status
"""
                for name, status in module_status.items():
                    icon = "✅" if status.get('loaded', False) else "❌"
                    status_report += f"- {icon} **{name}**: {'Loaded' if status.get('loaded', False) else 'Failed'}\n"
                
                status_report += f"""
## 📈 Usage Analytics
- **Total Tools**: {analytics.get('total_tools', 0)}
- **Active Modules**: {analytics.get('active_modules', 0)}
- **Most Used Tool**: {analytics.get('most_used_tool', 'N/A')}
- **Average Success Rate**: {analytics.get('average_success_rate', 0):.2%}

## 🛠️ Available Tools
{self._format_available_tools()}
"""
                return status_report
                
            except Exception as e:
                return f"❌ Error getting system status: {str(e)}"
        
        def get_tool_list() -> List[str]:
            """Get list of available tools"""
            tools = self.tool_manager.get_available_tools()
            return [tool['name'] for tool in tools]
        
        # Create Gradio interface
        with gr.Blocks(title="🚀 Interactive MCP Tools", theme=gr.themes.Soft()) as interface:
            gr.Markdown("# 🚀 Interactive MCP Tools System")
            gr.Markdown("Dynamic tool management with real-time requirement detection and automatic module loading.")
            
            with gr.Tab("💬 Chat Interface"):
                chatbot = gr.Chatbot(
                    value=[["system", "👋 Welcome! I can detect your requirements and automatically load the right tools. Just tell me what you need help with!"]],
                    height=400
                )
                
                with gr.Row():
                    user_input = gr.Textbox(
                        placeholder="Describe what you need help with...",
                        label="Your Request",
                        scale=4
                    )
                    submit_btn = gr.Button("Send", scale=1, variant="primary")
                
                submit_btn.click(
                    process_user_input,
                    inputs=[user_input, chatbot],
                    outputs=[user_input, chatbot]
                )
                
                user_input.submit(
                    process_user_input,
                    inputs=[user_input, chatbot], 
                    outputs=[user_input, chatbot]
                )
            
            with gr.Tab("🔧 Tool Execution"):
                with gr.Row():
                    tool_dropdown = gr.Dropdown(
                        choices=get_tool_list(),
                        label="Select Tool",
                        scale=2
                    )
                    refresh_tools_btn = gr.Button("🔄 Refresh", scale=1)
                
                parameters_input = gr.Textbox(
                    placeholder='{"param1": "value1", "param2": "value2"}',
                    label="Parameters (JSON format)",
                    lines=3
                )
                
                execute_btn = gr.Button("▶️ Execute Tool", variant="primary")
                
                result_output = gr.Markdown(label="Result")
                
                refresh_tools_btn.click(
                    lambda: gr.Dropdown(choices=get_tool_list()),
                    outputs=tool_dropdown
                )
                
                execute_btn.click(
                    execute_tool_interface,
                    inputs=[tool_dropdown, parameters_input],
                    outputs=result_output
                )
            
            with gr.Tab("📊 System Status"):
                status_output = gr.Markdown()
                refresh_status_btn = gr.Button("🔄 Refresh Status", variant="secondary")
                
                refresh_status_btn.click(
                    get_system_status,
                    outputs=status_output
                )
                
                # Auto-refresh on load
                interface.load(get_system_status, outputs=status_output)
        
        return interface
    
    def launch_gradio(self, **kwargs):
        """Launch Gradio interface"""
        interface = self.create_gradio_interface()
        return interface.launch(**kwargs)
    
    async def run_server(self):
        """Run the MCP server"""
        async with self.server.run_stdio() as streams:
            await self.server.run()
    
    def shutdown(self):
        """Shutdown the server"""
        self.tool_manager.shutdown()

# Global instance
interactive_server = InteractiveMCPServer()
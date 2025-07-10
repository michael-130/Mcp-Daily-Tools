import asyncio
import json
import importlib
import inspect
import threading
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Set
from pathlib import Path
from dataclasses import dataclass, asdict
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess
import sys
import pkg_resources
from concurrent.futures import ThreadPoolExecutor
import sqlite3

logger = logging.getLogger(__name__)

@dataclass
class ToolRequirement:
    """Tool requirement specification"""
    name: str
    description: str
    category: str
    priority: int = 1
    dependencies: List[str] = None
    auto_install: bool = True
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.dependencies is None:
            self.dependencies = []

@dataclass
class ModuleStatus:
    """Module status tracking"""
    name: str
    loaded: bool = False
    last_updated: datetime = None
    error_count: int = 0
    last_error: str = ""
    dependencies_met: bool = True
    
    def __post_init__(self):
        if self.last_updated is None:
            self.last_updated = datetime.now()

class RequirementDetector:
    """Detects new user requirements and tool needs"""
    
    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self.patterns = {
            "financial": ["budget", "expense", "money", "cost", "financial", "payment"],
            "health": ["wellness", "health", "fitness", "exercise", "sleep", "stress"],
            "productivity": ["task", "schedule", "time", "productivity", "focus", "work"],
            "security": ["security", "privacy", "encrypt", "audit", "compliance"],
            "data": ["report", "analysis", "chart", "visualization", "insight"]
        }
        self.setup_database()
    
    def setup_database(self):
        """Setup requirement tracking database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_requests (
                id INTEGER PRIMARY KEY,
                request_text TEXT,
                detected_category TEXT,
                confidence REAL,
                timestamp TEXT,
                processed BOOLEAN DEFAULT FALSE
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tool_usage (
                id INTEGER PRIMARY KEY,
                tool_name TEXT,
                usage_count INTEGER DEFAULT 1,
                last_used TEXT,
                success_rate REAL DEFAULT 1.0
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def detect_requirements(self, user_input: str) -> List[ToolRequirement]:
        """Detect tool requirements from user input"""
        requirements = []
        user_input_lower = user_input.lower()
        
        # Store user request
        self._store_user_request(user_input)
        
        # Detect categories
        for category, keywords in self.patterns.items():
            confidence = sum(1 for keyword in keywords if keyword in user_input_lower) / len(keywords)
            
            if confidence > 0.2:  # Threshold for requirement detection
                requirement = ToolRequirement(
                    name=f"{category}_tool",
                    description=f"Tool for {category} related tasks",
                    category=category,
                    priority=int(confidence * 5)
                )
                requirements.append(requirement)
        
        return requirements
    
    def _store_user_request(self, request_text: str):
        """Store user request for analysis"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO user_requests (request_text, timestamp)
            VALUES (?, ?)
        ''', (request_text, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()

class DependencyManager:
    """Manages automatic installation and updates of dependencies"""
    
    def __init__(self):
        self.installed_packages = set()
        self.failed_installations = {}
        self.update_cache()
    
    def update_cache(self):
        """Update cache of installed packages"""
        try:
            self.installed_packages = {pkg.project_name.lower() for pkg in pkg_resources.working_set}
        except Exception as e:
            logger.error(f"Failed to update package cache: {e}")
    
    def check_dependencies(self, dependencies: List[str]) -> Dict[str, bool]:
        """Check if dependencies are installed"""
        status = {}
        for dep in dependencies:
            dep_name = dep.split('>=')[0].split('==')[0].strip()
            status[dep] = dep_name.lower() in self.installed_packages
        return status
    
    def install_dependencies(self, dependencies: List[str]) -> Dict[str, bool]:
        """Install missing dependencies"""
        results = {}
        
        for dep in dependencies:
            if dep in self.failed_installations:
                # Skip if recently failed
                if datetime.now() - self.failed_installations[dep] < timedelta(hours=1):
                    results[dep] = False
                    continue
            
            try:
                logger.info(f"Installing dependency: {dep}")
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install", dep],
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                if result.returncode == 0:
                    results[dep] = True
                    self.installed_packages.add(dep.split('>=')[0].split('==')[0].strip().lower())
                    logger.info(f"Successfully installed: {dep}")
                else:
                    results[dep] = False
                    self.failed_installations[dep] = datetime.now()
                    logger.error(f"Failed to install {dep}: {result.stderr}")
                    
            except subprocess.TimeoutExpired:
                results[dep] = False
                self.failed_installations[dep] = datetime.now()
                logger.error(f"Installation timeout for: {dep}")
            except Exception as e:
                results[dep] = False
                self.failed_installations[dep] = datetime.now()
                logger.error(f"Installation error for {dep}: {e}")
        
        return results

class ConfigurationManager:
    """Manages dynamic configuration updates"""
    
    def __init__(self, config_path: str = "config"):
        self.config_path = Path(config_path)
        self.config_path.mkdir(exist_ok=True)
        self.configurations = {}
        self.load_configurations()
    
    def load_configurations(self):
        """Load all configuration files"""
        for config_file in self.config_path.glob("*.json"):
            try:
                with open(config_file, 'r') as f:
                    config_name = config_file.stem
                    self.configurations[config_name] = json.load(f)
                    logger.info(f"Loaded configuration: {config_name}")
            except Exception as e:
                logger.error(f"Failed to load config {config_file}: {e}")
    
    def update_configuration(self, name: str, config: Dict[str, Any]):
        """Update configuration dynamically"""
        self.configurations[name] = config
        
        # Save to file
        config_file = self.config_path / f"{name}.json"
        try:
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2, default=str)
            logger.info(f"Updated configuration: {name}")
        except Exception as e:
            logger.error(f"Failed to save config {name}: {e}")
    
    def get_configuration(self, name: str) -> Dict[str, Any]:
        """Get configuration by name"""
        return self.configurations.get(name, {})

class FileWatcher(FileSystemEventHandler):
    """Watches for file changes and triggers reloads"""
    
    def __init__(self, callback: Callable[[str], None]):
        self.callback = callback
        self.last_modified = {}
    
    def on_modified(self, event):
        if event.is_directory:
            return
        
        file_path = event.src_path
        current_time = time.time()
        
        # Debounce rapid file changes
        if file_path in self.last_modified:
            if current_time - self.last_modified[file_path] < 1.0:
                return
        
        self.last_modified[file_path] = current_time
        
        if file_path.endswith('.py'):
            logger.info(f"Python file changed: {file_path}")
            self.callback(file_path)

class DynamicToolManager:
    """Enhanced dynamic tool manager with real-time monitoring"""
    
    def __init__(self):
        self.modules: Dict[str, ModuleStatus] = {}
        self.loaded_tools: Dict[str, Callable] = {}
        self.module_instances: Dict[str, Any] = {}
        self.requirement_detector = RequirementDetector()
        self.dependency_manager = DependencyManager()
        self.config_manager = ConfigurationManager()
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.monitoring_active = False
        self.file_observer = None
        self.setup_monitoring()
    
    def setup_monitoring(self):
        """Setup file system monitoring"""
        self.file_observer = Observer()
        file_watcher = FileWatcher(self.on_file_changed)
        
        # Watch current directory and subdirectories
        self.file_observer.schedule(file_watcher, ".", recursive=True)
        self.file_observer.start()
        self.monitoring_active = True
        
        logger.info("File system monitoring started")
    
    def on_file_changed(self, file_path: str):
        """Handle file changes"""
        try:
            # Extract module name from file path
            module_name = Path(file_path).stem
            
            if module_name in self.modules:
                logger.info(f"Reloading module due to file change: {module_name}")
                self.reload_module(module_name)
        except Exception as e:
            logger.error(f"Error handling file change {file_path}: {e}")
    
    def detect_and_load_requirements(self, user_input: str) -> Dict[str, Any]:
        """Detect requirements and automatically load needed modules"""
        requirements = self.requirement_detector.detect_requirements(user_input)
        results = {
            "detected_requirements": [asdict(req) for req in requirements],
            "loaded_modules": [],
            "failed_modules": [],
            "installed_dependencies": []
        }
        
        for requirement in requirements:
            try:
                # Check if module exists
                module_path = f"{requirement.category.lower()}_module"
                
                if self.module_exists(module_path):
                    # Check and install dependencies
                    if requirement.dependencies:
                        dep_status = self.dependency_manager.check_dependencies(requirement.dependencies)
                        missing_deps = [dep for dep, installed in dep_status.items() if not installed]
                        
                        if missing_deps and requirement.auto_install:
                            install_results = self.dependency_manager.install_dependencies(missing_deps)
                            results["installed_dependencies"].extend([dep for dep, success in install_results.items() if success])
                    
                    # Load module
                    if self.load_module_by_category(requirement.category):
                        results["loaded_modules"].append(requirement.name)
                    else:
                        results["failed_modules"].append(requirement.name)
                else:
                    logger.warning(f"Module not found for category: {requirement.category}")
                    results["failed_modules"].append(requirement.name)
                    
            except Exception as e:
                logger.error(f"Error processing requirement {requirement.name}: {e}")
                results["failed_modules"].append(requirement.name)
        
        return results
    
    def module_exists(self, module_path: str) -> bool:
        """Check if module file exists"""
        return Path(f"{module_path}.py").exists()
    
    def load_module_by_category(self, category: str) -> bool:
        """Load module by category"""
        module_mapping = {
            "financial": "financial_compliance",
            "health": "health_focus", 
            "productivity": "task_automation",
            "security": "security_privacy",
            "data": "data_reports",
            "api": "api_tools_module",
            "research": "api_tools_module",
            "information": "api_tools_module"
        }
        
        module_name = module_mapping.get(category.lower())
        if module_name:
            return self.load_module(module_name)
        return False
    
    def load_module(self, module_name: str) -> bool:
        """Load or reload a module"""
        try:
            # Update module status
            if module_name not in self.modules:
                self.modules[module_name] = ModuleStatus(name=module_name)
            
            status = self.modules[module_name]
            
            # Import or reload module
            if module_name in sys.modules:
                module = importlib.reload(sys.modules[module_name])
            else:
                module = importlib.import_module(module_name)
            
            # Find module class
            module_class_name = ''.join(word.capitalize() for word in module_name.split('_')) + 'Module'
            
            if hasattr(module, module_class_name):
                module_class = getattr(module, module_class_name)
                instance = module_class()
                self.module_instances[module_name] = instance
                
                # Load tools from module
                self._load_tools_from_instance(module_name, instance)
                
                # Update status
                status.loaded = True
                status.last_updated = datetime.now()
                status.error_count = 0
                status.last_error = ""
                
                logger.info(f"Successfully loaded module: {module_name}")
                return True
            else:
                raise AttributeError(f"Module class {module_class_name} not found")
                
        except Exception as e:
            # Update error status
            status = self.modules.get(module_name, ModuleStatus(name=module_name))
            status.loaded = False
            status.error_count += 1
            status.last_error = str(e)
            self.modules[module_name] = status
            
            logger.error(f"Failed to load module {module_name}: {e}")
            return False
    
    def reload_module(self, module_name: str):
        """Reload a specific module"""
        if module_name in self.module_instances:
            # Remove old tools
            tools_to_remove = [tool for tool in self.loaded_tools.keys() if tool.startswith(module_name)]
            for tool in tools_to_remove:
                del self.loaded_tools[tool]
            
            # Reload module
            self.load_module(module_name)
    
    def _load_tools_from_instance(self, module_name: str, instance: Any):
        """Load tools from module instance"""
        # Get all public methods that could be tools
        for method_name in dir(instance):
            if not method_name.startswith('_'):
                method = getattr(instance, method_name)
                if callable(method) and hasattr(method, '__doc__'):
                    tool_name = f"{module_name}_{method_name}"
                    self.loaded_tools[tool_name] = method
    
    def get_module_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all modules"""
        return {name: asdict(status) for name, status in self.modules.items()}
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get all available tools with metadata"""
        tools = []
        for tool_name, tool_func in self.loaded_tools.items():
            try:
                # Extract metadata from function
                signature = inspect.signature(tool_func)
                doc = tool_func.__doc__ or "No description available"
                
                tool_info = {
                    "name": tool_name,
                    "description": doc.split('\n')[0] if doc else "No description",
                    "parameters": [
                        {
                            "name": param.name,
                            "type": str(param.annotation) if param.annotation != param.empty else "Any",
                            "default": str(param.default) if param.default != param.empty else None,
                            "required": param.default == param.empty
                        }
                        for param in signature.parameters.values()
                    ],
                    "module": tool_name.split('_')[0] if '_' in tool_name else "unknown",
                    "loaded": True
                }
                tools.append(tool_info)
            except Exception as e:
                logger.error(f"Error getting tool info for {tool_name}: {e}")
        
        return tools
    
    async def execute_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """Execute a tool asynchronously"""
        if tool_name not in self.loaded_tools:
            return {"error": f"Tool {tool_name} not found or not loaded"}
        
        try:
            tool_func = self.loaded_tools[tool_name]
            
            # Execute in thread pool for CPU-bound tasks
            if inspect.iscoroutinefunction(tool_func):
                result = await tool_func(**kwargs)
            else:
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(self.executor, lambda: tool_func(**kwargs))
            
            # Update usage statistics
            self._update_tool_usage(tool_name, success=True)
            
            return {"result": result, "success": True}
            
        except Exception as e:
            self._update_tool_usage(tool_name, success=False)
            logger.error(f"Error executing tool {tool_name}: {e}")
            return {"error": str(e), "success": False}
    
    def _update_tool_usage(self, tool_name: str, success: bool):
        """Update tool usage statistics"""
        try:
            conn = sqlite3.connect(self.requirement_detector.db_path)
            cursor = conn.cursor()
            
            # Get current stats
            cursor.execute('SELECT usage_count, success_rate FROM tool_usage WHERE tool_name = ?', (tool_name,))
            row = cursor.fetchone()
            
            if row:
                usage_count, success_rate = row
                new_usage_count = usage_count + 1
                new_success_rate = (success_rate * usage_count + (1 if success else 0)) / new_usage_count
                
                cursor.execute('''
                    UPDATE tool_usage 
                    SET usage_count = ?, success_rate = ?, last_used = ?
                    WHERE tool_name = ?
                ''', (new_usage_count, new_success_rate, datetime.now().isoformat(), tool_name))
            else:
                cursor.execute('''
                    INSERT INTO tool_usage (tool_name, usage_count, success_rate, last_used)
                    VALUES (?, 1, ?, ?)
                ''', (tool_name, 1.0 if success else 0.0, datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Error updating tool usage for {tool_name}: {e}")
    
    def get_usage_analytics(self) -> Dict[str, Any]:
        """Get tool usage analytics"""
        try:
            conn = sqlite3.connect(self.requirement_detector.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT tool_name, usage_count, success_rate, last_used
                FROM tool_usage
                ORDER BY usage_count DESC
            ''')
            
            usage_data = cursor.fetchall()
            conn.close()
            
            return {
                "total_tools": len(self.loaded_tools),
                "active_modules": len([m for m in self.modules.values() if m.loaded]),
                "usage_stats": [
                    {
                        "tool_name": row[0],
                        "usage_count": row[1],
                        "success_rate": row[2],
                        "last_used": row[3]
                    }
                    for row in usage_data
                ],
                "most_used_tool": usage_data[0][0] if usage_data else None,
                "average_success_rate": sum(row[2] for row in usage_data) / len(usage_data) if usage_data else 0
            }
        except Exception as e:
            logger.error(f"Error getting usage analytics: {e}")
            return {"error": str(e)}
    
    def shutdown(self):
        """Shutdown the tool manager"""
        if self.file_observer:
            self.file_observer.stop()
            self.file_observer.join()
        
        self.executor.shutdown(wait=True)
        self.monitoring_active = False
        logger.info("Dynamic tool manager shutdown complete")
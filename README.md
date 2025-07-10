# Dynamic MCP Tools with Free API Integrations

A comprehensive, interactive Model Context Protocol (MCP) tools system with dynamic module loading and free API integrations. No authentication required for most features!

## 🌟 Features

### Dynamic Tool Management
- **Real-time requirement detection** - Automatically detects what tools you need based on your requests
- **Automatic module loading** - Loads the right modules on-demand
- **File system monitoring** - Automatically reloads modules when code changes
- **Dependency management** - Installs missing dependencies automatically
- **Usage analytics** - Tracks tool usage and performance

### Free API Integrations (No Auth Required)
- **🔬 arXiv** - Search academic papers and research
- **🐙 GitHub** - Repository information and statistics  
- **🌍 REST Countries** - Comprehensive country data
- **₿ CoinDesk** - Bitcoin price information
- **💭 QuoteGarden** - Inspirational quotes
- **🐱 Cat Facts** - Random fun facts
- **🧪 HTTPBin** - HTTP testing utilities

### Core Modules
- **Task Automation** - ML-powered task estimation and scheduling
- **Data Reports** - AI insights and visualizations
- **Financial Compliance** - Budget tracking and compliance
- **Health & Focus** - Wellness monitoring and focus sessions
- **Security & Privacy** - Security audits and privacy compliance

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd dynamic-mcp-tools

# Install dependencies
pip install -r requirements.txt
```

### Running the System

```bash
# Simple start - just run the app!
python app.py

# Alternative quick start options
python quick_start.py web      # Web interface (same as app.py)
python quick_start.py mcp      # MCP server only  
python quick_start.py test     # Test API connections
python quick_start.py install  # Install dependencies

# Advanced options (using main.py)
python main.py --mode gradio   # Web interface with options
python main.py --mode mcp      # MCP server only
python main.py --test-apis     # Test APIs on startup
python main.py --debug        # Enable debug logging
- **💬 Chat Interface** - Natural language interaction with automatic tool detection
- **🔧 Tool Execution** - Direct tool execution with parameter input
- **📊 System Status** - Real-time monitoring of modules and APIs

## 📖 Usage Examples

### Research Papers
```python
# Search for machine learning papers
result = api_module.search_research_papers_sync(
    query="machine learning",
    max_results=10,
    category="cs.LG"
)
```

### GitHub Repository Info
```python
# Get repository statistics
result = api_module.get_repository_info_sync("microsoft", "vscode")
print(f"Stars: {result['stars']:,}")
```

### Country Information
```python
# Look up country data
result = api_module.lookup_country_sync("Japan")
print(f"Population: {result['population_formatted']}")
```

### Batch API Requests
```python
# Execute multiple API calls
batch_requests = [
    {"method": "search_research_papers", "params": {"query": "AI"}},
    {"method": "get_repository_info", "params": {"owner": "python", "repo": "cpython"}},
    {"method": "lookup_country", "params": {"country_name": "Canada"}}
]
result = api_module.batch_api_request_sync(batch_requests)
```

## 🛠️ API Reference

### Available APIs

| API | Description | Rate Limit | Auth Required |
|-----|-------------|------------|---------------|
| arXiv | Academic papers | 1000/hour | No |
| GitHub | Repository data | 60/hour | No |
| REST Countries | Country information | 1000/hour | No |
| CoinDesk | Bitcoin prices | 1000/hour | No |
| QuoteGarden | Inspirational quotes | 1000/hour | No |
| Cat Facts | Fun facts | 1000/hour | No |

### Core Functions

#### Research & Development
- `search_research_papers(query, max_results, category)` - Search arXiv papers
- `get_repository_info(owner, repo)` - Get GitHub repo stats
- `test_api_connectivity(api_name)` - Test API connections

#### Information & Data
- `lookup_country(country_name)` - Get country information
- `get_crypto_price(currency)` - Get cryptocurrency prices
- `get_inspiration(author, category)` - Get inspirational quotes
- `get_fun_fact(category)` - Get random fun facts

#### System Management
- `batch_api_request(requests)` - Execute multiple API calls
- `get_api_status()` - Get system status and analytics

## 🔧 Configuration

### Environment Variables
```bash
# Optional: Set custom cache directory
export MCP_CACHE_DIR="/path/to/cache"

# Optional: Set custom config directory  
export MCP_CONFIG_DIR="/path/to/config"
```

### Module Configuration
Modules are automatically detected and loaded. You can customize module behavior by editing the configuration files in the `config/` directory.

## 📊 Monitoring & Analytics

The system provides comprehensive monitoring:

- **Real-time module status** - See which modules are loaded and healthy
- **API usage statistics** - Track API calls and success rates
- **Tool performance metrics** - Monitor tool execution times and success rates
- **Cache efficiency** - Monitor cache hit rates and storage usage

## 🧪 Testing

Run the example demonstrations:

```bash
# Run all API examples
python examples/api_usage_examples.py

# Test specific functionality
python -c "
from api_tools_module import APIToolsModule
api = APIToolsModule()
result = api.search_research_papers_sync('quantum computing', 5)
print(f'Found {result[\"total_results\"]} papers')
"
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add your API integration or tool module
4. Test thoroughly
5. Submit a pull request

### Adding New APIs

To add a new free API:

1. Add the API endpoint to `api_integrations.py`
2. Implement the API methods in `api_tools_module.py`
3. Add tests and examples
4. Update documentation

## 📝 License

This project is open source and available under the MIT License.

## 🆘 Support

- **Issues**: Report bugs and request features via GitHub Issues
- **Documentation**: Check the `examples/` directory for usage examples
- **API Status**: Use the built-in API connectivity testing tools

## 🔮 Roadmap

- [ ] Additional free APIs (weather, news, etc.)
- [ ] Plugin system for custom API integrations
- [ ] Advanced caching and rate limiting
- [ ] Export/import of tool configurations
- [ ] Integration with more MCP clients
- [ ] Performance optimizations
- [ ] Enhanced error handling and retry logic

---

**Note**: This system is designed to work with free APIs that don't require authentication. For APIs that do require keys (marked in the documentation), you'll need to obtain free API keys from the respective services.
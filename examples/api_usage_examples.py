#!/usr/bin/env python3
"""
Examples of using the API Tools Module
Demonstrates various free API integrations without authentication requirements
"""

import asyncio
import json
from pathlib import Path
import sys

# Add parent directory to path to import modules
sys.path.append(str(Path(__file__).parent.parent))

from api_tools_module import APIToolsModule

async def demo_research_papers():
    """Demo arXiv research paper search"""
    print("🔬 Searching for research papers on 'machine learning'...")
    
    api_module = APIToolsModule()
    result = await api_module.search_research_papers(
        query="machine learning",
        max_results=5,
        category="cs.LG"  # Computer Science - Machine Learning
    )
    
    if "error" not in result:
        print(f"Found {result['total_results']} papers:")
        for i, paper in enumerate(result['papers'][:3], 1):
            print(f"\n{i}. {paper['title']}")
            print(f"   Authors: {paper['authors']}")
            print(f"   Published: {paper['published']}")
            print(f"   Categories: {paper['categories']}")
            print(f"   Summary: {paper['summary']}")
    else:
        print(f"Error: {result['error']}")

async def demo_github_repo():
    """Demo GitHub repository information"""
    print("\n🐙 Getting GitHub repository info for 'microsoft/vscode'...")
    
    api_module = APIToolsModule()
    result = await api_module.get_repository_info("microsoft", "vscode")
    
    if "error" not in result:
        print(f"Repository: {result['full_name']}")
        print(f"Description: {result['description']}")
        print(f"Language: {result['language']}")
        print(f"Stars: {result['stars']:,}")
        print(f"Forks: {result['forks']:,}")
        print(f"Open Issues: {result['issues']:,}")
        print(f"Activity Score: {result['activity_score']:,}")
        print(f"Age: {result.get('age_days', 'N/A')} days")
    else:
        print(f"Error: {result['error']}")

async def demo_country_info():
    """Demo country information lookup"""
    print("\n🌍 Looking up country information for 'Japan'...")
    
    api_module = APIToolsModule()
    result = await api_module.lookup_country("Japan")
    
    if "error" not in result:
        print(f"Country: {result['name']} ({result['official_name']})")
        print(f"Capital: {', '.join(result['capital'])}")
        print(f"Population: {result['population_formatted']}")
        print(f"Area: {result['area_formatted']}")
        print(f"Population Density: {result.get('population_density', 'N/A')} people/km²")
        print(f"Region: {result['region']} - {result['subregion']}")
        print(f"Languages: {', '.join(result['languages'])}")
        print(f"Currencies: {', '.join(result['currencies'])}")
        print(f"Flag: {result['flag']}")
    else:
        print(f"Error: {result['error']}")

async def demo_crypto_price():
    """Demo cryptocurrency price"""
    print("\n₿ Getting Bitcoin price...")
    
    api_module = APIToolsModule()
    result = await api_module.get_crypto_price("bitcoin")
    
    if "error" not in result:
        analysis = result.get('price_analysis', {})
        print(f"Bitcoin Price: {analysis.get('formatted_price', 'N/A')}")
        print(f"Price Level: {analysis.get('price_level', 'N/A')}")
        print(f"Last Updated: {result.get('time', {}).get('updated', 'N/A')}")
    else:
        print(f"Error: {result['error']}")

async def demo_inspiration():
    """Demo inspirational quotes"""
    print("\n💭 Getting inspirational quote...")
    
    api_module = APIToolsModule()
    result = await api_module.get_inspiration()
    
    if "error" not in result:
        print(f"Quote: {result.get('formatted_quote', 'N/A')}")
        print(f"Genre: {result.get('genre', 'N/A')}")
        print(f"Word Count: {result.get('word_count', 'N/A')}")
    else:
        print(f"Error: {result['error']}")

async def demo_fun_fact():
    """Demo fun facts"""
    print("\n🐱 Getting a fun cat fact...")
    
    api_module = APIToolsModule()
    result = await api_module.get_fun_fact("cats")
    
    if "error" not in result:
        print(f"Cat Fact: {result.get('fact', 'N/A')}")
        print(f"Length: {result.get('length', 'N/A')} characters")
        print(f"Reading Time: ~{result.get('reading_time_seconds', 'N/A')} seconds")
    else:
        print(f"Error: {result['error']}")

async def demo_api_connectivity():
    """Demo API connectivity testing"""
    print("\n🔍 Testing API connectivity...")
    
    api_module = APIToolsModule()
    result = await api_module.test_api_connectivity()
    
    if "error" not in result:
        print(f"Total APIs: {result['total_apis']}")
        print(f"Available APIs: {result['available_apis']}")
        print(f"Success Rate: {result['success_rate']}")
        
        print("\nDetailed Results:")
        for api_name, test_result in result['test_results'].items():
            status = "✅" if test_result.get('available', False) else "❌"
            print(f"  {status} {api_name}: {test_result.get('status_code', 'N/A')}")
    else:
        print(f"Error: {result['error']}")

async def demo_batch_requests():
    """Demo batch API requests"""
    print("\n📦 Executing batch API requests...")
    
    api_module = APIToolsModule()
    
    # Define batch requests
    batch_requests = [
        {
            "method": "search_research_papers",
            "params": {"query": "artificial intelligence", "max_results": 3}
        },
        {
            "method": "get_repository_info", 
            "params": {"owner": "python", "repo": "cpython"}
        },
        {
            "method": "lookup_country",
            "params": {"country_name": "Canada"}
        },
        {
            "method": "get_fun_fact",
            "params": {"category": "cats"}
        }
    ]
    
    result = await api_module.batch_api_request(batch_requests)
    
    if "error" not in result:
        print(f"Batch Execution Results:")
        print(f"Total Requests: {result['total_requests']}")
        print(f"Successful: {result['successful_requests']}")
        print(f"Failed: {result['failed_requests']}")
        print(f"Success Rate: {result['success_rate']}")
        
        print("\nIndividual Results:")
        for req_result in result['results']:
            status = "✅" if req_result['success'] else "❌"
            print(f"  {status} {req_result['method']}")
    else:
        print(f"Error: {result['error']}")

def demo_sync_usage():
    """Demo synchronous usage (for non-async environments)"""
    print("\n🔄 Demo synchronous API usage...")
    
    api_module = APIToolsModule()
    
    # Search for papers synchronously
    result = api_module.search_research_papers_sync("quantum computing", max_results=2)
    if "error" not in result:
        print(f"Found {result['total_results']} quantum computing papers")
    
    # Get repository info synchronously
    result = api_module.get_repository_info_sync("torvalds", "linux")
    if "error" not in result:
        print(f"Linux kernel has {result['stars']:,} stars")
    
    # Get API status
    status = api_module.get_api_status()
    print(f"API Manager Status: {status['total_apis']} total APIs available")

async def main():
    """Run all demos"""
    print("🚀 API Tools Module Demo")
    print("=" * 50)
    
    try:
        # Run async demos
        await demo_research_papers()
        await demo_github_repo()
        await demo_country_info()
        await demo_crypto_price()
        await demo_inspiration()
        await demo_fun_fact()
        await demo_api_connectivity()
        await demo_batch_requests()
        
        # Run sync demo
        demo_sync_usage()
        
        print("\n✅ All demos completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {str(e)}")
    
    finally:
        # Cleanup
        from api_integrations import api_manager
        await api_manager.close()

if __name__ == "__main__":
    asyncio.run(main())
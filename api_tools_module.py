import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from api_integrations import api_manager

logger = logging.getLogger(__name__)

class APIToolsModule:
    """Module for API-based tools and integrations"""
    
    def __init__(self):
        self.api_manager = api_manager
        self.supported_apis = [
            "arxiv", "github", "restcountries", "coinapi", 
            "quotegarden", "catfacts", "httpbin"
        ]
    
    async def search_research_papers(self, query: str, max_results: int = 10, category: str = None) -> Dict[str, Any]:
        """Search for research papers on arXiv
        
        Args:
            query (str): Search query for papers
            max_results (int, optional): Maximum number of results. Defaults to 10
            category (str, optional): arXiv category filter. Defaults to None
            
        Returns:
            Dict[str, Any]: Search results with paper information
        """
        try:
            result = await self.api_manager.search_arxiv(query, max_results, category)
            
            if "error" in result:
                return result
            
            # Format results for better readability
            formatted_papers = []
            for paper in result.get("papers", []):
                formatted_paper = {
                    "title": paper["title"],
                    "authors": ", ".join(paper["authors"][:3]) + ("..." if len(paper["authors"]) > 3 else ""),
                    "summary": paper["summary"][:200] + "..." if len(paper["summary"]) > 200 else paper["summary"],
                    "published": paper["published"][:10],  # Just the date
                    "categories": ", ".join(paper["categories"][:3]),
                    "pdf_url": paper["pdf_url"],
                    "arxiv_id": paper["id"].split("/")[-1] if "/" in paper["id"] else paper["id"]
                }
                formatted_papers.append(formatted_paper)
            
            return {
                "query": query,
                "total_results": len(formatted_papers),
                "papers": formatted_papers,
                "search_time": datetime.now().isoformat(),
                "source": "arXiv"
            }
            
        except Exception as e:
            logger.error(f"Error searching research papers: {e}")
            return {"error": str(e)}
    
    def search_research_papers_sync(self, query: str, max_results: int = 10, category: str = None) -> Dict[str, Any]:
        """Synchronous wrapper for research paper search"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.search_research_papers(query, max_results, category))
        finally:
            loop.close()
    
    async def get_repository_info(self, owner: str, repo: str) -> Dict[str, Any]:
        """Get GitHub repository information
        
        Args:
            owner (str): Repository owner/organization
            repo (str): Repository name
            
        Returns:
            Dict[str, Any]: Repository information and statistics
        """
        try:
            result = await self.api_manager.get_github_repo_info(owner, repo)
            
            if "error" in result:
                return result
            
            # Add some calculated fields
            if result.get("created_at") and result.get("updated_at"):
                created = datetime.fromisoformat(result["created_at"].replace("Z", "+00:00"))
                updated = datetime.fromisoformat(result["updated_at"].replace("Z", "+00:00"))
                result["age_days"] = (datetime.now().replace(tzinfo=created.tzinfo) - created).days
                result["last_updated_days"] = (datetime.now().replace(tzinfo=updated.tzinfo) - updated).days
            
            # Add activity score
            stars = result.get("stars", 0)
            forks = result.get("forks", 0)
            result["activity_score"] = stars + (forks * 2)
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting repository info: {e}")
            return {"error": str(e)}
    
    def get_repository_info_sync(self, owner: str, repo: str) -> Dict[str, Any]:
        """Synchronous wrapper for repository info"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.get_repository_info(owner, repo))
        finally:
            loop.close()
    
    async def lookup_country(self, country_name: str) -> Dict[str, Any]:
        """Look up country information
        
        Args:
            country_name (str): Name of the country to look up
            
        Returns:
            Dict[str, Any]: Comprehensive country information
        """
        try:
            result = await self.api_manager.get_country_info(country_name)
            
            if "error" in result:
                return result
            
            # Add some calculated fields
            if result.get("population") and result.get("area"):
                result["population_density"] = round(result["population"] / result["area"], 2)
            
            # Format large numbers
            if result.get("population"):
                result["population_formatted"] = f"{result['population']:,}"
            
            if result.get("area"):
                result["area_formatted"] = f"{result['area']:,} km²"
            
            return result
            
        except Exception as e:
            logger.error(f"Error looking up country: {e}")
            return {"error": str(e)}
    
    def lookup_country_sync(self, country_name: str) -> Dict[str, Any]:
        """Synchronous wrapper for country lookup"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.lookup_country(country_name))
        finally:
            loop.close()
    
    async def get_crypto_price(self, currency: str = "bitcoin") -> Dict[str, Any]:
        """Get cryptocurrency price information
        
        Args:
            currency (str, optional): Cryptocurrency to get price for. Defaults to "bitcoin"
            
        Returns:
            Dict[str, Any]: Price information and market data
        """
        try:
            # Currently only supports Bitcoin through CoinDesk API
            if currency.lower() != "bitcoin":
                return {"error": "Currently only Bitcoin is supported"}
            
            result = await self.api_manager.get_bitcoin_price()
            
            if "error" in result:
                return result
            
            # Add trend analysis (mock for now)
            if result.get("usd_rate_float"):
                price = result["usd_rate_float"]
                result["price_analysis"] = {
                    "current_price_usd": price,
                    "price_level": "high" if price > 50000 else "medium" if price > 30000 else "low",
                    "formatted_price": f"${price:,.2f}"
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting crypto price: {e}")
            return {"error": str(e)}
    
    def get_crypto_price_sync(self, currency: str = "bitcoin") -> Dict[str, Any]:
        """Synchronous wrapper for crypto price"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.get_crypto_price(currency))
        finally:
            loop.close()
    
    async def get_inspiration(self, author: str = None, category: str = None) -> Dict[str, Any]:
        """Get inspirational quote
        
        Args:
            author (str, optional): Specific author to get quote from. Defaults to None
            category (str, optional): Quote category/genre. Defaults to None
            
        Returns:
            Dict[str, Any]: Inspirational quote with metadata
        """
        try:
            result = await self.api_manager.get_random_quote(author, category)
            
            if "error" in result:
                return result
            
            # Add some enhancements
            quote_text = result.get("quote", "")
            if quote_text:
                result["word_count"] = len(quote_text.split())
                result["character_count"] = len(quote_text)
                result["formatted_quote"] = f'"{quote_text}" - {result.get("author", "Unknown")}'
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting inspiration: {e}")
            return {"error": str(e)}
    
    def get_inspiration_sync(self, author: str = None, category: str = None) -> Dict[str, Any]:
        """Synchronous wrapper for inspiration"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.get_inspiration(author, category))
        finally:
            loop.close()
    
    async def get_fun_fact(self, category: str = "cats") -> Dict[str, Any]:
        """Get random fun fact
        
        Args:
            category (str, optional): Category of fact. Defaults to "cats"
            
        Returns:
            Dict[str, Any]: Fun fact with metadata
        """
        try:
            # Currently only supports cat facts
            if category.lower() != "cats":
                return {"error": "Currently only cat facts are supported"}
            
            result = await self.api_manager.get_cat_fact()
            
            if "error" in result:
                return result
            
            # Add some enhancements
            fact_text = result.get("fact", "")
            if fact_text:
                result["category"] = "cats"
                result["word_count"] = len(fact_text.split())
                result["reading_time_seconds"] = max(3, len(fact_text.split()) * 0.5)  # Rough estimate
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting fun fact: {e}")
            return {"error": str(e)}
    
    def get_fun_fact_sync(self, category: str = "cats") -> Dict[str, Any]:
        """Synchronous wrapper for fun facts"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.get_fun_fact(category))
        finally:
            loop.close()
    
    async def test_api_connectivity(self, api_name: str = None) -> Dict[str, Any]:
        """Test API connectivity
        
        Args:
            api_name (str, optional): Specific API to test. Defaults to None (test all)
            
        Returns:
            Dict[str, Any]: Connectivity test results
        """
        try:
            if api_name:
                if api_name not in self.supported_apis:
                    return {"error": f"Unsupported API: {api_name}"}
                
                result = await self.api_manager.test_api_connection(api_name)
                return result
            else:
                # Test all APIs
                results = {}
                for api in self.supported_apis:
                    results[api] = await self.api_manager.test_api_connection(api)
                
                # Summary
                available_count = sum(1 for result in results.values() if result.get("available", False))
                
                return {
                    "total_apis": len(self.supported_apis),
                    "available_apis": available_count,
                    "unavailable_apis": len(self.supported_apis) - available_count,
                    "success_rate": f"{(available_count / len(self.supported_apis) * 100):.1f}%",
                    "test_results": results,
                    "test_time": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error testing API connectivity: {e}")
            return {"error": str(e)}
    
    def test_api_connectivity_sync(self, api_name: str = None) -> Dict[str, Any]:
        """Synchronous wrapper for API connectivity test"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.test_api_connectivity(api_name))
        finally:
            loop.close()
    
    def get_api_status(self) -> Dict[str, Any]:
        """Get current API manager status
        
        Returns:
            Dict[str, Any]: API manager status and statistics
        """
        try:
            status = self.api_manager.get_api_status()
            status["supported_apis"] = self.supported_apis
            status["module_info"] = {
                "name": "API Tools Module",
                "version": "1.0.0",
                "description": "Integration with free APIs for research, development, and general information",
                "last_updated": datetime.now().isoformat()
            }
            return status
            
        except Exception as e:
            logger.error(f"Error getting API status: {e}")
            return {"error": str(e)}
    
    async def batch_api_request(self, requests: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute multiple API requests in batch
        
        Args:
            requests (List[Dict[str, Any]]): List of API requests to execute
            
        Returns:
            Dict[str, Any]: Batch execution results
        """
        try:
            results = []
            
            for i, request in enumerate(requests):
                method = request.get("method")
                params = request.get("params", {})
                
                try:
                    if method == "search_research_papers":
                        result = await self.search_research_papers(**params)
                    elif method == "get_repository_info":
                        result = await self.get_repository_info(**params)
                    elif method == "lookup_country":
                        result = await self.lookup_country(**params)
                    elif method == "get_crypto_price":
                        result = await self.get_crypto_price(**params)
                    elif method == "get_inspiration":
                        result = await self.get_inspiration(**params)
                    elif method == "get_fun_fact":
                        result = await self.get_fun_fact(**params)
                    else:
                        result = {"error": f"Unknown method: {method}"}
                    
                    results.append({
                        "request_id": i,
                        "method": method,
                        "success": "error" not in result,
                        "result": result
                    })
                    
                except Exception as e:
                    results.append({
                        "request_id": i,
                        "method": method,
                        "success": False,
                        "error": str(e)
                    })
            
            successful = sum(1 for r in results if r["success"])
            
            return {
                "total_requests": len(requests),
                "successful_requests": successful,
                "failed_requests": len(requests) - successful,
                "success_rate": f"{(successful / len(requests) * 100):.1f}%",
                "results": results,
                "execution_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in batch API request: {e}")
            return {"error": str(e)}
    
    def batch_api_request_sync(self, requests: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Synchronous wrapper for batch API requests"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.batch_api_request(requests))
        finally:
            loop.close()
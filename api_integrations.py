import asyncio
import json
import logging
import aiohttp
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import urllib.parse
import feedparser
import requests
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class APIEndpoint:
    """API endpoint configuration"""
    name: str
    base_url: str
    description: str
    rate_limit: int = 100  # requests per hour
    requires_auth: bool = False
    response_format: str = "json"
    category: str = "general"

class FreeAPIManager:
    """Manager for free API integrations"""
    
    def __init__(self):
        self.session = None
        self.rate_limits = {}
        self.api_endpoints = self._setup_api_endpoints()
        self.cache = {}
        self.cache_ttl = 3600  # 1 hour cache
    
    def _setup_api_endpoints(self) -> Dict[str, APIEndpoint]:
        """Setup available free API endpoints"""
        return {
            "arxiv": APIEndpoint(
                name="arXiv",
                base_url="http://export.arxiv.org/api/query",
                description="Academic papers and preprints",
                rate_limit=1000,
                response_format="xml",
                category="research"
            ),
            "openweather": APIEndpoint(
                name="OpenWeatherMap",
                base_url="http://api.openweathermap.org/data/2.5",
                description="Weather data (requires free API key)",
                rate_limit=60,
                requires_auth=True,
                category="weather"
            ),
            "newsapi": APIEndpoint(
                name="NewsAPI",
                base_url="https://newsapi.org/v2",
                description="News articles (requires free API key)",
                rate_limit=100,
                requires_auth=True,
                category="news"
            ),
            "github": APIEndpoint(
                name="GitHub",
                base_url="https://api.github.com",
                description="GitHub repositories and user data",
                rate_limit=60,
                category="development"
            ),
            "jsonplaceholder": APIEndpoint(
                name="JSONPlaceholder",
                base_url="https://jsonplaceholder.typicode.com",
                description="Fake REST API for testing",
                rate_limit=1000,
                category="testing"
            ),
            "httpbin": APIEndpoint(
                name="HTTPBin",
                base_url="https://httpbin.org",
                description="HTTP testing service",
                rate_limit=1000,
                category="testing"
            ),
            "restcountries": APIEndpoint(
                name="REST Countries",
                base_url="https://restcountries.com/v3.1",
                description="Country information",
                rate_limit=1000,
                category="geography"
            ),
            "coinapi": APIEndpoint(
                name="CoinAPI",
                base_url="https://api.coindesk.com/v1/bpi",
                description="Bitcoin price index",
                rate_limit=1000,
                category="finance"
            ),
            "catfacts": APIEndpoint(
                name="Cat Facts",
                base_url="https://catfact.ninja",
                description="Random cat facts",
                rate_limit=1000,
                category="fun"
            ),
            "quotegarden": APIEndpoint(
                name="QuoteGarden",
                base_url="https://quotegarden.herokuapp.com/api/v3",
                description="Inspirational quotes",
                rate_limit=1000,
                category="quotes"
            )
        }
    
    async def get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers={
                    'User-Agent': 'Dynamic-MCP-Tools/1.0'
                }
            )
        return self.session
    
    def _check_rate_limit(self, api_name: str) -> bool:
        """Check if API rate limit allows request"""
        now = datetime.now()
        if api_name not in self.rate_limits:
            self.rate_limits[api_name] = []
        
        # Remove old requests (older than 1 hour)
        self.rate_limits[api_name] = [
            req_time for req_time in self.rate_limits[api_name]
            if now - req_time < timedelta(hours=1)
        ]
        
        endpoint = self.api_endpoints.get(api_name)
        if endpoint and len(self.rate_limits[api_name]) >= endpoint.rate_limit:
            return False
        
        self.rate_limits[api_name].append(now)
        return True
    
    def _get_cache_key(self, api_name: str, endpoint: str, params: Dict[str, Any]) -> str:
        """Generate cache key"""
        param_str = json.dumps(params, sort_keys=True)
        return f"{api_name}:{endpoint}:{hash(param_str)}"
    
    def _get_cached_response(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached response if valid"""
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if datetime.now() - timestamp < timedelta(seconds=self.cache_ttl):
                return cached_data
            else:
                del self.cache[cache_key]
        return None
    
    def _cache_response(self, cache_key: str, data: Dict[str, Any]):
        """Cache response data"""
        self.cache[cache_key] = (data, datetime.now())
    
    async def search_arxiv(self, query: str, max_results: int = 10, category: str = None) -> Dict[str, Any]:
        """Search arXiv for academic papers"""
        try:
            if not self._check_rate_limit("arxiv"):
                return {"error": "Rate limit exceeded for arXiv API"}
            
            # Build query parameters
            params = {
                'search_query': query,
                'start': 0,
                'max_results': min(max_results, 100)  # arXiv limit
            }
            
            if category:
                params['search_query'] = f"cat:{category} AND {query}"
            
            cache_key = self._get_cache_key("arxiv", "search", params)
            cached = self._get_cached_response(cache_key)
            if cached:
                return cached
            
            session = await self.get_session()
            endpoint = self.api_endpoints["arxiv"]
            
            async with session.get(endpoint.base_url, params=params) as response:
                if response.status == 200:
                    xml_content = await response.text()
                    result = self._parse_arxiv_response(xml_content)
                    self._cache_response(cache_key, result)
                    return result
                else:
                    return {"error": f"arXiv API error: {response.status}"}
                    
        except Exception as e:
            logger.error(f"Error searching arXiv: {e}")
            return {"error": str(e)}
    
    def _parse_arxiv_response(self, xml_content: str) -> Dict[str, Any]:
        """Parse arXiv XML response"""
        try:
            root = ET.fromstring(xml_content)
            namespace = {'atom': 'http://www.w3.org/2005/Atom'}
            
            papers = []
            for entry in root.findall('atom:entry', namespace):
                paper = {
                    'title': entry.find('atom:title', namespace).text.strip(),
                    'summary': entry.find('atom:summary', namespace).text.strip(),
                    'authors': [
                        author.find('atom:name', namespace).text
                        for author in entry.findall('atom:author', namespace)
                    ],
                    'published': entry.find('atom:published', namespace).text,
                    'updated': entry.find('atom:updated', namespace).text,
                    'id': entry.find('atom:id', namespace).text,
                    'pdf_url': None,
                    'categories': []
                }
                
                # Get PDF URL
                for link in entry.findall('atom:link', namespace):
                    if link.get('title') == 'pdf':
                        paper['pdf_url'] = link.get('href')
                        break
                
                # Get categories
                for category in entry.findall('atom:category', namespace):
                    paper['categories'].append(category.get('term'))
                
                papers.append(paper)
            
            return {
                'papers': papers,
                'total_results': len(papers),
                'query_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error parsing arXiv response: {e}")
            return {"error": f"Failed to parse arXiv response: {str(e)}"}
    
    async def get_github_repo_info(self, owner: str, repo: str) -> Dict[str, Any]:
        """Get GitHub repository information"""
        try:
            if not self._check_rate_limit("github"):
                return {"error": "Rate limit exceeded for GitHub API"}
            
            cache_key = self._get_cache_key("github", "repo", {"owner": owner, "repo": repo})
            cached = self._get_cached_response(cache_key)
            if cached:
                return cached
            
            session = await self.get_session()
            endpoint = self.api_endpoints["github"]
            url = f"{endpoint.base_url}/repos/{owner}/{repo}"
            
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    result = {
                        'name': data.get('name'),
                        'full_name': data.get('full_name'),
                        'description': data.get('description'),
                        'language': data.get('language'),
                        'stars': data.get('stargazers_count'),
                        'forks': data.get('forks_count'),
                        'issues': data.get('open_issues_count'),
                        'created_at': data.get('created_at'),
                        'updated_at': data.get('updated_at'),
                        'clone_url': data.get('clone_url'),
                        'homepage': data.get('homepage'),
                        'topics': data.get('topics', [])
                    }
                    self._cache_response(cache_key, result)
                    return result
                else:
                    return {"error": f"GitHub API error: {response.status}"}
                    
        except Exception as e:
            logger.error(f"Error getting GitHub repo info: {e}")
            return {"error": str(e)}
    
    async def get_country_info(self, country: str) -> Dict[str, Any]:
        """Get country information"""
        try:
            if not self._check_rate_limit("restcountries"):
                return {"error": "Rate limit exceeded for REST Countries API"}
            
            cache_key = self._get_cache_key("restcountries", "country", {"country": country})
            cached = self._get_cached_response(cache_key)
            if cached:
                return cached
            
            session = await self.get_session()
            endpoint = self.api_endpoints["restcountries"]
            url = f"{endpoint.base_url}/name/{urllib.parse.quote(country)}"
            
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if data:
                        country_data = data[0]  # Take first match
                        result = {
                            'name': country_data.get('name', {}).get('common'),
                            'official_name': country_data.get('name', {}).get('official'),
                            'capital': country_data.get('capital', []),
                            'population': country_data.get('population'),
                            'area': country_data.get('area'),
                            'region': country_data.get('region'),
                            'subregion': country_data.get('subregion'),
                            'languages': list(country_data.get('languages', {}).values()),
                            'currencies': list(country_data.get('currencies', {}).keys()),
                            'timezones': country_data.get('timezones', []),
                            'flag': country_data.get('flag'),
                            'maps': country_data.get('maps', {})
                        }
                        self._cache_response(cache_key, result)
                        return result
                    else:
                        return {"error": "Country not found"}
                else:
                    return {"error": f"REST Countries API error: {response.status}"}
                    
        except Exception as e:
            logger.error(f"Error getting country info: {e}")
            return {"error": str(e)}
    
    async def get_bitcoin_price(self) -> Dict[str, Any]:
        """Get current Bitcoin price"""
        try:
            if not self._check_rate_limit("coinapi"):
                return {"error": "Rate limit exceeded for CoinAPI"}
            
            cache_key = self._get_cache_key("coinapi", "currentprice", {})
            cached = self._get_cached_response(cache_key)
            if cached:
                return cached
            
            session = await self.get_session()
            endpoint = self.api_endpoints["coinapi"]
            url = f"{endpoint.base_url}/currentprice.json"
            
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    result = {
                        'time': data.get('time', {}).get('updated'),
                        'disclaimer': data.get('disclaimer'),
                        'bpi': data.get('bpi', {}),
                        'usd_rate': data.get('bpi', {}).get('USD', {}).get('rate'),
                        'usd_rate_float': data.get('bpi', {}).get('USD', {}).get('rate_float')
                    }
                    self._cache_response(cache_key, result)
                    return result
                else:
                    return {"error": f"CoinAPI error: {response.status}"}
                    
        except Exception as e:
            logger.error(f"Error getting Bitcoin price: {e}")
            return {"error": str(e)}
    
    async def get_random_quote(self, author: str = None, category: str = None) -> Dict[str, Any]:
        """Get random inspirational quote"""
        try:
            if not self._check_rate_limit("quotegarden"):
                return {"error": "Rate limit exceeded for QuoteGarden API"}
            
            params = {}
            if author:
                params['author'] = author
            if category:
                params['genre'] = category
            
            cache_key = self._get_cache_key("quotegarden", "quotes/random", params)
            cached = self._get_cached_response(cache_key)
            if cached:
                return cached
            
            session = await self.get_session()
            endpoint = self.api_endpoints["quotegarden"]
            url = f"{endpoint.base_url}/quotes/random"
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('statusCode') == 200:
                        quote_data = data.get('data', {})
                        result = {
                            'quote': quote_data.get('quoteText'),
                            'author': quote_data.get('quoteAuthor'),
                            'genre': quote_data.get('quoteGenre'),
                            'id': quote_data.get('_id')
                        }
                        self._cache_response(cache_key, result)
                        return result
                    else:
                        return {"error": "No quote found"}
                else:
                    return {"error": f"QuoteGarden API error: {response.status}"}
                    
        except Exception as e:
            logger.error(f"Error getting random quote: {e}")
            return {"error": str(e)}
    
    async def get_cat_fact(self) -> Dict[str, Any]:
        """Get random cat fact"""
        try:
            if not self._check_rate_limit("catfacts"):
                return {"error": "Rate limit exceeded for Cat Facts API"}
            
            cache_key = self._get_cache_key("catfacts", "fact", {})
            # Don't cache cat facts - they should be random
            
            session = await self.get_session()
            endpoint = self.api_endpoints["catfacts"]
            url = f"{endpoint.base_url}/fact"
            
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        'fact': data.get('fact'),
                        'length': data.get('length')
                    }
                else:
                    return {"error": f"Cat Facts API error: {response.status}"}
                    
        except Exception as e:
            logger.error(f"Error getting cat fact: {e}")
            return {"error": str(e)}
    
    async def test_api_connection(self, api_name: str) -> Dict[str, Any]:
        """Test connection to a specific API"""
        try:
            if api_name not in self.api_endpoints:
                return {"error": f"Unknown API: {api_name}"}
            
            endpoint = self.api_endpoints[api_name]
            session = await self.get_session()
            
            # Simple GET request to test connectivity
            async with session.get(endpoint.base_url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                return {
                    'api_name': api_name,
                    'status_code': response.status,
                    'response_time': response.headers.get('X-Response-Time', 'N/A'),
                    'available': response.status < 400,
                    'test_time': datetime.now().isoformat()
                }
                
        except Exception as e:
            return {
                'api_name': api_name,
                'available': False,
                'error': str(e),
                'test_time': datetime.now().isoformat()
            }
    
    def get_api_status(self) -> Dict[str, Any]:
        """Get status of all APIs"""
        return {
            'total_apis': len(self.api_endpoints),
            'rate_limits': {
                api: len(requests) for api, requests in self.rate_limits.items()
            },
            'cache_size': len(self.cache),
            'available_apis': list(self.api_endpoints.keys()),
            'api_categories': {
                category: [
                    name for name, endpoint in self.api_endpoints.items()
                    if endpoint.category == category
                ]
                for category in set(endpoint.category for endpoint in self.api_endpoints.values())
            }
        }
    
    async def close(self):
        """Close the session"""
        if self.session and not self.session.closed:
            await self.session.close()

# Global instance
api_manager = FreeAPIManager()
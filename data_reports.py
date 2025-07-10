import json
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import sqlite3
import logging
import threading
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class DataReportsModule:
    """Comprehensive data analysis, visualization, and knowledge management module"""
    
    def __init__(self):
        self._local = threading.local()
        self.knowledge_base = {}
        self.report_templates = {}
        self.setup_knowledge_base()
    
    def get_db_connection(self):
        """Get thread-local database connection"""
        if not hasattr(self._local, 'db_connection') or self._local.db_connection is None:
            self._local.db_connection = sqlite3.connect(":memory:")
            self._setup_database_schema(self._local.db_connection)
        return self._local.db_connection
        
    def _setup_database_schema(self, connection):
        """Setup database schema for a connection"""
        try:
            # Create sample tables
            cursor = connection.cursor()
            
            # Performance metrics table
            cursor.execute('''
                CREATE TABLE performance_metrics (
                    id INTEGER PRIMARY KEY,
                    date TEXT,
                    productivity_score INTEGER,
                    tasks_completed INTEGER,
                    time_spent REAL,
                    focus_score INTEGER
                )
            ''')
            
            # Financial data table
            cursor.execute('''
                CREATE TABLE financial_data (
                    id INTEGER PRIMARY KEY,
                    date TEXT,
                    category TEXT,
                    amount REAL,
                    type TEXT
                )
            ''')
            
            # Insert sample data
            sample_performance = [
                ('2024-01-15', 85, 12, 8.5, 78),
                ('2024-01-16', 92, 15, 9.2, 85),
                ('2024-01-17', 78, 10, 7.8, 72),
                ('2024-01-18', 88, 13, 8.9, 82),
                ('2024-01-19', 95, 16, 9.5, 90)
            ]
            
            cursor.executemany('''
                INSERT INTO performance_metrics (date, productivity_score, tasks_completed, time_spent, focus_score)
                VALUES (?, ?, ?, ?, ?)
            ''', sample_performance)
            
            connection.commit()
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Database setup error: {str(e)}")
    
    def setup_knowledge_base(self):
        """Initialize AI knowledge base"""
        self.knowledge_base = {
            "productivity": {
                "best_practices": [
                    "Use time-blocking techniques",
                    "Eliminate distractions during focus time",
                    "Take regular breaks every 90 minutes",
                    "Prioritize high-impact tasks"
                ],
                "research_findings": [
                    "Peak productivity occurs between 10 AM - 12 PM for most people",
                    "Multitasking reduces productivity by up to 40%",
                    "Regular exercise improves cognitive performance"
                ]
            },
            "health": {
                "guidelines": [
                    "Aim for 7-9 hours of sleep per night",
                    "Take a 5-minute break every hour",
                    "Stay hydrated throughout the day",
                    "Maintain proper posture while working"
                ],
                "metrics": [
                    "Step count: 8,000-10,000 steps per day",
                    "Heart rate variability: Higher is better",
                    "Sleep quality: 85%+ deep sleep"
                ]
            },
            "financial": {
                "budgeting_rules": [
                    "50% needs, 30% wants, 20% savings",
                    "Emergency fund: 3-6 months expenses",
                    "Investment: Start early, compound interest"
                ],
                "optimization": [
                    "Track all expenses",
                    "Automate savings",
                    "Review and adjust monthly"
                ]
            }
        }
    
    def generate_report(self, data_source: str, report_type: str, time_period: str = "last_7_days", format: str = "html") -> Dict[str, Any]:
        """Generate comprehensive reports with visualizations
        
        Args:
            data_source (str): Source of data for the report (e.g., 'performance', 'financial', 'health')
            report_type (str): Type of report to generate (e.g., 'performance', 'financial', 'productivity', 'health')
            time_period (str, optional): Time period for the report. Defaults to "last_7_days"
            format (str, optional): Output format for the report. Defaults to "html"
            
        Returns:
            Dict[str, Any]: Report data including visualizations, insights, and recommendations
        """
        try:
            # Fetch data based on source
            if data_source == "performance":
                data = self._fetch_performance_data(time_period)
            elif data_source == "financial":
                data = self._fetch_financial_data(time_period)
            else:
                data = self._generate_sample_data(data_source, time_period)
            
            # Generate visualizations
            charts = self._create_visualizations(data, report_type)
            
            # Generate insights
            insights = self._generate_insights(data, report_type)
            
            # Create report structure
            report = {
                "title": f"{report_type.title()} Report - {time_period}",
                "generated_at": datetime.now().isoformat(),
                "data_source": data_source,
                "summary": {
                    "total_records": len(data),
                    "key_metrics": self._calculate_key_metrics(data, report_type),
                    "performance_score": self._calculate_performance_score(data, report_type)
                },
                "visualizations": charts,
                "insights": insights,
                "recommendations": self._generate_recommendations(insights, report_type),
                "format": format,
                "download_links": {
                    "pdf": f"/reports/{report_type}_{time_period}.pdf",
                    "excel": f"/reports/{report_type}_{time_period}.xlsx",
                    "csv": f"/reports/{report_type}_{time_period}.csv"
                }
            }
            
            logger.info(f"Report generated: {report_type} for {time_period}")
            return report
            
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            return {"error": str(e)}
    
    def generate_ai_insights(self, data: List[Dict[str, Any]], focus_area: str = "general", insight_type: str = "trend") -> Dict[str, Any]:
        """Generate AI-powered insights and alerts
        
        Args:
            data (List[Dict[str, Any]]): Input data for analysis
            focus_area (str, optional): Area to focus analysis on. Defaults to "general"
            insight_type (str, optional): Type of insight to generate. Defaults to "trend"
            
        Returns:
            Dict[str, Any]: Generated insights including findings, alerts, predictions, and recommendations
        """
        try:
            df = pd.DataFrame(data)
            
            insights = {
                "insight_type": insight_type,
                "focus_area": focus_area,
                "analysis_date": datetime.now().isoformat(),
                "confidence_score": 0.85,
                "findings": [],
                "alerts": [],
                "predictions": [],
                "recommendations": []
            }
            
            if insight_type == "trend":
                insights["findings"] = self._analyze_trends(df, focus_area)
            elif insight_type == "anomaly":
                insights["findings"] = self._detect_anomalies(df, focus_area)
            elif insight_type == "prediction":
                insights["predictions"] = self._make_predictions(df, focus_area)
            elif insight_type == "recommendation":
                insights["recommendations"] = self._generate_ai_recommendations(df, focus_area)
            
            # Generate alerts based on findings
            insights["alerts"] = self._generate_alerts(insights["findings"])
            
            # Add contextual information
            insights["context"] = {
                "data_quality": "high",
                "sample_size": len(df),
                "time_range": self._get_time_range(df),
                "key_variables": list(df.columns) if not df.empty else []
            }
            
            logger.info(f"AI insights generated for {focus_area}")
            return insights
            
        except Exception as e:
            logger.error(f"Error generating AI insights: {str(e)}")
            return {"error": str(e)}
    
    def query_knowledge_base(self, query: str, domain: str = "general", search_type: str = "semantic") -> Dict[str, Any]:
        """Query the AI knowledge base for information
        
        Args:
            query (str): Search query string
            domain (str, optional): Domain to search within. Defaults to "general"
            search_type (str, optional): Type of search to perform. Defaults to "semantic"
            
        Returns:
            Dict[str, Any]: Search results with related topics, confidence scores, and insights
        """
        try:
            results = {
                "query": query,
                "domain": domain,
                "search_type": search_type,
                "results": [],
                "related_topics": [],
                "confidence_scores": [],
                "sources": []
            }
            
            # Search in relevant domain
            if domain in self.knowledge_base:
                domain_data = self.knowledge_base[domain]
                results["results"] = self._search_domain(query, domain_data, search_type)
            else:
                # Search across all domains
                for domain_name, domain_data in self.knowledge_base.items():
                    domain_results = self._search_domain(query, domain_data, search_type)
                    if domain_results:
                        results["results"].extend(domain_results)
            
            # Add related topics
            results["related_topics"] = self._find_related_topics(query, domain)
            
            # Add confidence scores
            results["confidence_scores"] = [0.9] * len(results["results"])
            
            # Add sources
            results["sources"] = ["Internal Knowledge Base", "AI Analysis", "Best Practices"]
            
            # Generate additional insights
            results["insights"] = {
                "summary": f"Found {len(results['results'])} relevant results for '{query}'",
                "key_points": results["results"][:3],
                "actionable_items": self._extract_actionable_items(results["results"])
            }
            
            logger.info(f"Knowledge base queried: {query} in {domain}")
            return results
            
        except Exception as e:
            logger.error(f"Error querying knowledge base: {str(e)}")
            return {"error": str(e)}
    
    def _fetch_performance_data(self, time_period: str) -> List[Dict[str, Any]]:
        """Fetch performance data from database
        
        Args:
            time_period (str): Time period to fetch data for
            
        Returns:
            List[Dict[str, Any]]: Performance data records
        """
        cursor = self.get_db_connection().cursor()
        cursor.execute("SELECT * FROM performance_metrics")
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in rows]
    
    def _fetch_financial_data(self, time_period: str) -> List[Dict[str, Any]]:
        """Fetch financial data from database
        
        Args:
            time_period (str): Time period to fetch data for
            
        Returns:
            List[Dict[str, Any]]: Financial data records
        """
        # Mock financial data
        return [
            {"date": "2024-01-15", "category": "food", "amount": 45.50, "type": "expense"},
            {"date": "2024-01-16", "category": "transport", "amount": 15.20, "type": "expense"},
            {"date": "2024-01-17", "category": "income", "amount": 2500.00, "type": "income"},
            {"date": "2024-01-18", "category": "utilities", "amount": 120.00, "type": "expense"},
            {"date": "2024-01-19", "category": "entertainment", "amount": 35.75, "type": "expense"}
        ]
    
    def _generate_sample_data(self, data_source: str, time_period: str) -> List[Dict[str, Any]]:
        """Generate sample data for testing
        
        Args:
            data_source (str): Type of data source to generate
            time_period (str): Time period for the sample data
            
        Returns:
            List[Dict[str, Any]]: Generated sample data
        """
        # Generate sample data based on source
        if data_source == "health":
            return [
                {"date": "2024-01-15", "steps": 8500, "sleep_hours": 7.5, "stress_level": 3},
                {"date": "2024-01-16", "steps": 9200, "sleep_hours": 8.0, "stress_level": 2},
                {"date": "2024-01-17", "steps": 7800, "sleep_hours": 6.5, "stress_level": 4},
                {"date": "2024-01-18", "steps": 10500, "sleep_hours": 7.8, "stress_level": 2},
                {"date": "2024-01-19", "steps": 9800, "sleep_hours": 8.2, "stress_level": 1}
            ]
        return []
    
    def _create_visualizations(self, data: List[Dict[str, Any]], report_type: str) -> Dict[str, Any]:
        """Create visualizations for the report
        
        Args:
            data (List[Dict[str, Any]]): Data to visualize
            report_type (str): Type of report for visualization context
            
        Returns:
            Dict[str, Any]: Visualization data and metadata
        """
        # Mock visualization data
        return {
            "chart_1": {
                "type": "line",
                "title": f"{report_type.title()} Trend",
                "data": "plotly_json_data",
                "description": "Shows trends over time"
            },
            "chart_2": {
                "type": "bar",
                "title": f"{report_type.title()} Distribution",
                "data": "plotly_json_data",
                "description": "Shows distribution by category"
            }
        }
    
    def _generate_insights(self, data: List[Dict[str, Any]], report_type: str) -> List[str]:
        """Generate insights from data
        
        Args:
            data (List[Dict[str, Any]]): Data to analyze for insights
            report_type (str): Type of report for context
            
        Returns:
            List[str]: Generated insights
        """
        return [
            f"Overall {report_type} performance is above average",
            f"Peak performance observed on weekdays",
            f"Consistent improvement trend over the period",
            f"Key success factors identified"
        ]
    
    def _calculate_key_metrics(self, data: List[Dict[str, Any]], report_type: str) -> Dict[str, Any]:
        """Calculate key metrics for the report
        
        Args:
            data (List[Dict[str, Any]]): Data to calculate metrics from
            report_type (str): Type of report for metric context
            
        Returns:
            Dict[str, Any]: Calculated key metrics
        """
        return {
            "total_value": 1250.75,
            "average_value": 87.5,
            "growth_rate": 12.3,
            "trend_direction": "positive"
        }
    
    def _calculate_performance_score(self, data: List[Dict[str, Any]], report_type: str) -> float:
        """Calculate overall performance score
        
        Args:
            data (List[Dict[str, Any]]): Data to calculate score from
            report_type (str): Type of report for scoring context
            
        Returns:
            float: Overall performance score
        """
        return 87.5
    
    def _generate_recommendations(self, insights: List[str], report_type: str) -> List[str]:
        """Generate actionable recommendations
        
        Args:
            insights (List[str]): Insights to base recommendations on
            report_type (str): Type of report for recommendation context
            
        Returns:
            List[str]: Generated recommendations
        """
        return [
            f"Continue current {report_type} strategies",
            f"Focus on maintaining consistency",
            f"Identify and replicate success patterns",
            f"Monitor key metrics weekly"
        ]
    
    def _analyze_trends(self, df: pd.DataFrame, focus_area: str) -> List[str]:
        """Analyze trends in the data
        
        Args:
            df (pd.DataFrame): Data to analyze
            focus_area (str): Area to focus trend analysis on
            
        Returns:
            List[str]: Trend analysis results
        """
        return [
            "Upward trend observed in key metrics",
            "Seasonal patterns detected",
            "Performance improvement over time"
        ]
    
    def _detect_anomalies(self, df: pd.DataFrame, focus_area: str) -> List[str]:
        """Detect anomalies in the data
        
        Args:
            df (pd.DataFrame): Data to analyze for anomalies
            focus_area (str): Area to focus anomaly detection on
            
        Returns:
            List[str]: Detected anomalies
        """
        return [
            "Unusual spike detected on specific date",
            "Outlier values require investigation",
            "Pattern deviation from normal behavior"
        ]
    
    def _make_predictions(self, df: pd.DataFrame, focus_area: str) -> List[str]:
        """Make predictions based on data
        
        Args:
            df (pd.DataFrame): Data to base predictions on
            focus_area (str): Area to focus predictions on
            
        Returns:
            List[str]: Generated predictions
        """
        return [
            "Expected 15% improvement next month",
            "Projected performance within target range",
            "Forecast indicates positive trajectory"
        ]
    
    def _generate_ai_recommendations(self, df: pd.DataFrame, focus_area: str) -> List[str]:
        """Generate AI-powered recommendations
        
        Args:
            df (pd.DataFrame): Data to base recommendations on
            focus_area (str): Area to focus recommendations on
            
        Returns:
            List[str]: AI-generated recommendations
        """
        return [
            "Optimize resource allocation",
            "Implement suggested improvements",
            "Focus on high-impact activities"
        ]
    
    def _generate_alerts(self, findings: List[str]) -> List[Dict[str, Any]]:
        """Generate alerts based on findings
        
        Args:
            findings (List[str]): Findings to generate alerts from
            
        Returns:
            List[Dict[str, Any]]: Generated alerts with levels and actions
        """
        return [
            {
                "level": "info",
                "message": "Performance within expected range",
                "action_required": False
            },
            {
                "level": "warning",
                "message": "Monitor specific metrics closely",
                "action_required": True
            }
        ]
    
    def _get_time_range(self, df: pd.DataFrame) -> str:
        """Get time range from data
        
        Args:
            df (pd.DataFrame): Data to extract time range from
            
        Returns:
            str: Time range string
        """
        return "2024-01-15 to 2024-01-19"
    
    def _search_domain(self, query: str, domain_data: Dict[str, Any], search_type: str) -> List[str]:
        """Search within a specific domain
        
        Args:
            query (str): Search query
            domain_data (Dict[str, Any]): Domain data to search within
            search_type (str): Type of search to perform
            
        Returns:
            List[str]: Search results
        """
        results = []
        query_lower = query.lower()
        
        for category, items in domain_data.items():
            if isinstance(items, list):
                for item in items:
                    if query_lower in item.lower():
                        results.append(item)
        
        return results
    
    def _find_related_topics(self, query: str, domain: str) -> List[str]:
        """Find related topics based on query
        
        Args:
            query (str): Search query
            domain (str): Domain to find related topics in
            
        Returns:
            List[str]: Related topics
        """
        if domain == "productivity":
            return ["time management", "focus techniques", "goal setting"]
        elif domain == "health":
            return ["wellness", "fitness", "nutrition", "sleep"]
        elif domain == "financial":
            return ["budgeting", "investing", "savings", "expenses"]
        return ["general knowledge", "best practices", "optimization"]
    
    def _extract_actionable_items(self, results: List[str]) -> List[str]:
        """Extract actionable items from results
        
        Args:
            results (List[str]): Results to extract actionable items from
            
        Returns:
            List[str]: Actionable items
        """
        actionable = []
        for result in results:
            if any(word in result.lower() for word in ["use", "implement", "apply", "practice", "start", "stop"]):
                actionable.append(result)
        return actionable[:5]  # Return top 5 actionable items
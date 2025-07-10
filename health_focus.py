import json
import time
import sqlite3
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
import psutil
import requests
from geopy.geocoders import Nominatim
import schedule

logger = logging.getLogger(__name__)

class HealthFocusModule:
    """Comprehensive wellness, productivity, and environmental monitoring module"""
    
    def __init__(self):
        self._local = threading.local()
        self.focus_session_active = False
        self.current_session = None
        self.wellness_metrics = {}
        self.environment_data = {}
        self.habit_tracker = {}
        self.setup_wellness_tracking()
        self.setup_environment_monitoring()
    
    def get_db_connection(self):
        """Get thread-local database connection"""
        if not hasattr(self._local, 'db_connection') or self._local.db_connection is None:
            self._local.db_connection = sqlite3.connect(":memory:")
            self._setup_database_schema(self._local.db_connection)
        return self._local.db_connection
        
    def _setup_database_schema(self, connection):
        """Setup database schema for a connection"""
        try:
            cursor = connection.cursor()
            
            # Wellness metrics table
            cursor.execute('''
                CREATE TABLE wellness_metrics (
                    id INTEGER PRIMARY KEY,
                    date TEXT,
                    steps INTEGER,
                    sleep_hours REAL,
                    stress_level INTEGER,
                    energy_level INTEGER,
                    mood_score INTEGER,
                    water_intake REAL,
                    exercise_minutes INTEGER,
                    created_at TEXT
                )
            ''')
            
            # Focus sessions table
            cursor.execute('''
                CREATE TABLE focus_sessions (
                    id INTEGER PRIMARY KEY,
                    start_time TEXT,
                    end_time TEXT,
                    duration INTEGER,
                    session_type TEXT,
                    productivity_score INTEGER,
                    distractions_blocked INTEGER,
                    breaks_taken INTEGER,
                    completed BOOLEAN
                )
            ''')
            
            # Environment data table
            cursor.execute('''
                CREATE TABLE environment_data (
                    id INTEGER PRIMARY KEY,
                    location TEXT,
                    temperature REAL,
                    humidity REAL,
                    air_quality INTEGER,
                    noise_level REAL,
                    light_level REAL,
                    timestamp TEXT
                )
            ''')
            
            # Habit tracking table
            cursor.execute('''
                CREATE TABLE habit_tracking (
                    id INTEGER PRIMARY KEY,
                    habit_name TEXT,
                    date TEXT,
                    completed BOOLEAN,
                    streak_count INTEGER,
                    notes TEXT
                )
            ''')
            
            # Insert sample wellness data
            sample_wellness = [
                ('2024-01-15', 8500, 7.5, 3, 4, 4, 2.1, 30, datetime.now().isoformat()),
                ('2024-01-16', 9200, 8.0, 2, 5, 5, 2.5, 45, datetime.now().isoformat()),
                ('2024-01-17', 7800, 6.5, 4, 3, 3, 1.8, 20, datetime.now().isoformat()),
                ('2024-01-18', 10500, 7.8, 2, 4, 4, 2.3, 60, datetime.now().isoformat()),
                ('2024-01-19', 9800, 8.2, 1, 5, 5, 2.7, 40, datetime.now().isoformat())
            ]
            
            cursor.executemany('''
                INSERT INTO wellness_metrics (date, steps, sleep_hours, stress_level, energy_level, mood_score, water_intake, exercise_minutes, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', sample_wellness)
            
            connection.commit()
            logger.info("Health and wellness database initialized successfully")
            
        except Exception as e:
            logger.error(f"Health database setup error: {str(e)}")
    
    def setup_wellness_tracking(self):
        """Setup wellness tracking parameters"""
        self.wellness_targets = {
            "steps": 10000,
            "sleep_hours": 8.0,
            "stress_level": 2,  # 1-5 scale, lower is better
            "energy_level": 4,  # 1-5 scale, higher is better
            "mood_score": 4,    # 1-5 scale, higher is better
            "water_intake": 2.5,  # liters
            "exercise_minutes": 30
        }
        
        self.wellness_weights = {
            "steps": 0.2,
            "sleep_hours": 0.25,
            "stress_level": 0.2,
            "energy_level": 0.15,
            "mood_score": 0.1,
            "water_intake": 0.05,
            "exercise_minutes": 0.05
        }
    
    def setup_environment_monitoring(self):
        """Setup environment monitoring"""
        self.environment_thresholds = {
            "temperature": {"min": 20, "max": 25},  # Celsius
            "humidity": {"min": 40, "max": 60},     # Percentage
            "air_quality": {"max": 50},             # AQI
            "noise_level": {"max": 50},             # Decibels
            "light_level": {"min": 300, "max": 1000}  # Lux
        }
    
    def perform_wellness_check(self, metrics: List[str], time_period: str = "today", include_recommendations: bool = True) -> Dict[str, Any]:
        """Perform comprehensive wellness assessment
        
        Args:
            metrics (List[str]): List of wellness metrics to check
            time_period (str, optional): Time period for assessment. Defaults to "today"
            include_recommendations (bool, optional): Whether to include recommendations. Defaults to True
            
        Returns:
            Dict[str, Any]: Wellness assessment with scores, achievements, and recommendations
        """
        try:
            # Get wellness data
            cursor = self.get_db_connection().cursor()
            
            if time_period == "today":
                date_filter = datetime.now().strftime("%Y-%m-%d")
                cursor.execute('SELECT * FROM wellness_metrics WHERE date = ?', (date_filter,))
            else:
                cursor.execute('SELECT * FROM wellness_metrics ORDER BY date DESC LIMIT 7')
            
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            wellness_data = [dict(zip(columns, row)) for row in rows]
            
            if not wellness_data:
                return {"error": "No wellness data available"}
            
            # Calculate wellness scores
            latest_data = wellness_data[0] if wellness_data else {}
            
            wellness_result = {
                "assessment_date": datetime.now().isoformat(),
                "time_period": time_period,
                "overall_score": 0,
                "metric_scores": {},
                "achievements": [],
                "areas_for_improvement": [],
                "recommendations": [],
                "trends": {},
                "alerts": []
            }
            
            # Calculate individual metric scores
            total_score = 0
            for metric in metrics:
                if metric in latest_data and metric in self.wellness_targets:
                    current_value = latest_data[metric]
                    target_value = self.wellness_targets[metric]
                    weight = self.wellness_weights.get(metric, 0.1)
                    
                    # Calculate score based on metric type
                    if metric == "stress_level":
                        # Lower is better for stress
                        score = max(0, (6 - current_value) / 5 * 100)
                    elif metric in ["steps", "sleep_hours", "energy_level", "mood_score", "water_intake", "exercise_minutes"]:
                        # Higher is better
                        score = min(100, (current_value / target_value) * 100)
                    else:
                        score = 75  # Default score
                    
                    wellness_result["metric_scores"][metric] = {
                        "current_value": current_value,
                        "target_value": target_value,
                        "score": round(score, 1),
                        "status": self._get_metric_status(score)
                    }
                    
                    total_score += score * weight
            
            wellness_result["overall_score"] = round(total_score, 1)
            
            # Generate achievements
            wellness_result["achievements"] = self._identify_achievements(wellness_result["metric_scores"])
            
            # Identify areas for improvement
            wellness_result["areas_for_improvement"] = self._identify_improvement_areas(wellness_result["metric_scores"])
            
            # Generate recommendations
            if include_recommendations:
                wellness_result["recommendations"] = self._generate_wellness_recommendations(wellness_result)
            
            # Analyze trends
            if len(wellness_data) > 1:
                wellness_result["trends"] = self._analyze_wellness_trends(wellness_data, metrics)
            
            # Generate alerts
            wellness_result["alerts"] = self._generate_wellness_alerts(wellness_result)
            
            logger.info(f"Wellness check completed - Overall score: {wellness_result['overall_score']}")
            return wellness_result
            
        except Exception as e:
            logger.error(f"Error performing wellness check: {str(e)}")
            return {"error": str(e)}
    
    def start_focus_session(self, duration: int, session_type: str, block_distractions: bool = True) -> Dict[str, Any]:
        """Start a focused work session with distraction blocking
        
        Args:
            duration (int): Duration of focus session in minutes
            session_type (str): Type of focus session
            block_distractions (bool, optional): Whether to block distractions. Defaults to True
            
        Returns:
            Dict[str, Any]: Focus session details with schedule and tips
        """
        try:
            if self.focus_session_active:
                return {"error": "Focus session already active"}
            
            session_id = int(time.time())
            start_time = datetime.now()
            
            self.current_session = {
                "id": session_id,
                "start_time": start_time,
                "duration": duration,
                "session_type": session_type,
                "block_distractions": block_distractions,
                "distractions_blocked": 0,
                "breaks_taken": 0,
                "productivity_score": 0
            }
            
            self.focus_session_active = True
            
            # Start session monitoring in background
            session_thread = threading.Thread(target=self._monitor_focus_session)
            session_thread.daemon = True
            session_thread.start()
            
            # Setup distraction blocking if enabled
            if block_distractions:
                self._setup_distraction_blocking()
            
            # Schedule breaks based on session type
            break_schedule = self._calculate_break_schedule(duration, session_type)
            
            result = {
                "session_id": session_id,
                "start_time": start_time.isoformat(),
                "duration_minutes": duration,
                "session_type": session_type,
                "end_time": (start_time + timedelta(minutes=duration)).isoformat(),
                "distraction_blocking": block_distractions,
                "break_schedule": break_schedule,
                "session_tips": self._get_session_tips(session_type),
                "status": "active",
                "progress": {
                    "elapsed_minutes": 0,
                    "remaining_minutes": duration,
                    "completion_percentage": 0
                }
            }
            
            logger.info(f"Focus session started: {session_type} for {duration} minutes")
            return result
            
        except Exception as e:
            logger.error(f"Error starting focus session: {str(e)}")
            return {"error": str(e)}
    
    def monitor_environment(self, location: str, metrics: List[str] = None, alert_thresholds: Dict[str, Any] = None) -> Dict[str, Any]:
        """Monitor environmental conditions and health metrics
        
        Args:
            location (str): Location to monitor
            metrics (List[str], optional): Environmental metrics to monitor. Defaults to None
            alert_thresholds (Dict[str, Any], optional): Custom alert thresholds. Defaults to None
            
        Returns:
            Dict[str, Any]: Environment monitoring results with analysis and recommendations
        """
        try:
            if not metrics:
                metrics = ["temperature", "humidity", "air_quality"]
            
            # Get current environment data
            environment_data = self._collect_environment_data(location, metrics)
            
            # Store in database
            cursor = self.get_db_connection().cursor()
            cursor.execute('''
                INSERT INTO environment_data (location, temperature, humidity, air_quality, noise_level, light_level, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                location,
                environment_data.get("temperature", 0),
                environment_data.get("humidity", 0),
                environment_data.get("air_quality", 0),
                environment_data.get("noise_level", 0),
                environment_data.get("light_level", 0),
                datetime.now().isoformat()
            ))
            self.get_db_connection().commit()
            
            # Analyze environment quality
            analysis = self._analyze_environment_quality(environment_data, alert_thresholds or self.environment_thresholds)
            
            result = {
                "location": location,
                "timestamp": datetime.now().isoformat(),
                "metrics": environment_data,
                "analysis": analysis,
                "overall_score": analysis["overall_score"],
                "recommendations": self._generate_environment_recommendations(analysis),
                "alerts": analysis["alerts"],
                "optimal_conditions": self.environment_thresholds,
                "health_impact": self._assess_health_impact(environment_data)
            }
            
            logger.info(f"Environment monitoring completed for {location}")
            return result
            
        except Exception as e:
            logger.error(f"Error monitoring environment: {str(e)}")
            return {"error": str(e)}
    
    def _get_metric_status(self, score: float) -> str:
        """Get status based on metric score
        
        Args:
            score (float): Metric score (0-100)
            
        Returns:
            str: Status description
        """
        if score >= 90:
            return "excellent"
        elif score >= 75:
            return "good"
        elif score >= 60:
            return "fair"
        else:
            return "needs_improvement"
    
    def _identify_achievements(self, metric_scores: Dict[str, Any]) -> List[str]:
        """Identify wellness achievements
        
        Args:
            metric_scores (Dict[str, Any]): Wellness metric scores
            
        Returns:
            List[str]: Identified achievements
        """
        achievements = []
        
        for metric, data in metric_scores.items():
            if data["score"] >= 90:
                achievements.append(f"Excellent {metric.replace('_', ' ')} performance!")
            elif data["current_value"] >= data["target_value"]:
                achievements.append(f"Target achieved for {metric.replace('_', ' ')}")
        
        return achievements
    
    def _identify_improvement_areas(self, metric_scores: Dict[str, Any]) -> List[str]:
        """Identify areas needing improvement
        
        Args:
            metric_scores (Dict[str, Any]): Wellness metric scores
            
        Returns:
            List[str]: Areas needing improvement
        """
        improvements = []
        
        for metric, data in metric_scores.items():
            if data["score"] < 60:
                improvements.append(f"{metric.replace('_', ' ').title()} needs attention")
        
        return improvements
    
    def _generate_wellness_recommendations(self, wellness_result: Dict[str, Any]) -> List[str]:
        """Generate personalized wellness recommendations
        
        Args:
            wellness_result (Dict[str, Any]): Wellness assessment results
            
        Returns:
            List[str]: Personalized recommendations
        """
        recommendations = []
        
        for metric, data in wellness_result["metric_scores"].items():
            if data["score"] < 75:
                if metric == "steps":
                    recommendations.append("Take more walking breaks throughout the day")
                elif metric == "sleep_hours":
                    recommendations.append("Establish a consistent bedtime routine")
                elif metric == "stress_level":
                    recommendations.append("Practice deep breathing or meditation")
                elif metric == "water_intake":
                    recommendations.append("Set hourly reminders to drink water")
                elif metric == "exercise_minutes":
                    recommendations.append("Schedule short exercise sessions")
        
        # Add general recommendations
        if wellness_result["overall_score"] < 80:
            recommendations.append("Consider consulting with a wellness coach")
            recommendations.append("Track your metrics daily for better insights")
        
        return recommendations
    
    def _analyze_wellness_trends(self, wellness_data: List[Dict[str, Any]], metrics: List[str]) -> Dict[str, Any]:
        """Analyze wellness trends over time
        
        Args:
            wellness_data (List[Dict[str, Any]]): Historical wellness data
            metrics (List[str]): Metrics to analyze trends for
            
        Returns:
            Dict[str, Any]: Trend analysis results
        """
        trends = {}
        
        for metric in metrics:
            values = [data.get(metric, 0) for data in wellness_data if metric in data]
            if len(values) >= 2:
                if values[-1] > values[0]:
                    trends[metric] = "improving"
                elif values[-1] < values[0]:
                    trends[metric] = "declining"
                else:
                    trends[metric] = "stable"
        
        return trends
    
    def _generate_wellness_alerts(self, wellness_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate wellness alerts
        
        Args:
            wellness_result (Dict[str, Any]): Wellness assessment results
            
        Returns:
            List[Dict[str, Any]]: Generated alerts
        """
        alerts = []
        
        if wellness_result["overall_score"] < 60:
            alerts.append({
                "type": "wellness_warning",
                "message": "Overall wellness score is below recommended level",
                "severity": "high",
                "action_required": True
            })
        
        for metric, data in wellness_result["metric_scores"].items():
            if data["score"] < 50:
                alerts.append({
                    "type": "metric_alert",
                    "metric": metric,
                    "message": f"{metric.replace('_', ' ').title()} is significantly below target",
                    "severity": "medium",
                    "action_required": True
                })
        
        return alerts
    
    def _monitor_focus_session(self):
        """Monitor active focus session"""
        while self.focus_session_active and self.current_session:
            time.sleep(60)  # Check every minute
            
            elapsed = (datetime.now() - self.current_session["start_time"]).total_seconds() / 60
            
            if elapsed >= self.current_session["duration"]:
                self._end_focus_session()
                break
    
    def _setup_distraction_blocking(self):
        """Setup distraction blocking mechanisms"""
        # This would integrate with system-level blocking tools
        # For now, we'll just log the setup
        logger.info("Distraction blocking activated")
    
    def _calculate_break_schedule(self, duration: int, session_type: str) -> List[str]:
        """Calculate optimal break schedule
        
        Args:
            duration (int): Session duration in minutes
            session_type (str): Type of focus session
            
        Returns:
            List[str]: Break schedule
        """
        breaks = []
        
        if session_type == "pomodoro":
            # 25-minute work, 5-minute break
            for i in range(25, duration, 30):
                breaks.append(f"Break at {i} minutes")
        elif session_type == "deep_work":
            # 90-minute cycles with 15-minute breaks
            for i in range(90, duration, 105):
                breaks.append(f"Break at {i} minutes")
        else:
            # Default: break every hour
            for i in range(60, duration, 60):
                breaks.append(f"Break at {i} minutes")
        
        return breaks
    
    def _get_session_tips(self, session_type: str) -> List[str]:
        """Get tips for the session type
        
        Args:
            session_type (str): Type of focus session
            
        Returns:
            List[str]: Session tips
        """
        tips = {
            "pomodoro": [
                "Focus on one task at a time",
                "Take short breaks between sessions",
                "Use a timer to stay on track"
            ],
            "deep_work": [
                "Eliminate all distractions",
                "Work on your most important task",
                "Take longer breaks to recharge"
            ],
            "meeting": [
                "Prepare agenda in advance",
                "Take notes during discussion",
                "Follow up with action items"
            ]
        }
        
        return tips.get(session_type, ["Stay focused", "Take breaks when needed"])
    
    def _end_focus_session(self):
        """End the current focus session"""
        if self.current_session:
            end_time = datetime.now()
            duration = (end_time - self.current_session["start_time"]).total_seconds() / 60
            
            # Calculate productivity score (mock calculation)
            productivity_score = min(100, max(0, 100 - self.current_session["distractions_blocked"] * 5))
            
            # Store session in database
            cursor = self.get_db_connection().cursor()
            cursor.execute('''
                INSERT INTO focus_sessions (start_time, end_time, duration, session_type, productivity_score, distractions_blocked, breaks_taken, completed)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                self.current_session["start_time"].isoformat(),
                end_time.isoformat(),
                duration,
                self.current_session["session_type"],
                productivity_score,
                self.current_session["distractions_blocked"],
                self.current_session["breaks_taken"],
                True
            ))
            self.get_db_connection().commit()
            
            self.focus_session_active = False
            self.current_session = None
            
            logger.info(f"Focus session completed - Productivity score: {productivity_score}")
    
    def _collect_environment_data(self, location: str, metrics: List[str]) -> Dict[str, Any]:
        """Collect environment data from various sources
        
        Args:
            location (str): Location to collect data for
            metrics (List[str]): Environmental metrics to collect
            
        Returns:
            Dict[str, Any]: Collected environment data
        """
        # Mock environment data collection
        # In a real implementation, this would integrate with:
        # - Weather APIs
        # - Air quality APIs
        # - IoT sensors
        # - System monitoring tools
        
        data = {}
        
        if "temperature" in metrics:
            data["temperature"] = 22.5  # Mock temperature in Celsius
        
        if "humidity" in metrics:
            data["humidity"] = 45.0  # Mock humidity percentage
        
        if "air_quality" in metrics:
            data["air_quality"] = 35  # Mock AQI value
        
        if "noise_level" in metrics:
            data["noise_level"] = 40.0  # Mock noise level in dB
        
        if "light_level" in metrics:
            data["light_level"] = 500.0  # Mock light level in lux
        
        return data
    
    def _analyze_environment_quality(self, environment_data: Dict[str, Any], thresholds: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze environment quality against thresholds
        
        Args:
            environment_data (Dict[str, Any]): Environment data to analyze
            thresholds (Dict[str, Any]): Quality thresholds
            
        Returns:
            Dict[str, Any]: Environment quality analysis
        """
        analysis = {
            "overall_score": 0,
            "metric_scores": {},
            "alerts": [],
            "status": "good"
        }
        
        total_score = 0
        metric_count = 0
        
        for metric, value in environment_data.items():
            if metric in thresholds:
                threshold = thresholds[metric]
                score = 100  # Default good score
                
                if "min" in threshold and value < threshold["min"]:
                    score = max(0, (value / threshold["min"]) * 100)
                elif "max" in threshold and value > threshold["max"]:
                    score = max(0, 100 - ((value - threshold["max"]) / threshold["max"]) * 100)
                
                analysis["metric_scores"][metric] = {
                    "value": value,
                    "score": round(score, 1),
                    "status": "good" if score >= 75 else "warning" if score >= 50 else "poor"
                }
                
                if score < 75:
                    analysis["alerts"].append({
                        "metric": metric,
                        "message": f"{metric.replace('_', ' ').title()} is outside optimal range",
                        "severity": "warning" if score >= 50 else "high"
                    })
                
                total_score += score
                metric_count += 1
        
        if metric_count > 0:
            analysis["overall_score"] = round(total_score / metric_count, 1)
            
            if analysis["overall_score"] >= 80:
                analysis["status"] = "excellent"
            elif analysis["overall_score"] >= 60:
                analysis["status"] = "good"
            else:
                analysis["status"] = "needs_improvement"
        
        return analysis
    
    def _generate_environment_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate environment improvement recommendations
        
        Args:
            analysis (Dict[str, Any]): Environment quality analysis
            
        Returns:
            List[str]: Environment improvement recommendations
        """
        recommendations = []
        
        for metric, data in analysis["metric_scores"].items():
            if data["status"] != "good":
                if metric == "temperature":
                    recommendations.append("Adjust room temperature for optimal comfort")
                elif metric == "humidity":
                    recommendations.append("Use humidifier or dehumidifier to optimize humidity")
                elif metric == "air_quality":
                    recommendations.append("Improve ventilation or use air purifier")
                elif metric == "noise_level":
                    recommendations.append("Reduce noise sources or use noise-canceling headphones")
                elif metric == "light_level":
                    recommendations.append("Adjust lighting for optimal visibility")
        
        return recommendations
    
    def _assess_health_impact(self, environment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess health impact of environment conditions
        
        Args:
            environment_data (Dict[str, Any]): Environment data to assess
            
        Returns:
            Dict[str, Any]: Health impact assessment
        """
        impact = {
            "overall_impact": "neutral",
            "specific_impacts": {},
            "recommendations": []
        }
        
        # Assess each metric's health impact
        for metric, value in environment_data.items():
            if metric == "air_quality" and value > 50:
                impact["specific_impacts"]["respiratory"] = "negative"
                impact["recommendations"].append("Consider using air purifier")
            
            if metric == "noise_level" and value > 60:
                impact["specific_impacts"]["stress"] = "negative"
                impact["recommendations"].append("Reduce noise exposure")
        
        # Determine overall impact
        negative_impacts = sum(1 for impact_val in impact["specific_impacts"].values() if impact_val == "negative")
        if negative_impacts > 0:
            impact["overall_impact"] = "negative"
        
        return impact
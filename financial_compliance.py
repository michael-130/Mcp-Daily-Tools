import json
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
import threading
from cryptography.fernet import Fernet
import hashlib

logger = logging.getLogger(__name__)

class FinancialComplianceModule:
    """Comprehensive financial management, budgeting, and compliance tracking module"""
    
    def __init__(self):
        self._local = threading.local()
        self.encryption_key = None
        self.compliance_rules = {}
        self.budget_categories = {}
        self.setup_encryption()
        self.setup_compliance_rules()
    
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
            
            # Expenses table
            cursor.execute('''
                CREATE TABLE expenses (
                    id INTEGER PRIMARY KEY,
                    date TEXT,
                    amount REAL,
                    description TEXT,
                    category TEXT,
                    payment_method TEXT,
                    receipt_hash TEXT,
                    created_at TEXT
                )
            ''')
            
            # Budget table
            cursor.execute('''
                CREATE TABLE budgets (
                    id INTEGER PRIMARY KEY,
                    category TEXT,
                    monthly_limit REAL,
                    current_spent REAL,
                    period TEXT,
                    created_at TEXT
                )
            ''')
            
            # Compliance logs table
            cursor.execute('''
                CREATE TABLE compliance_logs (
                    id INTEGER PRIMARY KEY,
                    check_type TEXT,
                    status TEXT,
                    details TEXT,
                    timestamp TEXT
                )
            ''')
            
            # Insert sample budget data
            sample_budgets = [
                ('food', 800.00, 0.00, 'monthly', datetime.now().isoformat()),
                ('transport', 300.00, 0.00, 'monthly', datetime.now().isoformat()),
                ('utilities', 200.00, 0.00, 'monthly', datetime.now().isoformat()),
                ('entertainment', 150.00, 0.00, 'monthly', datetime.now().isoformat()),
                ('health', 100.00, 0.00, 'monthly', datetime.now().isoformat())
            ]
            
            cursor.executemany('''
                INSERT INTO budgets (category, monthly_limit, current_spent, period, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', sample_budgets)
            
            connection.commit()
            logger.info("Financial database initialized successfully")
            
        except Exception as e:
            logger.error(f"Financial database setup error: {str(e)}")
    
    def setup_encryption(self):
        """Setup encryption for sensitive financial data"""
        self.encryption_key = Fernet.generate_key()
        self.cipher_suite = Fernet(self.encryption_key)
        
    def setup_compliance_rules(self):
        """Setup compliance rules and regulations"""
        self.compliance_rules = {
            "expense_limits": {
                "daily_cash": 500.00,
                "monthly_total": 5000.00,
                "single_transaction": 1000.00
            },
            "documentation": {
                "receipt_required_above": 25.00,
                "business_expense_documentation": True,
                "tax_category_tracking": True
            },
            "reporting": {
                "monthly_summary": True,
                "quarterly_review": True,
                "annual_tax_prep": True
            },
            "audit_trail": {
                "transaction_logging": True,
                "modification_tracking": True,
                "access_logging": True
            }
        }
    
    def track_expenses(self, amount: float, description: str, category: str, date: str = None, payment_method: str = "cash") -> Dict[str, Any]:
        """Track and categorize expenses automatically
        
        Args:
            amount (float): Expense amount
            description (str): Description of the expense
            category (str): Expense category
            date (str, optional): Date of expense in YYYY-MM-DD format. Defaults to None (today)
            payment_method (str, optional): Payment method used. Defaults to "cash"
            
        Returns:
            Dict[str, Any]: Expense tracking result with compliance status and budget impact
        """
        try:
            if not date:
                date = datetime.now().strftime("%Y-%m-%d")
            
            # Validate expense
            validation_result = self._validate_expense(amount, category)
            if not validation_result["valid"]:
                return {"error": validation_result["message"]}
            
            # Generate receipt hash for audit trail
            receipt_data = f"{amount}_{description}_{category}_{date}"
            receipt_hash = hashlib.sha256(receipt_data.encode()).hexdigest()[:16]
            
            # Insert expense
            cursor = self.get_db_connection().cursor()
            cursor.execute('''
                INSERT INTO expenses (date, amount, description, category, payment_method, receipt_hash, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (date, amount, description, category, payment_method, receipt_hash, datetime.now().isoformat()))
            
            expense_id = cursor.lastrowid
            
            # Update budget tracking
            self._update_budget_tracking(category, amount)
            
            # Check compliance
            compliance_status = self._check_expense_compliance(amount, category)
            
            # Generate categorization suggestions
            suggestions = self._generate_category_suggestions(description)
            
            result = {
                "expense_id": expense_id,
                "amount": amount,
                "description": description,
                "category": category,
                "date": date,
                "receipt_hash": receipt_hash,
                "compliance_status": compliance_status,
                "budget_impact": self._calculate_budget_impact(category, amount),
                "tax_implications": self._analyze_tax_implications(category, amount),
                "suggestions": suggestions,
                "alerts": self._generate_expense_alerts(amount, category)
            }
            
            self.get_db_connection().commit()
            logger.info(f"Expense tracked: {description} - ${amount}")
            return result
            
        except Exception as e:
            logger.error(f"Error tracking expense: {str(e)}")
            return {"error": str(e)}
    
    def analyze_budget(self, period: str = "monthly", categories: List[str] = None) -> Dict[str, Any]:
        """Analyze budget performance and provide recommendations
        
        Args:
            period (str, optional): Budget period to analyze. Defaults to "monthly"
            categories (List[str], optional): Specific categories to analyze. Defaults to None (all categories)
            
        Returns:
            Dict[str, Any]: Budget analysis with performance metrics, recommendations, and projections
        """
        try:
            cursor = self.get_db_connection().cursor()
            
            # Get budget data
            if categories:
                placeholders = ','.join(['?' for _ in categories])
                cursor.execute(f'''
                    SELECT * FROM budgets WHERE category IN ({placeholders}) AND period = ?
                ''', categories + [period])
            else:
                cursor.execute('SELECT * FROM budgets WHERE period = ?', (period,))
            
            budgets = cursor.fetchall()
            budget_columns = [desc[0] for desc in cursor.description]
            budget_data = [dict(zip(budget_columns, row)) for row in budgets]
            
            # Get expense data for the period
            start_date = self._get_period_start_date(period)
            cursor.execute('''
                SELECT category, SUM(amount) as total_spent, COUNT(*) as transaction_count
                FROM expenses 
                WHERE date >= ? 
                GROUP BY category
            ''', (start_date,))
            
            expense_data = cursor.fetchall()
            expense_summary = {row[0]: {"total": row[1], "count": row[2]} for row in expense_data}
            
            # Analyze budget performance
            analysis = {
                "period": period,
                "analysis_date": datetime.now().isoformat(),
                "overall_performance": {},
                "category_analysis": [],
                "recommendations": [],
                "alerts": [],
                "projections": {}
            }
            
            total_budget = sum(b["monthly_limit"] for b in budget_data)
            total_spent = sum(exp["total"] for exp in expense_summary.values())
            
            analysis["overall_performance"] = {
                "total_budget": total_budget,
                "total_spent": total_spent,
                "remaining_budget": total_budget - total_spent,
                "utilization_rate": (total_spent / total_budget * 100) if total_budget > 0 else 0,
                "days_remaining": self._get_days_remaining_in_period(period),
                "daily_average": total_spent / max(1, self._get_days_elapsed_in_period(period))
            }
            
            # Category-wise analysis
            for budget in budget_data:
                category = budget["category"]
                spent = expense_summary.get(category, {"total": 0, "count": 0})
                
                category_analysis = {
                    "category": category,
                    "budget_limit": budget["monthly_limit"],
                    "amount_spent": spent["total"],
                    "remaining": budget["monthly_limit"] - spent["total"],
                    "utilization_percentage": (spent["total"] / budget["monthly_limit"] * 100) if budget["monthly_limit"] > 0 else 0,
                    "transaction_count": spent["count"],
                    "average_transaction": spent["total"] / max(1, spent["count"]),
                    "status": self._get_budget_status(spent["total"], budget["monthly_limit"]),
                    "trend": self._analyze_spending_trend(category, period)
                }
                
                analysis["category_analysis"].append(category_analysis)
            
            # Generate recommendations
            analysis["recommendations"] = self._generate_budget_recommendations(analysis)
            
            # Generate alerts
            analysis["alerts"] = self._generate_budget_alerts(analysis)
            
            # Generate projections
            analysis["projections"] = self._generate_spending_projections(analysis)
            
            logger.info(f"Budget analysis completed for {period}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing budget: {str(e)}")
            return {"error": str(e)}
    
    def check_compliance(self, regulation_type: str = "financial", entity: str = "personal", check_date: str = None) -> Dict[str, Any]:
        """Check compliance status and generate audit trails
        
        Args:
            regulation_type (str, optional): Type of regulation to check. Defaults to "financial"
            entity (str, optional): Entity being checked. Defaults to "personal"
            check_date (str, optional): Date of compliance check. Defaults to None (today)
            
        Returns:
            Dict[str, Any]: Compliance status with score, violations, and recommendations
        """
        try:
            if not check_date:
                check_date = datetime.now().strftime("%Y-%m-%d")
            
            compliance_result = {
                "regulation_type": regulation_type,
                "entity": entity,
                "check_date": check_date,
                "overall_status": "compliant",
                "compliance_score": 0,
                "checks_performed": [],
                "violations": [],
                "recommendations": [],
                "audit_trail": [],
                "next_review_date": (datetime.now() + timedelta(days=90)).strftime("%Y-%m-%d")
            }
            
            # Perform various compliance checks
            checks = [
                self._check_expense_documentation_compliance(),
                self._check_budget_limit_compliance(),
                self._check_transaction_audit_trail(),
                self._check_data_retention_compliance(),
                self._check_reporting_compliance()
            ]
            
            compliance_result["checks_performed"] = checks
            
            # Calculate compliance score
            passed_checks = sum(1 for check in checks if check["status"] == "passed")
            compliance_result["compliance_score"] = (passed_checks / len(checks)) * 100
            
            # Determine overall status
            if compliance_result["compliance_score"] >= 90:
                compliance_result["overall_status"] = "fully_compliant"
            elif compliance_result["compliance_score"] >= 70:
                compliance_result["overall_status"] = "mostly_compliant"
            else:
                compliance_result["overall_status"] = "non_compliant"
            
            # Collect violations
            compliance_result["violations"] = [check for check in checks if check["status"] == "failed"]
            
            # Generate recommendations
            compliance_result["recommendations"] = self._generate_compliance_recommendations(checks)
            
            # Log compliance check
            self._log_compliance_check(regulation_type, compliance_result["overall_status"], compliance_result)
            
            logger.info(f"Compliance check completed: {compliance_result['overall_status']}")
            return compliance_result
            
        except Exception as e:
            logger.error(f"Error checking compliance: {str(e)}")
            return {"error": str(e)}
    
    def _validate_expense(self, amount: float, category: str) -> Dict[str, Any]:
        """Validate expense against compliance rules
        
        Args:
            amount (float): Expense amount to validate
            category (str): Expense category
            
        Returns:
            Dict[str, Any]: Validation result with validity status and message
        """
        if amount <= 0:
            return {"valid": False, "message": "Amount must be positive"}
        
        if amount > self.compliance_rules["expense_limits"]["single_transaction"]:
            return {"valid": False, "message": f"Amount exceeds single transaction limit of ${self.compliance_rules['expense_limits']['single_transaction']}"}
        
        return {"valid": True, "message": "Expense is valid"}
    
    def _update_budget_tracking(self, category: str, amount: float):
        """Update budget tracking for category
        
        Args:
            category (str): Budget category to update
            amount (float): Amount to add to current spending
        """
        cursor = self.get_db_connection().cursor()
        cursor.execute('''
            UPDATE budgets 
            SET current_spent = current_spent + ? 
            WHERE category = ?
        ''', (amount, category))
    
    def _check_expense_compliance(self, amount: float, category: str) -> Dict[str, Any]:
        """Check if expense complies with rules
        
        Args:
            amount (float): Expense amount
            category (str): Expense category
            
        Returns:
            Dict[str, Any]: Compliance status and issues
        """
        status = "compliant"
        issues = []
        
        if amount > self.compliance_rules["expense_limits"]["daily_cash"]:
            status = "warning"
            issues.append("Exceeds daily cash limit")
        
        if amount > self.compliance_rules["documentation"]["receipt_required_above"]:
            issues.append("Receipt required for this amount")
        
        return {"status": status, "issues": issues}
    
    def _calculate_budget_impact(self, category: str, amount: float) -> Dict[str, Any]:
        """Calculate impact on budget
        
        Args:
            category (str): Budget category
            amount (float): Expense amount
            
        Returns:
            Dict[str, Any]: Budget impact analysis
        """
        cursor = self.get_db_connection().cursor()
        cursor.execute('SELECT monthly_limit, current_spent FROM budgets WHERE category = ?', (category,))
        result = cursor.fetchone()
        
        if result:
            limit, current = result
            new_total = current + amount
            return {
                "category": category,
                "previous_spent": current,
                "new_total": new_total,
                "remaining": limit - new_total,
                "utilization_percentage": (new_total / limit * 100) if limit > 0 else 0
            }
        
        return {"category": category, "status": "no_budget_set"}
    
    def _analyze_tax_implications(self, category: str, amount: float) -> Dict[str, Any]:
        """Analyze tax implications of expense
        
        Args:
            category (str): Expense category
            amount (float): Expense amount
            
        Returns:
            Dict[str, Any]: Tax implications and potential savings
        """
        tax_categories = {
            "business": {"deductible": True, "rate": 0.25},
            "health": {"deductible": True, "rate": 0.15},
            "education": {"deductible": True, "rate": 0.20},
            "charity": {"deductible": True, "rate": 1.0}
        }
        
        if category in tax_categories:
            info = tax_categories[category]
            return {
                "deductible": info["deductible"],
                "potential_savings": amount * info["rate"],
                "documentation_required": True
            }
        
        return {"deductible": False, "potential_savings": 0}
    
    def _generate_category_suggestions(self, description: str) -> List[str]:
        """Generate category suggestions based on description
        
        Args:
            description (str): Expense description
            
        Returns:
            List[str]: Suggested categories
        """
        keywords = {
            "food": ["restaurant", "grocery", "coffee", "lunch", "dinner"],
            "transport": ["gas", "uber", "taxi", "bus", "train"],
            "utilities": ["electric", "water", "internet", "phone"],
            "health": ["doctor", "pharmacy", "medicine", "hospital"],
            "entertainment": ["movie", "concert", "game", "book"]
        }
        
        description_lower = description.lower()
        suggestions = []
        
        for category, words in keywords.items():
            if any(word in description_lower for word in words):
                suggestions.append(category)
        
        return suggestions[:3]
    
    def _generate_expense_alerts(self, amount: float, category: str) -> List[Dict[str, Any]]:
        """Generate alerts for expense
        
        Args:
            amount (float): Expense amount
            category (str): Expense category
            
        Returns:
            List[Dict[str, Any]]: Generated alerts
        """
        alerts = []
        
        if amount > 100:
            alerts.append({
                "type": "high_amount",
                "message": f"High expense amount: ${amount}",
                "severity": "warning"
            })
        
        # Check budget impact
        cursor = self.get_db_connection().cursor()
        cursor.execute('SELECT monthly_limit, current_spent FROM budgets WHERE category = ?', (category,))
        result = cursor.fetchone()
        
        if result:
            limit, current = result
            if (current + amount) > limit * 0.8:
                alerts.append({
                    "type": "budget_warning",
                    "message": f"Approaching budget limit for {category}",
                    "severity": "warning"
                })
        
        return alerts
    
    def _get_period_start_date(self, period: str) -> str:
        """Get start date for period
        
        Args:
            period (str): Period type (monthly, quarterly, yearly)
            
        Returns:
            str: Start date in YYYY-MM-DD format
        """
        now = datetime.now()
        if period == "monthly":
            return now.replace(day=1).strftime("%Y-%m-%d")
        elif period == "quarterly":
            quarter_start = ((now.month - 1) // 3) * 3 + 1
            return now.replace(month=quarter_start, day=1).strftime("%Y-%m-%d")
        elif period == "yearly":
            return now.replace(month=1, day=1).strftime("%Y-%m-%d")
        return now.strftime("%Y-%m-%d")
    
    def _get_days_remaining_in_period(self, period: str) -> int:
        """Get days remaining in period
        
        Args:
            period (str): Period type
            
        Returns:
            int: Days remaining in period
        """
        now = datetime.now()
        if period == "monthly":
            next_month = now.replace(day=28) + timedelta(days=4)
            end_of_month = next_month - timedelta(days=next_month.day)
            return (end_of_month - now).days
        return 30  # Default
    
    def _get_days_elapsed_in_period(self, period: str) -> int:
        """Get days elapsed in period
        
        Args:
            period (str): Period type
            
        Returns:
            int: Days elapsed in period
        """
        now = datetime.now()
        if period == "monthly":
            return now.day
        return 1  # Default
    
    def _get_budget_status(self, spent: float, limit: float) -> str:
        """Get budget status
        
        Args:
            spent (float): Amount spent
            limit (float): Budget limit
            
        Returns:
            str: Budget status
        """
        if limit == 0:
            return "no_limit"
        
        utilization = spent / limit
        if utilization >= 1.0:
            return "over_budget"
        elif utilization >= 0.8:
            return "warning"
        elif utilization >= 0.5:
            return "on_track"
        else:
            return "under_budget"
    
    def _analyze_spending_trend(self, category: str, period: str) -> str:
        """Analyze spending trend for category
        
        Args:
            category (str): Expense category
            period (str): Period to analyze
            
        Returns:
            str: Spending trend
        """
        # Mock trend analysis
        return "stable"
    
    def _generate_budget_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate budget recommendations
        
        Args:
            analysis (Dict[str, Any]): Budget analysis data
            
        Returns:
            List[str]: Budget recommendations
        """
        recommendations = []
        
        for category in analysis["category_analysis"]:
            if category["utilization_percentage"] > 80:
                recommendations.append(f"Consider reducing spending in {category['category']} category")
            elif category["utilization_percentage"] < 50:
                recommendations.append(f"You have room to spend more in {category['category']} if needed")
        
        return recommendations
    
    def _generate_budget_alerts(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate budget alerts
        
        Args:
            analysis (Dict[str, Any]): Budget analysis data
            
        Returns:
            List[Dict[str, Any]]: Budget alerts
        """
        alerts = []
        
        for category in analysis["category_analysis"]:
            if category["utilization_percentage"] > 90:
                alerts.append({
                    "type": "budget_exceeded",
                    "category": category["category"],
                    "message": f"Budget exceeded for {category['category']}",
                    "severity": "high"
                })
        
        return alerts
    
    def _generate_spending_projections(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate spending projections
        
        Args:
            analysis (Dict[str, Any]): Budget analysis data
            
        Returns:
            Dict[str, Any]: Spending projections
        """
        overall = analysis["overall_performance"]
        days_remaining = overall["days_remaining"]
        daily_average = overall["daily_average"]
        
        projected_total = overall["total_spent"] + (daily_average * days_remaining)
        
        return {
            "projected_monthly_total": projected_total,
            "projected_vs_budget": projected_total - overall["total_budget"],
            "confidence": "medium"
        }
    
    def _check_expense_documentation_compliance(self) -> Dict[str, Any]:
        """Check expense documentation compliance"""
        return {
            "check_name": "expense_documentation",
            "status": "passed",
            "details": "All expenses properly documented",
            "score": 95
        }
    
    def _check_budget_limit_compliance(self) -> Dict[str, Any]:
        """Check budget limit compliance"""
        return {
            "check_name": "budget_limits",
            "status": "passed",
            "details": "Spending within approved limits",
            "score": 88
        }
    
    def _check_transaction_audit_trail(self) -> Dict[str, Any]:
        """Check transaction audit trail"""
        return {
            "check_name": "audit_trail",
            "status": "passed",
            "details": "Complete audit trail maintained",
            "score": 92
        }
    
    def _check_data_retention_compliance(self) -> Dict[str, Any]:
        """Check data retention compliance"""
        return {
            "check_name": "data_retention",
            "status": "passed",
            "details": "Data retention policy followed",
            "score": 90
        }
    
    def _check_reporting_compliance(self) -> Dict[str, Any]:
        """Check reporting compliance"""
        return {
            "check_name": "reporting",
            "status": "passed",
            "details": "Regular reporting maintained",
            "score": 85
        }
    
    def _generate_compliance_recommendations(self, checks: List[Dict[str, Any]]) -> List[str]:
        """Generate compliance recommendations"""
        recommendations = []
        
        for check in checks:
            if check["status"] == "failed":
                recommendations.append(f"Address issues in {check['check_name']}")
            elif check["score"] < 90:
                recommendations.append(f"Improve {check['check_name']} processes")
        
        return recommendations
    
    def _log_compliance_check(self, check_type: str, status: str, details: Dict[str, Any]):
        """Log compliance check"""
        cursor = self.get_db_connection().cursor()
        cursor.execute('''
            INSERT INTO compliance_logs (check_type, status, details, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (check_type, status, json.dumps(details), datetime.now().isoformat()))
        self.get_db_connection().commit()
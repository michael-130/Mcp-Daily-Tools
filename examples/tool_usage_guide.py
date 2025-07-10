#!/usr/bin/env python3
"""
Tool Usage Guide and Examples
Shows how to properly use each tool with correct parameters
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

def show_task_automation_examples():
    """Show examples for Task Automation tools"""
    print("🤖 Task Automation Examples")
    print("-" * 40)
    
    print("\n1. Estimate Task Time:")
    print("   Parameters:")
    print('   {"task_description": "Write a research paper", "task_type": "technical", "complexity": "high"}')
    
    print("\n2. Schedule Task:")
    print("   Parameters:")
    print('   {"task": "Team meeting", "priority": "high", "deadline": "2024-12-31T15:00:00", "estimated_duration": 2}')
    
    print("\n3. Automate Email:")
    print("   Parameters:")
    print('   {"email_type": "meeting_request", "recipient": "team@company.com", "subject": "Weekly Sync"}')

def show_data_reports_examples():
    """Show examples for Data Reports tools"""
    print("\n📊 Data Reports Examples")
    print("-" * 40)
    
    print("\n1. Generate Report:")
    print("   Parameters:")
    print('   {"data_source": "performance", "report_type": "productivity", "time_period": "last_7_days"}')
    
    print("\n2. AI Insights:")
    print("   Parameters:")
    print('   {"data": [{"metric": "productivity", "value": 85}], "focus_area": "productivity", "insight_type": "trend"}')
    
    print("\n3. Knowledge Query:")
    print("   Parameters:")
    print('   {"query": "best productivity practices", "domain": "productivity", "search_type": "semantic"}')

def show_financial_examples():
    """Show examples for Financial tools"""
    print("\n💰 Financial Compliance Examples")
    print("-" * 40)
    
    print("\n1. Track Expenses:")
    print("   Parameters:")
    print('   {"amount": 45.50, "description": "Lunch meeting", "category": "food", "payment_method": "card"}')
    
    print("\n2. Budget Analysis:")
    print("   Parameters:")
    print('   {"period": "monthly", "categories": ["food", "transport", "utilities"]}')
    
    print("\n3. Compliance Check:")
    print("   Parameters:")
    print('   {"regulation_type": "financial", "entity": "personal"}')

def show_health_examples():
    """Show examples for Health & Focus tools"""
    print("\n🏃 Health & Focus Examples")
    print("-" * 40)
    
    print("\n1. Wellness Check:")
    print("   Parameters:")
    print('   {"metrics": ["steps", "sleep_hours", "stress_level"], "time_period": "today", "include_recommendations": true}')
    
    print("\n2. Focus Session:")
    print("   Parameters:")
    print('   {"duration": 90, "session_type": "deep_work", "block_distractions": true}')
    
    print("\n3. Environment Monitor:")
    print("   Parameters:")
    print('   {"location": "home_office", "metrics": ["temperature", "humidity", "air_quality"]}')

def show_security_examples():
    """Show examples for Security & Privacy tools"""
    print("\n🔒 Security & Privacy Examples")
    print("-" * 40)
    
    print("\n1. Security Audit:")
    print("   Parameters:")
    print('   {"scope": "system", "audit_type": "comprehensive", "generate_report": true}')
    
    print("\n2. Encrypt Data:")
    print("   Parameters:")
    print('   {"data_type": "personal", "encryption_level": "advanced", "key_rotation": true}')
    
    print("\n3. Privacy Check:")
    print("   Parameters:")
    print('   {"regulation": "GDPR", "data_categories": ["personal", "financial"], "generate_report": true}')

def show_api_examples():
    """Show examples for API tools"""
    print("\n🌐 API Tools Examples")
    print("-" * 40)
    
    print("\n1. Search Research Papers:")
    print("   Parameters:")
    print('   {"query": "machine learning", "max_results": 10, "category": "cs.LG"}')
    
    print("\n2. Get Repository Info:")
    print("   Parameters:")
    print('   {"owner": "microsoft", "repo": "vscode"}')
    
    print("\n3. Lookup Country:")
    print("   Parameters:")
    print('   {"country_name": "Japan"}')
    
    print("\n4. Get Crypto Price:")
    print("   Parameters:")
    print('   {"currency": "bitcoin"}')

def show_common_mistakes():
    """Show common parameter mistakes to avoid"""
    print("\n❌ Common Mistakes to Avoid")
    print("-" * 40)
    
    print("\n1. Don't use 'param' as a parameter name")
    print("   ❌ Wrong: {'param': 'value'}")
    print("   ✅ Correct: {'task_description': 'value'}")
    
    print("\n2. Use correct parameter names")
    print("   ❌ Wrong: {'description': 'task'}")
    print("   ✅ Correct: {'task_description': 'task'}")
    
    print("\n3. Provide required parameters")
    print("   ❌ Wrong: {} (empty parameters)")
    print("   ✅ Correct: {'task_description': 'Write report'}")
    
    print("\n4. Use valid JSON format")
    print('   ❌ Wrong: {task: "value"}')
    print('   ✅ Correct: {"task": "value"}')

def main():
    """Show all examples"""
    print("🚀 MCP Tools - Usage Guide")
    print("=" * 50)
    
    show_task_automation_examples()
    show_data_reports_examples()
    show_financial_examples()
    show_health_examples()
    show_security_examples()
    show_api_examples()
    show_common_mistakes()
    
    print("\n" + "=" * 50)
    print("💡 Tips:")
    print("1. Always use proper JSON format for parameters")
    print("2. Check the tool documentation for required parameters")
    print("3. Use the examples above as templates")
    print("4. Test with simple parameters first")

if __name__ == "__main__":
    main()
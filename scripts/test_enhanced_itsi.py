#!/usr/bin/env python3
"""
Enhanced ITSI Integration Test Script
Tests all ITSI tools including the newly added ones
"""

import sys
import os
import asyncio
import json
from datetime import datetime

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from splunk_mcp.main import (
    get_itsi_services,
    get_itsi_service_health,
    get_itsi_kpis,
    get_itsi_alerts,
    get_itsi_entities,
    get_itsi_entity_types,
    get_itsi_glass_tables,
    get_itsi_service_analytics,
    # New ITSI tools
    get_itsi_deep_dives,
    get_itsi_home_views,
    get_itsi_kpi_templates,
    get_itsi_notable_events,
    get_itsi_correlation_searches,
    get_itsi_maintenance_calendars,
    get_itsi_teams
)

class MockUser:
    """Mock user for testing"""
    def __init__(self):
        self.user_id = "test_user"
        self.username = "test_user"
        self.roles = ["admin", "itsi_user"]

async def test_itsi_tool(tool_name, tool_func, *args):
    """Test an individual ITSI tool"""
    print(f"\n{'='*50}")
    print(f"Testing: {tool_name}")
    print(f"{'='*50}")
    
    try:
        # Create mock user
        mock_user = MockUser()
        
        # Call the tool function with mock user
        if args:
            result = await tool_func(*args, current_user=mock_user.__dict__)
        else:
            result = await tool_func(current_user=mock_user.__dict__)
        
        print(f"✅ {tool_name} - SUCCESS")
        print(f"Result type: {type(result)}")
        
        if isinstance(result, list):
            print(f"Number of items: {len(result)}")
            if result:
                print("Sample item keys:", list(result[0].keys()) if result[0] else "Empty item")
        elif isinstance(result, dict):
            print("Result keys:", list(result.keys()))
        
        # Pretty print first few items for lists
        if isinstance(result, list) and result:
            print("\nFirst item preview:")
            print(json.dumps(result[0], indent=2, default=str)[:500] + "..." if len(str(result[0])) > 500 else json.dumps(result[0], indent=2, default=str))
        elif isinstance(result, dict):
            print("\nResult preview:")
            print(json.dumps(result, indent=2, default=str)[:500] + "..." if len(str(result)) > 500 else json.dumps(result, indent=2, default=str))
            
        return True
        
    except Exception as e:
        print(f"❌ {tool_name} - FAILED")
        print(f"Error: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        return False

async def main():
    """Main test function"""
    print("🚀 Starting Enhanced ITSI Integration Tests")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Test cases: (name, function, *args)
    test_cases = [
        # Existing ITSI tools
        ("ITSI Services", get_itsi_services),
        ("ITSI Service Health", get_itsi_service_health, "test_service"),
        ("ITSI KPIs", get_itsi_kpis),
        ("ITSI Alerts", get_itsi_alerts),
        ("ITSI Entities", get_itsi_entities),
        ("ITSI Entity Types", get_itsi_entity_types),
        ("ITSI Glass Tables", get_itsi_glass_tables),
        ("ITSI Service Analytics", get_itsi_service_analytics, "test_service", "-24h"),
        
        # New ITSI tools
        ("ITSI Deep Dives", get_itsi_deep_dives),
        ("ITSI Home Views", get_itsi_home_views),
        ("ITSI KPI Templates", get_itsi_kpi_templates),
        ("ITSI Notable Events", get_itsi_notable_events),
        ("ITSI Correlation Searches", get_itsi_correlation_searches),
        ("ITSI Maintenance Calendars", get_itsi_maintenance_calendars),
        ("ITSI Teams", get_itsi_teams),
    ]
    
    # Run tests
    results = []
    for test_case in test_cases:
        name = test_case[0]
        func = test_case[1]
        args = test_case[2:] if len(test_case) > 2 else []
        
        success = await test_itsi_tool(name, func, *args)
        results.append((name, success))
    
    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"Total tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success rate: {(passed/total)*100:.1f}%")
    
    print("\nDetailed Results:")
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status} - {name}")
    
    # Test specific service queries
    print(f"\n{'='*60}")
    print("TESTING WITH SPECIFIC SERVICE")
    print(f"{'='*60}")
    
    service_specific_tests = [
        ("ITSI Services (filtered)", get_itsi_services, "web_service"),
        ("ITSI KPIs (filtered)", get_itsi_kpis, "web_service"),
        ("ITSI Alerts (filtered)", get_itsi_alerts, "web_service"),
        ("ITSI Entities (filtered)", get_itsi_entities, "web_service"),
        ("ITSI Deep Dives (filtered)", get_itsi_deep_dives, "web_service"),
        ("ITSI Notable Events (filtered)", get_itsi_notable_events, "web_service", "-1h"),
    ]
    
    for test_case in service_specific_tests:
        name = test_case[0]
        func = test_case[1]
        args = test_case[2:] if len(test_case) > 2 else []
        
        await test_itsi_tool(name, func, *args)
    
    print(f"\n🎉 Enhanced ITSI Integration Tests Completed!")
    print(f"Timestamp: {datetime.now().isoformat()}")

if __name__ == "__main__":
    asyncio.run(main())
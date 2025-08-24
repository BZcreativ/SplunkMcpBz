#!/usr/bin/env python3
"""
ITSI Helper Functions Test Script
Tests the ITSI helper functions directly without requiring full server setup
"""

import sys
import os
import json
from datetime import datetime

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_itsi_helper_imports():
    """Test that all ITSI helper functions can be imported"""
    print("Testing ITSI Helper Function Imports")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    try:
        from splunk_mcp.itsi_helper import ITSIHelper
        print("✅ ITSIHelper class imported successfully")
        
        # Check if all new methods exist
        helper_methods = [
            'get_service_entities',
            'get_services', 
            'get_kpis',
            'get_service_health',
            'get_alerts',
            'get_service_analytics',
            'get_entity_types',
            'get_glass_tables',
            # New methods
            'get_deep_dives',
            'get_home_views',
            'get_kpi_templates',
            'get_notable_events',
            'get_correlation_searches',
            'get_maintenance_calendars',
            'get_teams'
        ]
        
        print(f"\n{'='*50}")
        print("Checking ITSIHelper Methods")
        print(f"{'='*50}")
        
        missing_methods = []
        for method in helper_methods:
            if hasattr(ITSIHelper, method):
                print(f"✅ {method} - Found")
            else:
                print(f"❌ {method} - Missing")
                missing_methods.append(method)
        
        if missing_methods:
            print(f"\n❌ Missing methods: {missing_methods}")
            return False
        else:
            print(f"\n✅ All {len(helper_methods)} methods found in ITSIHelper class")
            return True
            
    except ImportError as e:
        print(f"❌ Failed to import ITSIHelper: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_method_signatures():
    """Test method signatures of new ITSI helper functions"""
    print(f"\n{'='*50}")
    print("Testing Method Signatures")
    print(f"{'='*50}")
    
    try:
        from splunk_mcp.itsi_helper import ITSIHelper
        import inspect
        
        # Test method signatures
        method_signatures = {
            'get_deep_dives': ['service_name'],
            'get_home_views': [],
            'get_kpi_templates': [],
            'get_notable_events': ['service_name', 'time_range'],
            'get_correlation_searches': [],
            'get_maintenance_calendars': [],
            'get_teams': []
        }
        
        for method_name, expected_params in method_signatures.items():
            if hasattr(ITSIHelper, method_name):
                method = getattr(ITSIHelper, method_name)
                sig = inspect.signature(method)
                params = list(sig.parameters.keys())[1:]  # Skip 'self'
                
                print(f"✅ {method_name}")
                print(f"   Expected params: {expected_params}")
                print(f"   Actual params: {params}")
                
                # Check if expected parameters are present (allowing for additional optional params)
                for expected_param in expected_params:
                    if expected_param not in params:
                        print(f"   ⚠️  Missing expected parameter: {expected_param}")
            else:
                print(f"❌ {method_name} - Method not found")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing method signatures: {e}")
        return False

def test_code_syntax():
    """Test that the code syntax is valid by attempting to compile"""
    print(f"\n{'='*50}")
    print("Testing Code Syntax")
    print(f"{'='*50}")
    
    try:
        # Test itsi_helper.py syntax
        itsi_helper_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'splunk_mcp', 'itsi_helper.py')
        with open(itsi_helper_path, 'r') as f:
            code = f.read()
        
        compile(code, itsi_helper_path, 'exec')
        print("✅ itsi_helper.py - Syntax valid")
        
        # Test main.py syntax (just compile, don't execute)
        main_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'splunk_mcp', 'main.py')
        with open(main_path, 'r') as f:
            code = f.read()
        
        compile(code, main_path, 'exec')
        print("✅ main.py - Syntax valid")
        
        return True
        
    except SyntaxError as e:
        print(f"❌ Syntax error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing syntax: {e}")
        return False

def count_itsi_tools():
    """Count the number of ITSI tools in main.py"""
    print(f"\n{'='*50}")
    print("Counting ITSI Tools in main.py")
    print(f"{'='*50}")
    
    try:
        main_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'splunk_mcp', 'main.py')
        with open(main_path, 'r') as f:
            content = f.read()
        
        # Count @mcp.tool() decorators followed by get_itsi functions
        import re
        pattern = r'@mcp\.tool\(\)\s*async def (get_itsi_\w+)'
        matches = re.findall(pattern, content)
        
        print(f"Found {len(matches)} ITSI tools:")
        for i, tool in enumerate(matches, 1):
            print(f"  {i}. {tool}")
        
        # Expected tools (8 original + 7 new = 15 total)
        expected_tools = [
            'get_itsi_services',
            'get_itsi_service_health', 
            'get_itsi_kpis',
            'get_itsi_alerts',
            'get_itsi_entities',
            'get_itsi_entity_types',
            'get_itsi_glass_tables',
            'get_itsi_service_analytics',
            'get_itsi_deep_dives',
            'get_itsi_home_views',
            'get_itsi_kpi_templates',
            'get_itsi_notable_events',
            'get_itsi_correlation_searches',
            'get_itsi_maintenance_calendars',
            'get_itsi_teams'
        ]
        
        print(f"\nExpected {len(expected_tools)} tools, found {len(matches)} tools")
        
        missing_tools = set(expected_tools) - set(matches)
        extra_tools = set(matches) - set(expected_tools)
        
        if missing_tools:
            print(f"❌ Missing tools: {missing_tools}")
        if extra_tools:
            print(f"ℹ️  Extra tools: {extra_tools}")
        
        if len(matches) >= len(expected_tools) and not missing_tools:
            print("✅ All expected ITSI tools found")
            return True
        else:
            return False
            
    except Exception as e:
        print(f"❌ Error counting ITSI tools: {e}")
        return False

def main():
    """Main test function"""
    print("ITSI Helper Functions Test Suite")
    print("="*60)
    
    tests = [
        ("Import Test", test_itsi_helper_imports),
        ("Method Signatures Test", test_method_signatures),
        ("Code Syntax Test", test_code_syntax),
        ("ITSI Tools Count Test", count_itsi_tools)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\nRunning: {test_name}")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
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
    
    if passed == total:
        print(f"\nAll tests passed! ITSI integration is ready.")
    else:
        print(f"\nSome tests failed. Please review the issues above.")
    
    print(f"\nCompleted: {datetime.now().isoformat()}")

if __name__ == "__main__":
    main()
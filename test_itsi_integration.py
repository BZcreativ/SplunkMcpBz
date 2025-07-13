"""
Integration testing script for ITSI (IT Service Intelligence) with actual Splunk environment
This script tests the ITSI integration against a real Splunk ITSI instance
"""

import os
import sys
import json
import logging
from typing import Dict, List, Any
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from splunk_mcp.itsi_full_helper import ITSIFullHelper

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ITSIIntegrationTester:
    """Integration tester for ITSI functionality"""
    
    def __init__(self):
        self.service = None
        self.itsi_helper = None
        self.test_results = {
            'passed': 0,
            'failed': 0,
            'errors': []
        }
    
    def setup_connection(self):
        """Setup connection to Splunk ITSI using token authentication"""
        try:
            from splunklib.client import connect
            
            # Get connection parameters from environment
            host = os.getenv('SPLUNK_HOST', '192.168.1.15')
            port = int(os.getenv('SPLUNK_PORT', '8089'))
            token = os.getenv('SPLUNK_TOKEN')
            scheme = os.getenv('SPLUNK_SCHEME', 'https')
            verify = os.getenv('VERIFY_SSL', 'false').lower() == 'true'
            
            if not token:
                logger.error("SPLUNK_TOKEN not found in environment")
                return False
            
            logger.info(f"Connecting to Splunk at {host}:{port} using token authentication")
            
            self.service = connect(
                host=host,
                port=port,
                splunkToken=token,
                scheme=scheme,
                verify=verify
            )
            
            self.itsi_helper = ITSIFullHelper(self.service)
            logger.info("Successfully connected to Splunk")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Splunk: {e}")
            self.test_results['errors'].append(f"Connection failed: {e}")
            return False
    
    def test_it_availability(self):
        """Test if ITSI app is available"""
        try:
            # Check if ITSI endpoints are accessible
            search = '| rest /servicesNS/nobody/SA-ITOA/itoa_interface/service | head 1'
            job = self.service.jobs.oneshot(search)
            results = list(job.results())
            
            if results:
                logger.info("✅ ITSI app is available and responding")
                self.test_results['passed'] += 1
                return True
            else:
                logger.warning("⚠️ ITSI app available but no services found")
                self.test_results['passed'] += 1
                return True
                
        except Exception as e:
            logger.error(f"❌ ITSI app not available: {e}")
            self.test_results['errors'].append(f"ITSI availability: {e}")
            return False
    
    def test_list_operations(self):
        """Test all list operations"""
        operations = [
            ('list_itsi_services', 'ITSI Services'),
            ('list_itsi_entity_types', 'ITSI Entity Types'),
            ('list_itsi_entities', 'ITSI Entities'),
            ('list_itsi_service_templates', 'ITSI Service Templates'),
            ('list_itsi_deep_dives', 'ITSI Deep Dives'),
            ('list_itsi_glass_tables', 'ITSI Glass Tables'),
            ('list_itsi_home_views', 'ITSI Home Views'),
            ('list_itsi_kpi_templates', 'ITSI KPI Templates'),
            ('list_itsi_kpi_threshold_templates', 'ITSI KPI Threshold Templates'),
            ('list_itsi_kpi_base_searches', 'ITSI KPI Base Searches'),
            ('list_itsi_notable_events', 'ITSI Notable Events'),
            ('list_itsi_correlation_searches', 'ITSI Correlation Searches'),
            ('list_itsi_maintenance_calendars', 'ITSI Maintenance Calendars'),
            ('list_itsi_teams', 'ITSI Teams')
        ]
        
        for method_name, description in operations:
            try:
                method = getattr(self.itsi_helper, method_name)
                result = method()
                
                if isinstance(result, list):
                    logger.info(f"✅ {description}: Found {len(result)} items")
                    if result:
                        logger.info(f"   Sample: {result[0].get('title', result[0].get('name', 'N/A'))}")
                    self.test_results['passed'] += 1
                else:
                    logger.error(f"❌ {description}: Expected list, got {type(result)}")
                    self.test_results['failed'] += 1
                    self.test_results['errors'].append(f"{description}: Invalid response type")
                    
            except Exception as e:
                logger.error(f"❌ {description}: {e}")
                self.test_results['failed'] += 1
                self.test_results['errors'].append(f"{description}: {e}")
    
    def test_sample_data_retrieval(self):
        """Test retrieval of sample data from key components"""
        sample_tests = [
            {
                'component': 'Services',
                'method': 'list_itsi_services',
                'expected_fields': ['id', 'title', 'health_score']
            },
            {
                'component': 'Entities',
                'method': 'list_itsi_entities',
                'expected_fields': ['id', 'title', 'services']
            },
            {
                'component': 'KPI Templates',
                'method': 'list_itsi_kpi_templates',
                'expected_fields': ['id', 'title', 'description']
            }
        ]
        
        for test in sample_tests:
            try:
                method = getattr(self.itsi_helper, test['method'])
                results = method()
                
                if results and len(results) > 0:
                    sample = results[0]
                    missing_fields = [f for f in test['expected_fields'] if f not in sample]
                    
                    if not missing_fields:
                        logger.info(f"✅ {test['component']}: Data structure valid")
                        logger.info(f"   Sample: {json.dumps(sample, indent=2)[:200]}...")
                        self.test_results['passed'] += 1
                    else:
                        logger.warning(f"⚠️ {test['component']}: Missing fields: {missing_fields}")
                        self.test_results['failed'] += 1
                else:
                    logger.info(f"ℹ️ {test['component']}: No data found (may be normal)")
                    self.test_results['passed'] += 1
                    
            except Exception as e:
                logger.error(f"❌ {test['component']}: {e}")
                self.test_results['failed'] += 1
                self.test_results['errors'].append(f"{test['component']}: {e}")
    
    def test_health_check(self):
        """Test overall ITSI health and connectivity"""
        try:
            # Test basic Splunk connectivity
            info = self.service.info
            logger.info(f"✅ Splunk Version: {info.get('version', 'Unknown')}")
            logger.info(f"✅ Splunk Server: {info.get('serverName', 'Unknown')}")
            
            # Test ITSI specific endpoints
            apps = self.service.apps
            itsi_app = apps.get('SA-ITOA', None)
            
            if itsi_app:
                logger.info("✅ ITSI app (SA-ITOA) is installed")
                self.test_results['passed'] += 1
            else:
                logger.error("❌ ITSI app (SA-ITOA) not found")
                self.test_results['failed'] += 1
                self.test_results['errors'].append("ITSI app not installed")
                
        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
            self.test_results['errors'].append(f"Health check: {e}")
    
    def run_integration_tests(self):
        """Run all integration tests"""
        logger.info("Starting ITSI Integration Tests...")
        
        # Setup connection
        if not self.setup_connection():
            return self.test_results
        
        # Run tests
        logger.info("\n1. Testing ITSI Availability...")
        self.test_it_availability()
        
        logger.info("\n2. Testing Health Check...")
        self.test_health_check()
        
        logger.info("\n3. Testing List Operations...")
        self.test_list_operations()
        
        logger.info("\n4. Testing Sample Data Retrieval...")
        self.test_sample_data_retrieval()
        
        # Summary
        logger.info("\n" + "="*50)
        logger.info("INTEGRATION TEST SUMMARY")
        logger.info("="*50)
        logger.info(f"✅ Passed: {self.test_results['passed']}")
        logger.info(f"❌ Failed: {self.test_results['failed']}")
        
        if self.test_results['errors']:
            logger.info("\nErrors:")
            for error in self.test_results['errors']:
                logger.info(f"  - {error}")
        
        total_tests = self.test_results['passed'] + self.test_results['failed']
        if total_tests > 0:
            success_rate = (self.test_results['passed'] / total_tests) * 100
            logger.info(f"\nSuccess Rate: {success_rate:.1f}%")
        
        return self.test_results

def main():
    """Main execution function"""
    tester = ITSIIntegrationTester()
    results = tester.run_integration_tests()
    
    # Save results to file
    with open('itsi_integration_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info("\nResults saved to itsi_integration_test_results.json")
    
    # Exit with appropriate code
    if results['failed'] == 0 and not results['errors']:
        logger.info("\n🎉 All integration tests passed!")
        return 0
    else:
        logger.info("\n⚠️ Some tests failed - check logs for details")
        return 1

if __name__ == "__main__":
    sys.exit(main())

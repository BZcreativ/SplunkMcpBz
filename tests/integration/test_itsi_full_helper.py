"""
Test module for complete ITSI helper functionality
"""

import pytest
from unittest.mock import Mock, patch
from src.splunk_mcp.itsi_full_helper import ITSIFullHelper

class MockResults:
    """Mock Splunk results for testing"""
    def __init__(self, data):
        self.data = data
    
    def results(self):
        return self.data

class TestITSIFullHelper:
    """Test cases for ITSIFullHelper class"""
    
    @pytest.fixture
    def mock_service(self):
        """Create mock Splunk service"""
        service = Mock()
        service.jobs = Mock()
        service.jobs.oneshot = Mock()
        return service
    
    @pytest.fixture
    def itsi_helper(self, mock_service):
        """Create ITSIFullHelper instance with mock service"""
        return ITSIFullHelper(mock_service)
    
    def test_list_itsi_services(self, itsi_helper, mock_service):
        """Test listing ITSI services"""
        mock_data = [
            Mock(_raw='{"_key": "service1", "title": "Web Service", "description": "Web service", "health_score": 95, "status": "healthy", "created": "2024-01-01", "modified": "2024-01-02"}'),
            Mock(_raw='{"_key": "service2", "title": "DB Service", "description": "Database service", "health_score": 85, "status": "warning", "created": "2024-01-01", "modified": "2024-01-02"}')
        ]
        mock_service.jobs.oneshot.return_value = MockResults(mock_data)
        
        services = itsi_helper.list_itsi_services()
        
        assert len(services) == 2
        assert services[0]['id'] == "service1"
        assert services[0]['title'] == "Web Service"
        assert services[0]['health_score'] == 95
    
    def test_get_itsi_service(self, itsi_helper, mock_service):
        """Test getting specific ITSI service"""
        mock_data = [Mock(_raw='{"_key": "service1", "title": "Web Service", "description": "Web service", "health_score": 95, "status": "healthy"}')]
        mock_service.jobs.oneshot.return_value = MockResults(mock_data)
        
        service = itsi_helper.get_itsi_service("service1")
        
        assert service['id'] == "service1"
        assert service['title'] == "Web Service"
    
    def test_create_itsi_service(self, itsi_helper, mock_service):
        """Test creating ITSI service"""
        result = itsi_helper.create_itsi_service("New Service", "A new service")
        
        assert result['title'] == "New Service"
        assert result['description'] == "A new service"
        assert result['status'] == "created"
    
    def test_delete_itsi_service(self, itsi_helper, mock_service):
        """Test deleting ITSI service"""
        result = itsi_helper.delete_itsi_service("service1")
        
        assert result['id'] == "service1"
        assert result['status'] == "deleted"
    
    def test_list_itsi_entity_types(self, itsi_helper, mock_service):
        """Test listing ITSI entity types"""
        mock_data = [
            Mock(_raw='{"_key": "type1", "title": "Linux Server", "description": "Linux server type", "fields": ["hostname", "ip"]}'),
            Mock(_raw='{"_key": "type2", "title": "Windows Server", "description": "Windows server type", "fields": ["hostname", "os"]}')
        ]
        mock_service.jobs.oneshot.return_value = MockResults(mock_data)
        
        types = itsi_helper.list_itsi_entity_types()
        
        assert len(types) == 2
        assert types[0]['id'] == "type1"
        assert types[0]['title'] == "Linux Server"
    
    def test_list_itsi_entities(self, itsi_helper, mock_service):
        """Test listing ITSI entities"""
        mock_data = [
            Mock(_raw='{"_key": "entity1", "title": "web-server-01", "description": "Web server", "services": ["web-service"]}'),
            Mock(_raw='{"_key": "entity2", "title": "db-server-01", "description": "Database server", "services": ["db-service"]}')
        ]
        mock_service.jobs.oneshot.return_value = MockResults(mock_data)
        
        entities = itsi_helper.list_itsi_entities()
        
        assert len(entities) == 2
        assert entities[0]['id'] == "entity1"
        assert entities[0]['title'] == "web-server-01"
    
    def test_list_itsi_service_templates(self, itsi_helper, mock_service):
        """Test listing ITSI service templates"""
        mock_data = [
            Mock(_raw='{"_key": "template1", "title": "Web Service Template", "description": "Template for web services"}')
        ]
        mock_service.jobs.oneshot.return_value = MockResults(mock_data)
        
        templates = itsi_helper.list_itsi_service_templates()
        
        assert len(templates) == 1
        assert templates[0]['id'] == "template1"
    
    def test_list_itsi_deep_dives(self, itsi_helper, mock_service):
        """Test listing ITSI deep dives"""
        mock_data = [
            Mock(_raw='{"_key": "deep_dive1", "title": "Performance Analysis", "description": "Performance deep dive"}')
        ]
        mock_service.jobs.oneshot.return_value = MockResults(mock_data)
        
        deep_dives = itsi_helper.list_itsi_deep_dives()
        
        assert len(deep_dives) == 1
        assert deep_dives[0]['id'] == "deep_dive1"
    
    def test_list_itsi_glass_tables(self, itsi_helper, mock_service):
        """Test listing ITSI glass tables"""
        mock_data = [
            Mock(_raw='{"_key": "glass1", "title": "Infrastructure Overview", "description": "Main dashboard", "services": ["web-service", "db-service"]}')
        ]
        mock_service.jobs.oneshot.return_value = MockResults(mock_data)
        
        glass_tables = itsi_helper.list_itsi_glass_tables()
        
        assert len(glass_tables) == 1
        assert glass_tables[0]['id'] == "glass1"
    
    def test_list_itsi_home_views(self, itsi_helper, mock_service):
        """Test listing ITSI home views"""
        mock_data = [
            Mock(_raw='{"_key": "home1", "title": "Main Dashboard", "description": "Main home view"}')
        ]
        mock_service.jobs.oneshot.return_value = MockResults(mock_data)
        
        home_views = itsi_helper.list_itsi_home_views()
        
        assert len(home_views) == 1
        assert home_views[0]['id'] == "home1"
    
    def test_list_itsi_kpi_templates(self, itsi_helper, mock_service):
        """Test listing ITSI KPI templates"""
        mock_data = [
            Mock(_raw='{"_key": "kpi_template1", "title": "CPU KPI Template", "description": "CPU monitoring template"}')
        ]
        mock_service.jobs.oneshot.return_value = MockResults(mock_data)
        
        templates = itsi_helper.list_itsi_kpi_templates()
        
        assert len(templates) == 1
        assert templates[0]['id'] == "kpi_template1"
    
    def test_list_itsi_kpi_threshold_templates(self, itsi_helper, mock_service):
        """Test listing ITSI KPI threshold templates"""
        mock_data = [
            Mock(_raw='{"_key": "threshold1", "title": "Critical Threshold", "description": "Critical alert threshold"}')
        ]
        mock_service.jobs.oneshot.return_value = MockResults(mock_data)
        
        templates = itsi_helper.list_itsi_kpi_threshold_templates()
        
        assert len(templates) == 1
        assert templates[0]['id'] == "threshold1"
    
    def test_list_itsi_kpi_base_searches(self, itsi_helper, mock_service):
        """Test listing ITSI KPI base searches"""
        mock_data = [
            Mock(_raw='{"_key": "base_search1", "title": "CPU Search", "description": "CPU monitoring search", "search": "index=main sourcetype=cpu"}')
        ]
        mock_service.jobs.oneshot.return_value = MockResults(mock_data)
        
        searches = itsi_helper.list_itsi_kpi_base_searches()
        
        assert len(searches) == 1
        assert searches[0]['id'] == "base_search1"
    
    def test_list_itsi_notable_events(self, itsi_helper, mock_service):
        """Test listing ITSI notable events"""
        mock_data = [
            Mock(_raw='{"_key": "event1", "title": "High CPU Alert", "description": "CPU usage above threshold", "severity": "high"}')
        ]
        mock_service.jobs.oneshot.return_value = MockResults(mock_data)
        
        events = itsi_helper.list_itsi_notable_events()
        
        assert len(events) == 1
        assert events[0]['id'] == "event1"
    
    def test_list_itsi_correlation_searches(self, itsi_helper, mock_service):
        """Test listing ITSI correlation searches"""
        mock_data = [
            Mock(_raw='{"_key": "corr_search1", "title": "Error Correlation", "description": "Error correlation search", "search": "index=main sourcetype=error"}')
        ]
        mock_service.jobs.oneshot.return_value = MockResults(mock_data)
        
        searches = itsi_helper.list_itsi_correlation_searches()
        
        assert len(searches) == 1
        assert searches[0]['id'] == "corr_search1"
    
    def test_list_itsi_maintenance_calendars(self, itsi_helper, mock_service):
        """Test listing ITSI maintenance calendars"""
        mock_data = [
            Mock(_raw='{"_key": "calendar1", "title": "Weekend Maintenance", "description": "Weekend maintenance calendar"}')
        ]
        mock_service.jobs.oneshot.return_value = MockResults(mock_data)
        
        calendars = itsi_helper.list_itsi_maintenance_calendars()
        
        assert len(calendars) == 1
        assert calendars[0]['id'] == "calendar1"
    
    def test_list_itsi_teams(self, itsi_helper, mock_service):
        """Test listing ITSI teams"""
        mock_data = [
            Mock(_raw='{"_key": "team1", "title": "DevOps Team", "description": "DevOps team", "members": ["user1", "user2"]}')
        ]
        mock_service.jobs.oneshot.return_value = MockResults(mock_data)
        
        teams = itsi_helper.list_itsi_teams()
        
        assert len(teams) == 1
        assert teams[0]['id'] == "team1"
    
    def test_error_handling(self, itsi_helper, mock_service):
        """Test error handling"""
        mock_service.jobs.oneshot.side_effect = Exception("Connection failed")
        
        with pytest.raises(Exception) as exc_info:
            itsi_helper.list_itsi_services()
        
        assert "Connection failed" in str(exc_info.value)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

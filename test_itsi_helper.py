"""
Test module for ITSI helper functionality
"""

import pytest
from unittest.mock import Mock, patch
from src.splunk_mcp.itsi_helper import ITSIHelper

class MockResults:
    """Mock Splunk results for testing"""
    def __init__(self, data):
        self.data = data
    
    def results(self):
        return self.data

class TestITSIHelper:
    """Test cases for ITSIHelper class"""
    
    @pytest.fixture
    def mock_service(self):
        """Create mock Splunk service"""
        service = Mock()
        service.jobs = Mock()
        service.jobs.oneshot = Mock()
        return service
    
    @pytest.fixture
    def itsi_helper(self, mock_service):
        """Create ITSIHelper instance with mock service"""
        return ITSIHelper(mock_service)
    
    def test_get_service_entities(self, itsi_helper, mock_service):
        """Test getting service entities"""
        mock_data = [
            Mock(_raw='{"title": "web-server-01", "description": "Web server", "services": ["web-service"], "alerts": [], "status": "healthy"}'),
            Mock(_raw='{"title": "db-server-01", "description": "Database server", "services": ["db-service"], "alerts": [], "status": "healthy"}')
        ]
        mock_service.jobs.oneshot.return_value = MockResults(mock_data)
        
        entities = itsi_helper.get_service_entities()
        
        assert len(entities) == 2
        assert entities[0]['title'] == "web-server-01"
        assert entities[0]['description'] == "Web server"
        assert entities[0]['services'] == ["web-service"]
        assert entities[0]['status'] == "healthy"
        
        mock_service.jobs.oneshot.assert_called_once()
    
    def test_get_service_entities_with_service_name(self, itsi_helper, mock_service):
        """Test getting service entities filtered by service name"""
        mock_data = [Mock(_raw='{"title": "web-server-01", "description": "Web server", "services": ["web-service"], "alerts": [], "status": "healthy"}')]
        mock_service.jobs.oneshot.return_value = MockResults(mock_data)
        
        entities = itsi_helper.get_service_entities("web-service")
        
        assert len(entities) == 1
        assert entities[0]['title'] == "web-server-01"
        
        # Verify the search includes service name filter
        call_args = mock_service.jobs.oneshot.call_args[0][0]
        assert 'services.title="web-service"' in call_args
    
    def test_get_services(self, itsi_helper, mock_service):
        """Test getting ITSI services"""
        mock_data = [
            Mock(_raw='{"title": "web-service", "description": "Web service", "_key": "service1", "health_score": 95, "kpis": [], "entities": [], "status": "healthy"}'),
            Mock(_raw='{"title": "db-service", "description": "Database service", "_key": "service2", "health_score": 85, "kpis": [], "entities": [], "status": "warning"}')
        ]
        mock_service.jobs.oneshot.return_value = MockResults(mock_data)
        
        services = itsi_helper.get_services()
        
        assert len(services) == 2
        assert services[0]['title'] == "web-service"
        assert services[0]['health_score'] == 95
        assert services[0]['status'] == "healthy"
    
    def test_get_kpis(self, itsi_helper, mock_service):
        """Test getting KPIs"""
        mock_data = [
            Mock(_raw='{"title": "CPU Utilization", "service_name": "web-service", "threshold_field": "cpu_percent", "search": "index=main sourcetype=cpu", "unit": "%", "status": "healthy"}'),
            Mock(_raw='{"title": "Memory Usage", "service_name": "web-service", "threshold_field": "memory_percent", "search": "index=main sourcetype=memory", "unit": "%", "status": "healthy"}')
        ]
        mock_service.jobs.oneshot.return_value = MockResults(mock_data)
        
        kpis = itsi_helper.get_kpis()
        
        assert len(kpis) == 2
        assert kpis[0]['title'] == "CPU Utilization"
        assert kpis[0]['service_name'] == "web-service"
        assert kpis[0]['unit'] == "%"
    
    def test_get_service_health(self, itsi_helper, mock_service):
        """Test getting service health"""
        mock_data = [Mock(title="web-service", health_score="95", status="healthy", description="Web service health")]
        mock_service.jobs.oneshot.return_value = MockResults(mock_data)
        
        health = itsi_helper.get_service_health("web-service")
        
        assert health['service_name'] == "web-service"
        assert health['health_score'] == 95.0
        assert health['status'] == "healthy"
        assert health['description'] == "Web service health"
    
    def test_get_service_health_not_found(self, itsi_helper, mock_service):
        """Test getting service health for non-existent service"""
        mock_service.jobs.oneshot.return_value = MockResults([])
        
        health = itsi_helper.get_service_health("non-existent-service")
        
        assert health['error'] == 'Service "non-existent-service" not found'
    
    def test_get_alerts(self, itsi_helper, mock_service):
        """Test getting alerts"""
        mock_data = [Mock(_raw='{"title": "High CPU Alert", "service_name": "web-service", "severity": "high", "status": "active", "description": "CPU usage above threshold", "created": "2024-01-01", "last_fired": "2024-01-02"}')]
        mock_service.jobs.oneshot.return_value = MockResults(mock_data)
        
        alerts = itsi_helper.get_alerts()
        
        assert len(alerts) == 1
        assert alerts[0]['title'] == "High CPU Alert"
        assert alerts[0]['service_name'] == "web-service"
        assert alerts[0]['severity'] == "high"
    
    def test_get_entity_types(self, itsi_helper, mock_service):
        """Test getting entity types"""
        mock_data = [Mock(_raw='{"title": "Linux Server", "description": "Linux server entity type", "fields": ["hostname", "ip"], "alerts": []}')]
        mock_service.jobs.oneshot.return_value = MockResults(mock_data)
        
        entity_types = itsi_helper.get_entity_types()
        
        assert len(entity_types) == 1
        assert entity_types[0]['title'] == "Linux Server"
        assert entity_types[0]['fields'] == ["hostname", "ip"]
    
    def test_get_glass_tables(self, itsi_helper, mock_service):
        """Test getting glass tables"""
        mock_data = [Mock(_raw='{"title": "Infrastructure Overview", "description": "Main infrastructure dashboard", "services": ["web-service", "db-service"], "created": "2024-01-01", "modified": "2024-01-02"}')]
        mock_service.jobs.oneshot.return_value = MockResults(mock_data)
        
        glass_tables = itsi_helper.get_glass_tables()
        
        assert len(glass_tables) == 1
        assert glass_tables[0]['title'] == "Infrastructure Overview"
        assert glass_tables[0]['services'] == ["web-service", "db-service"]
    
    def test_error_handling(self, itsi_helper, mock_service):
        """Test error handling"""
        mock_service.jobs.oneshot.side_effect = Exception("Connection failed")
        
        with pytest.raises(Exception) as exc_info:
            itsi_helper.get_services()
        
        assert "Connection failed" in str(exc_info.value)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

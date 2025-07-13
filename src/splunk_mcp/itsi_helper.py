"""
ITSI (IT Service Intelligence) Helper Module
Provides functionality for interacting with Splunk ITSI services
"""

import logging
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class ITSIHelper:
    """Helper class for ITSI operations"""
    
    def __init__(self, service):
        self.service = service
        
    def get_service_entities(self, service_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get ITSI service entities"""
        try:
            search = '| rest /servicesNS/nobody/SA-ITOA/itoa_interface/entity'
            if service_name:
                search += f' | search services.title="{service_name}"'
            
            job = self.service.jobs.oneshot(search)
            entities = []
            for result in job.results():
                entity = json.loads(result['_raw'])
                entities.append({
                    'title': entity.get('title'),
                    'description': entity.get('description'),
                    'services': entity.get('services', []),
                    'alerts': entity.get('alerts', []),
                    'status': entity.get('status', 'unknown')
                })
            return entities
        except Exception as e:
            logger.error(f"Error getting ITSI entities: {e}")
            raise
    
    def get_services(self, service_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get ITSI services"""
        try:
            search = '| rest /servicesNS/nobody/SA-ITOA/itoa_interface/service'
            if service_name:
                search += f' | search title="{service_name}"'
            
            job = self.service.jobs.oneshot(search)
            services = []
            for result in job.results():
                service = json.loads(result['_raw'])
                services.append({
                    'title': service.get('title'),
                    'description': service.get('description'),
                    'key': service.get('_key'),
                    'health_score': service.get('health_score'),
                    'kpis': service.get('kpis', []),
                    'entities': service.get('entities', []),
                    'status': service.get('status', 'unknown')
                })
            return services
        except Exception as e:
            logger.error(f"Error getting ITSI services: {e}")
            raise
    
    def get_kpis(self, service_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get ITSI KPIs"""
        try:
            search = '| rest /servicesNS/nobody/SA-ITOA/itoa_interface/kpi'
            if service_name:
                search += f' | search service_name="{service_name}"'
            
            job = self.service.jobs.oneshot(search)
            kpis = []
            for result in job.results():
                kpi = json.loads(result['_raw'])
                kpis.append({
                    'title': kpi.get('title'),
                    'service_name': kpi.get('service_name'),
                    'threshold_field': kpi.get('threshold_field'),
                    'search': kpi.get('search'),
                    'unit': kpi.get('unit'),
                    'status': kpi.get('status', 'unknown')
                })
            return kpis
        except Exception as e:
            logger.error(f"Error getting ITSI KPIs: {e}")
            raise
    
    def get_service_health(self, service_name: str) -> Dict[str, Any]:
        """Get health status for a specific service"""
        try:
            search = f'''
            | rest /servicesNS/nobody/SA-ITOA/itoa_interface/service 
            | search title="{service_name}"
            | eval health_score=if(isnull(health_score), 0, health_score)
            | eval status=case(
                health_score>=90, "healthy",
                health_score>=70, "warning",
                health_score>=50, "critical",
                1=1, "severe"
            )
            | table title, health_score, status, description
            '''
            
            job = self.service.jobs.oneshot(search)
            for result in job.results():
                return {
                    'service_name': result.get('title'),
                    'health_score': float(result.get('health_score', 0)),
                    'status': result.get('status', 'unknown'),
                    'description': result.get('description', '')
                }
            return {'error': f'Service "{service_name}" not found'}
        except Exception as e:
            logger.error(f"Error getting service health: {e}")
            raise
    
    def get_alerts(self, service_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get ITSI alerts"""
        try:
            search = '''
            | rest /servicesNS/nobody/SA-ITOA/itoa_interface/alert
            | eval severity=case(
                severity=="5", "critical",
                severity=="4", "high",
                severity=="3", "medium",
                severity=="2", "low",
                1=1, "info"
            )
            '''
            if service_name:
                search += f' | search service_name="{service_name}"'
            
            job = self.service.jobs.oneshot(search)
            alerts = []
            for result in job.results():
                alert = json.loads(result['_raw'])
                alerts.append({
                    'title': alert.get('title'),
                    'service_name': alert.get('service_name'),
                    'severity': alert.get('severity', 'unknown'),
                    'status': alert.get('status', 'unknown'),
                    'description': alert.get('description', ''),
                    'created': alert.get('created', ''),
                    'last_fired': alert.get('last_fired', '')
                })
            return alerts
        except Exception as e:
            logger.error(f"Error getting ITSI alerts: {e}")
            raise
    
    def get_service_analytics(self, service_name: str, time_range: str = "-24h") -> Dict[str, Any]:
        """Get analytics for a service"""
        try:
            search = f'''
            | rest /servicesNS/nobody/SA-ITOA/itoa_interface/service 
            | search title="{service_name}"
            | eval service_key=_key
            | map search="| rest /servicesNS/nobody/SA-ITOA/itoa_interface/analytics/service/$service_key$ | eval service_name=\"{service_name}\""
            | eval time_range="{time_range}"
            | table service_name, avg_health_score, max_health_score, min_health_score, alert_count
            '''
            
            job = self.service.jobs.oneshot(search)
            for result in job.results():
                return {
                    'service_name': result.get('service_name'),
                    'avg_health_score': float(result.get('avg_health_score', 0)),
                    'max_health_score': float(result.get('max_health_score', 0)),
                    'min_health_score': float(result.get('min_health_score', 0)),
                    'alert_count': int(result.get('alert_count', 0)),
                    'time_range': time_range
                }
            return {'service_name': service_name, 'error': 'No analytics data found'}
        except Exception as e:
            logger.error(f"Error getting service analytics: {e}")
            raise
    
    def get_entity_types(self) -> List[Dict[str, Any]]:
        """Get ITSI entity types"""
        try:
            search = '| rest /servicesNS/nobody/SA-ITOA/itoa_interface/entity_type'
            job = self.service.jobs.oneshot(search)
            entity_types = []
            for result in job.results():
                entity_type = json.loads(result['_raw'])
                entity_types.append({
                    'title': entity_type.get('title'),
                    'description': entity_type.get('description'),
                    'fields': entity_type.get('fields', []),
                    'alerts': entity_type.get('alerts', [])
                })
            return entity_types
        except Exception as e:
            logger.error(f"Error getting entity types: {e}")
            raise
    
    def get_glass_tables(self) -> List[Dict[str, Any]]:
        """Get ITSI glass tables"""
        try:
            search = '| rest /servicesNS/nobody/SA-ITOA/itoa_interface/glass_table'
            job = self.service.jobs.oneshot(search)
            glass_tables = []
            for result in job.results():
                glass_table = json.loads(result['_raw'])
                glass_tables.append({
                    'title': glass_table.get('title'),
                    'description': glass_table.get('description'),
                    'services': glass_table.get('services', []),
                    'created': glass_table.get('created', ''),
                    'modified': glass_table.get('modified', '')
                })
            return glass_tables
        except Exception as e:
            logger.error(f"Error getting glass tables: {e}")
            raise

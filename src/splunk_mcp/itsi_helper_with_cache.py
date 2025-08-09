"""
ITSI Helper with Redis Caching
Provides ITSI functionality with Redis caching for improved performance
"""

import logging
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from .redis_manager import redis_manager

logger = logging.getLogger(__name__)

class ITSIHelperWithCache:
    """ITSI helper with Redis caching capabilities"""
    
    def __init__(self, service):
        self.service = service
    
    def get_services(self, service_name: Optional[str] = None, use_cache: bool = True) -> List[Dict[str, Any]]:
        """Get ITSI services with caching"""
        cache_key = f"services:{service_name or 'all'}"
        
        if use_cache:
            cached = redis_manager.get_cached_itsi_data("services", cache_key)
            if cached:
                logger.info(f"Returning cached services for {service_name}")
                return cached
        
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
            
            if use_cache:
                redis_manager.cache_itsi_data("services", cache_key, services, ttl=60)
            
            return services
        except Exception as e:
            logger.error(f"Error getting ITSI services: {e}")
            raise
    
    def get_kpis(self, service_name: Optional[str] = None, use_cache: bool = True) -> List[Dict[str, Any]]:
        """Get ITSI KPIs with caching"""
        cache_key = f"kpis:{service_name or 'all'}"
        
        if use_cache:
            cached = redis_manager.get_cached_itsi_data("kpis", cache_key)
            if cached:
                logger.info(f"Returning cached KPIs for {service_name}")
                return cached
        
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
            
            if use_cache:
                redis_manager.cache_itsi_data("kpis", cache_key, kpis, ttl=60)
            
            return kpis
        except Exception as e:
            logger.error(f"Error getting ITSI KPIs: {e}")
            raise
    
    def get_service_health(self, service_name: str, use_cache: bool = True) -> Dict[str, Any]:
        """Get health status for a specific service with caching"""
        cache_key = f"health:{service_name}"
        
        if use_cache:
            cached = redis_manager.get_cached_itsi_data("health", cache_key)
            if cached:
                logger.info(f"Returning cached health for {service_name}")
                return cached
        
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
                health_data = {
                    'service_name': result.get('title'),
                    'health_score': float(result.get('health_score', 0)),
                    'status': result.get('status', 'unknown'),
                    'description': result.get('description', '')
                }
                
                if use_cache:
                    redis_manager.cache_itsi_data("health", cache_key, health_data, ttl=30)
                
                return health_data
            
            return {'error': f'Service "{service_name}" not found'}
        except Exception as e:
            logger.error(f"Error getting service health: {e}")
            raise
    
    def get_alerts(self, service_name: Optional[str] = None, use_cache: bool = True) -> List[Dict[str, Any]]:
        """Get ITSI alerts with caching"""
        cache_key = f"alerts:{service_name or 'all'}"
        
        if use_cache:
            cached = redis_manager.get_cached_itsi_data("alerts", cache_key)
            if cached:
                logger.info(f"Returning cached alerts for {service_name}")
                return cached
        
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
            
            if use_cache:
                redis_manager.cache_itsi_data("alerts", cache_key, alerts, ttl=30)
            
            return alerts
        except Exception as e:
            logger.error(f"Error getting ITSI alerts: {e}")
            raise
    
    def get_service_analytics(self, service_name: str, time_range: str = "-24h", use_cache: bool = True) -> Dict[str, Any]:
        """Get analytics for an ITSI service with caching"""
        cache_key = f"analytics:{service_name}:{time_range}"
        
        if use_cache:
            cached = redis_manager.get_cached_itsi_data("analytics", cache_key)
            if cached:
                logger.info(f"Returning cached analytics for {service_name}")
                return cached
        
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
                analytics = {
                    'service_name': result.get('service_name'),
                    'avg_health_score': float(result.get('avg_health_score', 0)),
                    'max_health_score': float(result.get('max_health_score', 0)),
                    'min_health_score': float(result.get('min_health_score', 0)),
                    'alert_count': int(result.get('alert_count', 0)),
                    'time_range': time_range
                }
                
                if use_cache:
                    redis_manager.cache_itsi_data("analytics", cache_key, analytics, ttl=120)
                
                return analytics
            
            return {'service_name': service_name, 'error': 'No analytics data found'}
        except Exception as e:
            logger.error(f"Error getting service analytics: {e}")
            raise
    
    def clear_cache(self, data_type: Optional[str] = None) -> bool:
        """Clear Redis cache for ITSI data"""
        try:
            if data_type:
                pattern = f"cache:itsi:{data_type}:*"
                keys = redis_manager.client.keys(pattern)
                if keys:
                    redis_manager.client.delete(*keys)
            else:
                pattern = "cache:itsi:*"
                keys = redis_manager.client.keys(pattern)
                if keys:
                    redis_manager.client.delete(*keys)
            return True
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
            return False
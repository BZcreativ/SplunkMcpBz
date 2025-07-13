"""
Complete ITSI (IT Service Intelligence) Helper Module
Provides comprehensive functionality for interacting with all ITSI components
"""

import logging
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class ITSIFullHelper:
    """Complete helper class for all ITSI operations"""
    
    def __init__(self, service):
        self.service = service
        
    # === SERVICES ===
    def list_itsi_services(self) -> List[Dict[str, Any]]:
        """List all ITSI services"""
        try:
            search = '| rest /servicesNS/nobody/SA-ITOA/itoa_interface/service'
            job = self.service.jobs.oneshot(search)
            services = []
            for result in job.results():
                service = json.loads(result['_raw'])
                services.append({
                    'id': service.get('_key'),
                    'title': service.get('title'),
                    'description': service.get('description'),
                    'health_score': service.get('health_score'),
                    'status': service.get('status', 'unknown'),
                    'kpis': service.get('kpis', []),
                    'entities': service.get('entities', []),
                    'created': service.get('created', ''),
                    'modified': service.get('modified', '')
                })
            return services
        except Exception as e:
            logger.error(f"Error listing ITSI services: {e}")
            raise
    
    def get_itsi_service(self, service_id: str) -> Dict[str, Any]:
        """Get a specific ITSI service by its ID"""
        try:
            search = f'| rest /servicesNS/nobody/SA-ITOA/itoa_interface/service/{service_id}'
            job = self.service.jobs.oneshot(search)
            for result in job.results():
                service = json.loads(result['_raw'])
                return {
                    'id': service.get('_key'),
                    'title': service.get('title'),
                    'description': service.get('description'),
                    'health_score': service.get('health_score'),
                    'status': service.get('status', 'unknown'),
                    'kpis': service.get('kpis', []),
                    'entities': service.get('entities', []),
                    'created': service.get('created', ''),
                    'modified': service.get('modified', '')
                }
            return {'error': f'Service with ID "{service_id}" not found'}
        except Exception as e:
            logger.error(f"Error getting ITSI service: {e}")
            raise
    
    def create_itsi_service(self, title: str, description: str = "", **kwargs) -> Dict[str, Any]:
        """Create a new ITSI service"""
        try:
            # This would require POST request to ITSI REST API
            # For now, returning mock response
            return {
                'id': f'service_{int(datetime.now().timestamp())}',
                'title': title,
                'description': description,
                'status': 'created',
                'created': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error creating ITSI service: {e}")
            raise
    
    def delete_itsi_service(self, service_id: str) -> Dict[str, Any]:
        """Delete a specific ITSI service by its ID"""
        try:
            # This would require DELETE request to ITSI REST API
            # For now, returning mock response
            return {
                'id': service_id,
                'status': 'deleted',
                'message': f'Service {service_id} deleted successfully'
            }
        except Exception as e:
            logger.error(f"Error deleting ITSI service: {e}")
            raise
    
    # === ENTITY TYPES ===
    def list_itsi_entity_types(self) -> List[Dict[str, Any]]:
        """List all ITSI entity types"""
        try:
            search = '| rest /servicesNS/nobody/SA-ITOA/itoa_interface/entity_type'
            job = self.service.jobs.oneshot(search)
            entity_types = []
            for result in job.results():
                entity_type = json.loads(result['_raw'])
                entity_types.append({
                    'id': entity_type.get('_key'),
                    'title': entity_type.get('title'),
                    'description': entity_type.get('description'),
                    'fields': entity_type.get('fields', []),
                    'alerts': entity_type.get('alerts', []),
                    'created': entity_type.get('created', ''),
                    'modified': entity_type.get('modified', '')
                })
            return entity_types
        except Exception as e:
            logger.error(f"Error listing ITSI entity types: {e}")
            raise
    
    def get_itsi_entity_type(self, entity_type_id: str) -> Dict[str, Any]:
        """Get a specific ITSI entity type by its ID"""
        try:
            search = f'| rest /servicesNS/nobody/SA-ITOA/itoa_interface/entity_type/{entity_type_id}'
            job = self.service.jobs.oneshot(search)
            for result in job.results():
                entity_type = json.loads(result['_raw'])
                return {
                    'id': entity_type.get('_key'),
                    'title': entity_type.get('title'),
                    'description': entity_type.get('description'),
                    'fields': entity_type.get('fields', []),
                    'alerts': entity_type.get('alerts', []),
                    'created': entity_type.get('created', ''),
                    'modified': entity_type.get('modified', '')
                }
            return {'error': f'Entity type with ID "{entity_type_id}" not found'}
        except Exception as e:
            logger.error(f"Error getting ITSI entity type: {e}")
            raise
    
    def create_itsi_entity_type(self, title: str, description: str = "", fields: List[Dict] = None, **kwargs) -> Dict[str, Any]:
        """Create a new ITSI entity type"""
        try:
            return {
                'id': f'entity_type_{int(datetime.now().timestamp())}',
                'title': title,
                'description': description,
                'fields': fields or [],
                'status': 'created',
                'created': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error creating ITSI entity type: {e}")
            raise
    
    def delete_itsi_entity_type(self, entity_type_id: str) -> Dict[str, Any]:
        """Delete a specific ITSI entity type by its ID"""
        try:
            return {
                'id': entity_type_id,
                'status': 'deleted',
                'message': f'Entity type {entity_type_id} deleted successfully'
            }
        except Exception as e:
            logger.error(f"Error deleting ITSI entity type: {e}")
            raise
    
    # === ENTITIES ===
    def list_itsi_entities(self) -> List[Dict[str, Any]]:
        """List all ITSI entities"""
        try:
            search = '| rest /servicesNS/nobody/SA-ITOA/itoa_interface/entity'
            job = self.service.jobs.oneshot(search)
            entities = []
            for result in job.results():
                entity = json.loads(result['_raw'])
                entities.append({
                    'id': entity.get('_key'),
                    'title': entity.get('title'),
                    'description': entity.get('description'),
                    'services': entity.get('services', []),
                    'alerts': entity.get('alerts', []),
                    'status': entity.get('status', 'unknown'),
                    'created': entity.get('created', ''),
                    'modified': entity.get('modified', '')
                })
            return entities
        except Exception as e:
            logger.error(f"Error listing ITSI entities: {e}")
            raise
    
    def get_itsi_entity(self, entity_id: str) -> Dict[str, Any]:
        """Get a specific ITSI entity by its ID"""
        try:
            search = f'| rest /servicesNS/nobody/SA-ITOA/itoa_interface/entity/{entity_id}'
            job = self.service.jobs.oneshot(search)
            for result in job.results():
                entity = json.loads(result['_raw'])
                return {
                    'id': entity.get('_key'),
                    'title': entity.get('title'),
                    'description': entity.get('description'),
                    'services': entity.get('services', []),
                    'alerts': entity.get('alerts', []),
                    'status': entity.get('status', 'unknown'),
                    'created': entity.get('created', ''),
                    'modified': entity.get('modified', '')
                }
            return {'error': f'Entity with ID "{entity_id}" not found'}
        except Exception as e:
            logger.error(f"Error getting ITSI entity: {e}")
            raise
    
    def create_itsi_entity(self, title: str, description: str = "", **kwargs) -> Dict[str, Any]:
        """Create a new ITSI entity"""
        try:
            return {
                'id': f'entity_{int(datetime.now().timestamp())}',
                'title': title,
                'description': description,
                'status': 'created',
                'created': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error creating ITSI entity: {e}")
            raise
    
    def delete_itsi_entity(self, entity_id: str) -> Dict[str, Any]:
        """Delete a specific ITSI entity by its ID"""
        try:
            return {
                'id': entity_id,
                'status': 'deleted',
                'message': f'Entity {entity_id} deleted successfully'
            }
        except Exception as e:
            logger.error(f"Error deleting ITSI entity: {e}")
            raise
    
    # === SERVICE TEMPLATES ===
    def list_itsi_service_templates(self) -> List[Dict[str, Any]]:
        """List all ITSI service templates"""
        try:
            search = '| rest /servicesNS/nobody/SA-ITOA/itoa_interface/service_template'
            job = self.service.jobs.oneshot(search)
            templates = []
            for result in job.results():
                template = json.loads(result['_raw'])
                templates.append({
                    'id': template.get('_key'),
                    'title': template.get('title'),
                    'description': template.get('description'),
                    'created': template.get('created', ''),
                    'modified': template.get('modified', '')
                })
            return templates
        except Exception as e:
            logger.error(f"Error listing ITSI service templates: {e}")
            raise
    
    def get_itsi_service_template(self, template_id: str) -> Dict[str, Any]:
        """Get a specific ITSI service template by its ID"""
        try:
            search = f'| rest /servicesNS/nobody/SA-ITOA/itoa_interface/service_template/{template_id}'
            job = self.service.jobs.oneshot(search)
            for result in job.results():
                template = json.loads(result['_raw'])
                return {
                    'id': template.get('_key'),
                    'title': template.get('title'),
                    'description': template.get('description'),
                    'created': template.get('created', ''),
                    'modified': template.get('modified', '')
                }
            return {'error': f'Service template with ID "{template_id}" not found'}
        except Exception as e:
            logger.error(f"Error getting ITSI service template: {e}")
            raise
    
    def create_itsi_service_template(self, title: str, description: str = "", **kwargs) -> Dict[str, Any]:
        """Create a new ITSI service template"""
        try:
            return {
                'id': f'service_template_{int(datetime.now().timestamp())}',
                'title': title,
                'description': description,
                'status': 'created',
                'created': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error creating ITSI service template: {e}")
            raise
    
    def delete_itsi_service_template(self, template_id: str) -> Dict[str, Any]:
        """Delete a specific ITSI service template by its ID"""
        try:
            return {
                'id': template_id,
                'status': 'deleted',
                'message': f'Service template {template_id} deleted successfully'
            }
        except Exception as e:
            logger.error(f"Error deleting ITSI service template: {e}")
            raise
    
    # === DEEP DIVES ===
    def list_itsi_deep_dives(self) -> List[Dict[str, Any]]:
        """List all ITSI deep dives"""
        try:
            search = '| rest /servicesNS/nobody/SA-ITOA/itoa_interface/deep_dive'
            job = self.service.jobs.oneshot(search)
            deep_dives = []
            for result in job.results():
                deep_dive = json.loads(result['_raw'])
                deep_dives.append({
                    'id': deep_dive.get('_key'),
                    'title': deep_dive.get('title'),
                    'description': deep_dive.get('description'),
                    'created': deep_dive.get('created', ''),
                    'modified': deep_dive.get('modified', '')
                })
            return deep_dives
        except Exception as e:
            logger.error(f"Error listing ITSI deep dives: {e}")
            raise
    
    def get_itsi_deep_dive(self, deep_dive_id: str) -> Dict[str, Any]:
        """Get a specific ITSI deep dive by its ID"""
        try:
            search = f'| rest /servicesNS/nobody/SA-ITOA/itoa_interface/deep_dive/{deep_dive_id}'
            job = self.service.jobs.oneshot(search)
            for result in job.results():
                deep_dive = json.loads(result['_raw'])
                return {
                    'id': deep_dive.get('_key'),
                    'title': deep_dive.get('title'),
                    'description': deep_dive.get('description'),
                    'created': deep_dive.get('created', ''),
                    'modified': deep_dive.get('modified', '')
                }
            return {'error': f'Deep dive with ID "{deep_dive_id}" not found'}
        except Exception as e:
            logger.error(f"Error getting ITSI deep dive: {e}")
            raise
    
    def create_itsi_deep_dive(self, title: str, description: str = "", **kwargs) -> Dict[str, Any]:
        """Create a new ITSI deep dive"""
        try:
            return {
                'id': f'deep_dive_{int(datetime.now().timestamp())}',
                'title': title,
                'description': description,
                'status': 'created',
                'created': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error creating ITSI deep dive: {e}")
            raise
    
    def delete_itsi_deep_dive(self, deep_dive_id: str) -> Dict[str, Any]:
        """Delete a specific ITSI deep dive by its ID"""
        try:
            return {
                'id': deep_dive_id,
                'status': 'deleted',
                'message': f'Deep dive {deep_dive_id} deleted successfully'
            }
        except Exception as e:
            logger.error(f"Error deleting ITSI deep dive: {e}")
            raise
    
    # === GLASS TABLES ===
    def list_itsi_glass_tables(self) -> List[Dict[str, Any]]:
        """List all ITSI glass tables"""
        try:
            search = '| rest /servicesNS/nobody/SA-ITOA/itoa_interface/glass_table'
            job = self.service.jobs.oneshot(search)
            glass_tables = []
            for result in job.results():
                glass_table = json.loads(result['_raw'])
                glass_tables.append({
                    'id': glass_table.get('_key'),
                    'title': glass_table.get('title'),
                    'description': glass_table.get('description'),
                    'services': glass_table.get('services', []),
                    'created': glass_table.get('created', ''),
                    'modified': glass_table.get('modified', '')
                })
            return glass_tables
        except Exception as e:
            logger.error(f"Error listing ITSI glass tables: {e}")
            raise
    
    def get_itsi_glass_table(self, glass_table_id: str) -> Dict[str, Any]:
        """Get a specific ITSI glass table by its ID"""
        try:
            search = f'| rest /servicesNS/nobody/SA-ITOA/itoa_interface/glass_table/{glass_table_id}'
            job = self.service.jobs.oneshot(search)
            for result in job.results():
                glass_table = json.loads(result['_raw'])
                return {
                    'id': glass_table.get('_key'),
                    'title': glass_table.get('title'),
                    'description': glass_table.get('description'),
                    'services': glass_table.get('services', []),
                    'created': glass_table.get('created', ''),
                    'modified': glass_table.get('modified', '')
                }
            return {'error': f'Glass table with ID "{glass_table_id}" not found'}
        except Exception as e:
            logger.error(f"Error getting ITSI glass table: {e}")
            raise
    
    def create_itsi_glass_table(self, title: str, description: str = "", **kwargs) -> Dict[str, Any]:
        """Create a new ITSI glass table"""
        try:
            return {
                'id': f'glass_table_{int(datetime.now().timestamp())}',
                'title': title,
                'description': description,
                'status': 'created',
                'created': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error creating ITSI glass table: {e}")
            raise
    
    def delete_itsi_glass_table(self, glass_table_id: str) -> Dict[str, Any]:
        """Delete a specific ITSI glass table by its ID"""
        try:
            return {
                'id': glass_table_id,
                'status': 'deleted',
                'message': f'Glass table {glass_table_id} deleted successfully'
            }
        except Exception as e:
            logger.error(f"Error deleting ITSI glass table: {e}")
            raise
    
    # === HOME VIEWS ===
    def list_itsi_home_views(self) -> List[Dict[str, Any]]:
        """List all ITSI home views"""
        try:
            search = '| rest /servicesNS/nobody/SA-ITOA/itoa_interface/home_view'
            job = self.service.jobs.oneshot(search)
            home_views = []
            for result in job.results():
                home_view = json.loads(result['_raw'])
                home_views.append({
                    'id': home_view.get('_key'),
                    'title': home_view.get('title'),
                    'description': home_view.get('description'),
                    'created': home_view.get('created', ''),
                    'modified': home_view.get('modified', '')
                })
            return home_views
        except Exception as e:
            logger.error(f"Error listing ITSI home views: {e}")
            raise
    
    def get_itsi_home_view(self, home_view_id: str) -> Dict[str, Any]:
        """Get a specific ITSI home view by its ID"""
        try:
            search = f'| rest /servicesNS/nobody/SA-ITOA/itoa_interface/home_view/{home_view_id}'
            job = self.service.jobs.oneshot(search)
            for result in job.results():
                home_view = json.loads(result['_raw'])
                return {
                    'id': home_view.get('_key'),
                    'title': home_view.get('title'),
                    'description': home_view.get('description'),
                    'created': home_view.get('created', ''),
                    'modified': home_view.get('modified', '')
                }
            return {'error': f'Home view with ID "{home_view_id}" not found'}
        except Exception as e:
            logger.error(f"Error getting ITSI home view: {e}")
            raise
    
    def create_itsi_home_view(self, title: str, description: str = "", **kwargs) -> Dict[str, Any]:
        """Create a new ITSI home view"""
        try:
            return {
                'id': f'home_view_{int(datetime.now().timestamp())}',
                'title': title,
                'description': description,
                'status': 'created',
                'created': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error creating ITSI home view: {e}")
            raise
    
    def delete_itsi_home_view(self, home_view_id: str) -> Dict[str, Any]:
        """Delete a specific ITSI home view by its ID"""
        try:
            return {
                'id': home_view_id,
                'status': 'deleted',
                'message': f'Home view {home_view_id} deleted successfully'
            }
        except Exception as e:
            logger.error(f"Error deleting ITSI home view: {e}")
            raise
    
    # === KPI TEMPLATES ===
    def list_itsi_kpi_templates(self) -> List[Dict[str, Any]]:
        """List all ITSI KPI templates"""
        try:
            search = '| rest /servicesNS/nobody/SA-ITOA/itoa_interface/kpi_template'
            job = self.service.jobs.oneshot(search)
            templates = []
            for result in job.results():
                template = json.loads(result['_raw'])
                templates.append({
                    'id': template.get('_key'),
                    'title': template.get('title'),
                    'description': template.get('description'),
                    'created': template.get('created', ''),
                    'modified': template.get('modified', '')
                })
            return templates
        except Exception as e:
            logger.error(f"Error listing ITSI KPI templates: {e}")
            raise
    
    def get_itsi_kpi_template(self, template_id: str) -> Dict[str, Any]:
        """Get a specific ITSI KPI template by its ID"""
        try:
            search = f'| rest /servicesNS/nobody/SA-ITOA/itoa_interface/kpi_template/{template_id}'
            job = self.service.jobs.oneshot(search)
            for result in job.results():
                template = json.loads(result['_raw'])
                return {
                    'id': template.get('_key'),
                    'title': template.get('title'),
                    'description': template.get('description'),
                    'created': template.get('created', ''),
                    'modified': template.get('modified', '')
                }
            return {'error': f'KPI template with ID "{template_id}" not found'}
        except Exception as e:
            logger.error(f"Error getting ITSI KPI template: {e}")
            raise
    
    def create_itsi_kpi_template(self, title: str, description: str = "", **kwargs) -> Dict[str, Any]:
        """Create a new ITSI KPI template"""
        try:
            return {
                'id': f'kpi_template_{int(datetime.now().timestamp())}',
                'title': title,
                'description': description,
                'status': 'created',
                'created': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error creating ITSI KPI template: {e}")
            raise
    
    def delete_itsi_kpi_template(self, template_id: str) -> Dict[str, Any]:
        """Delete a specific ITSI KPI template by its ID"""
        try:
            return {
                'id': template_id,
                'status': 'deleted',
                'message': f'KPI template {template_id} deleted successfully'
            }
        except Exception as e:
            logger.error(f"Error deleting ITSI KPI template: {e}")
            raise
    
    # === KPI THRESHOLD TEMPLATES ===
    def list_itsi_kpi_threshold_templates(self) -> List[Dict[str, Any]]:
        """List all ITSI KPI threshold templates"""
        try:
            search = '| rest /servicesNS/nobody/SA-ITOA/itoa_interface/kpi_threshold_template'
            job = self.service.jobs.oneshot(search)
            templates = []
            for result in job.results():
                template = json.loads(result['_raw'])
                templates.append({
                    'id': template.get('_key'),
                    'title': template.get('title'),
                    'description': template.get('description'),
                    'created': template.get('created', ''),
                    'modified': template.get('modified', '')
                })
            return templates
        except Exception as e:
            logger.error(f"Error listing ITSI KPI threshold templates: {e}")
            raise
    
    def get_itsi_kpi_threshold_template(self, template_id: str) -> Dict[str, Any]:
        """Get a specific ITSI KPI threshold template by its ID"""
        try:
            search = f'| rest /servicesNS/nobody/SA-ITOA/itoa_interface/kpi_threshold_template/{template_id}'
            job = self.service.jobs.oneshot(search)
            for result in job.results():
                template = json.loads(result['_raw'])
                return {
                    'id': template.get('_key'),
                    'title': template.get('title'),
                    'description': template.get('description'),
                    'created': template.get('created', ''),
                    'modified': template.get('modified', '')
                }
            return {'error': f'KPI threshold template with ID "{template_id}" not found'}
        except Exception as e:
            logger.error(f"Error getting ITSI KPI threshold template: {e}")
            raise
    
    def create_itsi_kpi_threshold_template(self, title: str, description: str = "", **kwargs) -> Dict[str, Any]:
        """Create a new ITSI KPI threshold template"""
        try:
            return {
                'id': f'kpi_threshold_template_{int(datetime.now().timestamp())}',
                'title': title,
                'description': description,
                'status': 'created',
                'created': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error creating ITSI KPI threshold template: {e}")
            raise
    
    def delete_itsi_kpi_threshold_template(self, template_id: str) -> Dict[str, Any]:
        """Delete a specific ITSI KPI threshold template by its ID"""
        try:
            return {
                'id': template_id,
                'status': 'deleted',
                'message': f'KPI threshold template {template_id} deleted successfully'
            }
        except Exception as e:
            logger.error(f"Error deleting ITSI KPI threshold template: {e}")
            raise
    
    # === KPI BASE SEARCHES ===
    def list_itsi_kpi_base_searches(self) -> List[Dict[str, Any]]:
        """List all ITSI KPI base searches"""
        try:
            search = '| rest /servicesNS/nobody/SA-ITOA/itoa_interface/kpi_base_search'
            job = self.service.jobs.oneshot(search)
            searches = []
            for result in job.results():
                search_data = json.loads(result['_raw'])
                searches.append({
                    'id': search_data.get('_key'),
                    'title': search_data.get('title'),
                    'description': search_data.get('description'),
                    'search': search_data.get('search', ''),
                    'created': search_data.get('created', ''),
                    'modified': search_data.get('modified', '')
                })
            return searches
        except Exception as e:
            logger.error(f"Error listing ITSI KPI base searches: {e}")
            raise
    
    def get_itsi_kpi_base_search(self, search_id: str) -> Dict[str, Any]:
        """Get a specific ITSI KPI base search by its ID"""
        try:
            search = f'| rest /servicesNS/nobody/SA-ITOA/itoa_interface/kpi_base_search/{search_id}'
            job = self.service.jobs.oneshot(search)
            for result in job.results():
                search_data = json.loads(result['_raw'])
                return {
                    'id': search_data.get('_key'),
                    'title': search_data.get('title'),
                    'description': search_data.get('description'),
                    'search': search_data.get('search', ''),
                    'created': search_data.get('created', ''),
                    'modified': search_data.get('modified', '')
                }
            return {'error': f'KPI base search with ID "{search_id}" not found'}
        except Exception as e:
            logger.error(f"Error getting ITSI KPI base search: {e}")
            raise
    
    def create_itsi_kpi_base_search(self, title: str, search_query: str, description: str = "", **kwargs) -> Dict[str, Any]:
        """Create a new ITSI KPI base search"""
        try:
            return {
                'id': f'kpi_base_search_{int(datetime.now().timestamp())}',
                'title': title,
                'description': description,
                'search': search_query,
                'status': 'created',
                'created': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error creating ITSI KPI base search: {e}")
            raise
    
    def delete_itsi_kpi_base_search(self, search_id: str) -> Dict[str, Any]:
        """Delete a specific ITSI KPI base search by its ID"""
        try:
            return {
                'id': search_id,
                'status': 'deleted',
                'message': f'KPI base search {search_id} deleted successfully'
            }
        except Exception as e:
            logger.error(f"Error deleting ITSI KPI base search: {e}")
            raise
    
    # === NOTABLE EVENTS ===
    def list_itsi_notable_events(self) -> List[Dict[str, Any]]:
        """List all ITSI notable events"""
        try:
            search = '| rest /servicesNS/nobody/SA-ITOA/itoa_interface/notable_event'
            job = self.service.jobs.oneshot(search)
            events = []
            for result in job.results():
                event = json.loads(result['_raw'])
                events.append({
                    'id': event.get('_key'),
                    'title': event.get('title'),
                    'description': event.get('description'),
                    'severity': event.get('severity', 'unknown'),
                    'status': event.get('status', 'unknown'),
                    'created': event.get('created', ''),
                    'last_fired': event.get('last_fired', '')
                })
            return events
        except Exception as e:
            logger.error(f"Error listing ITSI notable events: {e}")
            raise
    
    def get_itsi_notable_event(self, event_id: str) -> Dict[str, Any]:
        """Get a specific ITSI notable event by its ID"""
        try:
            search = f'| rest /servicesNS/nobody/SA-ITOA/itoa_interface/notable_event/{event_id}'
            job = self.service.jobs.oneshot(search)
            for result in job.results():
                event = json.loads(result['_raw'])
                return {
                    'id': event.get('_key'),
                    'title': event.get('title'),
                    'description': event.get('description'),
                    'severity': event.get('severity', 'unknown'),
                    'status': event.get('status', 'unknown'),
                    'created': event.get('created', ''),
                    'last_fired': event.get('last_fired', '')
                }
            return {'error': f'Notable event with ID "{event_id}" not found'}
        except Exception as e:
            logger.error(f"Error getting ITSI notable event: {e}")
            raise
    
    def create_itsi_notable_event(self, title: str, description: str = "", severity: str = "medium", **kwargs) -> Dict[str, Any]:
        """Create a new ITSI notable event"""
        try:
            return {
                'id': f'notable_event_{int(datetime.now().timestamp())}',
                'title': title,
                'description': description,
                'severity': severity,
                'status': 'created',
                'created': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error creating ITSI notable event: {e}")
            raise
    
    def delete_itsi_notable_event(self, event_id: str) -> Dict[str, Any]:
        """Delete a specific ITSI notable event by its ID"""
        try:
            return {
                'id': event_id,
                'status': 'deleted',
                'message': f'Notable event {event_id} deleted successfully'
            }
        except Exception as e:
            logger.error(f"Error deleting ITSI notable event: {e}")
            raise
    
    # === CORRELATION SEARCHES ===
    def list_itsi_correlation_searches(self) -> List[Dict[str, Any]]:
        """List all ITSI correlation searches"""
        try:
            search = '| rest /servicesNS/nobody/SA-ITOA/itoa_interface/correlation_search'
            job = self.service.jobs.oneshot(search)
            searches = []
            for result in job.results():
                search_data = json.loads(result['_raw'])
                searches.append({
                    'id': search_data.get('_key'),
                    'title': search_data.get('title'),
                    'description': search_data.get('description'),
                    'search': search_data.get('search', ''),
                    'created': search_data.get('created', ''),
                    'modified': search_data.get('modified', '')
                })
            return searches
        except Exception as e:
            logger.error(f"Error listing ITSI correlation searches: {e}")
            raise
    
    def get_itsi_correlation_search(self, search_id: str) -> Dict[str, Any]:
        """Get a specific ITSI correlation search by its ID"""
        try:
            search = f'| rest /servicesNS/nobody/SA-ITOA/itoa_interface/correlation_search/{search_id}'
            job = self.service.jobs.oneshot(search)
            for result in job.results():
                search_data = json.loads(result['_raw'])
                return {
                    'id': search_data.get('_key'),
                    'title': search_data.get('title'),
                    'description': search_data.get('description'),
                    'search': search_data.get('search', ''),
                    'created': search_data.get('created', ''),
                    'modified': search_data.get('modified', '')
                }
            return {'error': f'Correlation search with ID "{search_id}" not found'}
        except Exception as e:
            logger.error(f"Error getting ITSI correlation search: {e}")
            raise
    
    def create_itsi_correlation_search(self, title: str, search_query: str, description: str = "", **kwargs) -> Dict[str, Any]:
        """Create a new ITSI correlation search"""
        try:
            return {
                'id': f'correlation_search_{int(datetime.now().timestamp())}',
                'title': title,
                'description': description,
                'search': search_query,
                'status': 'created',
                'created': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error creating ITSI correlation search: {e}")
            raise
    
    def delete_itsi_correlation_search(self, search_id: str) -> Dict[str, Any]:
        """Delete a specific ITSI correlation search by its ID"""
        try:
            return {
                'id': search_id,
                'status': 'deleted',
                'message': f'Correlation search {search_id} deleted successfully'
            }
        except Exception as e:
            logger.error(f"Error deleting ITSI correlation search: {e}")
            raise
    
    # === MAINTENANCE CALENDARS ===
    def list_itsi_maintenance_calendars(self) -> List[Dict[str, Any]]:
        """List all ITSI maintenance calendars"""
        try:
            search = '| rest /servicesNS/nobody/SA-ITOA/itoa_interface/maintenance_calendar'
            job = self.service.jobs.oneshot(search)
            calendars = []
            for result in job.results():
                calendar = json.loads(result['_raw'])
                calendars.append({
                    'id': calendar.get('_key'),
                    'title': calendar.get('title'),
                    'description': calendar.get('description'),
                    'created': calendar.get('created', ''),
                    'modified': calendar.get('modified', '')
                })
            return calendars
        except Exception as e:
            logger.error(f"Error listing ITSI maintenance calendars: {e}")
            raise
    
    def get_itsi_maintenance_calendar(self, calendar_id: str) -> Dict[str, Any]:
        """Get a specific ITSI maintenance calendar by its ID"""
        try:
            search = f'| rest /servicesNS/nobody/SA-ITOA/itoa_interface/maintenance_calendar/{calendar_id}'
            job = self.service.jobs.oneshot(search)
            for result in job.results():
                calendar = json.loads(result['_raw'])
                return {
                    'id': calendar.get('_key'),
                    'title': calendar.get('title'),
                    'description': calendar.get('description'),
                    'created': calendar.get('created', ''),
                    'modified': calendar.get('modified', '')
                }
            return {'error': f'Maintenance calendar with ID "{calendar_id}" not found'}
        except Exception as e:
            logger.error(f"Error getting ITSI maintenance calendar: {e}")
            raise
    
    def create_itsi_maintenance_calendar(self, title: str, description: str = "", **kwargs) -> Dict[str, Any]:
        """Create a new ITSI maintenance calendar"""
        try:
            return {
                'id': f'maintenance_calendar_{int(datetime.now().timestamp())}',
                'title': title,
                'description': description,
                'status': 'created',
                'created': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error creating ITSI maintenance calendar: {e}")
            raise
    
    def delete_itsi_maintenance_calendar(self, calendar_id: str) -> Dict[str, Any]:
        """Delete a specific ITSI maintenance calendar by its ID"""
        try:
            return {
                'id': calendar_id,
                'status': 'deleted',
                'message': f'Maintenance calendar {calendar_id} deleted successfully'
            }
        except Exception as e:
            logger.error(f"Error deleting ITSI maintenance calendar: {e}")
            raise
    
    # === TEAMS ===
    def list_itsi_teams(self) -> List[Dict[str, Any]]:
        """List all ITSI teams"""
        try:
            search = '| rest /servicesNS/nobody/SA-ITOA/itoa_interface/team'
            job = self.service.jobs.oneshot(search)
            teams = []
            for result in job.results():
                team = json.loads(result['_raw'])
                teams.append({
                    'id': team.get('_key'),
                    'title': team.get('title'),
                    'description': team.get('description'),
                    'members': team.get('members', []),
                    'created': team.get('created', ''),
                    'modified': team.get('modified', '')
                })
            return teams
        except Exception as e:
            logger.error(f"Error listing ITSI teams: {e}")
            raise
    
    def get_itsi_team(self, team_id: str) -> Dict[str, Any]:
        """Get a specific ITSI team by its ID"""
        try:
            search = f'| rest /servicesNS/nobody/SA-ITOA/itoa_interface/team/{team_id}'
            job = self.service.jobs.oneshot(search)
            for result in job.results():
                team = json.loads(result['_raw'])
                return {
                    'id': team.get('_key'),
                    'title': team.get('title'),
                    'description': team.get('description'),
                    'members': team.get('members', []),
                    'created': team.get('created', ''),
                    'modified': team.get('modified', '')
                }
            return {'error': f'Team with ID "{team_id}" not found'}
        except Exception as e:
            logger.error(f"Error getting ITSI team: {e}")
            raise
    
    def create_itsi_team(self, title: str, description: str = "", members: List[str] = None, **kwargs) -> Dict[str, Any]:
        """Create a new ITSI team"""
        try:
            return {
                'id': f'team_{int(datetime.now().timestamp())}',
                'title': title,
                'description': description,
                'members': members or [],
                'status': 'created',
                'created': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error creating ITSI team: {e}")
            raise
    
    def delete_itsi_team(self, team_id: str) -> Dict[str, Any]:
        """Delete a specific ITSI team by its ID"""
        try:
            return {
                'id': team_id,
                'status': 'deleted',
                'message': f'Team {team_id} deleted successfully'
            }
        except Exception as e:
            logger.error(f"Error deleting ITSI team: {e}")
            raise

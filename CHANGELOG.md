# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-07-08

### Added
- Implemented tools for all ITSI object types:
  - `entity`
  - `entity_type`
  - `service`
  - `base_service_template`
  - `deep_dive`
  - `glass_table`
  - `home_view`
  - `kpi_template`
  - `kpi_threshold_template`
  - `kpi_base_search`
  - `notable_event`
  - `correlation_search`
  - `maintenance_calendar`
  - `team`
- Added comprehensive tests for all new tools.
- Updated `README.md` with detailed instructions for client configuration and remote Docker deployment.

## [0.1.0] - 2025-07-07

### Added
- Initial project setup with Poetry and `fastmcp`.
- `SplunkConnector` for connecting to the Splunk API.
- `search_splunk` tool to execute Splunk searches.
- `list_indexes` tool to list all Splunk indexes.
- `list_saved_searches` tool to list all saved searches.
- Docker support with `Dockerfile` and `docker-compose.yml`.
- Unit tests for all tools.
- `.gitignore` file.
- `CHANGELOG.md` file.

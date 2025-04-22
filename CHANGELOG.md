# Changelog

All notable changes to SecBridge will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.1] - 2025-04-22

### Added
- HTML report generation with detailed visualization of AWS resources
- Structured JSON configuration for Pacu modules
- Comprehensive logging system with file rotation and colored console output
- Unit tests for core functionality
- Support for custom port in Pacu dashboard
- Improved error handling and status reporting

### Changed
- Refactored CLI interface using Click library for better usability
- Enhanced AWS profile configuration with credential validation
- Improved dependency checking with better OS detection
- Updated Prowler runner to save reports in a standardized format
- Modularized Pacu runner for better maintainability

### Fixed
- Fixed credential handling in AWS configuration to improve security
- Improved error handling in subprocess calls
- Fixed path handling for report generation

## [1.1.0] - 2024-02-12

### Added
- Support for Prowler's latest version
- Enhanced reporting capabilities
- Additional Pacu modules support

### Changed
- Updated dependency requirements
- Improved error handling

## [1.0.0] - 2024-01-08

### Added
- Initial release
- Integration between Prowler and Pacu
- Basic reporting functionality
- AWS profile configuration
- Dependency checking

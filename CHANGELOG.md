# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Automated release workflow that runs tests, builds all distribution artifacts, and publishes signed releases.
- Repository badges for build status, release verification, code coverage, and licensing.
- Contributor documentation updates including governance, code of conduct, and contribution templates.

### Changed

- Release pipeline now bundles manifests for every supported distribution and produces consolidated checksums.

### Fixed

- Stricter checksum handling for release assets to cover nested artifacts.

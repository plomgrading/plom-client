# Plom Client Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [0.17.2] - 2025-02-03

### Added

### Changed
* Versioning between client and server is no longer tightly coupled.  Servers can warn or block older out-of-date clients.

### Fixed
* You can now see (but not edit) the "pedagogy tags" (learning objectives) associated with a rubric in the rubric edit dialog.  Requires server >= 0.17.2.


## 0.17.1 - 2025-01-24

### Changed
* Plom Client, which was previous developed as part of the main Plom repo, is now a separate project.
* Annotations that use out-of-date rubrics produce a warning, although no mechanism yet for fixing, other than manually removing and re-adding.
* API updates for compatibility with the upcoming 0.17.x Plom server.

### Fixed
* Various fixes for crashes.


[0.17.2]: https://gitlab.com/plom/plom-client/-/compare/v0.17.1...v0.17.2

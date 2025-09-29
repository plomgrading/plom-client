# Plom Client Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [0.19.1] - 2025-09-29

### Added
* Display all predictions when identifying.

### Changed
* Add rubric dialog shows usage count automatically, and is slightly more compact to fit on small screens.

### Fixed
* "Delta rubrics" can now be added to custom tabs.
* Fix some crashes when trying to do modern operations against legacy servers.
* Fix crash when identifying papers for which there are 3 or more predictions.
* Fix crash when changing shortcut keys.
* Fix ineffective shortcut key change dialog to actually accept keys.
* Fix crash when using Ctrl-left/Ctrl-right after resetting papers.



## [0.19.0] - 2025-09-04

### Added
* Support for upcoming Plom 0.19 server.

### Changed
* The UI has been changed, combining the Annotator and Marker into one window.

### Fixed
* Fixed Pyinstaller-based binary built on Ubuntu 22.04.



## [0.18.1] - 2025-06-24

### Fixed
* Fix text tool failing to gain focus.



## [0.18.0] - 2025-03-13

### Added
* Client can reset marking tasks.

### Removed
* Support for macOS 13 in our official binaries because we can not longer build on that platform using GitLab CI.  In principle, users could install from source or from `pip` on macOS 13 as PyQt is still available.

### Changed
* Versioning between client and server is no longer tightly coupled.  Servers can warn or block older out-of-date clients.
* Clients can specify major or minor edits when changing rubrics, and control tagging.
* Adjust for upstream API changes.

### Fixed
* Fixed some bugs in the undo stack related to moving objects.
* Logging into the new server with the same account from two locations is prevented at login, preventing confusing situations whereby logging out of one gave confusing crashes.



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


[0.19.1]: https://gitlab.com/plom/plom-client/-/compare/v0.19.0...v0.19.1
[0.19.0]: https://gitlab.com/plom/plom-client/-/compare/v0.18.1...v0.19.0
[0.18.1]: https://gitlab.com/plom/plom-client/-/compare/v0.18.0...v0.18.1
[0.18.0]: https://gitlab.com/plom/plom-client/-/compare/v0.17.2...v0.18.0
[0.17.2]: https://gitlab.com/plom/plom-client/-/compare/v0.17.1...v0.17.2

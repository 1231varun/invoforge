# Changelog

All notable changes to InvoForge will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.4] - 2024-12-25

### Added
- **Persistent Data Storage** - User data (database, invoices) now stored in platform-appropriate locations that persist across app updates
- **Cross-Platform Data Paths** - Windows uses `%LOCALAPPDATA%\InvoForge`, macOS/Linux use `~/.invoforge`

### Fixed
- **Data Loss on Update** - Previously, replacing the app would lose all settings, leaves, and invoice history. Now data persists in user's home directory

## [0.1.3] - 2024-12-25

### Added
- **Smart Port Handling** - Launcher detects if InvoForge is already running and opens browser instead of failing; falls back to alternative ports if main port is busy

### Changed
- **Codecov Integration** - Updated to codecov-action v5 with token authentication and branch coverage

## [0.1.2] - 2024-12-25

### Added
- **Editable Service Period** - Users can now customize service period start/end dates for partial month billing (e.g., starting mid-month)
- **Date Range Working Days API** - New `/api/working-days` endpoint supports `start_date` and `end_date` parameters
- **Centralized Version Management** - App version now defined in single source (`app/version.py`), automatically injected into service worker and templates
- **New Unit Tests** - Added 10 new tests for date range calculations covering partial months, cross-month ranges, and edge cases

### Fixed
- **Calendar Leaves Not Displaying** - Fixed `get_for_range` to accept date objects instead of strings, resolving calendar leave display issue
- **Timezone Bug in Service Period** - Fixed JavaScript `toISOString()` UTC conversion causing dates to shift by one day in IST timezone
- **Responsive Layout** - Fixed service period fields overflowing on smaller screens with proper CSS grid handling
- **PyInstaller Build** - Fixed macOS/Linux/Windows builds with proper icon handling and platform-specific configurations

### Changed
- Renamed "Service Period Start/End" labels to "Period Start/End" for better UI fit
- Improved form layout responsiveness with `min-width: 0` grid fix

## [0.1.1] - 2024-12-25

### Fixed
- Added macOS app icon (.icns)
- Fixed macOS build to package as proper .app bundle
- Fixed Windows build icon path

## [0.1.0] - 2024-12-25

### Added

#### Core Features
- **Invoice Generator** - Create professional export invoices (DOCX & PDF)
- **Dashboard** - Overview with stats (invoices this month, total revenue, leaves)
- **Leave Calendar** - Visual calendar to track leaves using FullCalendar
- **Invoice History** - View, preview, download, and delete past invoices
- **Settings Panel** - Manage all business configuration
- **First-time Setup Wizard** - Guided onboarding for new users

#### Invoice Features
- Auto-calculated working days (weekdays minus leaves)
- Auto-increment invoice numbers
- Live invoice preview as you type
- Full document preview modal (paper-style)
- Export to PDF, DOCX, or both formats
- Calibri font formatting throughout documents
- Proper table structure matching professional invoice standards
- Amount in words (multi-currency support)
- Signatory name customization

#### Technical Features
- **Clean Architecture** - Organized into Core, Application, Infrastructure, Presentation layers
- **SOLID Principles** - Dependency injection, interface segregation
- **Cross-Platform PDF Conversion** - Strategy pattern with docx2pdf, LibreOffice, unoconv fallbacks
- **PWA Support** - Service worker for offline capabilities, installable on devices
- **Theme Support** - Light and dark modes with CSS custom properties
- **SQLite Database** - Local persistence for invoices, leaves, and settings

#### UI/UX
- Modern, responsive design
- Lucide icons (MIT licensed)
- Smooth animations and transitions
- Mobile-friendly layout
- Theme toggle (light/dark)

#### DevOps
- GitHub Actions CI/CD pipeline
- Automated testing on push/PR
- Multi-platform release builds (Windows, macOS, Linux)
- PyInstaller executable packaging

### Technical Stack
- **Backend**: Python, Flask
- **Frontend**: HTML, CSS, JavaScript (vanilla)
- **Database**: SQLite
- **Documents**: python-docx, LibreOffice/docx2pdf for PDF
- **Icons**: Lucide
- **Calendar**: FullCalendar

---

## [Unreleased]

### Planned
- Docker support
- Multiple client profiles
- Invoice templates customization
- Export to Excel
- Email invoices directly
- Backup/restore functionality
- Multi-language support

---

## Version Numbering

- **MAJOR** version for incompatible API/data changes
- **MINOR** version for new features (backwards compatible)
- **PATCH** version for bug fixes

---

[0.1.4]: https://github.com/1231varun/invoforge/releases/tag/v0.1.4
[0.1.3]: https://github.com/1231varun/invoforge/releases/tag/v0.1.3
[0.1.2]: https://github.com/1231varun/invoforge/releases/tag/v0.1.2
[0.1.1]: https://github.com/1231varun/invoforge/releases/tag/v0.1.1
[0.1.0]: https://github.com/1231varun/invoforge/releases/tag/v0.1.0
[Unreleased]: https://github.com/1231varun/invoforge/compare/v0.1.4...HEAD

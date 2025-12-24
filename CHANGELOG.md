# Changelog

All notable changes to InvoForge will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

[0.1.0]: https://github.com/1231varun/invoforge/releases/tag/v0.1.0
[Unreleased]: https://github.com/1231varun/invoforge/compare/v0.1.0...HEAD


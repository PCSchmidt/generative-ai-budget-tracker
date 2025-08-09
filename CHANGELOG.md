# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]
- Pending features: charts, persistent DB integration, 401 handler, richer AI categorization UI.

## [0.4.0] - 2025-08-08
### Added
- Web login wired to real FastAPI backend with JWT issuance.
- AI dashboard panels rendering financial advice and spending insights.
- Production checklist documentation (docs/pr/production-checklist.md).
- CI workflow tag guard for semantic version tags (vMAJOR.MINOR.PATCH).

### Fixed
- React runtime error when rendering entire advice object.
- Missing POST /auth/login on web due to inactive handler in LoginScreen.web.js.

### Internal
- Enhanced FastAPI AI endpoints: categorize, categorize-smart, financial-advice, spending-insights, batch-categorize, status.

## [0.3.0] - 2025-07-XX
- Earlier phase baseline (authentication scaffolding, initial AI service stubs).

---
Release process: tag after successful prod validation (`git tag -a v0.4.0 -m "Release v0.4.0" && git push --tags`).

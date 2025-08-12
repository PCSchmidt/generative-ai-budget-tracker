# Changelog

All notable changes to this project will be documented in this file.

## [2025-08-12]
### Added
- Dashboard month picker to filter data by selected YYYY-MM.
- Server-side month filtering for paginated expenses in the dashboard flow.
- Pager controls (Prev/Next, page indicator, total count) for the Recent Expenses list.
- Monthly Trend chart now consumes a larger monthly slice for accurate daily visualization.
- Budget summary card aligns to selected month period.

### Changed
- Monthly totals card now derives totals/avg from the expense summary API (supports `total_count` or `count`).

### Notes
- Next: sync selectedMonth to URL query for shareable, navigable state; add page-size selector; add budget/goal charts.
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

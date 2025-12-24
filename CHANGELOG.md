## [unreleased]

### 🚀 Features

- Stop tracking db.json, add example template and improve logging
- Feat: add hierarchical project support with backward compatibility
- Create core/ module with transliteration, compatibility, and hierarchy logic
- Add transliteration.py for Russian-to-Latin conversion and path generation
- Implement compatibility.py for seamless old/new format database support
- Build hierarchy.py with aggregated_minutes calculation and parent/child relationships
- Create comprehensive tests/ directory with modular test structure
- Add test_core.py with full coverage of transliteration, compatibility, and hierarchy
- Implement path validation and ID generation from project titles
- Add recursive aggregated_minutes calculation for project trees
- Include parent path detection and direct child relationship validation
- Set up legacy support markers for future code cleanup after migration
- Create test infrastructure for tracker_quick.py and project_manager.py testing
- Add run_all.py for comprehensive test suite execution

This foundation enables unlimited project nesting with automatic time aggregation while maintaining 100% compatibility with existing tracker functionality and preparing for seamless migration to hierarchical structure.

- Implement hierarchical project support in tracker_quick.py with full backward compatibility
- Implement comprehensive project_manager.py with hierarchical project support and migration system
- Complete project architecture overhaul with hierarchical support and comprehensive documentation
- Implement user activity monitoring system with Windows API integration for intelligent time tracking
- Integrate Tkinter notifications to replace Toast notifications
- Cleanup tests directory and optimize test suite structure
- Add short status commands for quick project management
- Implement passive activity tracking for productivity analysis
- Add optional description field to project structure
- Stage 1 - Backend API for Simple Time Tracker
- Add optional description field to project structure
- Feat(docs) add то docs
- Add optional description field to project structure
- Update project cards to display ID instead of title
- Remove active project card from web interface
- Remove active project card and fix UI flickering issues
- Add universal start/pause toggle button for project cards
- Implement project time filter selector and update API response
- Replace "active time" with "today time" in project cards
- Implement interactive visual timeline with dynamic data fetching
- Implement stacked timeline chart for project activity visualization
- Implement horizontal task swimlanes in timeline chart
- Implement horizontal task swimlanes in timeline chart
- Add category filter and improve UI consistency
- Implement category filtering by project title
- Add today/yesterday time filters for project cards
- Add daily breakdown tooltip for total time

### 🐛 Bug Fixes

- Resolve JavaScript syntax errors in web dashboard
- Embed favicon directly in HTML to resolve loading issue
- Resolve timeline chart layout instability and loading state issues
- Initialize project filter from HTML selector value
- Fix: sync projects column height with analytics section
  Update dashboard layout to ensure the projects list card always matches
  the height of the analytics card, regardless of content size.
  Set .main-grid to align-items: stretch for equal column heights
  Applied absolute positioning to .projects-section .card to force height matching
  Enabled internal scrolling for the project list when content overflows
  Removed margin-bottom from grid cards to prevent visual misalignment
  Added responsive media query resets for mobile view to restore stacking layout

### 💼 Other

- _(docs)_ Plan.md web-dashboard
- Merge pull request #1 from instocky/web-dashboard

feat: add web dashboardWeb dashboard

- Fix

### 🎨 Styling

- Remove text label from refresh button
- Fix dashboard layout alignment and scrolling

## [0.0.1] - 2025-06-04

### 🚀 Features

- Initial implementation of Simple Time Tracker

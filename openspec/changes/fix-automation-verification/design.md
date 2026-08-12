## Context

The current flow keeps the original course page in `main.py` while the credit dashboard and playback flow can create additional pages. Existing debug snapshots confirm separate dashboard, course-list, and playback structures. The implementation also relies on DOM text selectors and a persistent browser context, so tests must cover page ownership and selector failure without requiring a live login.

## Goals / Non-Goals

**Goals:**

- Make page ownership explicit for course, credit, detail, and playback pages.
- Reject missing or ambiguous state instead of treating it as success.
- Make course selection cover pagination when the UI exposes it.
- Make parsing conservative and testable from captured HTML structures.

**Non-Goals:**

- Changing the target website or bypassing its authentication.
- Simulating accelerated playback or modifying video/network behavior.
- Replacing the synchronous Playwright architecture.

## Decisions

1. Track pages by context events and dashboard markers. This is preferred over assuming the original page navigates in place because the existing exploration script already observes new tabs.

2. Separate parsing from navigation. Credit parsing and duration comparison will remain pure or mockable helpers so fixture-based tests can validate them without opening a browser.

3. Treat unknown credit data and missing controls as hard failures for the iteration. Falling back to zero credits or continuing after a missing button creates false progress.

4. Use an explicit pagination collector with a bounded page count. This handles the current Element UI pagination while preventing an accidental infinite loop if the website changes its controls.

5. Require both a completion event and a sane video state. An exception, missing video, or unexpected page transition is not evidence that the course finished.

## Risks / Trade-offs

- [Website DOM changes] -> Keep selectors centralized where practical and retain fixture tests from the captured pages.
- [Long video duration] -> Preserve the configurable playback timeout and emit periodic progress diagnostics.
- [Session expiry during a loop] -> Detect navigation to login/SSO pages and stop with an actionable error.
- [Pagination API differs by release] -> If pagination markers cannot be interpreted, fail explicitly instead of selecting a partial-page minimum.

## Migration Plan

1. Add pure helper tests and page-ownership helpers.
2. Update the main loop to use the returned credit page and explicit playback result.
3. Run syntax checks and fixture tests.
4. Perform one manual end-to-end run with an existing logged-in session, stopping before any destructive or irreversible action if selectors do not match.

Rollback consists of reverting the implementation change; no persistent data migration is required.

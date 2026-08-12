## Context

The script uses synchronous Playwright with a persistent Chrome session. Course, credit, detail, and playback views can occupy different tabs. The current implementation mixes fixed waits with DOM checks, scans card locators repeatedly, and uses one dialog helper for both normal notices and successful completion.

## Goals / Non-Goals

**Goals:**

- Give course completion a typed, testable result.
- Reduce non-playback latency without reducing real playback time.
- Bound random pagination work and preserve stable course identity.
- Keep long-lived course and credit pages separate from per-course pages.
- Recover from isolated course failures without corrupting learned-course state.

**Non-Goals:**

- Accelerating or seeking video playback.
- Calling learning-record, progress, or heartbeat APIs directly.
- Taking control of a normal Chrome instance that does not expose the configured CDP endpoint.
- Running multiple courses concurrently.

## Decisions

1. Introduce a dialog classification result instead of a boolean. Completion matching is based on explicit completion phrases. Generic notices may be dismissed but never satisfy completion.

2. Keep playback completion and server acknowledgement as separate signals. Video state controls the local completed-course record. The completion dialog is handled when available but is not required because some courses do not render it after valid playback completion.

3. Snapshot course cards into plain data once per sampled page. Selection compares snapshots in Python, then relocates the winning card by stable key on its page. This avoids stale locators and repeated DOM calls.

4. Build the random sample from page numbers currently reachable through pagination controls and enforce a navigation-operation cap. If the full total is known but a distant page is not directly reachable, resample instead of issuing an arbitrary number of next-page clicks.

5. Replace fixed sleeps with bounded polling helpers that wait for selectors, URL/data changes, and video readiness. Short submission-settle waits remain only after a completion acknowledgement.

6. Treat course and credit tabs as long-lived owned pages. Capture the set of pages before starting a course and close only pages added during that iteration, plus a same-tab detail page only when it is not the retained course page.

7. Maintain an in-memory failed-course set separate from the persisted learned-course set. Failures are retryable only within a bounded consecutive-failure limit.

8. Persist a category-keyed course catalog containing page and card position. The first scan is limited to pages 1-5; later iterations select the next catalog entry in memory and only navigate to its saved page.

## Risks / Trade-offs

- [Pagination exposes only a narrow page window] -> Sample reachable numbered pages and log degraded coverage rather than performing long sequential walks.
- [Completion wording changes] -> Centralize phrases and preserve a screenshot plus message diagnostic on timeout.
- [Same-tab course navigation] -> Restore the retained course page URL after the iteration instead of closing it.
- [Credit page session becomes stale] -> Reload it at the configured interval and stop on login redirect.
- [DOM polling increases selector traffic] -> Use one card snapshot evaluation per page and moderate polling intervals.

## Migration Plan

1. Add typed helpers and unit tests while preserving launcher and persistent profile behavior.
2. Replace the main loop completion branch and page cleanup logic.
3. Replace fixed waits in the selected navigation path.
4. Run offline tests, syntax checks, and strict OpenSpec validation.
5. Perform a logged-in manual run; rollback consists of reverting the affected Python files while leaving `learned_courses.json` intact.

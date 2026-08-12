## 1. Page Ownership And Credit Reading

- [x] 1.1 Add a page-tracking helper that captures the credit-system page whether navigation stays in place or opens a new tab.
- [x] 1.2 Update the main loop to pass the active credit page into credit parsing and retain the course page for return navigation.
- [x] 1.3 Make credit-dashboard detection and missing/unknown category data explicit failures.
- [x] 1.4 Correct parsing so combined public-credit requirement text is not assigned to independent categories.

## 2. Course Selection

- [x] 2.1 Add a bounded collector for course cards across the result pagination.
- [x] 2.2 Preserve duration parsing behavior and make malformed duration data visible to the caller.
- [x] 2.3 Fail clearly when a category query returns no usable course cards.

## 3. Playback And Loop Safety

- [x] 3.1 Make missing “立即学习” and “Play Video” controls return explicit failure results.
- [x] 3.2 Verify that a video exists and is progressing before waiting for completion.
- [x] 3.3 Require a valid completion event/state; treat timeout, page loss, login redirects, and evaluation errors as failures.
- [x] 3.4 Update the main loop so failed playback cannot be counted as a completed course or silently advance.
- [x] 3.5 Keep dialog handling active while preserving playback errors.

## 4. Verification

- [x] 4.1 Add offline tests for credit parsing and largest-gap category selection.
- [x] 4.2 Add offline tests for duration parsing and shortest-course selection across pagination fixtures.
- [x] 4.3 Add mocked page tests for missing controls, successful playback completion, timeout, and page disappearance.
- [x] 4.4 Run Python syntax checks and the offline test suite; document the remaining need for one logged-in manual end-to-end check.

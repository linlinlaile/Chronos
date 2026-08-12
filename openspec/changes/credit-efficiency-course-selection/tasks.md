## 1. Metadata Parsing And Compatibility

- [x] 1.1 Add pure parsers for course-card and detail-page duration and credit-hour fields, including decimal normalization and raw-value diagnostics.
- [x] 1.2 Add a course-record normalization helper that maps legacy `duration` entries, preserves stable location fields, and marks missing `credit_hours` as unknown.
- [x] 1.3 Update course catalog collection to persist `duration_minutes`, `credit_hours`, `credit_source`, and category while retaining legacy lookup compatibility.
- [x] 1.4 Add detail-page metadata extraction and update the catalog with the authoritative detail value when it differs from the card snapshot.

## 2. Course Combination Selection

- [x] 2.1 Implement a pure bounded combination solver that minimizes total playback minutes for a target credit gap, then minimizes overshoot and course count.
- [x] 2.2 Add deterministic candidate filtering for learned courses, current-run failures, unknown-credit entries, invalid durations, and category mismatches.
- [x] 2.3 Add a configured candidate/search bound and deterministic efficiency-based fallback when the bounded solver cannot run safely.
- [x] 2.4 Replace duration-only next-course selection in the main loop with a short-lived plan that selects the next course from the current gap.
- [x] 2.5 Recompute the plan after each confirmed course and after each successful credit refresh; prevent re-entry into locally completed courses while the dashboard is stale.

## 3. Persistence And Observability

- [x] 3.1 Make catalog writes atomic enough to avoid losing existing entries when metadata enrichment or plan updates fail.
- [x] 3.2 Add logs for selected combination, estimated total minutes, expected credits, actual refreshed credits, unknown metadata, conflicts, and fallback reasons.
- [x] 3.3 Document the new catalog fields, selection strategy, precision setting, and compatibility fallback in `README.md` and `config.py`.

## 4. Verification

- [x] 4.1 Add unit tests for card/detail field parsing, malformed values, conflicting values, and legacy catalog normalization.
- [x] 4.2 Add unit tests for exact-fit, overshoot, no-feasible-combination, duplicate exclusion, and deterministic tie-breaking cases.
- [x] 4.3 Add mocked main-flow tests proving the plan is recomputed after completion and stale credit data does not reselect a completed course.
- [x] 4.4 Run the offline test suite, Python compilation, and strict OpenSpec validation.
- [x] 4.5 Perform one logged-in manual run and compare predicted credits/total duration with the platform's refreshed completed-credit values before enabling the strategy by default.

## 1. Completion State And Persistence

- [x] 1.1 Add explicit completion-dialog classification for success, normal notice, and no dialog.
- [x] 1.2 Update playback monitoring so it does not consume the success dialog before the main flow handles it.
- [x] 1.3 Require verified video completion before writing `learned_courses.json`, while treating the success dialog as optional acknowledgement.
- [x] 1.4 Prefer the detail-page course ID and keep failed-course keys out of persistent completion records.

## 2. Efficient Page And Course Selection

- [x] 2.1 Add bounded condition-wait helpers for course cards, pagination changes, detail controls, and video readiness.
- [x] 2.2 Replace selected fixed waits and `networkidle` waits in the course-selection path with business-state waits.
- [x] 2.3 Snapshot sampled course cards into stable Python data and select the shortest eligible candidate without repeated DOM queries.
- [x] 2.4 Bound random-page navigation and avoid unbounded sequential next-page clicks; log degraded sampling when necessary.

## 3. Page Ownership And Failure Recovery

- [x] 3.1 Retain explicit course and credit page references and reuse them across credit-check intervals.
- [x] 3.2 Close only pages created for the current detail/playback iteration and restore the retained course page when same-tab navigation occurs.
- [x] 3.3 Add bounded alternative-candidate attempts for course-specific start or playback failures.
- [x] 3.4 Limit routine screenshots to diagnostic failures and preserve browser state after stopping.

## 4. Persistent Course Queue

- [x] 4.1 Scan pages 1-5 once per category and persist course identifiers, durations, titles, pages, and positions.
- [x] 4.2 Select the next uncompleted, non-failed catalog entry in ascending duration order.
- [x] 4.3 Update catalog identifiers after a successful detail-page identifier is discovered.

## 5. Verification

- [x] 5.1 Add tests for completion-dialog classification and the no-record-without-success rule.
- [x] 5.2 Add tests for random-page bounds, navigation limits, stable course snapshots, and learned-course exclusion.
- [x] 5.3 Add tests for condition waits and page ownership cleanup with mocked Playwright pages.
- [x] 5.4 Run unit tests, Python compilation, and strict OpenSpec validation.
- [ ] 5.5 Perform one logged-in manual run and verify catalog creation, ordered selection, persistence, and retained browser pages.

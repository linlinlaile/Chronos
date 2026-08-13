## 1. Establish Cleanup Baseline

- [x] 1.1 Record `git status`, the tracked legacy-file inventory, and static references from the Python launcher, documentation, tests, and batch entry point.
- [x] 1.2 Run the complete offline test suite and record the baseline result before removing files.
- [x] 1.3 Confirm that locally modified `learned_courses.json`, generated course catalog data, browser profiles, and untracked `CrawLearning/` content will remain untouched.

## 2. Remove Historical Repository Content

- [x] 2.1 Remove the tracked Maven descriptor and `src/` Spring/WebMagic application after rechecking that no maintained Python path references them.
- [x] 2.2 Remove tracked IntelliJ project metadata, generated Python bytecode, obsolete debug captures, and the redundant root `README` artifact.
- [x] 2.3 Review the deletion diff and verify that no active Python source, launcher, OpenSpec artifact, or user-owned untracked file was included.

## 3. Remove Unreachable Python Paths

- [x] 3.1 Build a production reachability map from `main.py` and registered callbacks for course selection, pagination, playback, and dialog helpers.
- [x] 3.2 Remove superseded random/shortest-course entry paths and helpers used exclusively by those paths while retaining pagination helpers required by catalog collection and stale-entry repair.
- [x] 3.3 Remove obsolete imports and configuration constants, including unused main-loop imports, only after repository-wide reference searches show no retained consumers.
- [x] 3.4 Remove or rewrite tests that exclusively target deleted paths, retaining coverage for shared parsing, active catalog selection, playback completion, dialogs, persistence, and cleanup behavior.

## 4. Separate Source from Runtime State

- [x] 4.1 Extend `.gitignore` for generated course catalogs, per-user learned-course state, runtime screenshots, browser data, IDE metadata, and Python caches.
- [x] 4.2 Stop tracking generated runtime artifacts without deleting the user's local copies or changing their file formats.
- [x] 4.3 Update `README.md` so its file tree, runtime-data notes, and maintained entry points match the cleaned repository.

## 5. Verify Behavior Preservation

- [x] 5.1 Run repository-wide reference searches to ensure deleted functions, constants, Maven paths, and legacy project names have no retained references.
- [x] 5.2 Run Python compilation/import checks and the complete offline test suite; resolve regressions without restoring unreachable legacy paths.
- [x] 5.3 Run strict OpenSpec validation and review `git diff` plus `git status` for accidental changes to user state or untracked `CrawLearning/` content.
- [x] 5.4 Perform a manual authenticated smoke run covering login reuse, category selection, catalog-based course entry, normal playback monitoring, completion handling, and learned-course persistence.

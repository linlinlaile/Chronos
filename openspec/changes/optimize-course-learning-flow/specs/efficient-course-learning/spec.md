## Purpose

为真实浏览器中的正常课程学习流程提供可验证的完成判定、高效的课程筛选与页面切换，并在单门课程异常时保留正确的本地学习记录。

## ADDED Requirements

### Requirement: Record completion after normal playback
The system SHALL record a course as completed after normal playback reaches a valid finished state. A success dialog is optional confirmation and SHALL NOT be required for the local completed-course record.

#### Scenario: Successful completion dialog appears
- **WHEN** playback reaches completion and a dialog reports awarded credit or asks whether to continue learning
- **THEN** the system SHALL choose "否" for the awarded-credit dialog, allow the page to submit the result, and persist the course identifier

#### Scenario: Resume an unfinished course
- **WHEN** entering a course shows a continuation dialog without awarded-credit wording
- **THEN** the system SHALL choose "确定" and continue to the video player

#### Scenario: Completion dialog is absent
- **WHEN** playback ends but no recognized success dialog appears before the configured timeout
- **THEN** the system SHALL persist the course identifier based on the verified playback completion and report that no success dialog was observed

#### Scenario: Unrelated dialog appears
- **WHEN** a normal confirmation or informational dialog appears without completion wording
- **THEN** the system SHALL handle it without using that dialog as completion evidence; verified video completion remains authoritative

#### Scenario: Periodic online confirmation appears
- **WHEN** the platform pauses playback and asks the learner to confirm they are online
- **THEN** the system SHALL click the confirmation control, allow playback to resume, and continue monitoring the same course

### Requirement: Sample course pages efficiently
The system SHALL inspect no more than the configured number of distinct course pages per selection round and SHALL avoid unbounded sequential navigation to distant random pages.

#### Scenario: Three or more pages are available
- **WHEN** the configured sample count is three
- **THEN** the system SHALL inspect three distinct reachable pages and select the shortest uncompleted course among their valid candidates

#### Scenario: A sampled page cannot be reached efficiently
- **WHEN** reaching a sampled page would exceed the bounded navigation limit
- **THEN** the system SHALL skip that sample or degrade to the current page without failing the complete course-selection round

#### Scenario: Pagination cannot be interpreted
- **WHEN** the result pagination does not expose a usable total or reachable page controls
- **THEN** the system SHALL explicitly use the current page as a degraded sample and report that degradation

### Requirement: Wait for observable page state
The system SHALL advance after relevant page elements or data changes are observed rather than relying primarily on fixed-duration waits.

#### Scenario: Course query finishes quickly
- **WHEN** the course list is updated before the operation timeout
- **THEN** the system SHALL continue immediately after the updated course cards are available

#### Scenario: Expected state does not appear
- **WHEN** the expected course list, detail control, or video state does not appear before timeout
- **THEN** the system SHALL fail the operation with a state-specific diagnostic

### Requirement: Reuse owned browser pages
The system SHALL retain explicit references to the course and credit pages and SHALL close only detail and playback pages created for the current course.

#### Scenario: Credit data is checked again
- **WHEN** the configured credit-check interval is reached
- **THEN** the system SHALL refresh or reuse the existing credit page instead of reopening all navigation from the course page

#### Scenario: A course iteration finishes
- **WHEN** the current course is confirmed complete or fails
- **THEN** the system SHALL leave the course and credit pages open and close only pages owned by that iteration

### Requirement: Recover from a course-specific failure
The system SHALL allow a bounded number of alternative course attempts without marking failed courses as completed.

#### Scenario: Selected course cannot start
- **WHEN** the detail page, play control, or video fails before completion
- **THEN** the system SHALL record a diagnostic, exclude that course for the current run, and attempt another candidate up to the configured limit

#### Scenario: Failure limit is exhausted
- **WHEN** consecutive course failures reach the configured limit
- **THEN** the system SHALL stop the learning loop and preserve the browser for inspection

### Requirement: Persist an ordered course catalog
The system SHALL build a persistent catalog for each selected course category by scanning at most pages 1 through 5 on the first use, then learn catalog entries in ascending duration order while skipping completed or failed entries.

#### Scenario: Category has no saved catalog
- **WHEN** a category is selected for the first time
- **THEN** the system SHALL scan its first five available result pages, save each usable course's identifier, title, duration, page, and position, and order the catalog by duration

#### Scenario: Category catalog already exists
- **WHEN** a category is selected and its catalog is available
- **THEN** the system SHALL use the next uncompleted, non-failed catalog entry directly without rescanning pages 1 through 5

#### Scenario: Saved catalog has become stale
- **WHEN** a saved course cannot be found anywhere in the current first five pages
- **THEN** the system SHALL rebuild that category catalog once and continue selection without consuming a course playback failure attempt

#### Scenario: Catalog entry is completed
- **WHEN** a catalog entry finishes normal playback
- **THEN** the system SHALL persist its completion and continue with the next entry in duration order

## Purpose

为已登录用户提供可验证的课程自动化流程，确保每一轮确实读取了最新学时、选择了符合规则的课程并完成了真实的视频播放。

## ADDED Requirements

### Requirement: Read credit data from the active credit-system page

The system SHALL identify and use the page that displays the credit-management dashboard after navigation, including when that dashboard opens in a new tab.

#### Scenario: Credit system opens a new tab
- **WHEN** the user activates the credit-system entry from the course page
- **THEN** the system SHALL wait for the new page, use it for credit extraction, and retain the course page for returning to course selection

#### Scenario: Credit dashboard cannot be found
- **WHEN** navigation does not produce a page containing the credit dashboard markers within the configured timeout
- **THEN** the system SHALL stop the current iteration with an explicit error and SHALL NOT select a course based on empty credit data

### Requirement: Parse independent credit categories

The system SHALL calculate category gaps only from independently labeled completed-credit values and SHALL NOT assign a combined requirement value to an individual category.

#### Scenario: Dashboard contains a combined public-credit requirement
- **WHEN** the dashboard displays a combined requirement such as “行业公需和一般公需”
- **THEN** the parser SHALL ignore that combined line for independent category completion values

#### Scenario: Category is absent from completed values
- **WHEN** a configured category has no independently parsed completed value
- **THEN** the system SHALL treat the value as unknown and stop with a diagnostic error rather than silently treating it as zero

### Requirement: Select the shortest available course

The system SHALL select the shortest course among all available result pages for the selected category, or explicitly report that pagination cannot be evaluated.

#### Scenario: Multiple result pages exist
- **WHEN** the query result contains pagination
- **THEN** the system SHALL inspect each available result page before selecting a course

#### Scenario: No courses are available
- **WHEN** the selected category query returns no course cards
- **THEN** the system SHALL stop the iteration with a clear no-course diagnostic

### Requirement: Verify playback before advancing

The system SHALL require a successful play action and a real video completion signal before closing the course and starting another iteration.

#### Scenario: Play controls are missing
- **WHEN** the detail or playback page lacks the expected learning or play control
- **THEN** the system SHALL fail the iteration explicitly and SHALL NOT report the course as completed

#### Scenario: Video completes
- **WHEN** the video element emits a completion signal and its current time reaches its known duration
- **THEN** the system SHALL mark the course as completed and proceed to cleanup

#### Scenario: Playback times out or the page disappears
- **WHEN** no valid completion signal is received before the timeout, or the playback page is closed or navigates unexpectedly
- **THEN** the system SHALL report failure and SHALL NOT advance the learning loop as if the course completed

### Requirement: Handle confirmation dialogs without masking failures

The system SHALL automatically confirm supported confirmation dialogs while preserving explicit errors from the underlying course operation.

#### Scenario: Confirmation dialog appears during playback
- **WHEN** a supported confirmation dialog is visible
- **THEN** the system SHALL confirm it and continue monitoring playback

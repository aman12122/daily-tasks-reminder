# Requirements Document

## Document Info

| Field | Value |
|-------|-------|
| Project | Daily Tasks Reminder System |
| Version | 1.0 |
| Status | Draft |

---

## Functional Requirements

### Core Features (MVP)

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-001 | System shall read the "Daily Tasks" note from Apple Notes | Must Have |
| FR-002 | System shall identify unchecked (incomplete) items from the note | Must Have |
| FR-003 | System shall send an SMS containing all unchecked items | Must Have |
| FR-004 | System shall trigger automatically at 10:00 PM daily | Must Have |
| FR-005 | System shall send "All tasks completed." if no unchecked items exist | Must Have |
| FR-006 | System shall format the message with bullet points | Must Have |

### Future Features

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-007 | System shall support multiple notes (Work Tasks, Personal Tasks, Others) | Future |
| FR-008 | System shall send a morning briefing SMS at 7:00 AM | Future |
| FR-009 | System shall send an optional midday check-in SMS | Future |
| FR-010 | System shall include next-day calendar events in the 10pm message | Future |

---

## Non-Functional Requirements

| ID | Requirement | Category |
|----|-------------|----------|
| NFR-001 | SMS shall be delivered within 60 seconds of trigger time | Performance |
| NFR-002 | Automation shall run in background without interrupting user activity | Usability |
| NFR-003 | System shall work on iOS 26.2 and later | Compatibility |
| NFR-004 | Twilio credentials shall be stored within the Shortcut only | Security |
| NFR-005 | System shall require no manual intervention for daily operation | Reliability |

---

## User Stories

| ID | User Story | Acceptance Criteria |
|----|------------|---------------------|
| US-001 | As a user, I want to receive an SMS at 10pm with my incomplete tasks so I can review what slipped through the cracks | SMS received at 10pm containing unchecked items |
| US-002 | As a user, I want the message formatted clearly so I can quickly scan remaining items | Message uses bullet points with one task per line |
| US-003 | As a user, I want confirmation if all tasks are done so I know I completed everything | "All tasks completed." message sent when list is empty |
| US-004 | As a user, I want the automation to run silently so it doesn't interrupt what I'm doing | No prompts, popups, or full-screen takeovers |

---

## Assumptions

| ID | Assumption |
|----|------------|
| A-001 | User has an iPhone running iOS 26.2 or later |
| A-002 | User has a valid Twilio account with sufficient balance |
| A-003 | A note titled "Daily Tasks" exists in Apple Notes |
| A-004 | Tasks in the note use Apple Notes' checkbox format |
| A-005 | iPhone is powered on and connected to internet at 10:00 PM |
| A-006 | User's phone number can receive SMS from Twilio |

---

## Constraints

| ID | Constraint | Impact |
|----|------------|--------|
| C-001 | Limited to iOS Shortcuts capabilities | Some advanced logic may not be possible |
| C-002 | Dependent on Twilio for SMS delivery | Subject to Twilio service availability |
| C-003 | Requires active internet connection | No offline fallback |
| C-004 | Cannot run if iPhone is powered off | Missed notifications on those nights |
| C-005 | Apple Notes has no external API | Must use Shortcuts' native Notes actions |

---

## Acceptance Criteria (MVP)

The MVP is considered complete when:

- [ ] At 10:00 PM, the Shortcut triggers automatically
- [ ] The Shortcut reads the "Daily Tasks" note without user intervention
- [ ] Unchecked items are correctly identified and extracted
- [ ] An SMS is received within 60 seconds containing the unchecked items
- [ ] The message format matches the specified template
- [ ] If all items are checked, the message reads "All tasks completed."
- [ ] The entire process runs without any user prompts or interruptions

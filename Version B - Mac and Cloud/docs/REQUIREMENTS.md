# Requirements Document - Version B

## Document Info

| Field | Value |
|-------|-------|
| Project | Daily Tasks Reminder System |
| Version | 2.0 (Mac + Cloud) |
| Architecture | Hybrid (Local Sync + Serverless Delivery) |
| Status | Draft |

---

## Functional Requirements

### Core Features (MVP)

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-001 | **Mac Agent:** System shall read the "Daily Tasks" note from Apple Notes on the local Mac | Must Have |
| FR-002 | **Mac Agent:** System shall parse the note and extract unchecked items into a JSON format | Must Have |
| FR-003 | **Mac Agent:** System shall upload the JSON data to a secure AWS S3 bucket | Must Have |
| FR-004 | **Mac Agent:** System shall run automatically in the background (via launchd) every 1 hour | Must Have |
| FR-005 | **Cloud Trigger:** System shall trigger an AWS Lambda function at 10:00 PM local time daily | Must Have |
| FR-006 | **Cloud Logic:** Lambda function shall fetch the latest JSON from S3 | Must Have |
| FR-008 | **Note Format:** User shall format tasks using text-based checkboxes (`[ ]` for unfinished, `[x]` for finished) instead of native Note checklists | Must Have |

---

## Non-Functional Requirements

| ID | Requirement | Category |
|----|-------------|----------|
| NFR-001 | **Zero Cost:** System shall operate within AWS Free Tier limits ($0.00/month) | Cost |
| NFR-002 | **Staleness:** System shall acknowledge that data is only as fresh as the last Mac sync event | Data Integrity |
| NFR-003 | **Security:** AWS credentials shall not be hardcoded; S3 bucket shall not be public | Security |
| NFR-004 | **Reliability:** SMS shall be sent even if the Mac is powered off at 10:00 PM | Reliability |
| NFR-005 | **Resilience:** Lambda shall fail gracefully if the S3 file is missing or empty | Robustness |

---

## User Stories

| ID | User Story | Acceptance Criteria |
|----|------------|---------------------|
| US-001 | As a user, I want to receive my reminder even if my laptop is in my backpack at 10pm | SMS received while Mac is sleeping/off |
| US-002 | As a user, I want the system to cost nothing so I don't incur monthly fees for a simple reminder | AWS billing dashboard remains at $0.00 |
| US-003 | As a user, I want the data to sync automatically without me running a script manually | Updates in Notes app appear in evening SMS |

---

## Assumptions & Constraints

| ID | Type | Description |
|----|------|-------------|
| A-001 | Assumption | User's Mac is powered on and connected to internet at least once during the day |
| A-002 | Assumption | "Daily Tasks" note structure remains consistent (HTML/Text format) |
| C-001 | Constraint | AWS Free Tier limits (5GB S3, 400k Lambda seconds) |
| C-002 | Constraint | AppleScript requires local execution context (cannot run on AWS) |

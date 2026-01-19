# Build Plan - Version B

## Document Info
| Field | Value |
|-------|-------|
| Strategy | Incremental (Local -> Cloud -> Automation) |
| Status | In Progress |

---

## Phase 1: Local Data Extraction (Mac)
**Goal:** Successfully read and parse Apple Notes data into JSON on the local machine.

| ID | Task | Status |
|----|------|--------|
| 1.1 | Write `sync_tasks.py` probe to fetch raw Apple Notes HTML | **Pending** |
| 1.2 | Analyze raw HTML structure to identify checkbox patterns | **Pending** |
| 1.3 | Implement parsing logic in Python to extract unchecked items | **Pending** |
| 1.4 | Generate valid `tasks.json` output locally | **Pending** |

---

## Phase 2: Cloud Storage (AWS S3)
**Goal:** Sync local JSON data to the cloud securely.

| ID | Task | Status |
|----|------|--------|
| 2.1 | Configure AWS CLI on Mac (`aws configure`) | **Pending** |
| 2.2 | Create private S3 bucket (e.g., `daily-tasks-reminder-data`) | **Pending** |
| 2.3 | Create IAM User for Mac with restricted `s3:PutObject` policy | **Pending** |
| 2.4 | Update `sync_tasks.py` to upload JSON to S3 | **Pending** |
| 2.5 | Verify file appears in AWS Console | **Pending** |

---

## Phase 3: Serverless Logic (AWS Lambda)
**Goal:** Read data from cloud and send SMS.

| ID | Task | Status |
|----|------|--------|
| 3.1 | Create Lambda function `daily_task_notifier` (Python) | **Pending** |
| 3.2 | Attach IAM role with `s3:GetObject` permission | **Pending** |
| 3.3 | Implement logic: Read S3 -> Filter Unchecked -> Format Message | **Pending** |
| 3.4 | Implement Twilio API integration (using `requests` or `urllib`) | **Pending** |
| 3.5 | Test Lambda manually (Test Event) | **Pending** |

---

## Phase 4: Automation & Scheduling
**Goal:** Automate the entire pipeline.

| ID | Task | Status |
|----|------|--------|
| 4.1 | **Mac:** Create `com.user.dailytasks.plist` for `launchd` (Hourly sync) | **Pending** |
| 4.2 | **Mac:** Load and start the background daemon | **Pending** |
| 4.3 | **Cloud:** Create EventBridge Schedule (Cron) for 10:00 PM | **Pending** |
| 4.4 | **End-to-End Test:** Create task -> Wait for sync -> Wait for trigger -> Receive SMS | **Pending** |

---

## Rollback Plan
If AWS costs trigger or integration fails:
1. Delete S3 Bucket and Lambda Function.
2. Unload `launchd` job on Mac (`launchctl unload ...`).
3. Revert to Version A (iOS Shortcuts).

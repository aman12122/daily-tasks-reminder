# Build Plan

## Document Info

| Field | Value |
|-------|-------|
| Project | Daily Tasks Reminder System |
| Version | 1.0 |
| Approach | MVP First (Incremental) |

---

## Overview

This build plan follows an incremental approach, starting with the simplest working version and adding complexity in layers. Each phase produces a testable, functional system.

```
Phase 1          Phase 2          Phase 3          Phase 4          Phase 5
────────────────────────────────────────────────────────────────────────────▶

[Foundation] ──▶ [Notes] ──▶ [Formatting] ──▶ [Automation] ──▶ [Polish]
 Test SMS        Read Note    Message Format    10pm Trigger     Edge Cases
 Works           Works        Works             Works            Handled
```

---

## Phase 1: Foundation

**Goal:** Verify Twilio SMS delivery works from iOS Shortcuts

### Tasks

| # | Task | Description |
|---|------|-------------|
| 1.1 | Create new Shortcut | Name: "Daily Tasks Reminder" |
| 1.2 | Add "Get Contents of URL" action | Configure for Twilio API |
| 1.3 | Configure authentication | Set up Basic Auth with Account SID and Auth Token |
| 1.4 | Set request body | Hardcode a test message: "Test from Daily Tasks Reminder" |
| 1.5 | Run manually | Tap the Shortcut to execute |
| 1.6 | Verify SMS received | Confirm message arrives on phone |

### Definition of Done

- [ ] Shortcut created and configured
- [ ] Manual execution sends SMS successfully
- [ ] SMS received within 60 seconds

### Test Case

| Input | Expected Output |
|-------|-----------------|
| Run Shortcut manually | Receive SMS: "Test from Daily Tasks Reminder" |

### Rollback

If Twilio integration fails:
1. Verify Account SID and Auth Token are correct
2. Confirm Twilio phone number is valid and active
3. Check Twilio console for error logs
4. Verify recipient phone number is verified (required for trial accounts)

---

## Phase 2: Notes Integration

**Goal:** Read content from the "Daily Tasks" note

### Prerequisites

- [ ] Phase 1 completed successfully
- [ ] "Daily Tasks" note exists in Apple Notes with sample tasks

### Tasks

| # | Task | Description |
|---|------|-------------|
| 2.1 | Add "Find Notes" action | Filter: Name is "Daily Tasks" |
| 2.2 | Add "Get Text from Input" action | Extract note body as text |
| 2.3 | Replace hardcoded message | Use note content as SMS body |
| 2.4 | Run manually | Test with sample note |
| 2.5 | Verify SMS contains note content | Confirm raw note text is received |

### Definition of Done

- [ ] Shortcut reads "Daily Tasks" note
- [ ] SMS contains the note's content (unformatted is OK for now)

### Test Case

| Input | Expected Output |
|-------|-----------------|
| Note contains 3 tasks (2 unchecked, 1 checked) | SMS shows full note content |

### Rollback

If Notes integration fails:
1. Verify note is named exactly "Daily Tasks" (case-sensitive)
2. Check that Shortcuts has permission to access Notes
3. Test with a simpler note (plain text, no checkboxes)

---

## Phase 3: Message Formatting

**Goal:** Parse note content and format message correctly

### Prerequisites

- [ ] Phase 2 completed successfully

### Tasks

| # | Task | Description |
|---|------|-------------|
| 3.1 | Add text parsing logic | Split note by lines, identify unchecked items |
| 3.2 | Filter unchecked items | Keep only lines with unchecked checkbox markers |
| 3.3 | Format as bullet list | Prefix each item with "• " |
| 3.4 | Add message header | Prepend "📋 Tonight's unfinished items:" |
| 3.5 | Handle empty list | If no unchecked items, set message to "All tasks completed." |
| 3.6 | Test with mixed items | Note with some checked, some unchecked |
| 3.7 | Test with all checked | Verify "All tasks completed." is sent |

### Definition of Done

- [ ] Only unchecked items appear in SMS
- [ ] Message format matches specification
- [ ] Empty list shows "All tasks completed."

### Test Cases

| Input | Expected Output |
|-------|-----------------|
| 2 unchecked, 1 checked | SMS shows only 2 items as bullets |
| All items checked | SMS: "All tasks completed." |
| Empty note | SMS: "All tasks completed." |

### Rollback

If parsing fails:
1. Check checkbox character encoding (may vary)
2. Simplify to match any line containing specific text
3. Test with manually typed checkboxes vs. Notes-native checkboxes

---

## Phase 4: Automation

**Goal:** Set up 10pm daily trigger with background execution

### Prerequisites

- [ ] Phase 3 completed successfully

### Tasks

| # | Task | Description |
|---|------|-------------|
| 4.1 | Open Shortcuts app | Navigate to Automation tab |
| 4.2 | Create Personal Automation | Select "Time of Day" |
| 4.3 | Set time to 10:00 PM | Daily repeat |
| 4.4 | Select "Run Immediately" | Enables background execution |
| 4.5 | Add action: Run Shortcut | Select "Daily Tasks Reminder" |
| 4.6 | Disable "Notify When Run" | Optional: reduces notification noise |
| 4.7 | Wait for 10pm | Let automation trigger naturally |
| 4.8 | Verify SMS received | Confirm message arrives without intervention |

### Definition of Done

- [ ] Automation triggers at 10:00 PM
- [ ] SMS received without any user interaction
- [ ] No disruptive prompts or popups

### Test Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Phone in use at 10pm | SMS arrives, no interruption |
| Phone locked at 10pm | SMS arrives |
| Phone on Do Not Disturb | SMS arrives (notification may be silenced) |

### Rollback

If automation fails:
1. Verify automation is enabled (not paused)
2. Check that "Run Immediately" is selected
3. Ensure Shortcuts app has notification permissions
4. Test by setting trigger to 1 minute in future

---

## Phase 5: Polish & Documentation

**Goal:** Handle edge cases and finalize documentation

### Prerequisites

- [ ] Phase 4 completed successfully

### Tasks

| # | Task | Description |
|---|------|-------------|
| 5.1 | Test note not found | Rename note temporarily, verify error handling |
| 5.2 | Test empty note | Clear all content, verify behavior |
| 5.3 | Test special characters | Add tasks with emojis, punctuation |
| 5.4 | Test long task list | 10+ unchecked items |
| 5.5 | Update README.md | Mark implementation as complete |
| 5.6 | Record any issues | Document known limitations |
| 5.7 | Create backup | Export Shortcut (without sharing) |

### Definition of Done

- [ ] All edge cases tested
- [ ] Documentation updated
- [ ] System running reliably for 3+ days

### Edge Cases to Test

| Case | Expected Behavior |
|------|-------------------|
| Note named differently | Error message or graceful failure |
| Note with no checkboxes | Treat as all complete or empty |
| Very long message (>1600 chars) | Twilio splits into multiple SMS |
| No internet at 10pm | Fails silently, no SMS |

---

## Phase Summary

| Phase | Deliverable | Est. Effort |
|-------|-------------|-------------|
| Phase 1: Foundation | Working Twilio SMS from Shortcut | 15 min |
| Phase 2: Notes Integration | Shortcut reads Daily Tasks note | 10 min |
| Phase 3: Formatting | Parsed, formatted message | 20 min |
| Phase 4: Automation | 10pm daily trigger | 10 min |
| Phase 5: Polish | Tested, documented system | 15 min |

**Total Estimated Effort:** ~70 minutes

---

## Current Status

| Phase | Status |
|-------|--------|
| Phase 1: Foundation | **Completed** |
| Phase 2: Notes Integration | **Completed** |
| Phase 3: Formatting | **Completed** |
| Phase 4: Automation | **Completed** |
| Phase 5: Polish | **Completed** |

---

## Final Project Status
**COMPLETE** - All MVP requirements met. System is live and automated.
| Phase 5: Polish | Not Started |

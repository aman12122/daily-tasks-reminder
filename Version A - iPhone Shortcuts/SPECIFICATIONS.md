# Technical Specifications

## Document Info

| Field | Value |
|-------|-------|
| Project | Daily Tasks Reminder System |
| Version | 1.0 |
| Status | Draft |

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         iPhone                                   │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │ Apple Notes  │───▶│ iOS Shortcut │───▶│ HTTP Request │       │
│  │ "Daily Tasks"│    │  (10pm)      │    │              │       │
│  └──────────────┘    └──────────────┘    └──────┬───────┘       │
│                                                  │               │
└──────────────────────────────────────────────────│───────────────┘
                                                   │
                                                   ▼
                                          ┌──────────────┐
                                          │  Twilio API  │
                                          │              │
                                          └──────┬───────┘
                                                 │
                                                 ▼
                                          ┌──────────────┐
                                          │  SMS to User │
                                          │  +1 (Canada) │
                                          └──────────────┘
```

---

## Components

| Component | Type | Description |
|-----------|------|-------------|
| Apple Notes | Data Source | Stores "Daily Tasks" note with checkbox items |
| iOS Shortcuts | Automation Engine | Reads note, parses content, sends HTTP request |
| Twilio API | External Service | Receives HTTP request, delivers SMS |
| User's Phone | Receiver | Receives SMS notification |

---

## Data Flow

### Sequence of Operations

```
1. [10:00 PM] iOS triggers the Shortcut automation
                    │
                    ▼
2. Shortcut action: "Find Notes where Name is 'Daily Tasks'"
                    │
                    ▼
3. Shortcut action: "Get Body" from the note
                    │
                    ▼
4. Shortcut action: Parse text to find unchecked items
   - Split by newlines
   - Filter lines starting with "☐" or unchecked marker
                    │
                    ▼
5. Shortcut action: Construct message body
   - If items exist → format as bullet list
   - If no items → "All tasks completed."
                    │
                    ▼
6. Shortcut action: "Get Contents of URL" (HTTP POST to Twilio)
                    │
                    ▼
7. Twilio receives request, sends SMS
                    │
                    ▼
8. User receives SMS on their phone
```

---

## API Specifications

### Twilio Messages API

| Field | Value |
|-------|-------|
| Endpoint | `https://api.twilio.com/2010-04-01/Accounts/{AccountSID}/Messages.json` |
| Method | POST |
| Authentication | Basic Auth |
| Content-Type | application/x-www-form-urlencoded |

### Request Headers

| Header | Value |
|--------|-------|
| Authorization | Basic {Base64(AccountSID:AuthToken)} |
| Content-Type | application/x-www-form-urlencoded |

### Request Body Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| To | Recipient phone number (E.164 format) | +1XXXXXXXXXX |
| From | Twilio phone number | +1XXXXXXXXXX |
| Body | Message content | See message format below |

### Response (Success)

| Field | Value |
|-------|-------|
| Status Code | 201 Created |
| Body | JSON object with message SID |

### Response (Error)

| Status Code | Meaning |
|-------------|---------|
| 400 | Bad request (invalid parameters) |
| 401 | Authentication failed |
| 404 | Account not found |
| 429 | Rate limit exceeded |

---

## Message Format

### When Unchecked Items Exist

```
📋 Tonight's unfinished items:
• Task 1
• Task 2
• Task 3
```

### When All Items Checked

```
All tasks completed.
```

---

## Parsing Logic

### Apple Notes Checkbox Format

When exported via Shortcuts, Apple Notes checkboxes appear as:

| State | Character |
|-------|-----------|
| Unchecked | ☐ (Unicode: U+2610) or similar marker |
| Checked | ☑ (Unicode: U+2611) or similar marker |

### Parsing Steps

1. Get full note body as text
2. Split into lines
3. For each line:
   - Check if it starts with an unchecked marker
   - If yes, extract the task text (remove the checkbox character)
   - Add to list of incomplete items
4. If list is empty → all tasks complete
5. If list has items → format as bullet list

---

## Error Handling

| Scenario | Behavior |
|----------|----------|
| "Daily Tasks" note not found | Send SMS: "Error: Daily Tasks note not found" |
| Note exists but is empty | Send SMS: "All tasks completed." |
| Twilio API returns error | Shortcut fails silently (iOS limitation) |
| No internet connection | Shortcut fails silently (iOS limitation) |
| Invalid Twilio credentials | Shortcut fails silently (iOS limitation) |

### Limitations

iOS Shortcuts has limited error handling capabilities:
- No persistent logging
- No retry mechanism
- No failure notifications

For MVP, we accept these limitations. Future iterations could explore workarounds.

---

## Security Considerations

| Concern | Mitigation |
|---------|------------|
| Twilio Auth Token exposure | Store only within Shortcut; do not share Shortcut file |
| SMS content privacy | Messages contain only task titles, no sensitive data |
| Phone number privacy | Stored only within Shortcut configuration |

### Recommendations

1. Do not export or share the Shortcut file (contains credentials)
2. Consider using Twilio API Keys instead of main Auth Token for reduced scope
3. Regularly rotate Auth Token if security is a concern

---

## Technical Constraints

| Constraint | Details |
|------------|---------|
| No background processing on iOS | Shortcut runs only at trigger time |
| No persistent storage | Cannot cache or store state between runs |
| No external server | All logic must run within iOS Shortcuts |
| Twilio trial limitations | May have sending limits or require verified numbers |

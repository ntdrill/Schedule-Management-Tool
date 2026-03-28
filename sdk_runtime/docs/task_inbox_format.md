# Task Inbox Format (DRAFT)

This document defines the draft JSON format for files placed in Task_Inbox.

## Envelope
- `id`: unique task id (string)
- `type`: task type string
- `created_at`: ISO8601 timestamp (UTC)
- `source`: origin of the task (watcher/orchestrator/manual)

## Payload
- `payload`: type-specific object

## Example
```json
{
  "id": "task_123",
  "type": "watch_event",
  "created_at": "2026-02-08T12:00:00Z",
  "source": "orchestrator",
  "payload": {
    "watcher": "taskfolder",
    "added": ["..."],
    "removed": [],
    "modified": ["..."]
  }
}
```

# Ultron V1: WebSocket Interface & Contract Specification
*Document Version: 1.0.1 — WebSocket API Contract Specification*

This document provides a highly detailed, professional engineering contract of all WebSocket communication channels planned for **Phase 8 (WebSocket Layer)** and **Phase 9 (Voice System)**.

---

## 1. Overview of Communication Channels

```
                           ULTRON WEBSOCKET ENDPOINT TREE
                             ws://localhost:8000/
                                       │
         ┌──────────────┬──────────────┼──────────────┬──────────────┐
         ▼              ▼              ▼              ▼              ▼
     ws/chat        ws/voice       ws/events       ws/logs     ws/dashboard
  (Token Stream)  (Live Audio)   (Server Push)  (System Logs)  (RAM/CPU Metrics)
```

---

## 2. Channel 1: `ws/chat` (Main Conversation)
Handles real-time token streaming, active tool progress alerts, and floating widget triggers.

### A. Client Sends (Message Payload)
```json
{
  "type": "user_message",
  "session_id": "sess_98452_abc",
  "content": "Can you check my git status?"
}
```

### B. Server Streams (Progress Payload)
```json
{
  "type": "progress",
  "state": "analyzing_git",
  "detail": "Executing 'git status' on local directory..."
}
```

### C. Server Streams (Token Payload)
```json
{
  "type": "token",
  "content": "You are on "
}
```

### D. Server Streams (Widget Activation Payload)
```json
{
  "type": "widget",
  "widget_name": "GitWidget",
  "action": "open",
  "data": {
    "branch": "main",
    "uncommitted_files": ["src/App.jsx"],
    "conflicts": []
  }
}
```

---

## 3. Channel 2: `ws/voice` (Duplex Audio & Interrupts)
Manages binary audio streaming, continuous browser-transcribed inputs, and immediate barge-in (interruption) handshakes.

### A. Client Sends (Voice Start)
```json
{
  "type": "voice_start"
}
```

### B. Client Streams (Web Speech transcriptions)
```json
{
  "type": "transcript_chunk",
  "text": "actually, wait, stop.",
  "is_final": true
}
```

### C. Server Streams (Base64 audio chunks)
```json
{
  "type": "tts_chunk",
  "audio_data": "BASE64_ENCODED_BINARY_AUDIO_BYTES..."
}
```

### D. Client Sends (Barge-In Interrupt)
```json
{
  "type": "interrupt",
  "timestamp": "2026-07-31T01:18:02.124Z"
}
```

### E. Server Acknowledges Interrupt
```json
{
  "type": "interrupt_acknowledged",
  "last_spoken_sentence": "I was thinking..."
}
```

---

## 4. Channel 3: `ws/events` (Server Push Pipeline)
Provides asynchronous, server-initiated pushes for calendar reminders, background task alerts, and automated Zora triggers.

### A. Server Pushes (Automatic Zora Handoff Alert)
```json
{
  "type": "zora_auto_trigger",
  "reason": "Stress score 0.812 reached.",
  "message": "Hey... You okay? Let's take a break."
}
```

### B. Server Pushes (Active Reminder Alert)
```json
{
  "type": "reminder_trigger",
  "reminder_id": "rem_145",
  "title": "Time to test the billing middleware.",
  "timestamp": "2026-07-31T02:00:00Z"
}
```

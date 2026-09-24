# PersonalizedMeet AI Integration

This module is the AI processing service for the **Personalized Privacy-Aware Meeting Intelligence System**.

It is separate from:

- `PersonalizedMeet-backend` - Spring Boot APIs and PostgreSQL metadata
- `PersonalizedMeet-frontend` - React UI, implemented later

This service receives a recording reference from the backend, processes the recording, and returns a structured speaker-wise transcript.

## Current Scope

Implemented in this phase:

1. Speech-to-text service using `faster-whisper`.
2. Speaker diarization service using `pyannote.audio`.
3. FFmpeg-based audio extraction to normalize recordings into temporary WAV files.
4. Timestamp overlap alignment.
5. API endpoint for processing one recording.
6. Structured JSON response with speaker labels, timestamps, and text.
7. Speaker-wise transcripts grouped from the aligned segments.
8. Deterministic meeting information extraction for repeated-keyword topics, decision-style statements, and action-oriented statements.

Not implemented yet:

- participant name mapping
- speaker identity recognition
- sensitivity classification
- privacy filtering
- personalized summaries
- LLM integration
- frontend integration
- direct database writes

## Recommended Runtime

Use Python **3.10 or 3.11**.

The current machine reports Python 3.14.3, but major AI audio libraries such as `pyannote.audio`, `torch`, and `faster-whisper` are usually best supported on Python 3.10/3.11. Create a virtual environment with one of those versions before installing the full AI dependencies.

## Installation

From this folder:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If `py -3.11` is not available, install Python 3.11 first.

## FFmpeg Requirement

FFmpeg is required because uploaded recordings can arrive as containers such as MP4 or WebM. Before running `faster-whisper` or `pyannote.audio`, this service extracts the recording audio into one temporary WAV file and reuses that same WAV for both transcription and speaker diarization.

If `ffmpeg` is available on `PATH`, no extra configuration is needed. If it is installed elsewhere, set `FFMPEG_PATH` to the full executable path.

Example Windows configuration:

```powershell
$env:FFMPEG_PATH="C:\Path\To\ffmpeg\bin\ffmpeg.exe"
```

Or in `.env`:

```text
FFMPEG_PATH=C:\Path\To\ffmpeg\bin\ffmpeg.exe
```

## Configuration

Copy `.env.example` to `.env` and fill local values:

```powershell
Copy-Item .env.example .env
```

Important settings:

- `WHISPER_MODEL_SIZE`: Whisper model size, for example `base`, `small`, `medium`.
- `WHISPER_DEVICE`: `cpu` or `cuda`.
- `WHISPER_COMPUTE_TYPE`: `int8` for CPU-friendly use, or GPU-specific values if available.
- `PYANNOTE_MODEL`: default is `pyannote/speaker-diarization-3.1`.
- `HUGGINGFACE_TOKEN`: required for pyannote diarization models.
- `FFMPEG_PATH`: optional path to the FFmpeg executable. Defaults to `ffmpeg`.
- `ALLOWED_RECORDING_ROOTS`: optional safety setting restricting readable recording paths.
- `TOPIC_STOP_WORDS`: optional comma-separated words excluded from deterministic topic extraction.
- `TOPIC_MIN_OCCURRENCES`: minimum occurrences required for a word to be returned as a topic. Defaults to `2`.
- `DECISION_PATTERNS`: optional comma-separated phrases used to find source-backed decision statements.
- `ACTION_ITEM_PATTERNS`: optional comma-separated phrases used to find source-backed action-item statements.

Do not commit `.env` or real tokens.

## Hugging Face / Pyannote Requirement

Speaker diarization uses `pyannote.audio`, which requires:

1. A Hugging Face account.
2. Accepting the model terms for the selected pyannote model.
3. A Hugging Face access token set as `HUGGINGFACE_TOKEN`.

If the token is missing, the API returns a meaningful configuration error instead of silently failing.

## Start the Service

```powershell
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 9000
```

Health check:

```text
GET http://localhost:9000/api/health
```

## Process a Recording

Endpoint:

```text
POST http://localhost:9000/api/process-recording
```

Example request:

```json
{
  "recordingId": 2,
  "filePath": "C:/Users/Diksh/OneDrive/Documents/AI Assistant/PersonalizedMeet/PersonalizedMeet-backend/uploads/meeting-recordings/example.mp4"
}
```

Example response:

```json
{
  "recordingId": 2,
  "segments": [
    {
      "speaker": "SPEAKER_00",
      "startTime": 0.0,
      "endTime": 5.8,
      "text": "Good morning everyone."
    },
    {
      "speaker": "SPEAKER_01",
      "startTime": 6.2,
      "endTime": 12.4,
      "text": "The expansion proposal is ready."
    }
  ],
  "speakers": [
    {
      "speaker": "SPEAKER_00",
      "segments": [
        {
          "startTime": 0.0,
          "endTime": 5.8,
          "text": "Good morning everyone."
        }
      ],
      "fullTranscript": "Good morning everyone."
    }
  ],
  "meetingInformation": {
    "topics": [],
    "decisions": [],
    "actionItems": [],
    "peopleMentioned": []
  }
}
```

## Meeting Information Extraction

After timestamp alignment, the service keeps the original `segments` response and also groups them into chronological, speaker-wise transcripts. It then derives basic meeting information from the transcript using deterministic rules only:

- Topics are repeated meaningful words after configured stop words are excluded.
- Decisions and action items are original segments matching configurable rule phrases, with their speaker and timestamps preserved.
- `peopleMentioned` is currently empty by design; named-entity recognition is deferred rather than guessing names.

This is a conservative factual layer, not semantic understanding. An LLM-based extraction service can later enhance or replace it without changing the transcription, diarization, or alignment pipeline.

## Run Tests

From this folder with the virtual environment activated:

```powershell
python -m pytest
```

## How Speech-to-Text Works

`TranscriptionService` loads `faster-whisper` and returns timestamped text segments:

```json
{
  "start": 12.5,
  "end": 17.8,
  "text": "The proposed budget has been approved."
}
```

Timestamps are preserved because they are needed later for speaker attribution and privacy-aware information extraction.

## How Speaker Diarization Works

`DiarizationService` loads a pyannote speaker diarization pipeline. It identifies time ranges where anonymous speakers are active:

```text
SPEAKER_00: 0.0 -> 5.8
SPEAKER_01: 6.2 -> 12.4
```

This phase does not identify real people. Speaker labels remain anonymous.

## Alignment Strategy

`TranscriptService` aligns each transcription segment to the diarization segment with the largest timestamp overlap.

For example:

- transcription: `6.3 -> 12.2`
- diarization: `SPEAKER_01 6.2 -> 12.4`
- result: transcription text is assigned to `SPEAKER_01`

If no overlap exists, the segment is assigned to `UNKNOWN_SPEAKER`.

This approach is simple, readable, and suitable for the current backend foundation. It can be improved later with word-level timestamps or sentence splitting.

## Backend Communication

The Spring Boot backend should later call this AI API after a recording is uploaded.

Planned flow:

```text
Spring Boot Backend
    -> AI Processing API
    -> AI-Integration
    -> structured transcript JSON
    -> Spring Boot Backend
```

This AI service does not query PostgreSQL directly and does not modify backend database records.

## Limitations

- Requires separate model installation/downloads.
- Pyannote requires a Hugging Face token and accepted model terms.
- Speaker labels are anonymous.
- Real participant-to-speaker mapping is not implemented.
- Privacy filtering and personalized summaries are not implemented yet.
- Python 3.10/3.11 is recommended for the actual AI runtime.

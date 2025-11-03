# VR-Therapist Server API Reference

## Overview

This document provides technical details about the VR-Therapist server's internal APIs and functions.

## Server Endpoints

### Base URL
```
http://localhost:5000
```

### POST /process_wav

Process patient speech audio file.

**Request:**
```http
POST /process_wav HTTP/1.1
Content-Type: application/x-www-form-urlencoded

path=<base_path>&loaded_wav_file=patient_speech
```

**Parameters:**
- `path` (string): Base directory path where audio files are stored
- `loaded_wav_file` (string): Must be "patient_speech" to trigger processing

**Response:**
```json
{
  "status": "done"
}
```

**Behavior:**
- Sets the base path for audio file operations
- Flags that patient speech is ready for processing
- Does NOT immediately process the audio (use `/check_status` for that)

**Example:**
```python
import requests

response = requests.post('http://localhost:5000/process_wav', data={
    'path': 'C:/audio/session1/',
    'loaded_wav_file': 'patient_speech'
})
print(response.json())  # {"status": "done"}
```

### POST /reset_conversation

Clear conversation history and reset chat context.

**Request:**
```http
POST /reset_conversation HTTP/1.1
Content-Type: application/x-www-form-urlencoded

reset_conversation=yes
```

**Parameters:**
- `reset_conversation` (string): Must be "yes" to confirm reset

**Response:**
```json
{
  "status": "done"
}
```

**Behavior:**
- Clears `chat_history_list` (last 5 responses)
- Clears `message_history` (full conversation context)
- Does NOT reinitialize the AI client

**Example:**
```python
import requests

response = requests.post('http://localhost:5000/reset_conversation', data={
    'reset_conversation': 'yes'
})
print(response.json())  # {"status": "done"}
```

### GET /check_status

Poll for processing completion.

**Request:**
```http
GET /check_status HTTP/1.1
```

**Response (Processing Complete):**
```json
{
  "status": "done"
}
```

**Response (Still Processing):**
```json
{
  "status": "pending"
}
```

**Behavior:**
- Returns "pending" if no patient speech to process
- Returns "done" after successful processing
- Triggers the `process()` function on first call after patient speech is uploaded
- Automatically resets the `patient_wav_saved` flag

**Polling Example:**
```python
import requests
import time

while True:
    response = requests.get('http://localhost:5000/check_status')
    if response.json()['status'] == 'done':
        print("Processing complete!")
        break
    time.sleep(1)  # Poll every second
```

## Internal Functions

### therapy_session.py

#### initialize_client(hf_token)

Initialize Hugging Face Inference client.

**Parameters:**
- `hf_token` (str): Hugging Face API token

**Returns:**
- `InferenceClient`: Initialized Hugging Face client

**Example:**
```python
from therapy_session import initialize_client

client = initialize_client("hf_your_token_here")
```

#### initialize_tts()

Initialize Mozilla TTS model (singleton pattern).

**Parameters:** None

**Returns:**
- `TTS`: Initialized TTS instance

**Side Effects:**
- Downloads TTS models on first call (~200MB)
- Caches models in `~/.cache/tts/`
- Sets global `_tts_instance` variable

**Example:**
```python
from therapy_session import initialize_tts

tts = initialize_tts()  # First call: downloads models
tts = initialize_tts()  # Subsequent calls: uses cached instance
```

#### transcribe_audio(input_path)

Transcribe audio file to text using Google Speech Recognition.

**Parameters:**
- `input_path` (str): Path to WAV audio file

**Returns:**
- `str`: Transcribed text or error message

**Error Messages:**
- "Speech recognition could not understand audio"
- "Error occurred during speech recognition: {error}"

**Example:**
```python
from therapy_session import transcribe_audio

text = transcribe_audio("patient_speech.wav")
if "Error" not in text:
    print(f"Patient said: {text}")
```

#### generate_therapist_response(client, prompt_message, hf_token, model_name)

Generate therapist response using Hugging Face Inference API.

**Parameters:**
- `client` (InferenceClient): Hugging Face client
- `prompt_message` (str): Full prompt with instructions and context
- `hf_token` (str): Hugging Face API token (for retry)
- `model_name` (str): Model identifier (default: "meta-llama/Meta-Llama-3-8B-Instruct")

**Returns:**
- `str`: Generated therapist response

**Configuration:**
- Max tokens: 500
- Temperature: 0.7
- Streaming: Yes

**Error Handling:**
- Automatically retries once on failure
- Returns fallback message if both attempts fail

**Example:**
```python
from therapy_session import initialize_client, generate_therapist_response

client = initialize_client("hf_token")
response = generate_therapist_response(
    client=client,
    prompt_message="Patient says: I'm feeling anxious",
    hf_token="hf_token",
    model_name="meta-llama/Meta-Llama-3-8B-Instruct"
)
print(response)
```

#### synthesize_speech(text, output_path)

Synthesize speech using Mozilla TTS.

**Parameters:**
- `text` (str): Text to convert to speech
- `output_path` (str): Output file path (WAV format)

**Returns:**
- `bool`: True if successful, False otherwise

**Side Effects:**
- Creates output directory if it doesn't exist
- Converts .mp3 extension to .wav if needed
- Initializes TTS on first call

**Output Format:**
- Sample rate: 22050 Hz
- Channels: Mono
- Format: WAV (PCM)

**Example:**
```python
from therapy_session import synthesize_speech

success = synthesize_speech(
    text="Hello, how are you feeling today?",
    output_path="output/therapist_speech.wav"
)
if success:
    print("Audio generated successfully")
```

### app.py

#### process()

Main processing function for patient speech.

**Parameters:** None (uses global variables)

**Global Variables Used:**
- `client`: Hugging Face client
- `HF_TOKEN`: API token
- `MODEL_NAME`: AI model name
- `base_wav_path`: Audio file directory
- `chat_history_list`: Recent responses (max 5)
- `message_history`: Full conversation (max 10 messages)

**Workflow:**
1. Transcribe patient audio
2. Build prompt with context
3. Generate therapist response
4. Update conversation history
5. Synthesize speech
6. Save audio file

**Error Handling:**
- Catches and logs all exceptions
- Continues execution even if TTS fails
- Prints full traceback for debugging

**Example Output:**
```
Patient: I'm feeling very stressed today
Therapist: I hear that you're experiencing a lot of stress right now...
Speech synthesized successfully: C:/audio/therapist_speech.wav
```

## Configuration

### config.json

**Schema:**
```json
{
  "HF_TOKEN": "string (required)",
  "MODEL_NAME": "string (optional)"
}
```

**Fields:**

- **HF_TOKEN** (required)
  - Type: String
  - Description: Hugging Face API token
  - Format: "hf_..." (starts with hf_)
  - Obtain from: https://huggingface.co/settings/tokens

- **MODEL_NAME** (optional)
  - Type: String
  - Default: "meta-llama/Meta-Llama-3-8B-Instruct"
  - Description: Hugging Face model for chat completion
  - Examples:
    - "meta-llama/Meta-Llama-3-8B-Instruct"
    - "mistralai/Mistral-7B-Instruct-v0.2"
    - "microsoft/Phi-3-mini-4k-instruct"

## Data Structures

### chat_history_list

Recent therapist responses for prompt context.

**Type:** List[str]

**Max Size:** 5 items (FIFO)

**Example:**
```python
chat_history_list = [
    "Hello, I'm Josh. How are you feeling today?",
    "I understand you're feeling anxious. Can you tell me more?",
    "That sounds challenging. What triggered these feelings?",
    "I see. Have you experienced this before?",
    "Let's explore some coping strategies together."
]
```

### message_history

Full conversation history for context preservation.

**Type:** List[Dict[str, str]]

**Max Size:** 10 items (5 exchanges, FIFO)

**Schema:**
```python
[
    {"role": "patient", "content": "I'm feeling anxious"},
    {"role": "therapist", "content": "I hear that you're anxious..."},
    {"role": "patient", "content": "Yes, it started yesterday"},
    {"role": "therapist", "content": "Tell me what happened yesterday..."}
]
```

## Audio File Conventions

### Input Files

**File:** `{base_wav_path}patient_speech.wav`
- Format: WAV
- Sample rate: Any (16kHz recommended)
- Channels: Mono or Stereo
- Duration: Any (keep under 60 seconds for best results)

### Output Files

**File:** `{base_wav_path}therapist_speech.wav`
- Format: WAV (PCM)
- Sample rate: 22050 Hz
- Channels: Mono
- Bit depth: 16-bit

## Error Codes and Messages

### Hugging Face API Errors

| Error | Meaning | Solution |
|-------|---------|----------|
| "Invalid token" | Token is wrong or expired | Check config.json |
| "Rate limit exceeded" | Too many requests | Wait or upgrade plan |
| "Model not found" | Model name incorrect | Verify model name |
| "Model requires authentication" | License not accepted | Accept model license |

### TTS Errors

| Error | Meaning | Solution |
|-------|---------|----------|
| "Failed to initialize TTS" | Model download failed | Check internet, disk space |
| "Could not load model" | Cache corrupted | Clear ~/.cache/tts |
| "Error synthesizing speech" | Generation failed | Check text length, format |

### Transcription Errors

| Error | Meaning | Solution |
|-------|---------|----------|
| "Speech recognition could not understand audio" | Audio unclear | Improve audio quality |
| "Error occurred during speech recognition" | API failure | Check internet connection |

## Performance Metrics

### Response Times

**Typical values:**
- `transcribe_audio()`: 0.5-2s
- `generate_therapist_response()`: 1-3s (first call may be slower)
- `synthesize_speech()`: 1-5s (first call: 3-5s, subsequent: 1-2s)
- **Total processing time:** 2.5-10s

### Resource Usage

**Memory:**
- Flask server: ~50MB
- Hugging Face client: ~20MB
- TTS models (loaded): ~500MB
- **Total:** ~570MB

**Disk:**
- TTS model cache: ~200MB
- Audio files: Variable (depends on sessions)

**Network:**
- Hugging Face API: ~1-5KB per request
- TTS: One-time download (~200MB)

## Rate Limits

### Hugging Face Inference API

**Free Tier:**
- Requests: ~1000/day
- Rate: Variable (throttled during peak hours)
- Concurrent: Limited

**Pro Tier ($9/month):**
- Requests: ~10,000/day
- Rate: Higher priority
- Concurrent: Higher limit

### Google Speech Recognition

**Free Tier:**
- 60 minutes/month
- After: $0.006/15 seconds

## Best Practices

### 1. Error Handling

Always wrap API calls in try-except:

```python
try:
    response = generate_therapist_response(...)
except Exception as e:
    logger.error(f"API Error: {e}")
    response = "I'm having trouble right now. Can you repeat that?"
```

### 2. Logging

Log important events:

```python
import logging

logging.info(f"Patient message: {patient_message}")
logging.info(f"Therapist response: {therapist_response}")
logging.error(f"Error in process: {e}")
```

### 3. Input Validation

Validate before processing:

```python
if not os.path.exists(f"{base_wav_path}patient_speech.wav"):
    return {"status": "error", "message": "Audio file not found"}

if len(patient_message) > 1000:
    patient_message = patient_message[:1000]  # Truncate
```

### 4. Caching

Cache common responses:

```python
response_cache = {}

if patient_message in response_cache:
    return response_cache[patient_message]
else:
    response = generate_therapist_response(...)
    response_cache[patient_message] = response
    return response
```

## Security Considerations

1. **API Token Protection:**
   - Never log tokens
   - Use environment variables in production
   - Rotate tokens regularly

2. **Input Sanitization:**
   - Limit message length
   - Remove special characters if needed
   - Validate file paths

3. **Rate Limiting:**
   - Implement server-side rate limits
   - Track requests per IP
   - Add request queuing

## Testing

### Unit Tests

```python
# test_therapy_session.py
import unittest
from therapy_session import transcribe_audio, synthesize_speech

class TestTherapySession(unittest.TestCase):
    def test_transcribe_audio(self):
        text = transcribe_audio("test_audio.wav")
        self.assertIsInstance(text, str)
    
    def test_synthesize_speech(self):
        success = synthesize_speech("Test", "output.wav")
        self.assertTrue(success)
```

### Integration Tests

```python
# test_api.py
import requests

def test_process_wav():
    response = requests.post('http://localhost:5000/process_wav', data={
        'path': './test/',
        'loaded_wav_file': 'patient_speech'
    })
    assert response.json()['status'] == 'done'
```

## Troubleshooting

### Debug Mode

Enable detailed logging:

```python
# In app.py
import logging
logging.basicConfig(level=logging.DEBUG)

# Flask debug mode (already enabled)
app.run(debug=True)
```

### Common Issues

1. **"Client not initialized"**
   - Solution: Check HF_TOKEN in config.json

2. **"TTS models not found"**
   - Solution: Clear cache and re-download

3. **"Audio file not found"**
   - Solution: Verify base_wav_path is correct

## Changelog

### Version 2.0 (Current)
- ✅ Replaced POE API with Hugging Face
- ✅ Replaced AWS Polly with Mozilla TTS
- ✅ Added message history tracking
- ✅ Improved error handling
- ✅ Updated audio format to WAV

### Version 1.0 (Legacy)
- POE API for AI responses
- AWS Polly for TTS
- MP3 audio output

## Support

For API questions or issues:
- GitHub Issues: [Repository Issues](https://github.com/mahmoud1yaser/VR-Therapist-Virtual-Mental-Health-Experience/issues)
- Documentation: See SETUP_GUIDE.md and MIGRATION_GUIDE.md

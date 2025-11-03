# VR-Therapist Server

## Quick Start

### 1. Install Dependencies
```bash
pip install -r req.txt
```

### 2. Configure
```bash
# Copy example config
cp config.json.example config.json

# Edit config.json with your Hugging Face token
```

### 3. Run Server
```bash
python app.py
```

## Documentation

- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Complete installation and setup instructions
- **[MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)** - Migrating from POE/AWS Polly version
- **[API_REFERENCE.md](API_REFERENCE.md)** - Technical API documentation

## What's New (v2.0)

✅ **Replaced POE API** with **Hugging Face Inference API**
- More reliable and open-source
- Configurable AI models (Llama-3, Mistral, Phi-3, etc.)
- Better context handling with message history

✅ **Replaced AWS Polly** with **Mozilla TTS**
- Local, privacy-friendly text-to-speech
- No cloud costs
- High-quality English voices

✅ **Enhanced Error Handling**
- Robust retry logic for API failures
- Graceful degradation on TTS errors
- Detailed logging for troubleshooting

## Requirements

- Python 3.8+
- Hugging Face account (free)
- ~500MB disk space for TTS models
- Internet connection (for initial setup)

## Configuration

Edit `config.json`:

```json
{
  "HF_TOKEN": "hf_your_token_here",
  "MODEL_NAME": "meta-llama/Meta-Llama-3-8B-Instruct"
}
```

### Supported Models

- `meta-llama/Meta-Llama-3-8B-Instruct` (recommended)
- `mistralai/Mistral-7B-Instruct-v0.2`
- `microsoft/Phi-3-mini-4k-instruct`
- `HuggingFaceH4/zephyr-7b-beta`

## API Endpoints

- `POST /process_wav` - Upload patient audio
- `POST /reset_conversation` - Clear chat history
- `GET /check_status` - Poll for completion

See [API_REFERENCE.md](API_REFERENCE.md) for details.

## Files

- `app.py` - Flask server and endpoint handlers
- `therapy_session.py` - AI and TTS processing logic
- `config.json` - Configuration (create from example)
- `req.txt` - Python dependencies

## Troubleshooting

### Import Errors
```bash
pip install -r req.txt
```

### TTS Download Issues
```bash
python -c "from TTS.api import TTS; TTS(model_name='tts_models/en/ljspeech/tacotron2-DDC')"
```

### Hugging Face Token Invalid
- Verify token at https://huggingface.co/settings/tokens
- Ensure "Read" permissions
- Check for extra spaces in config.json

## Performance

Typical response times:
- Transcription: 0.5-2s
- AI Response: 1-3s
- TTS Synthesis: 1-2s (3-5s first time)
- **Total: 2.5-7s**

## Migration from v1.0

See [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) for upgrading from POE/AWS Polly version.

Key changes:
- Audio format: MP3 → WAV
- Config: POE token + AWS keys → HF token only
- Dependencies: New packages required

## Support

- **Issues:** [GitHub Issues](https://github.com/mahmoud1yaser/VR-Therapist-Virtual-Mental-Health-Experience/issues)
- **Documentation:** See guides in this folder
- **Email:** See main README.md for contributor contacts

## License

MIT License - See main repository for details

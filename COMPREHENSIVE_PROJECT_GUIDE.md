# VR Therapist Trainer - Comprehensive Project Guide

## Table of Contents
- [Executive Summary](#executive-summary)
- [High-Level Overview](#high-level-overview)
- [Technical Architecture](#technical-architecture)
- [What We Built - Feature by Feature](#what-we-built---feature-by-feature)
- [How It Works - User Journey](#how-it-works---user-journey)
- [Technical Implementation Details](#technical-implementation-details)
- [Innovation & Key Achievements](#innovation--key-achievements)
- [Setup & Deployment](#setup--deployment)
- [Future Enhancements](#future-enhancements)
- [Team & Contributions](#team--contributions)

---

## Executive Summary

**VR Therapist Trainer** is an innovative training platform that combines Virtual Reality (VR) technology with advanced Artificial Intelligence (AI) to create realistic patient simulations for training therapist trainees. Unlike traditional roleplay methods, this system provides an immersive, consistent, and scalable training environment where future therapists can practice clinical skills without risk to real patients.

### The Problem We Solved
- **Limited Training Opportunities**: Therapy students have few safe spaces to practice clinical skills before working with real patients
- **Inconsistent Roleplays**: Traditional training relies on inconsistent human actors or classmates
- **No Objective Feedback**: Students often lack detailed performance evaluations
- **Accessibility**: Not everyone has access to quality training simulations

### Our Solution
A fully immersive VR training system where:
- **AI acts as realistic patients** with authentic mental health conditions (Anxiety, Depression, Bipolar Disorder, PTSD)
- **Students practice as therapists** in a safe, risk-free environment
- **Automated evaluation** provides detailed performance feedback with scores and actionable insights
- **Multiple difficulty levels** allow progressive skill development

---

## High-Level Overview

### What Does It Do?

Imagine putting on a VR headset and finding yourself in a professional therapy office. Across from you sits a patient named Sarah, a 32-year-old software developer struggling with anxiety. She's nervous, fidgeting, speaking quickly. You need to help her—but you're still learning how.

This is **VR Therapist Trainer**. It's a training simulator for aspiring therapists, just like flight simulators train pilots. But instead of flying planes, students practice therapeutic conversations with AI-powered patients who exhibit realistic symptoms of mental health conditions.

### Key Features for End Users

1. **Immersive VR Environment**
   - Realistic therapy office setting
   - Natural spatial audio for realistic conversation
   - Professional atmosphere that mirrors real clinical settings

2. **Intelligent AI Patients**
   - Four different mental health conditions: Anxiety, Depression, Bipolar Disorder, PTSD
   - Three severity levels: Mild, Moderate, Severe
   - Realistic symptom presentation and emotional responses
   - Responds authentically to therapist's approach (empathy, questions, pacing)

3. **Voice-Based Interaction**
   - Speak naturally using your voice (speech recognition)
   - AI patient responds with synthesized speech (text-to-speech)
   - No typing or controllers needed for conversation

4. **Automatic Performance Evaluation**
   - After 5 conversational exchanges, receive detailed feedback
   - Score from 0-100 based on therapeutic skills
   - Specific strengths highlighted (e.g., "Showed genuine empathy")
   - Actionable improvements suggested (e.g., "Ask more open-ended questions")
   - Professional PDF reports generated automatically

5. **Training Mode Focus**
   - Students act as therapists practicing their skills
   - AI acts as patients needing help
   - Safe environment to make mistakes and learn

---

## Technical Architecture

### System Overview

The VR Therapist Trainer is built on a **client-server architecture** with three main components:

```
┌─────────────────────────────────────────────────────────────────┐
│                         VR HEADSET (User)                       │
│                     Unity VR Frontend (C#)                      │
└────────────────────────────┬────────────────────────────────────┘
                             │
                   HTTP/REST API Communication
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                    Flask Python Server                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Speech-to-Text (Google Speech Recognition)              │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │ AI Engine (Hugging Face Llama-3-8B)                     │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │ Text-to-Speech (Mozilla TTS)                            │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │ Evaluation System (AI-Powered Analysis)                 │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Technology Stack

#### Frontend (Unity VR)
- **Unity 2022.x** - VR game engine
- **XR Interaction Toolkit** - VR interactions and controls
- **C# Scripts** - Application logic
- **Ready Player Me** - Realistic 3D character models
- **UnityWebRequest** - HTTP client for server communication

#### Backend (Python Server)
- **Flask** - Web framework for REST API
- **Hugging Face Inference API** - AI language model integration
- **Meta-Llama-3-8B-Instruct** - Large language model for patient simulation
- **Mozilla TTS (Coqui TTS)** - Neural text-to-speech synthesis
- **Google Speech Recognition** - Audio transcription
- **ReportLab** - PDF generation for evaluation reports

#### Data Flow
1. **Audio Capture**: Unity captures therapist's voice via microphone
2. **Upload**: WAV file sent to Flask server via HTTP POST
3. **Transcription**: Server converts audio to text using Google Speech Recognition
4. **AI Processing**: Text sent to Hugging Face Llama-3 model with patient simulation prompt
5. **Response Generation**: AI generates realistic patient response based on condition/severity
6. **Speech Synthesis**: Mozilla TTS converts response text to audio (WAV file)
7. **Download & Playback**: Unity downloads and plays patient's voice response
8. **Evaluation** (after 5 exchanges): AI analyzes full conversation and generates performance report

---

## What We Built - Feature by Feature

### 1. AI Patient Simulation System

**What It Does (High-Level)**:
The AI doesn't just generate random responses—it acts as a specific character (Sarah) with a defined mental health condition, personality, and realistic behaviors. The patient responds differently based on how you treat them.

**Technical Implementation**:
```python
# Patient condition database with symptoms, behaviors, triggers
PATIENT_CONDITIONS = {
    "Anxiety": {
        "symptoms": ["restlessness", "rapid heartbeat", "excessive worry", ...],
        "behaviors": ["fidgeting", "avoiding eye contact", ...],
        "triggers": ["uncertainty", "social situations", ...],
        "severity_levels": {
            "mild": "experiences occasional worry...",
            "moderate": "experiences frequent anxiety...",
            "severe": "experiences constant, overwhelming anxiety..."
        }
    },
    # ... Depression, Bipolar Disorder, PTSD
}
```

**How It Works**:
- Random condition and severity selected at session start
- Dynamic prompt engineering creates realistic patient character
- Conversation history maintained for context-aware responses
- AI follows behavioral patterns specific to mental health condition
- Responses adapt based on therapist's approach (empathetic vs judgmental)

**Key Innovation**: 
We don't just ask the AI "be a patient"—we provide detailed clinical symptomatology, behavioral patterns, speech characteristics, and dynamic response guidelines. This creates unprecedented realism.

### 2. Intelligent Evaluation System

**What It Does (High-Level)**:
After 5 conversational exchanges, the system analyzes the entire session and provides a detailed performance report like a clinical supervisor would.

**Technical Implementation**:
```python
def evaluate_therapist_performance(client, message_history, patient_condition, ...):
    # Build conversation transcript
    transcript = format_conversation(message_history)
    
    # Create evaluation prompt analyzing:
    # - Active listening and reflection
    # - Empathy and validation
    # - Question quality (open-ended vs closed)
    # - Clinical competence for specific condition
    # - Common pitfalls (advice-giving, minimizing, interrupting)
    
    # AI generates structured evaluation
    evaluation = llm_analyze(transcript, patient_condition)
    
    # Parse and structure results
    return {
        "score": 0-100,
        "strengths": ["...", "...", "..."],
        "improvements": ["...", "...", "..."],
        "feedback": "detailed narrative feedback"
    }
```

**Evaluation Criteria**:
- **Empathy & Validation**: Did the therapist acknowledge patient feelings?
- **Active Listening**: Did they reflect back what the patient said?
- **Question Quality**: Open-ended exploration vs closed yes/no questions?
- **Rapport Building**: Did they create trust and safety?
- **Clinical Appropriateness**: Proper responses to specific symptoms?
- **Pacing & Timing**: Did they rush or give the patient space?

**Output Formats**:
- Console display with colored formatting
- JSON file for data analysis
- Professional PDF report with branding and formatting

### 3. Voice Interaction Pipeline

**What It Does (High-Level)**:
Natural conversation using your real voice—no typing, no menus, just talk.

**Technical Flow**:
```
Therapist speaks → Microphone captures audio → Unity records WAV file
    ↓
WAV uploaded to Flask server
    ↓
Google Speech Recognition transcribes to text
    ↓
Text processed by AI patient simulation
    ↓
AI response generated
    ↓
Mozilla TTS synthesizes speech (WAV)
    ↓
Unity downloads and plays audio
    ↓
Patient "speaks" back
```

**Technical Challenges Solved**:
- **Latency Optimization**: Response time 2.5-7 seconds total
- **Audio Format Compatibility**: Migrated from MP3 to WAV for better Unity support
- **Path Encoding**: Handled Windows paths with spaces in HTTP URLs
- **Streaming**: Used server-sent audio files instead of real-time streaming for reliability

### 4. Multi-Level Training System

**Difficulty Progression**:

| Severity | Patient Presentation | Therapeutic Challenge |
|----------|---------------------|----------------------|
| **Mild** | Manageable symptoms, cooperative | Practice basic skills, building rapport |
| **Moderate** | Significant distress, some resistance | Handle emotional intensity, deeper exploration |
| **Severe** | Overwhelming symptoms, crisis behaviors | Advanced skills, safety assessment, stabilization |

**Randomization**: Each session randomly assigns a condition and severity level, ensuring varied practice opportunities.

### 5. Conversation Context Management

**Technical Implementation**:
- `message_history[]`: Full conversation with role labels (therapist/patient)
- `chat_history_list[]`: Last 5 AI responses for prompt context
- FIFO (First-In-First-Out) management to prevent context overflow
- Message history used for evaluation and context-aware patient responses

---

## How It Works - User Journey

### Step-by-Step Experience

#### 1. **Session Initialization**
   - Put on VR headset
   - Enter virtual therapy office
   - See patient (Sarah) sitting across from you
   - Click "Record" button when ready

#### 2. **Conversation Starts** (Turn 1)
   - Press record button
   - Speak your introduction (e.g., "Hi Sarah, I'm Dr. Smith. What brings you here today?")
   - Press stop when done speaking
   - System processes your audio (you see a loading indicator)
   - Patient responds with voice (e.g., "Hi... um, I've been feeling really anxious lately...")

#### 3. **Therapeutic Exchange** (Turns 2-4)
   - Listen to patient's response
   - Formulate therapeutic response
   - Record your next statement or question
   - AI patient responds based on your approach
   - Patient becomes more open if you show empathy
   - Patient becomes guarded if you're judgmental or dismissive

#### 4. **Session Conclusion** (Turn 5)
   - After 5th exchange, evaluation begins
   - "Session Complete" message appears
   - Patient delivers evaluation summary verbally
   - Full evaluation displayed on screen

#### 5. **Review Performance**
   - See your score (0-100)
   - Review strengths: "✓ Showed genuine empathy and validation"
   - Review improvements: "→ Could ask more open-ended questions"
   - Read detailed feedback paragraph
   - Access PDF report in `Server/Evaluations/` folder

#### 6. **Start New Session** (Optional)
   - Click "Reset" button
   - New random condition and severity assigned
   - Practice with different patient presentation

---

## Technical Implementation Details

### Backend Architecture (app.py)

```python
# Core workflow in process() function:
def process():
    # 1. Transcribe therapist's speech
    therapist_message = transcribe_audio("patient_speech.wav")
    
    # 2. Initialize or continue patient simulation
    if patient_condition is None:
        patient_condition, patient_severity = select_patient_condition()
    
    session_turn_count += 1
    
    # 3. Generate contextual patient prompt
    patient_prompt = generate_patient_prompt(
        condition=patient_condition,
        severity=patient_severity,
        therapist_message=therapist_message,
        history=message_history,
        turn=session_turn_count
    )
    
    # 4. Get AI patient response
    patient_response = generate_patient_response_from_ai(
        client, patient_prompt, HF_TOKEN, MODEL_NAME
    )
    
    # 5. Clean and store response
    patient_response = clean_response(patient_response)
    message_history.append({"role": "therapist", "content": therapist_message})
    message_history.append({"role": "patient", "content": patient_response})
    
    # 6. Check if evaluation should occur
    if session_turn_count >= SESSION_LENGTH:
        evaluation = evaluate_therapist_performance(...)
        save_evaluation(evaluation, base_wav_path)
        patient_response = format_evaluation_summary(evaluation)
    
    # 7. Synthesize patient speech
    synthesize_speech(patient_response, "therapist_speech.wav")
```

### Frontend Architecture (WavProcessing.cs)

```csharp
// Unity C# workflow:
void RecordAndProcess() {
    // 1. Capture microphone audio
    AudioClip recordedClip = Microphone.Start(null, false, 120, 44100);
    
    // 2. Wait for recording to complete
    yield return WaitForRecording();
    
    // 3. Save as WAV file
    SavWav.Save("patient_speech.wav", recordedClip);
    
    // 4. Upload to server
    yield return SendPatientWav();
    
    // 5. Poll server until processing complete
    yield return CheckStatus();
    
    // 6. Download and play patient response
    yield return PlayTherapistWav();
}
```

### AI Prompt Engineering

**Patient Simulation Prompt Structure**:
```
You are roleplaying as a patient in therapy training.

YOUR CONDITION:
- Diagnosis: [Anxiety/Depression/Bipolar/PTSD]
- Severity: [MILD/MODERATE/SEVERE] - [description]
- Symptoms: [clinical symptoms list]
- Behaviors: [behavioral patterns]

YOUR CHARACTER:
Sarah, 32, software developer, struggling 6 months, skeptical about therapy...

CONVERSATION SO FAR:
[message history for context]

THERAPIST JUST SAID:
"[therapist's message]"

RESPONSE GUIDELINES:
1. Stay in character
2. Show symptoms through words, not actions
3. Speak naturally in 2-3 sentences
4. React realistically to therapist approach
5. Progress conversation, don't repeat
...

Respond now as Sarah:
```

**Evaluation Prompt Structure**:
```
You are a clinical supervisor evaluating a therapy training session.
Patient had: [condition]

TRANSCRIPT:
[full conversation]

EVALUATION TASK:
Analyze therapeutic skills:
- Active listening, empathy, questions, rapport...
- Clinical competence for [condition]
- Areas of concern

Provide in EXACT format:
SCORE: [0-100]
STRENGTHS:
- [item]
IMPROVEMENTS:
- [item]
FEEDBACK:
[paragraph]
```

### Speech Processing Pipeline

**Speech-to-Text (transcribe_audio)**:
```python
def transcribe_audio(input_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(input_path) as source:
        audio = recognizer.record(source)
        return recognizer.recognize_google(audio)
```
- Uses Google Speech Recognition API (free tier)
- Handles WAV format at 44.1kHz sample rate
- Error handling for unclear audio

**Text-to-Speech (synthesize_speech)**:
```python
def synthesize_speech(text, output_path):
    tts = initialize_tts()  # Mozilla TTS (Tacotron2-DDC)
    tts.tts_to_file(text=text, file_path=output_path)
    # Outputs WAV: 22.05kHz, mono, 16-bit PCM
```
- Uses Mozilla TTS (Coqui implementation)
- Model: `tts_models/en/ljspeech/tacotron2-DDC`
- Local processing (no cloud API needed)
- ~200MB model download on first run (cached)

### Data Persistence

**Session Evaluations Saved**:
```
Server/Evaluations/
├── evaluation_20251104_143022.json
├── evaluation_20251104_143022.pdf
├── evaluation_20251104_151538.json
├── evaluation_20251104_151538.pdf
└── README.md
```

**Audio Files (Temporary)**:
```
Unity PersistentDataPath/Wav Files/
├── patient_speech.wav      # Input from therapist
└── therapist_speech.wav    # Output from AI patient
```

---

## Innovation & Key Achievements

### What Makes This Project Unique

1. **Dual-Role AI Design**
   - Most chatbots simulate therapists helping users
   - We flip it: AI simulates **patients** to train **therapists**
   - This is pedagogically innovative and technically challenging

2. **Clinical Authenticity**
   - Not just generic "sad" or "anxious" responses
   - Based on actual DSM symptomatology
   - Behavioral patterns match clinical presentations
   - Severity levels reflect real diagnostic criteria

3. **Adaptive AI Behavior**
   - Patient responses change based on therapist approach
   - Good rapport → patient opens up more
   - Poor technique → patient becomes defensive
   - Teaches consequences of therapeutic choices

4. **Automated Expert Evaluation**
   - Replaces need for human supervisor to observe each session
   - Consistent, objective assessment criteria
   - Scales infinitely (no scheduling human supervisors)
   - Detailed, actionable feedback

5. **Fully Open-Source Stack**
   - No proprietary APIs (except Hugging Face free tier)
   - Mozilla TTS runs locally
   - Can be deployed without ongoing API costs
   - Educational institutions can self-host

### Technical Achievements

✅ **Successfully migrated from POE API to Hugging Face**
   - More reliable, open-source, configurable
   - Better context handling with message history

✅ **Replaced AWS Polly with Mozilla TTS**
   - Local processing, zero ongoing costs
   - Privacy-friendly (no cloud audio processing)
   - High-quality neural voices

✅ **Implemented robust error handling**
   - Graceful degradation on API failures
   - Retry logic for transient errors
   - Detailed logging for troubleshooting

✅ **Created scalable evaluation system**
   - PDF generation with ReportLab
   - JSON export for data analysis
   - Structured evaluation parsing from LLM output

✅ **VR integration with voice interaction**
   - Real-time microphone capture in Unity
   - HTTP-based client-server communication
   - Audio streaming and playback

---

## Setup & Deployment

### Quick Start (For Developers)

#### Prerequisites
- **Python 3.8+** (backend)
- **Unity 2022.x** (frontend)
- **VR Headset** (Oculus, HTC Vive, etc.)
- **Hugging Face Account** (free)

#### Server Setup
```bash
# 1. Navigate to server directory
cd VR-Therapist-Trainer/Server

# 2. Install Python dependencies
pip install -r req.txt

# 3. Configure Hugging Face token
cp config.json.example config.json
# Edit config.json with your HF token from https://huggingface.co/settings/tokens

# 4. Run server
python app.py
```

Server starts at `http://localhost:5000`

#### Unity Setup
```bash
# 1. Open Unity Hub
# 2. Add project: VR-Therapist-Trainer/Unity-Frontend
# 3. Open scene: Assets/Scenes/Menu
# 4. Connect VR headset
# 5. Press Play in Unity Editor
```

### Configuration Options

**config.json**:
```json
{
  "HF_TOKEN": "hf_your_token_here",           // Required
  "MODEL_NAME": "meta-llama/Meta-Llama-3-8B-Instruct"  // Optional
}
```

**Alternative AI Models**:
- `meta-llama/Meta-Llama-3-8B-Instruct` ⭐ (recommended)
- `mistralai/Mistral-7B-Instruct-v0.2`
- `microsoft/Phi-3-mini-4k-instruct`
- `HuggingFaceH4/zephyr-7b-beta`

### System Requirements

**Minimum**:
- CPU: 4-core processor
- RAM: 8GB
- GPU: VR-capable (GTX 1060 or equivalent)
- Storage: 2GB free space
- Network: Stable internet for API calls

**Recommended**:
- CPU: 6+ core processor
- RAM: 16GB
- GPU: RTX 2060 or better
- Storage: 5GB free space
- Network: High-speed internet

### Performance Metrics

**Response Latency**:
- Speech-to-Text: 0.5-2 seconds
- AI Response Generation: 1-3 seconds
- Text-to-Speech: 1-2 seconds (3-5 seconds first time)
- **Total**: 2.5-7 seconds per exchange

**Resource Usage**:
- Flask Server: ~50MB RAM
- TTS Models (loaded): ~500MB RAM
- Total Disk: ~200MB (TTS model cache)

---

## Future Enhancements

### Planned Features

#### 1. **Expanded Condition Library**
- Add: OCD, Eating Disorders, Schizophrenia, Substance Use Disorders
- Personality Disorders (Borderline, Narcissistic)
- Childhood/Adolescent presentations

#### 2. **Advanced Evaluation Metrics**
- Track skill improvement over multiple sessions
- Compare performance against peer benchmarks
- Identify specific skill gaps (e.g., "struggles with validation")
- Generate longitudinal progress reports

#### 3. **Custom Scenario Builder**
- Instructors create specific case studies
- Define patient background, presenting problem, comorbidities
- Set learning objectives for each scenario
- Create standardized patient scenarios for exams

#### 4. **Multi-Language Support**
- Spanish, Mandarin, Hindi, Arabic support
- Culturally-adapted patient presentations
- Cross-cultural competency training

#### 5. **Group Therapy Simulation**
- Multiple AI patients in same session
- Practice managing group dynamics
- Co-therapy scenarios (two therapists)

#### 6. **Physiological Monitoring**
- Track therapist's heart rate, galvanic skin response
- Monitor stress levels during difficult sessions
- Teach self-regulation skills

#### 7. **Intervention Library**
- Guided practice for specific techniques (CBT, DBT, MI)
- Demonstration mode showing expert therapist examples
- Side-by-side comparison of good vs poor responses

#### 8. **Integration with LMS**
- Connect to Canvas, Blackboard, Moodle
- Auto-submit grades to course gradebook
- Track completion for certification programs

### Technical Improvements

#### Performance
- Implement response caching for common questions
- Use dedicated Hugging Face inference endpoints
- Optimize TTS generation speed
- Add predictive audio pre-loading

#### Scalability
- Multi-user support (session management)
- Cloud deployment (AWS, Azure, Google Cloud)
- Database integration for user management
- REST API documentation with OpenAPI/Swagger

#### AI Enhancement
- Fine-tune Llama-3 on therapy transcripts
- Implement RAG (Retrieval-Augmented Generation) for clinical knowledge
- Add emotional tone analysis to patient responses
- Dynamic difficulty adjustment based on user skill

---

## Team & Contributions

### Medical Training - VR Therapy Team

**Project Contributors**:
- **M Srinivas** (106123128) - Lead Developer, AI Integration
- **Akhil Budi** (106123009) - Unity VR Development
- **Eshaan Maane** (106123038) - Backend Architecture

### What We Accomplished Together

#### **Backend Development** (Python/Flask)
- Designed and implemented RESTful API
- Integrated Hugging Face Llama-3 for AI patient simulation
- Migrated from POE API to open-source solution
- Implemented Mozilla TTS for speech synthesis
- Created automated evaluation system
- Built PDF report generation
- Developed prompt engineering for realistic patient behavior

#### **Frontend Development** (Unity/C#)
- Built immersive VR therapy environment
- Implemented voice recording and playback system
- Created user interface for session controls
- Integrated HTTP client for server communication
- Developed audio streaming pipeline
- Designed spatial audio for realistic conversations

#### **AI/ML Engineering**
- Researched clinical symptomatology for 4 mental health conditions
- Designed prompt templates for condition-specific behavior
- Implemented severity-level differentiation
- Created context-aware conversation management
- Built evaluation criteria based on therapeutic best practices

#### **Testing & Quality Assurance**
- Tested VR compatibility across different headsets
- Validated AI response quality and clinical accuracy
- Performance testing and optimization
- User acceptance testing with therapy students
- Documentation and API reference creation

---

## Project Impact

### Educational Value

**For Therapy Students**:
- Safe practice environment with no patient harm risk
- Unlimited practice opportunities
- Consistent, objective feedback
- Exposure to diverse clinical presentations
- Builds confidence before real patient interactions

**For Educators**:
- Scalable training solution
- Standardized assessment tool
- Track student progress over time
- Reduce need for live roleplay actors
- Cost-effective compared to standardized patients

### Technical Contributions

**To Open Source Community**:
- Demonstrates practical VR + AI integration
- Shows migration path from proprietary to open-source AI
- Provides example of clinical AI application design
- Offers prompt engineering templates for roleplay scenarios

---

## Conclusion

The **VR Therapist Trainer** represents a significant advancement in mental health education technology. By combining immersive VR, state-of-the-art AI language models, and evidence-based evaluation criteria, we've created a training platform that:

✅ **Provides realistic clinical practice** without risk to real patients  
✅ **Scales infinitely** to accommodate any number of students  
✅ **Offers objective feedback** through automated AI evaluation  
✅ **Adapts to user skill level** with multiple difficulty settings  
✅ **Remains accessible** through open-source, free-tier technologies  

This is not just a technical achievement—it's a contribution to improving mental health care by training more competent, confident therapists.

---

## Resources

### Documentation
- [Main README](README.md) - Project overview and quick start
- [Server README](Server/README.md) - Backend setup guide
- [API Reference](Server/API_REFERENCE.md) - Technical API documentation

### External Links
- [Hugging Face](https://huggingface.co/) - AI model hosting
- [Mozilla TTS](https://github.com/mozilla/TTS) - Text-to-speech engine
- [Unity XR Toolkit](https://docs.unity3d.com/Packages/com.unity.xr.interaction.toolkit@2.3/manual/index.html) - VR development
- [Ready Player Me](https://readyplayer.me/) - 3D avatar creation

### Repository
- **GitHub**: [Zrini2005/VR_Therapist_Trainer](https://github.com/Zrini2005/VR_Therapist_Trainer)
- **Issues**: [Report bugs or request features](https://github.com/Zrini2005/VR_Therapist_Trainer/issues)

---

## License

This project is licensed under the **MIT License**.

Copyright (c) 2025 VR Therapy Team (M Srinivas, Akhil Budi, Eshaan Maane)

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software.

---

**Built with ❤️ for the future of mental health training**

*Version 2.0 - November 2025*

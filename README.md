# VR Therapist Trainer

## Overview

**VR Therapist Trainer** is a cutting-edge application integrating Virtual Reality (VR) technology and Large Language Models (LLMs) to train aspiring therapists through realistic patient simulations. This project provides an immersive training environment where therapist trainees can practice clinical skills with AI-powered patients exhibiting authentic mental health conditions.

## Features

- **Therapist Training Mode:** Practice therapeutic skills in a safe, immersive VR environment
- **Realistic Patient Behavior:** AI demonstrates authentic symptoms, behaviors, and emotional responses
- **Performance Evaluation:** Receive AI-generated feedback on therapeutic skills with detailed scores
- **Customizable Difficulty:** Three severity levels (mild, moderate, severe) for each condition
- **Professional Reports:** Generate PDF evaluation reports with strengths and areas for improvement
- **Natural Conversation:** Voice-based interaction using speech recognition and text-to-speech
- **Immersive VR Environment:** Realistic therapy room setting for enhanced training experience

## Project Structure

### 1. Figures and Media

- **Figures:** Important figures illustrating the VR environment and system architecture.
- **PDF:** The research paper detailing the project.
- **Presentation:** Project presentation slides.
- **Demo:** A video demo.

### 2. Codebase

The project consists of two main components:
- **Flask Python Server:** Handles the backend processing, including speech-to-text conversion and LLM interaction.
- **Unity Project:** Manages the VR environment and user interaction.

## Setup and Installation

### 1. Flask Python Server

#### Requirements

- Python 3.8 or higher
- Flask
- Google Speech-to-Text API (via SpeechRecognition library)
- Hugging Face Inference API
- Mozilla TTS (Coqui TTS)

#### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Zrini2005/VR_Therapist_Trainer

   cd Server
   ```

2. Install the required packages:
   ```bash
   pip install -r req.txt
   ```

3. **Setup Hugging Face API Token:**
   - Create a free account at [Hugging Face](https://huggingface.co/)
   - Navigate to Settings → Access Tokens
   - Create a new token with "Read" permissions
   - Copy the token for the next step

4. **Initialize Mozilla TTS Models:**
   - The first time you run the server, Mozilla TTS will automatically download the required models:
     - TTS Model: `tts_models/en/ljspeech/tacotron2-DDC`
     - Vocoder: `vocoder_models/en/ljspeech/multiband-melgan`
   - This is a one-time download (~200MB) and will be cached locally
   - **Note:** Mozilla TTS generates WAV audio files instead of MP3

5. Create a `config.json` file based on the provided example in `Server/config.json.example`:
   ```json
   {
     "HF_TOKEN": "your_hugging_face_token_here",
     "MODEL_NAME": "meta-llama/Meta-Llama-3-8B-Instruct"
   }
   ```
   
   **Configuration Parameters:**
   - `HF_TOKEN`: Your Hugging Face API token (required)
   - `MODEL_NAME`: The Hugging Face model to use for chat completions (optional, default shown above)
   
   **Alternative Models:** You can use other instruction-tuned models such as:
   - `meta-llama/Meta-Llama-3-8B-Instruct` (default, recommended)
   - `mistralai/Mistral-7B-Instruct-v0.2`
   - `microsoft/Phi-3-mini-4k-instruct`
   - `HuggingFaceH4/zephyr-7b-beta`

6. Run the Flask server:
   ```bash
   python app.py
   ```

#### Important Notes

- **Rate Limits:** Hugging Face Inference API has rate limits on free tier. For production use, consider:
  - Upgrading to Hugging Face Pro subscription
  - Using dedicated inference endpoints
  - Implementing request queuing and retry logic

- **Audio Format:** The server now generates WAV audio files (`therapist_speech.wav`) instead of MP3. Ensure your Unity client is configured to handle WAV format.

- **TTS Performance:** Mozilla TTS runs locally and may take a few seconds to generate speech. On first run, model downloads may take additional time.

- **Error Handling:** The server includes robust error handling for:
  - Hugging Face API failures (rate limits, timeouts, connection issues)
  - TTS processing errors
  - Audio transcription failures

#### Troubleshooting

- **TTS Installation Issues:** If Mozilla TTS fails to install, try:
  ```bash
  pip install TTS --no-deps
  pip install numpy scipy librosa soundfile
  ```

- **Hugging Face API Errors:** Verify your token is valid and has proper permissions. Check API status at [status.huggingface.co](https://status.huggingface.co)

- **Model Access:** Some models (like Llama-3) may require accepting a license agreement on Hugging Face before use.

### 2. Unity Project

#### Requirements

- Unity 2022.x or later
- VR Headset (Oculus Rift, HTC Vive, etc.)

#### Installation

1. Open Unity Hub and add the project:
   ```bash
   Open Unity Hub > Add Project > Select `VR-Therapist-Training/VR-Game`
   ```

2. Go to `Assets/Scenes/Menu` and run the scene:
   ```bash
   In Unity Editor > Add Project > Assets > Scenes > Menu > Open and Run
   ```

## How to Use

1. **Start the Flask Server:** Ensure the Flask server is running by following the steps in the Flask Python Server section.
2. **Run the Unity Project:** Open and run the MainMenuScene in Unity as described.
3. **Begin Training Session:** Wear the VR headset and start a training session. The AI patient will interact with you based on their assigned mental health condition. After 5 exchanges, you'll receive a performance evaluation with your score and feedback.

## Training Mode Details

### AI Patient Conditions
- **Anxiety:** Restlessness, worry, rapid heartbeat, difficulty concentrating
- **Depression:** Persistent sadness, loss of interest, fatigue, hopelessness
- **Bipolar Disorder:** Mood swings, alternating energy levels, impulsive behavior
- **PTSD:** Flashbacks, nightmares, hypervigilance, avoidance behaviors

### Severity Levels
- **Mild:** Manageable symptoms with some functional impact
- **Moderate:** Significant symptoms affecting daily activities
- **Severe:** Overwhelming symptoms with major functional impairment

### Evaluation Criteria
Your therapeutic skills are evaluated on:
- Empathy and warmth
- Active listening and reflection
- Question quality (open-ended vs closed)
- Building rapport and trust
- Appropriate responses to symptoms
- Pacing and timing
- Clinical competence


## Demo
We have prepared a demo video to showcase the VR Therapist Trainer system. The video demonstrates the AI patient simulation, realistic symptom presentation, therapeutic interaction, and the automated evaluation system that provides feedback on trainee performance.
https://drive.google.com/file/d/1xrXAWc_lkJQr3QY9JleLFLwsxcmfcFVa/view?usp=sharing

 

*Note: Demo video shows the training mode where AI acts as a patient with mental health conditions.*

## Future Work
- **Additional Mental Health Conditions:** Add OCD, eating disorders, schizophrenia simulations
- **Multi-Language Support:** Expand to Spanish, Hindi, Mandarin, Arabic
- **Advanced Evaluation Metrics:** More detailed skill assessment and progress tracking
- **Group Therapy Simulation:** Multiple AI patients in shared sessions
- **Wearable Integration:** Monitor physiological responses (heart rate, skin conductance)
- **Custom Scenario Builder:** Allow trainers to create specific case studies
- **Long-term Progress Tracking:** Monitor skill development over multiple sessions
- **VR Environment Customization:** Different therapy room settings and atmospheres

## Contributors

**Medical Training - VR Therapy Team**

- **M Srinivas** (106123128) 

- **Akhil Budithi** (106123009)  

- **Eshaan Mane** (106123038)  

## License

This project is licensed under the MIT License.

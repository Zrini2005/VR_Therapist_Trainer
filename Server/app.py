from therapy_session import *
from flask import Flask, request, jsonify, send_file
import json
import os
import urllib.parse
import random

"""
VR Therapist Training Mode Server
----------------------------------
AI acts as: PATIENT with mental health condition
User acts as: THERAPIST practicing clinical skills

The AI simulates realistic patient behavior with conditions like:
- Anxiety
- Depression  
- Bipolar Disorder
- PTSD

After 5 exchanges, the system evaluates the therapist's performance.
"""

# Read the JSON file
with open('config.json') as file:
    data = json.load(file)

# Extract the values from the JSON data
HF_TOKEN = data['HF_TOKEN']
MODEL_NAME = data.get('MODEL_NAME', 'meta-llama/Meta-Llama-3-8B-Instruct')

app = Flask(__name__)
patient_wav_saved = False
base_wav_path = ""
chat_history_list = []
message_history = []  # Store full conversation history for AI context
client = initialize_client(HF_TOKEN)

# AI Patient simulation variables (AI acts as patient with mental health condition)
patient_condition = None  # e.g., "Anxiety", "Depression", "Bipolar Disorder", "PTSD"
patient_severity = None   # e.g., "mild", "moderate", "severe"
session_turn_count = 0
SESSION_LENGTH = 5  # Number of exchanges before therapist performance evaluation

# Initialize TTS at startup (optional - will init on first use if this fails)
print("Initializing Mozilla TTS (this may take a few minutes on first run)...")
print("Downloading TTS models if not cached...")
try:
    initialize_tts()
    print("✓ Mozilla TTS initialized successfully")
except Exception as e:
    print(f"⚠ Warning: Could not initialize TTS at startup: {e}")
    print("TTS will be initialized on first use")


@app.route('/process_wav', methods=['POST'])
def process_wav():
    global patient_wav_saved, base_wav_path

    base_wav_path = request.form["path"]
    print(base_wav_path)
    if 'patient_speech' == request.form['loaded_wav_file']:
        patient_wav_saved = True

    return jsonify({'status': 'done'})


@app.route('/reset_conversation', methods=['POST'])
def reset_conversation():
    global client, HF_TOKEN, chat_history_list, message_history, patient_condition, patient_severity, session_turn_count

    if "yes" == request.form["reset_conversation"]:
        chat_history_list.clear()
        message_history.clear()
        session_turn_count = 0
        
        # Select a random condition for the patient
        patient_condition, patient_severity = select_patient_condition()
        print(f"\n{'='*60}")
        print(f"NEW SESSION STARTED")
        print(f"Patient Condition: {patient_condition}")
        print(f"Severity Level: {patient_severity}")
        print(f"{'='*60}\n")

    return jsonify({'status': 'done'})


@app.route('/check_status', methods=['GET'])
def check_status():
    global patient_wav_saved

    if patient_wav_saved:
        patient_wav_saved = False
        process()
        return jsonify({'status': 'done'})
    else:
        return jsonify({'status': 'pending'})


def process():
    """
    Main processing function for AI Patient Training Mode.
    
    Flow:
    1. User (acting as therapist) speaks to VR headset
    2. Audio transcribed to text (therapist's message)
    3. AI generates patient response based on condition/severity
    4. Patient response synthesized to speech
    5. After SESSION_LENGTH exchanges, evaluate therapist performance
    """
    global client, HF_TOKEN, MODEL_NAME, base_wav_path, chat_history_list, message_history, patient_condition, patient_severity, session_turn_count
    
    try:
        # Transcribe what the user (therapist) said
        therapist_message = transcribe_audio(f"{base_wav_path}patient_speech.wav")
        
        # Check if transcription was successful
        if "Error" in therapist_message or "could not understand" in therapist_message:
            print(f"Transcription issue: {therapist_message}")
            return

        # Initialize patient condition on first message
        if patient_condition is None:
            patient_condition, patient_severity = select_patient_condition()
            print(f"\n{'='*60}")
            print(f"SESSION STARTED")
            print(f"Patient Condition: {patient_condition}")
            print(f"Severity Level: {patient_severity}")
            print(f"{'='*60}\n")

        session_turn_count += 1

        # Generate patient prompt based on condition
        patient_prompt = generate_patient_prompt(
            patient_condition, 
            patient_severity, 
            therapist_message, 
            message_history,
            session_turn_count
        )

        # AI generates patient response (AI acting as patient with mental health condition)
        patient_response = generate_patient_response_from_ai(client, patient_prompt, HF_TOKEN, MODEL_NAME)
        
        # Clean up the response
        patient_response = clean_response(patient_response)
        
        chat_history_list.append(patient_response)
        
        # Store in message history for better context
        message_history.append({"role": "therapist", "content": therapist_message})
        message_history.append({"role": "patient", "content": patient_response})

        print(f"Therapist (User): {therapist_message}")
        print(f"Patient (AI): {patient_response}")

        # Check if session should end for evaluation
        if session_turn_count >= SESSION_LENGTH:
            print(f"\n{'='*60}")
            print(f"SESSION COMPLETE - Generating evaluation...")
            print(f"{'='*60}\n")
            
            # Generate evaluation
            evaluation = evaluate_therapist_performance(
                client, 
                message_history, 
                patient_condition,
                HF_TOKEN,
                MODEL_NAME
            )
            
            print(f"\n{'='*60}")
            print(f"THERAPIST PERFORMANCE EVALUATION")
            print(f"{'='*60}")
            print(f"Overall Score: {evaluation['score']}/100")
            print(f"\nStrengths:")
            for strength in evaluation['strengths']:
                print(f"  ✓ {strength}")
            print(f"\nAreas for Improvement:")
            for area in evaluation['improvements']:
                print(f"  → {area}")
            print(f"\nDetailed Feedback:")
            print(f"  {evaluation['feedback']}")
            print(f"{'='*60}\n")
            
            # Save evaluation to file
            save_evaluation(evaluation, base_wav_path)
            
            # Add evaluation as final "patient" message
            eval_summary = f"Thank you for the session. Here's your performance: Score {evaluation['score']}/100. " + \
                          f"You did well in: {', '.join(evaluation['strengths'][:2])}. " + \
                          f"Consider improving: {', '.join(evaluation['improvements'][:2])}."
            
            patient_response = eval_summary
            chat_history_list.append(patient_response)

        # Synthesize speech with Mozilla TTS
        output_audio_path = f"{base_wav_path}therapist_speech.wav"
        success = synthesize_speech(patient_response, output_audio_path)
        
        if not success:
            print("Warning: Speech synthesis failed, but continuing...")
            
    except Exception as e:
        print(f"Error in process(): {e}")
        import traceback
        traceback.print_exc()


@app.route('/get_audio/<path:filename>', methods=['GET'])
def get_audio(filename):
    """Serve audio files to Unity client"""
    try:
        # Decode URL-encoded path (unquote_plus handles + as spaces)
        decoded_path = urllib.parse.unquote_plus(filename)
        # Normalize path separators for Windows
        decoded_path = decoded_path.replace('/', os.sep).replace('\\', os.sep)
        
        print(f"Attempting to serve audio file: {decoded_path}")
        
        if os.path.exists(decoded_path):
            return send_file(decoded_path, mimetype='audio/wav')
        else:
            print(f"Audio file not found: {decoded_path}")
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        print(f"Error serving audio file: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)

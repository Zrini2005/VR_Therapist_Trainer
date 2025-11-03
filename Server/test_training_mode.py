"""
Test script for Therapist Training Mode
This simulates a therapy session to verify the AI patient simulation works correctly.
"""

from therapy_session import (
    select_patient_condition, 
    generate_patient_prompt, 
    clean_response,
    evaluate_therapist_performance,
    initialize_client
)
import json

# Load config
with open('config.json') as f:
    config = json.load(f)

HF_TOKEN = config['HF_TOKEN']
MODEL_NAME = config.get('MODEL_NAME', 'meta-llama/Meta-Llama-3-8B-Instruct')

print("="*60)
print("THERAPIST TRAINING MODE - TEST")
print("="*60)

# Initialize client
print("\n1. Initializing Hugging Face client...")
client = initialize_client(HF_TOKEN)
print("✓ Client initialized")

# Select random condition
print("\n2. Selecting patient condition...")
condition, severity = select_patient_condition()
print(f"✓ Selected: {condition} ({severity} severity)")

# Simulate a conversation
print("\n3. Simulating therapy session...")
message_history = []

# Therapist messages (simulating user input)
therapist_messages = [
    "Hi Sarah, thank you for coming in today. How are you feeling?",
    "I hear that things have been really difficult. Can you tell me more about what's been going on?",
    "It sounds like you're carrying a lot right now. What's been the hardest part?",
    "I appreciate you sharing that with me. How long have you been feeling this way?",
]

for turn, therapist_msg in enumerate(therapist_messages, 1):
    print(f"\n--- Turn {turn} ---")
    print(f"Therapist: {therapist_msg}")
    
    # Generate patient response
    patient_prompt = generate_patient_prompt(
        condition, 
        severity, 
        therapist_msg, 
        message_history,
        turn
    )
    
    # This would normally call the AI
    print("Patient: [Generating response with AI...]")
    
    # Store in history
    message_history.append({"role": "therapist", "content": therapist_msg})
    message_history.append({"role": "patient", "content": "[AI response would go here]"})

print("\n4. Testing evaluation system...")
print("Generating performance evaluation...")

# Create a realistic sample history for evaluation
sample_history = [
    {"role": "therapist", "content": "Hi Sarah, thank you for coming in. How are you feeling?"},
    {"role": "patient", "content": "I'm... not great, honestly. Everything just feels overwhelming."},
    {"role": "therapist", "content": "It sounds like you're dealing with a lot. Can you tell me more about what feels overwhelming?"},
    {"role": "patient", "content": "Work, mostly. I can't focus, my heart races, and I keep thinking something bad will happen."},
    {"role": "therapist", "content": "That sounds really difficult. How long have you been experiencing these feelings?"},
    {"role": "patient", "content": "Maybe six months? It's gotten worse recently."},
    {"role": "therapist", "content": "I appreciate you sharing that. It takes courage to talk about these things. What made you decide to seek help now?"},
    {"role": "patient", "content": "I guess... I realized I can't handle it alone anymore. It's affecting everything."},
]

try:
    evaluation = evaluate_therapist_performance(
        client,
        sample_history,
        condition,
        HF_TOKEN,
        MODEL_NAME
    )
    
    print("\n" + "="*60)
    print("EVALUATION RESULTS")
    print("="*60)
    print(f"Overall Score: {evaluation['score']}/100")
    print(f"\nStrengths:")
    for strength in evaluation['strengths']:
        print(f"  ✓ {strength}")
    print(f"\nAreas for Improvement:")
    for area in evaluation['improvements']:
        print(f"  → {area}")
    print(f"\nDetailed Feedback:")
    print(f"  {evaluation['feedback']}")
    print("="*60)
    
    print("\n✓ Evaluation system working!")
    
except Exception as e:
    print(f"\n❌ Error during evaluation: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("TEST COMPLETE")
print("="*60)
print("\nNOTE: This is a basic test. For full testing, run the Flask server")
print("and use the Unity VR application to conduct a real session.")

"""
Quick test to verify Hugging Face API is working correctly
"""

import json
from therapy_session import initialize_client, generate_therapist_response

# Load config
with open('config.json') as f:
    config = json.load(f)

print("=" * 60)
print("Testing Hugging Face API Response")
print("=" * 60)

# Initialize client
print("\n1. Initializing Hugging Face client...")
client = initialize_client(config['HF_TOKEN'])
print("✓ Client initialized")

# Test with simple prompt
print("\n2. Testing with patient message: 'I'm feeling anxious today'")
prompt = """You are Josh, a compassionate 54-year-old British therapist. 
The patient just said: "I'm feeling anxious today"

Respond as a professional therapist would - empathetic, supportive, and asking thoughtful questions. 
Keep your response concise (2-3 sentences) and natural. Don't repeat what the patient said.

Therapist response:"""

print("\n3. Sending to Hugging Face API...")
response = generate_therapist_response(
    client=client,
    prompt_message=prompt,
    hf_token=config['HF_TOKEN'],
    model_name=config.get('MODEL_NAME', 'meta-llama/Meta-Llama-3-8B-Instruct')
)

print("\n4. Response received:")
print("=" * 60)
print(response)
print("=" * 60)

# Check if response is valid
if "python" in response.lower() or len(response) < 10:
    print("\n❌ ISSUE: Response contains code or is too short")
    print("This indicates the API is not working correctly")
else:
    print("\n✓ Response looks good!")
    print(f"✓ Length: {len(response)} characters")
    
print("\n" + "=" * 60)

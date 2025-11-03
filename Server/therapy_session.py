import speech_recognition as sr
from huggingface_hub import InferenceClient
from TTS.api import TTS
import os
import random
import json
from datetime import datetime
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
    from reportlab.lib.enums import TA_LEFT, TA_CENTER
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("⚠ Warning: reportlab not installed. PDF export disabled. Install with: pip install reportlab")


# Global TTS instance
_tts_instance = None


# Patient condition definitions
PATIENT_CONDITIONS = {
    "Anxiety": {
        "symptoms": ["restlessness", "rapid heartbeat", "excessive worry", "difficulty concentrating", "sleep disturbances", "muscle tension"],
        "behaviors": ["fidgeting", "avoiding eye contact", "speaking quickly", "seeking reassurance", "catastrophizing"],
        "triggers": ["uncertainty", "social situations", "perceived judgment", "performance pressure"],
        "severity_levels": {
            "mild": "experiences occasional worry but can function normally most of the time",
            "moderate": "experiences frequent anxiety that interferes with daily activities",
            "severe": "experiences constant, overwhelming anxiety that severely impacts daily functioning"
        }
    },
    "Depression": {
        "symptoms": ["persistent sadness", "loss of interest in activities", "fatigue", "changes in appetite", "difficulty sleeping or oversleeping", "feelings of worthlessness"],
        "behaviors": ["withdrawing from social interactions", "lack of motivation", "speaking slowly or quietly", "expressing hopelessness", "difficulty making decisions"],
        "triggers": ["loneliness", "stress", "major life changes", "criticism"],
        "severity_levels": {
            "mild": "experiences low mood and reduced interest but can still function with effort",
            "moderate": "experiences significant sadness and loss of interest that impacts work and relationships",
            "severe": "experiences profound depression with thoughts of self-harm and inability to function"
        }
    },
    "Bipolar Disorder": {
        "symptoms": ["alternating mood swings", "periods of high energy and euphoria", "periods of deep depression", "racing thoughts", "impulsive behavior", "irritability"],
        "behaviors": ["unpredictable mood changes", "excessive talking during manic phases", "withdrawal during depressive phases", "risky decision-making", "sleep pattern changes"],
        "triggers": ["stress", "sleep disruption", "substance use", "seasonal changes"],
        "severity_levels": {
            "mild": "experiences noticeable mood swings but maintains some stability",
            "moderate": "experiences significant mood episodes that disrupt work and relationships",
            "severe": "experiences extreme manic and depressive episodes requiring intervention"
        }
    },
    "PTSD": {
        "symptoms": ["flashbacks", "nightmares", "severe anxiety", "intrusive thoughts", "hypervigilance", "emotional numbness"],
        "behaviors": ["avoidance of trauma-related triggers", "startling easily", "difficulty trusting others", "emotional outbursts", "detachment from reality"],
        "triggers": ["reminders of trauma", "loud noises", "crowded places", "feeling trapped"],
        "severity_levels": {
            "mild": "experiences occasional intrusive thoughts and mild anxiety about trauma",
            "moderate": "experiences frequent flashbacks and significant avoidance behaviors",
            "severe": "experiences constant re-living of trauma with severe functional impairment"
        }
    }
}


def initialize_client(hf_token):
    """Initialize Hugging Face Inference client."""
    client = InferenceClient(token=hf_token)
    return client


def initialize_tts():
    """Initialize Mozilla TTS model (singleton pattern)."""
    global _tts_instance
    if _tts_instance is None:
        try:
            # Initialize TTS with a pretrained model
            # Using Tacotron2-DDC for English (simpler, more reliable)
            _tts_instance = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", 
                               progress_bar=False,
                               gpu=False)
            print("✓ Mozilla TTS initialized successfully")
        except Exception as e:
            print(f"⚠ Error initializing TTS model tacotron2-DDC: {e}")
            print("Attempting alternative TTS model (glow-tts)...")
            try:
                _tts_instance = TTS(model_name="tts_models/en/ljspeech/glow-tts", 
                                   progress_bar=False,
                                   gpu=False)
                print("✓ Mozilla TTS initialized with glow-tts model")
            except Exception as e2:
                print(f"⚠ Failed to initialize alternative model: {e2}")
                print("Attempting fast_pitch model...")
                try:
                    _tts_instance = TTS(model_name="tts_models/en/ljspeech/fast_pitch",
                                       progress_bar=False,
                                       gpu=False)
                    print("✓ Mozilla TTS initialized with fast_pitch model")
                except Exception as e3:
                    print(f"❌ All TTS models failed: {e3}")
                    raise
    return _tts_instance


def transcribe_audio(input_path):
    """Transcribe audio file to text using Google Speech Recognition."""
    recognizer = sr.Recognizer()
    with sr.AudioFile(input_path) as source:
        audio = recognizer.record(source)
        try:
            patient_text = recognizer.recognize_google(audio)
            return patient_text
        except sr.UnknownValueError:
            return "Speech recognition could not understand audio"
        except sr.RequestError as e:
            return f"Error occurred during speech recognition: {e}"


def generate_patient_response_from_ai(client, prompt_message, hf_token, model_name="meta-llama/Meta-Llama-3-8B-Instruct"):
    """
    Generate AI patient response using Hugging Face Inference API.
    
    Args:
        client: HuggingFace InferenceClient instance
        prompt_message: The prompt to send to the model
        hf_token: Hugging Face API token
        model_name: Model to use for inference
        
    Returns:
        str: Generated AI patient response (AI simulating a patient with mental health condition)
    """
    try:
        # Use chat completion with message history support
        messages = [
            {"role": "user", "content": prompt_message}
        ]
        
        response = ""
        for message in client.chat_completion(
            messages=messages,
            model=model_name,
            max_tokens=500,
            temperature=0.7,
            stream=True
        ):
            # Handle different response formats
            if hasattr(message, 'choices') and len(message.choices) > 0:
                delta = message.choices[0].delta
                if hasattr(delta, 'content') and delta.content:
                    response += delta.content
            elif hasattr(message, 'delta') and hasattr(message.delta, 'content'):
                if message.delta.content:
                    response += message.delta.content
        
        ai_patient_response = response.strip()
        
        # If no response, try non-streaming
        if not ai_patient_response:
            result = client.chat_completion(
                messages=messages,
                model=model_name,
                max_tokens=500,
                temperature=0.7,
                stream=False
            )
            if hasattr(result, 'choices') and len(result.choices) > 0:
                ai_patient_response = result.choices[0].message.content.strip()
        
    except Exception as e:
        print(f"Error with Hugging Face API: {e}")
        print("Attempting text generation instead of chat completion...")
        try:
            # Fallback to text_generation
            result = client.text_generation(
                prompt=prompt_message,
                model=model_name,
                max_new_tokens=500,
                temperature=0.7,
                return_full_text=False
            )
            ai_patient_response = result.strip() if isinstance(result, str) else str(result)
        except Exception as e2:
            print(f"Text generation also failed: {e2}")
            ai_patient_response = "I... I'm having trouble focusing right now. Can you repeat that?"
    
    return ai_patient_response


def synthesize_speech(text, output_path):
    """
    Synthesize speech using Mozilla TTS.
    
    Args:
        text: Text to convert to speech
        output_path: Path where to save the audio file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Initialize TTS if not already done
        tts = initialize_tts()
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Convert output path to .wav if it's .mp3 (Mozilla TTS outputs WAV)
        if output_path.endswith('.mp3'):
            wav_path = output_path.replace('.mp3', '.wav')
        else:
            wav_path = output_path
        
        # Generate speech
        tts.tts_to_file(text=text, file_path=wav_path)
        
        print(f"Speech synthesized successfully: {wav_path}")
        return True
        
    except Exception as e:
        print(f"Error synthesizing speech: {e}")
        return False


def select_patient_condition():
    """
    Randomly select a condition and severity level for the AI patient.
    
    Returns:
        tuple: (condition_name, severity_level)
    """
    condition = random.choice(list(PATIENT_CONDITIONS.keys()))
    severity = random.choice(["mild", "moderate", "severe"])
    return condition, severity


def generate_patient_prompt(condition, severity, therapist_message, message_history, turn_count):
    """
    Generate a realistic patient prompt based on condition and conversation context.
    
    Args:
        condition: The patient's mental health condition
        severity: Severity level (mild, moderate, severe)
        therapist_message: What the therapist just said
        message_history: Full conversation history
        turn_count: Current turn number
        
    Returns:
        str: Prompt for the AI to generate patient response
    """
    condition_data = PATIENT_CONDITIONS[condition]
    symptoms = ", ".join(condition_data["symptoms"][:4])
    behaviors = ", ".join(condition_data["behaviors"][:3])
    severity_desc = condition_data["severity_levels"][severity]
    
    # Build conversation context
    recent_context = ""
    if len(message_history) > 0:
        recent_exchanges = message_history[-4:]  # Last 2 exchanges
        context_parts = []
        for msg in recent_exchanges:
            role = "Therapist" if msg["role"] == "therapist" else "You"
            context_parts.append(f"{role}: {msg['content']}")
        recent_context = "\n".join(context_parts)
    
    # Opening behavior for first message
    opening_guidance = ""
    if turn_count == 1:
        opening_guidance = """This is the beginning of the therapy session. You are hesitant, perhaps nervous or guarded. You might:
- Give brief, cautious responses initially
- Test the therapist's empathy and understanding
- Show visible signs of your condition (anxiety, low energy, emotional volatility, or trauma responses)
- Not immediately open up about deep issues"""
    else:
        opening_guidance = f"""This is turn {turn_count} of the session. Based on how the therapist has been treating you:
- If they've shown empathy and good listening skills, gradually open up more
- If they've been judgmental or dismissive, become more guarded or defensive
- If they've asked good questions, provide more detailed answers
- Show realistic emotional progression (don't change too quickly)"""
    
    prompt = f"""You are roleplaying as a patient in a therapy training simulation. Your role is to help train therapists by acting as a realistic patient with mental health challenges.

YOUR CONDITION:
- Diagnosis: {condition}
- Severity: {severity.upper()} - {severity_desc}
- Primary Symptoms: {symptoms}
- Behavioral Patterns: {behaviors}

YOUR CHARACTER:
You are Sarah, a 32-year-old software developer. You've been struggling with {condition.lower()} for about 6 months. You're skeptical about therapy but decided to try it because things have been getting worse. You are intelligent, articulate, but emotionally struggling. You have a tendency to intellectualize your feelings as a defense mechanism.

CONVERSATION SO FAR:
{recent_context if recent_context else "This is the start of the session."}

THE THERAPIST JUST SAID:
"{therapist_message}"

{opening_guidance}

YOUR RESPONSE GUIDELINES:
1. Stay completely in character as Sarah with {condition}
2. Show symptoms through your WORDS, not action descriptions - never use *asterisks* or [brackets] for actions
3. Speak naturally in 2-3 sentences - not too long, not too short
4. React realistically to what the therapist says:
   - Appreciate genuine empathy and validation
   - Feel frustrated by clichés or dismissive comments
   - Respond defensively to leading or judgmental questions
   - Open up more when asked thoughtful, open-ended questions
5. Include emotional undertones in your speech, but NO action descriptions like *fidgets* or *pauses*
6. Don't be a "perfect patient" - show real human resistance, deflection, or ambivalence sometimes
7. Progress the conversation - don't just repeat the same information
8. If the therapist makes a mistake (interrupts, changes subject, gives advice too soon), react naturally

IMPORTANT: Only speak actual dialogue. Never include:
- *nervously fidgets* 
- [pauses]
- (looks down)
- *sighs*
Just say what Sarah would say out loud in 2-3 sentences.

AUTHENTIC SPEECH PATTERNS FOR {condition.upper()}:
{get_speech_pattern_guidance(condition)}

Respond now as Sarah, the patient:"""

    return prompt


def get_speech_pattern_guidance(condition):
    """Get condition-specific speech pattern guidance."""
    patterns = {
        "Anxiety": """- Speak with some hesitation, maybe trailing off
- Ask for reassurance ("Is that normal?" "Do you think I'm overreacting?")
- Jump between topics when anxious
- Use minimizing language ("It's probably nothing, but...")""",
        
        "Depression": """- Speak with low energy, shorter sentences
- Use hopeless language ("What's the point?" "Nothing helps")
- Struggle to articulate positive feelings
- Give flat, monotone responses when energy is very low""",
        
        "Bipolar Disorder": """- Energy level varies - sometimes rapid speech, sometimes withdrawn
- During high energy: tangential, enthusiastic, oversharing
- During low energy: withdrawn, brief, pessimistic
- May show irritability if feeling misunderstood""",
        
        "PTSD": """- May pause or become distracted when triggered
- Hypervigilant language ("I need to know..." "What if...")
- Avoid certain topics or details
- Occasional dissociation ("I don't know, I just... zoned out")"""
    }
    return patterns.get(condition, "")


def clean_response(response):
    """Clean up AI-generated responses."""
    # Remove common prefixes
    prefixes_to_remove = [
        "Patient: ", "Patient:", "Sarah: ", "Sarah:",
        "Response: ", "Response:", "You: ", "You:",
        "As Sarah: ", "As the patient: "
    ]
    
    for prefix in prefixes_to_remove:
        if response.startswith(prefix):
            response = response[len(prefix):].strip()
    
    # Remove quotes at start/end
    if response.startswith('"') and response.endswith('"'):
        response = response[1:-1]
    if response.startswith("'") and response.endswith("'"):
        response = response[1:-1]
    
    # Remove action descriptions in asterisks or brackets
    import re
    # Remove *action*, [action], (action)
    response = re.sub(r'\*[^*]+\*', '', response)
    response = re.sub(r'\[[^\]]+\]', '', response)
    response = re.sub(r'\([^)]*fidget[^)]*\)', '', response, flags=re.IGNORECASE)
    response = re.sub(r'\([^)]*pause[^)]*\)', '', response, flags=re.IGNORECASE)
    response = re.sub(r'\([^)]*sigh[^)]*\)', '', response, flags=re.IGNORECASE)
    response = re.sub(r'\([^)]*look[^)]*\)', '', response, flags=re.IGNORECASE)
    
    # Clean up multiple spaces and trim
    response = re.sub(r'\s+', ' ', response)
    response = response.strip()
    
    # Remove leading punctuation artifacts
    response = response.lstrip('.,;:')
    
    # Ensure we have a valid response
    if len(response) < 10 or "python" in response.lower() or "roleplaying" in response.lower():
        response = "I'm not sure how to answer that right now."
    
    return response


def evaluate_therapist_performance(client, message_history, patient_condition, hf_token, model_name):
    """
    Evaluate the therapist's performance using LLM analysis.
    
    Args:
        client: HuggingFace InferenceClient
        message_history: Full conversation history
        patient_condition: The patient's condition
        hf_token: HuggingFace token
        model_name: Model to use
        
    Returns:
        dict: Evaluation results with score, strengths, improvements, and feedback
    """
    # Build conversation transcript
    transcript = []
    for msg in message_history:
        role = "Therapist" if msg["role"] == "therapist" else "Patient"
        transcript.append(f"{role}: {msg['content']}")
    
    conversation_text = "\n".join(transcript)
    
    evaluation_prompt = f"""You are an expert clinical supervisor evaluating a therapy training session. The trainee therapist was working with a simulated patient who has {patient_condition}.

THERAPY SESSION TRANSCRIPT:
{conversation_text}

EVALUATION TASK:
Analyze this therapy session and provide a comprehensive evaluation of the therapist's performance. Consider:

1. THERAPEUTIC SKILLS:
   - Active listening and reflection
   - Empathy and validation
   - Open-ended questions vs closed questions
   - Avoiding judgment and giving space
   - Building rapport and trust
   - Pacing and timing

2. CLINICAL COMPETENCE:
   - Appropriate responses to {patient_condition} symptoms
   - Recognition of patient's emotional state
   - Use of evidence-based techniques
   - Avoiding common pitfalls (giving advice too early, minimizing feelings, interrupting)

3. AREAS OF CONCERN:
   - Missed opportunities to explore deeper
   - Inappropriate responses or questions
   - Breaking therapeutic alliance
   - Over-directing or under-directing

Provide your evaluation in this EXACT format:

SCORE: [number from 0-100]

STRENGTHS:
- [strength 1]
- [strength 2]
- [strength 3]

IMPROVEMENTS:
- [improvement area 1]
- [improvement area 2]
- [improvement area 3]

FEEDBACK:
[2-3 sentences of detailed, constructive feedback]

Be honest and constructive. A typical beginner therapist scores 50-65. Good therapists score 70-85. Excellent therapists score 85+."""

    try:
        # Generate evaluation
        evaluation_text = generate_patient_response_from_ai(client, evaluation_prompt, hf_token, model_name)
        
        # Parse the evaluation
        parsed = parse_evaluation(evaluation_text)
        return parsed
        
    except Exception as e:
        print(f"Error generating evaluation: {e}")
        # Return default evaluation on error
        return {
            "score": 60,
            "strengths": ["Showed basic empathy", "Asked some relevant questions", "Maintained professional demeanor"],
            "improvements": ["Could ask more open-ended questions", "Could validate emotions more explicitly", "Could explore patient's feelings more deeply"],
            "feedback": "The session showed basic therapeutic skills but there's room for growth in building deeper rapport and using advanced techniques. Continue practicing active listening and validation."
        }


def parse_evaluation(evaluation_text):
    """Parse the LLM evaluation response into structured data."""
    try:
        lines = evaluation_text.strip().split('\n')
        
        score = 60  # default
        strengths = []
        improvements = []
        feedback = ""
        
        current_section = None
        
        for line in lines:
            line = line.strip()
            
            if line.startswith("SCORE:"):
                # Extract number from score line
                score_text = line.replace("SCORE:", "").strip()
                # Extract first number found
                import re
                numbers = re.findall(r'\d+', score_text)
                if numbers:
                    score = int(numbers[0])
                    score = max(0, min(100, score))  # Clamp to 0-100
            
            elif line.startswith("STRENGTHS:"):
                current_section = "strengths"
            
            elif line.startswith("IMPROVEMENTS:"):
                current_section = "improvements"
            
            elif line.startswith("FEEDBACK:"):
                current_section = "feedback"
            
            elif line.startswith("-") and current_section in ["strengths", "improvements"]:
                item = line[1:].strip()
                if item:
                    if current_section == "strengths":
                        strengths.append(item)
                    else:
                        improvements.append(item)
            
            elif current_section == "feedback" and line:
                feedback += line + " "
        
        # Ensure we have at least some content
        if not strengths:
            strengths = ["Completed the therapy session", "Engaged with the patient", "Maintained professionalism"]
        if not improvements:
            improvements = ["Practice more active listening", "Ask more open-ended questions", "Deepen emotional exploration"]
        if not feedback:
            feedback = "Continue developing your therapeutic skills through practice and supervision."
        
        return {
            "score": score,
            "strengths": strengths[:5],  # Max 5 items
            "improvements": improvements[:5],
            "feedback": feedback.strip()
        }
        
    except Exception as e:
        print(f"Error parsing evaluation: {e}")
        return {
            "score": 60,
            "strengths": ["Showed engagement", "Maintained session structure"],
            "improvements": ["Continue skill development", "Practice advanced techniques"],
            "feedback": "Keep practicing to develop your therapeutic skills further."
        }


def save_evaluation(evaluation, base_path):
    """Save evaluation results to PDF and JSON files in project directory."""
    try:
        # Create evaluations directory in the Server folder
        current_dir = os.path.dirname(os.path.abspath(__file__))
        eval_dir = os.path.join(current_dir, "Evaluations")
        os.makedirs(eval_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save JSON version
        json_path = os.path.join(eval_dir, f"evaluation_{timestamp}.json")
        with open(json_path, 'w') as f:
            json.dump(evaluation, f, indent=2)
        print(f"✓ Evaluation JSON saved to: {json_path}")
        
        # Save PDF version if reportlab is available
        if REPORTLAB_AVAILABLE:
            pdf_path = os.path.join(eval_dir, f"evaluation_{timestamp}.pdf")
            create_evaluation_pdf(evaluation, pdf_path, timestamp)
            print(f"✓ Evaluation PDF saved to: {pdf_path}")
            print(f"\n{'='*60}")
            print(f"EVALUATION FILES SAVED TO:")
            print(f"{eval_dir}")
            print(f"{'='*60}\n")
        else:
            print(f"⚠ PDF not created (reportlab not installed)")
            print(f"JSON saved to: {eval_dir}")
        
        return True
        
    except Exception as e:
        print(f"Error saving evaluation: {e}")
        import traceback
        traceback.print_exc()
        return False


def create_evaluation_pdf(evaluation, pdf_path, timestamp):
    """Create a professional PDF evaluation report."""
    if not REPORTLAB_AVAILABLE:
        return
    
    try:
        doc = SimpleDocTemplate(pdf_path, pagesize=letter,
                                rightMargin=72, leftMargin=72,
                                topMargin=72, bottomMargin=18)
        
        # Container for the 'Flowable' objects
        elements = []
        
        # Define styles
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor='#2C3E50',
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor='#34495E',
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        )
        
        score_style = ParagraphStyle(
            'ScoreStyle',
            parent=styles['Normal'],
            fontSize=18,
            textColor='#27AE60' if evaluation['score'] >= 70 else '#E67E22' if evaluation['score'] >= 50 else '#E74C3C',
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontSize=11,
            textColor='#2C3E50',
            spaceAfter=6,
            leading=14
        )
        
        # Title
        elements.append(Paragraph("Therapist Performance Evaluation", title_style))
        elements.append(Spacer(1, 0.2*inch))
        
        # Timestamp
        date_str = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        elements.append(Paragraph(f"<i>Session Date: {date_str}</i>", body_style))
        elements.append(Spacer(1, 0.3*inch))
        
        # Score
        score_text = f"Overall Score: {evaluation['score']}/100"
        elements.append(Paragraph(score_text, score_style))
        
        # Score interpretation
        if evaluation['score'] >= 85:
            interpretation = "Excellent - Expert Level Performance"
        elif evaluation['score'] >= 70:
            interpretation = "Good - Solid Therapeutic Skills"
        elif evaluation['score'] >= 50:
            interpretation = "Beginner - Developing Skills"
        else:
            interpretation = "Needs Improvement"
        elements.append(Paragraph(f"<i>{interpretation}</i>", body_style))
        elements.append(Spacer(1, 0.3*inch))
        
        # Strengths
        elements.append(Paragraph("Strengths", heading_style))
        for strength in evaluation['strengths']:
            elements.append(Paragraph(f"✓ {strength}", body_style))
        elements.append(Spacer(1, 0.2*inch))
        
        # Areas for Improvement
        elements.append(Paragraph("Areas for Improvement", heading_style))
        for improvement in evaluation['improvements']:
            elements.append(Paragraph(f"→ {improvement}", body_style))
        elements.append(Spacer(1, 0.2*inch))
        
        # Detailed Feedback
        elements.append(Paragraph("Detailed Feedback", heading_style))
        elements.append(Paragraph(evaluation['feedback'], body_style))
        elements.append(Spacer(1, 0.4*inch))
        
        # Footer
        elements.append(Spacer(1, 0.3*inch))
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=9,
            textColor='#7F8C8D',
            alignment=TA_CENTER
        )
        elements.append(Paragraph("<i>VR Therapist Training System - AI-Generated Evaluation</i>", footer_style))
        
        # Build PDF
        doc.build(elements)
        
    except Exception as e:
        print(f"Error creating PDF: {e}")
        import traceback
        traceback.print_exc()


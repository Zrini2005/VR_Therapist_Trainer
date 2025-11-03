"""Quick test to show where evaluations will be saved"""
import os
from therapy_session import save_evaluation

# Get the directory where therapy_session.py is located
current_dir = os.path.dirname(os.path.abspath(__file__))
eval_dir = os.path.join(current_dir, "Evaluations")

print("="*60)
print("EVALUATION SAVE LOCATION TEST")
print("="*60)
print(f"\nEvaluations will be saved to:")
print(f"{eval_dir}")
print(f"\nFull path:")
print(f"{os.path.abspath(eval_dir)}")
print("\n" + "="*60)

# Test creating a dummy evaluation
test_eval = {
    "score": 75,
    "strengths": ["Test strength 1", "Test strength 2"],
    "improvements": ["Test improvement 1", "Test improvement 2"],
    "feedback": "This is a test evaluation to verify the save location works correctly."
}

print("\nCreating test evaluation...")
result = save_evaluation(test_eval, "")

if result:
    print("\n✓ Test evaluation created successfully!")
    print(f"\nCheck the folder: {eval_dir}")
else:
    print("\n✗ Test evaluation failed!")

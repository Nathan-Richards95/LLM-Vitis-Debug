from Models.Llama import Llama
import Models.Model as Model
from pathlib import Path

def extract_code(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    return text


def looks_like_full_code(generated: str, original: str):
    reasons = []

    if not generated.strip():
        reasons.append("empty output")

    if len(generated) < 0.65 * len(original):
        reasons.append("too short")

    if "```" in generated:
        reasons.append("markdown detected")

    if generated.count("{") != generated.count("}"):
        reasons.append("unbalanced braces")

    return len(reasons) == 0, reasons

# Load broken code
broken_path = Path("Test_Cases/Debug002/broken/broken.cpp")
broken_code = broken_path.read_text()

# Build prompt
prompt = f"""You are fixing a broken C++ source file for AMD Vitis/AIE.

Requirements:
- Return the COMPLETE corrected source file
- Do NOT return partial code
- Do NOT omit unchanged code
- Do NOT add explanations
- Do NOT use markdown fences
- Preserve all includes, declarations, and unchanged functions
- Only fix the bug(s) needed
- DOUBLE CHECK EVERYTHING, NO TEXT, ONLY THE ENTIRE CODE WITH APPROPRIATE BUG FIXES!!!!!!!!

Return the full corrected contents of the file below:

{broken_code}
"""

# Config
config = Model.GenerationConfig(
    model_name="qwen",
    max_tokens=1000000,
    temperature=0.2,
    top_p=0.9
)

# Run model
path = "/scratch/jgvincen/models/qwen2.5-32b-aie-merged"
model = Llama(config,path)

max_attempts = 3
final_code = None

for attempt in range(1, max_attempts + 1):
    print(f"\n===== Attempt {attempt}/{max_attempts} =====")

    response = model.generate([
        {"role": "user", "content": prompt}
    ])

    candidate = extract_code(response.text)

    valid, reasons = looks_like_full_code(candidate, broken_code)

    if valid:
        print("✔ Full code generated")
        final_code = candidate
        break

    print("✖ Incomplete output:")
    for r in reasons:
        print("  -", r)

    prompt = f"""Your previous response was incomplete.

Problems:
{chr(10).join("- " + r for r in reasons)}

Return the FULL corrected file.
Do not omit any code.
Do not explain anything.

Original:
{broken_code}

Previous output:
{candidate}
"""

# Fallback if all attempts fail
if final_code is None:
    print("Using last attempt")
    final_code = candidate

# Print final output
print("\n===== FINAL MODEL OUTPUT =====")
print(final_code)

# Save final output
output_path = Path("Test_Cases/Debug002/llm_output/llm_out.cpp")
output_path.parent.mkdir(parents=True, exist_ok=True)
output_path.write_text(final_code)

print(f"\nSaved output to: {output_path}")

"""
response = model.generate([
    {"role": "user", "content": prompt}
])

# Print output
print("===== MODEL OUTPUT =====")
print(response.text)

# Save output (VERY IMPORTANT for next step)
output_path = Path("Test_Cases/Debug005/llm_output/llm_out.cpp")
output_path.parent.mkdir(parents=True, exist_ok=True)
output_path.write_text(response.text)

print(f"\nSaved output to: {output_path}")
"""
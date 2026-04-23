from Models.Llama import Llama
import Models.Model as Model
from pathlib import Path

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
    model_name="codestral",
    max_tokens=300,
    temperature=0.2,
    top_p=0.9
)

# Run model
path = "/home/jgvincen/CEN571Proj/LLM-Vitis-Debug/Collab_Models/codestral-22b-aie-merged"
model = Llama(config,path)
response = model.generate([
    {"role": "user", "content": prompt}
])

# Print output
print("===== MODEL OUTPUT =====")
print(response.text)

# Save output (VERY IMPORTANT for next step)
output_path = Path("Test_Cases/Debug002/llm_output/llm_out.cpp")
output_path.parent.mkdir(parents=True, exist_ok=True)
output_path.write_text(response.text)

print(f"\nSaved output to: {output_path}")
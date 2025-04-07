import os
import csv
import json

# === CONFIGURATION ===
# Change the below theme for different folders with themes
# Make sure the theme has all 8 processor schematics inside.
theme_name = "cave_theme"
base_folder = os.path.dirname(os.path.abspath(__file__))
weights_folder = os.path.join(base_folder, theme_name, "BlockWeights")
output_json_path = os.path.join(base_folder, theme_name, "processor_block_weights.json")

replacements = []

# === PROCESS EACH BLOCK WEIGHT FILE ===
for file in sorted(os.listdir(weights_folder)):
    if not file.endswith("_blockWeights.csv"):
        continue

    file_path = os.path.join(weights_folder, file)
    with open(file_path, newline="") as f:
        reader = csv.DictReader(f)

        for row in reader:
            input_state = row["ProcessorType"]
            try:
                block_weights = json.loads(row["BlockWeights"])
            except json.JSONDecodeError as e:
                print(f"⚠️ Failed to parse JSON in {file}, column {row['Column']}: {e}")
                continue

            output_steps = [
                {
                    "output_state": block,
                    "step_size": weight
                } for block, weight in block_weights.items()
            ]

            replacements.append({
                "input_state": input_state,
                "output_steps": output_steps
            })


# This is where the structure is built, 
# If the structure needs to change, change it here. 
output_data = {
    "processors": [
        {
            "processor_type": "wotr:spot_gradient",
            "replacements": replacements
        }
    ]
}

# Commit to Json file. 
# TODO: Add error handling.
with open(output_json_path, "w") as out_f:
    json.dump(output_data, out_f, indent=2)

print(f"✅ Exported: {output_json_path}")

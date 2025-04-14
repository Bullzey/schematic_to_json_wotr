import os
import csv
import json
from amulet_nbt import load, CompoundTag
from collections import defaultdict

# === CONFIGURATION ===
# This section will need some kind of interface to select the theme folder, but for now it is hardcoded.
# The theme folder should contain the .schem files to be converted to CSV.
theme_name = "wout_theme"  # Name of the folder containing your .schem files
base_folder = os.path.dirname(os.path.abspath(__file__))
theme_folder = os.path.join(base_folder, theme_name)
csv_output_folder = os.path.join(theme_folder, "Blockcsv")
csv_counts_folder = os.path.join(theme_folder, "BlockCounts")
csv_weights_folder = os.path.join(theme_folder, "BlockWeights")
output_json_path = os.path.join(base_folder, theme_name, f"{theme_name}.json")


# Expected schematic files
# Files should be named Processor1.schem, Processor2.schem, etc.
expected_schems = {f"processor{i}.schem" for i in range(1, 9)}

# === SETUP ===
# Make sure the directories exists
os.makedirs(csv_output_folder, exist_ok=True)
os.makedirs(csv_counts_folder, exist_ok=True)
os.makedirs(csv_weights_folder, exist_ok=True)

# Check for unexpected files in the theme folder, currently checking for 8 files, this could be changed if wanted.
# If we want to change the amount of processor blocks we can change the expected_schems variable above.
# This will check for any files that are not in the expected_schems set and print them out.
all_files = {f for f in os.listdir(theme_folder) if os.path.isfile(os.path.join(theme_folder, f))}
unexpected = all_files - expected_schems

# Tells you what files are in the theme folder that are not in the expected_schems set.
# TODO: Fix as currently it's always printing this
if unexpected:
    print("⚠️ Found unexpected files in the theme folder:")
    for filename in sorted(unexpected):
        print(f"  - {filename}")
    print()

# Blocks we want to skip while exporting from schematic to csv, currently the end block of the template is bedrock.
ignored_blocks = {
    "minecraft:air",
    "minecraft:void_air",
    "minecraft:cave_air",
    "minecraft:bedrock",
}

# === COLUMN INDEX TO BLOCK TYPE SUFFIX ===
# This needs to be the correct order as the template. We could make this more dynamic by checking the template, but for now it is hardcoded.
column_suffixes = [
    "",  # 0 = base block
    "_directional_pillar",
    "_slab",
    "_stairs",
    "_wall",
    "_button",
    "_pressure_plate",
    "_fence",
    "_fence_gate",
    "_glass_pane",
    "_glass",
    "_trapdoor"#,
    #"_door" # Door is not accepted yet
]

# === PROCESS SCHEMATIC FILES ===
for schem_file in sorted(expected_schems):  # Keep output order consistent
    input_path = os.path.join(theme_folder, schem_file)
    output_path = os.path.join(csv_output_folder, os.path.splitext(schem_file)[0] + ".csv")

    if not os.path.exists(input_path):
        print(f"❌ Missing expected file: {schem_file}")
        continue

    # Load the schematic's NBT data
    nbt = load(input_path)
    compound: CompoundTag = nbt.compound

    width = compound["Width"].py_data
    height = compound["Height"].py_data
    length = compound["Length"].py_data

    palette = compound["Palette"]
    block_data = compound["BlockData"].py_data

    # Map palette index to block name (ignore properties like [facing=north])
    palette_lookup = {v.py_data: k.split("[")[0] for k, v in palette.items()}

    # Write block data to a CSV file
    with open(output_path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Depth", "Height", "Column", "Block"])

        index = 0
        for y in range(height):
            for z in range(length):
                for x in range(width):
                    block_index = block_data[index]
                    block_name = palette_lookup.get(block_index, "unknown")

                    if block_name not in ignored_blocks:
                        writer.writerow([x, y, z, block_name])

                    index += 1
    # This export gets used later down the line but is saved for sense checking if wanted. This can change to only be saved during run and no extra files to be saved
    print(f"✅ Exported: {os.path.relpath(output_path, base_folder)}")

# === HELPER: Convert counts to normalized weights summing to 1.0 ===
def normalize_weights(counts: dict[str, int]) -> dict[str, float]:
    total = sum(counts.values())
    if total == 0:
        return {}

    weights = {k: v / total for k, v in counts.items()}
    rounded = {k: round(v, 3) for k, v in weights.items()}

    # Ensure total sums to 1.0 (adjust for rounding error)
    diff = round(1.0 - sum(rounded.values()), 3)
    if diff != 0:
        # Pick block with highest count; break ties by key order
        max_blocks = [k for k, v in counts.items() if v == max(counts.values())]
        target_block = sorted(max_blocks)[0]
        rounded[target_block] = round(rounded[target_block] + diff, 3)

    return rounded

# === PROCESS EACH CSV FILE ===
for file in os.listdir(csv_output_folder):
    if not file.lower().endswith(".csv"):
        continue

    # === EXTRACT PROCESSOR NUMBER FROM FILENAME ===
    filename_base = os.path.splitext(file)[0].lower()
    if not filename_base.startswith("processor"):
        print(f"Skipping unrelated file: {file}")
        continue

    try:
        processor_num = int(filename_base.replace("processor", ""))
    except ValueError:
        print(f"⚠️ Could not extract processor number from {file}")
        continue

    processor_base = f"wotr:processor_block_{processor_num}"

    # === LOAD CSV ===
    input_csv = os.path.join(csv_output_folder, file)

    # stores the counts of each block in each column this file is unused tho. 
    counts_csv = os.path.join(csv_counts_folder, f"Processor{processor_num}_blockCounts.csv") 
    # This files stores the normalized weights of each block in each column.
    # This is the file that is used by the processor to determine which block to use in each column, and gets converted to Json
    weights_csv = os.path.join(csv_weights_folder, f"Processor{processor_num}_blockWeights.csv")

    column_block_counts = defaultdict(lambda: defaultdict(int))
    column_first_blocks = {}
    
    with open(input_csv, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            x = int(row["Depth"])
            y = int(row["Height"])
            z = int(row["Column"])
            block = row["Block"]

            if x == 0 and y == 0 and z not in column_first_blocks:
                column_first_blocks[z] = block

            column_block_counts[z][block] += 1

    # === VERIFY FIRST BLOCK IN EACH COLUMN ===
    # This checks against the template block to make sure the first block in each column is the expected one.
    # If the first block is not the expected one, we skip the file.
    valid = True
    for column, expected_suffix in enumerate(column_suffixes):
        expected_block = processor_base + expected_suffix
        actual_block = column_first_blocks.get(column)

        if actual_block != expected_block:
            print(f"❌ Column {column} in {file} expected '{expected_block}' at (0,0,{column}) but found '{actual_block}'")
            valid = False

    if not valid:
        print(f"⚠️ Skipping file due to incorrect placeholder blocks: {file}")
        continue

    # === EXPORT RAW COUNTS ===
    with open(counts_csv, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Column", "ProcessorType", "BlockCounts"])
        for column in sorted(column_block_counts):
            suffix = column_suffixes[column] if column < len(column_suffixes) else ""
            processor_type = processor_base + suffix
            block_counts = column_block_counts[column]
            block_counts.pop(processor_type, None)
            writer.writerow([column, processor_type, json.dumps(block_counts)])

    # === EXPORT NORMALIZED WEIGHTS ===
    with open(weights_csv, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Column", "ProcessorType", "BlockWeights"])
        for column in sorted(column_block_counts):
            suffix = column_suffixes[column] if column < len(column_suffixes) else ""
            processor_type = processor_base + suffix
            block_counts = dict(column_block_counts[column])
            block_counts.pop(processor_type, None)
            weights = normalize_weights(block_counts)
            writer.writerow([column, processor_type, json.dumps(weights)])

    print(f"✅ Exported: {counts_csv}")
    print(f"✅ Exported: {weights_csv}")


replacements = []
# === PROCESS EACH BLOCK WEIGHT FILE ===
for file in sorted(os.listdir(csv_weights_folder)):
    if not file.endswith("_blockWeights.csv"):
        continue

    file_path = os.path.join(csv_weights_folder, file)
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

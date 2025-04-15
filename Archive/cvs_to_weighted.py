import os
import csv
import json
from collections import defaultdict

# === CONFIGURATION ===
theme_name = "cave_theme"
base_folder = os.path.dirname(os.path.abspath(__file__))
theme_folder = os.path.join(base_folder, theme_name)
csv_input_folder = os.path.join(theme_folder, "CSV")
csv_counts_folder = os.path.join(theme_folder, "BlockCounts")
csv_weights_folder = os.path.join(theme_folder, "BlockWeights")

os.makedirs(csv_counts_folder, exist_ok=True)
os.makedirs(csv_weights_folder, exist_ok=True)

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
for file in os.listdir(csv_input_folder):
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
    input_csv = os.path.join(csv_input_folder, file)

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

import os
import csv
from amulet_nbt import load, CompoundTag

# === CONFIGURATION ===
# This section will need some kind of interface to select the theme folder, but for now it is hardcoded.
# The theme folder should contain the .schem files to be converted to CSV.
theme_name = "cave_theme"  # Name of the folder containing your .schem files
base_dir = os.path.dirname(os.path.abspath(__file__))  # Directory of this script
theme_dir = os.path.join(base_dir, theme_name)
csv_output_dir = os.path.join(theme_dir, "CSV")

# Expected schematic files
# Files should be named Processor1.schem, Processor2.schem, etc.
expected_schems = {f"Processor{i}.schem" for i in range(1, 9)}

# === SETUP ===
# Make sure the output directory exists
os.makedirs(csv_output_dir, exist_ok=True)

# Check for unexpected files in the theme folder, currently checking for 8 files, this could be changed if wanted.
# If we want to change the amount of processor blocks we can change the expected_schems variable above.
# This will check for any files that are not in the expected_schems set and print them out.
all_files = {f for f in os.listdir(theme_dir) if os.path.isfile(os.path.join(theme_dir, f))}
unexpected = all_files - expected_schems

# Tells you what files are in the theme folder that are not in the expected_schems set.
if unexpected:
    print("⚠️ Found unexpected files in the theme folder:")
    for filename in sorted(unexpected):
        print(f"  - {filename}")
    print()

# Blocks we want to skip while exporting, currently the end block is bedrock.
ignored_blocks = {
    "minecraft:air",
    "minecraft:void_air",
    "minecraft:cave_air",
    "minecraft:bedrock",
}

# === PROCESS SCHEMATIC FILES ===
for schem_file in sorted(expected_schems):  # Keep output order consistent
    input_path = os.path.join(theme_dir, schem_file)
    output_path = os.path.join(csv_output_dir, os.path.splitext(schem_file)[0] + ".csv")

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

    print(f"✅ Exported: {os.path.relpath(output_path, base_dir)}")

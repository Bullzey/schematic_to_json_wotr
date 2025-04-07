import os
import csv
from amulet_nbt import load
from amulet_nbt import CompoundTag

# === CONFIGURATION ===
theme_name = "cave_theme"  # Folder containing processor .schem files
base_folder = os.path.dirname(os.path.abspath(__file__))  # Folder where this script is
theme_folder = os.path.join(base_folder, theme_name)
csv_output_folder = os.path.join(theme_folder, "CSV")
expected_files = {f"Processor{i}.schem" for i in range(1, 9)}

# === CREATE OUTPUT FOLDER IF NEEDED ===
os.makedirs(csv_output_folder, exist_ok=True)

# === WARNING FOR UNEXPECTED FILES ===
all_files = {f for f in os.listdir(theme_folder) if os.path.isfile(os.path.join(theme_folder, f))}
unexpected_files = all_files - expected_files

if unexpected_files:
    print("⚠️ WARNING: Unexpected files found in the folder:")
    for file in unexpected_files:
        print("  -", file)
    print()

# === BLOCKS TO IGNORE ===
ignored_blocks = {
    "minecraft:air",
    "minecraft:void_air",
    "minecraft:cave_air"
}

# === PROCESS ONLY EXPECTED FILES ===
for schem_file in sorted(expected_files):  # Sort for consistent order
    input_path = os.path.join(theme_folder, schem_file)
    output_csv = os.path.join(csv_output_folder, os.path.splitext(schem_file)[0] + ".csv")

    if not os.path.exists(input_path):
        print(f"❌ Missing file: {schem_file}")
        continue

    nbt = load(input_path)
    compound: CompoundTag = nbt.compound

    width = compound["Width"].py_data
    height = compound["Height"].py_data
    length = compound["Length"].py_data

    palette = compound["Palette"]
    block_data = compound["BlockData"].py_data
    id_to_block = {v.py_data: k.split("[")[0] for k, v in palette.items()}

    with open(output_csv, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Depth", "Height", "Column", "Block"])

        index = 0
        for y in range(height):
            for z in range(length):
                for x in range(width):
                    palette_index = block_data[index]
                    block_name = id_to_block.get(palette_index, "unknown")

                    if block_name not in ignored_blocks:
                        writer.writerow([x, y, z, block_name])

                    index += 1

    print(f"✅ Exported: {os.path.relpath(output_csv, base_folder)}")

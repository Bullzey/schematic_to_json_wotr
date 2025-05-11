import os
import csv
import json
from amulet_nbt import load, CompoundTag
from collections import defaultdict
import tkinter as tk
from tkinter import simpledialog, filedialog
import sys

# Define the base folder as the directory where this script is located
base_folder = os.path.dirname(os.path.abspath(__file__))

# Function: select_theme_and_target
# Purpose: Creates a GUI popup to select a theme folder and a target (Room or POI)
# Input: None
# Output: Selected theme and target as strings
def select_theme_and_target():
    """Creates a popup to select the theme folder and target (Room or POI)."""
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    # Create a new popup window
    selection_window = tk.Toplevel()
    selection_window.title("Select Theme and Target")

    # Dropdown for theme selection
    tk.Label(selection_window, text="Select Theme", font=("Arial", 12, "bold")).grid(row=0, column=0, pady=10, padx=10)

    theme_var = tk.StringVar()
    theme_folders = [f for f in os.listdir(base_folder) if os.path.isdir(os.path.join(base_folder, f))]
    theme_dropdown = tk.OptionMenu(selection_window, theme_var, *theme_folders)
    theme_dropdown.grid(row=0, column=1, pady=10, padx=10)

    # Buttons for target selection
    tk.Label(selection_window, text="Select Target", font=("Arial", 12, "bold")).grid(row=1, column=0, pady=10, padx=10)

    target_var = tk.StringVar()

    def set_target(value):
        target_var.set(value)

    tk.Button(selection_window, text="Room", command=lambda: set_target("room"), width=10).grid(row=1, column=1, pady=5)
    tk.Button(selection_window, text="POI", command=lambda: set_target("poi"), width=10).grid(row=1, column=2, pady=5)

    # Submit button
    def submit():
        if not theme_var.get() or not target_var.get():
            tk.messagebox.showerror("Error", "Please select both a theme and a target.")
            return
        selection_window.destroy()

    tk.Button(selection_window, text="OK", command=submit).grid(row=2, columnspan=3, pady=10)

    selection_window.wait_window()

    return theme_var.get(), target_var.get()

# Function: show_checklist_popup
# Purpose: Creates a GUI popup with checkboxes and input fields for selecting features and setting processor rarities
# Input: Target type ("room" or "poi")
# Output: Dictionary of selected options and their values
def show_checklist_popup(target):
    """Creates a popup with checkboxes and rarity input fields with default values."""
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    checklist_window = tk.Toplevel()
    checklist_window.title("Select Features & Set Processor")

    # Initialize entry_dict at the start of the function
    entry_dict = {}

    # "Processor" header
    tk.Label(checklist_window, text="Processors", font=("Arial", 12, "bold")).grid(row=0, columnspan=2, pady=10)

    # Add input fields for mandatory items before the mushrooms without checkboxes
    mandatory_items = {
        "noise_scale_x": 0.075,
        "noise_scale_y": 0.075,
        "noise_scale_z": 0.075
    }

    # Add labels and input fields for mandatory items
    row_offset = 1  # Start after the "Processors" header
    for i, (key, default_value) in enumerate(mandatory_items.items()):
        tk.Label(checklist_window, text=key, font=("Arial", 10, "bold")).grid(row=row_offset + i, column=0, sticky="w")
        entry = tk.Entry(checklist_window, width=5)
        entry.insert(0, str(default_value))
        entry.grid(row=row_offset + i, column=1, padx=5)
        entry_dict[key] = entry

    # Adjust the row_offset for the mushrooms and vines to follow the mandatory items
    row_offset += len(mandatory_items)  # Correctly position after mandatory items

    # Define options based on target
    options = ["mushroom", "vines"] if target == "room" else ["chest"]

    # Default processor values
    default_values = {
        "mushroom": 0.05,
        "vines": 0.2,
        "chest": 0.6
    }

    var_dict = {}

    # "Rarity" label
    tk.Label(checklist_window, text="Rarity", font=("Arial", 10, "bold")).grid(row=row_offset, column=1, pady=5)

    # Create checkboxes and input fields for each option
    for i, option in enumerate(options):
        var = tk.IntVar(value=1 if option == "chest" else 0)  # Pre-check chest
        entry = tk.Entry(checklist_window, width=5)
        entry.insert(0, str(default_values.get(option, "")))  # Set default value

        # Create checkboxes for each option
        tk.Checkbutton(checklist_window, text=option, variable=var).grid(row=row_offset + i + 1, column=0, sticky="w")

        # Create input fields for rarity values next to each checkbox
        entry.grid(row=row_offset + i + 1, column=1, padx=5)

        var_dict[option] = var
        entry_dict[option] = entry

    row_offset += len(options) + 1  # row_offset is now the row *after* the last option element

    # If target is "room", replace cobweb checkbox and input box with an "Attachment" section
    if target == "room":
        # Add spacing before the attachment section
        row_offset += 1  # Increment row_offset to create space

        # Add the "Attachment" header and center it
        tk.Label(checklist_window, text="Attachments", font=("Arial", 12, "bold")).grid(row=row_offset, columnspan=9, pady=10)

        # Move down by one row to make space for the "Rarity" label
        row_offset += 1

        # Add headers for Name, Rarity, Up, Sides, Property 1, Value 1, Property 2, Value 2
        tk.Label(checklist_window, text="Name", font=("Arial", 10, "bold")).grid(row=row_offset, column=0, sticky="w", padx=5)
        tk.Label(checklist_window, text="Rarity", font=("Arial", 10, "bold")).grid(row=row_offset, column=1, sticky="w", padx=5)
        tk.Label(checklist_window, text="Up", font=("Arial", 10, "bold")).grid(row=row_offset, column=2, sticky="w", padx=5)
        tk.Label(checklist_window, text="Down", font=("Arial", 10, "bold")).grid(row=row_offset, column=3, sticky="w", padx=5)
        tk.Label(checklist_window, text="Sides", font=("Arial", 10, "bold")).grid(row=row_offset, column=4, sticky="w", padx=5)
        tk.Label(checklist_window, text="Property 1", font=("Arial", 10, "bold")).grid(row=row_offset, column=5, sticky="w", padx=5)
        tk.Label(checklist_window, text="Value 1", font=("Arial", 10, "bold")).grid(row=row_offset, column=6, sticky="w", padx=5)
        tk.Label(checklist_window, text="Property 2", font=("Arial", 10, "bold")).grid(row=row_offset, column=7, sticky="w", padx=5)
        tk.Label(checklist_window, text="Value 2", font=("Arial", 10, "bold")).grid(row=row_offset, column=8, sticky="w", padx=5)

        attachment_entries = []

        # Create 10 rows of input fields for attachments (Name, Rarity, Up, Sides, Property 1, Value 1, Property 2, Value 2)
        for i in range(11):
            name_entry = tk.Entry(checklist_window, width=20)
            name_entry.grid(row=row_offset + 1 + i, column=0, padx=5)

            # Rarity box width reduced to half
            rarity_entry = tk.Entry(checklist_window, width=5)
            rarity_entry.grid(row=row_offset + 1 + i, column=1, padx=5)

            up_var = tk.IntVar()
            up_checkbox = tk.Checkbutton(checklist_window, variable=up_var)
            up_checkbox.grid(row=row_offset + 1 + i, column=2, padx=5)

            down_var = tk.IntVar()
            down_checkbox = tk.Checkbutton(checklist_window, variable=down_var)
            down_checkbox.grid(row=row_offset + 1 + i, column=3, padx=5)

            # Sides box width reduced to half
            sides_entry = tk.Entry(checklist_window, width=5)
            sides_entry.grid(row=row_offset + 1 + i, column=4, padx=5)

            property_1_entry = tk.Entry(checklist_window, width=20)
            property_1_entry.grid(row=row_offset + 1 + i, column=5, padx=5)

            value_1_entry = tk.Entry(checklist_window, width=20)
            value_1_entry.grid(row=row_offset + 1 + i, column=6, padx=5)

            property_2_entry = tk.Entry(checklist_window, width=20)
            property_2_entry.grid(row=row_offset + 1 + i, column=7, padx=5)

            value_2_entry = tk.Entry(checklist_window, width=20)
            value_2_entry.grid(row=row_offset + 1 + i, column=8, padx=5)

            attachment_entries.append({
                "name": name_entry,
                "rarity": rarity_entry,
                "up": up_var,
                "down": down_var,
                "sides": sides_entry,
                "property_1": property_1_entry,
                "value_1": value_1_entry,
                "property_2": property_2_entry,
                "value_2": value_2_entry
            })

        # Store these input fields in the entry_dict
        entry_dict["attachments"] = attachment_entries

    def submit():
        selected_options = {}
        for opt in options:
            if var_dict[opt].get() == 1:  # Only add checked options
                processor = entry_dict[opt].get()
                try:
                    selected_options[opt] = float(processor)
                except ValueError:
                    selected_options[opt] = None  # Keep it empty if invalid

        # Include mandatory items
        for key in mandatory_items:
            try:
                selected_options[key] = float(entry_dict[key].get())
            except ValueError:
                selected_options[key] = mandatory_items[key]  # Use default if invalid

        # If "room" is selected, also add attachment details
        if target == "room":
            attachment_data = []
            for attachment in entry_dict["attachments"]:
                attachment_data.append({
                    "name": attachment["name"].get(),
                    "rarity": attachment["rarity"].get(),
                    "up": attachment["up"].get(),
                    "down": attachment["down"].get(),
                    "sides": attachment["sides"].get(),
                    "property_1": attachment["property_1"].get(),
                    "value_1": attachment["value_1"].get(),
                    "property_2": attachment["property_2"].get(),
                    "value_2": attachment["value_2"].get()
                })
            selected_options["attachments"] = attachment_data

        checklist_window.selected_options = selected_options
        checklist_window.destroy()

    # Determine the row for the submit button
    submit_button_actual_row = row_offset # Default if not 'room' and no attachments
    submit_button_column_span = 2 # Default for mandatory/options items

    if target == "room":
        # If attachments were added, row_offset was updated internally.
        # The last attachment entry is at (row_offset + 1 + 10)
        # So, submit button is at row_offset + 12
        submit_button_actual_row = row_offset + 12 # Accounts for 11 entry rows + header
        submit_button_column_span = 9 # To span across attachment columns

    submit_button = tk.Button(checklist_window, text="OK", command=submit)
    submit_button.grid(row=submit_button_actual_row, columnspan=submit_button_column_span, pady=10)

    checklist_window.selected_options = None
    checklist_window.wait_window()
    return checklist_window.selected_options
# Function: normalize_weights
# Purpose: Normalizes block counts into weights that sum to 1.0
# Input: Dictionary of block counts
# Output: Dictionary of normalized weights
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

# Blocks to ignore during processing
ignored_blocks = {
    "minecraft:air",
    "minecraft:void_air",
    "minecraft:cave_air",
    "minecraft:bedrock",
}

# Function: filter_blocks_to_ignore
# Purpose: Filters out blocks that should be ignored during processing
# Input: List of blocks to ignore and the block data
# Output: Filtered block data
def filter_blocks_to_ignore(block_data, blocks_to_ignore):
    """Filters out blocks that are in the ignore list."""
    return {block: count for block, count in block_data.items() if block not in blocks_to_ignore}

# Function: process_schematics
# Purpose: Processes .schem files to generate CSV files for block data, counts, and weights
# Input: Paths to theme folder, output folders for CSVs, and weights
# Output: List of processor replacements for JSON generation
def process_schematics(theme_folder, csv_output_folder, csv_counts_folder, csv_weights_folder):
    """Processes .schem files and generates JSON for processors."""
    expected_schems = {f"processor{i}.schem" for i in range(1, 9)}
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
        "_glass",
        "_glass_pane",
        "_trapdoor"
    ]

    # Extend the expected_schems to include optional processors 9 to 15
    optional_schems = {f"processor{i}.schem" for i in range(9, 16)}
    all_schems = sorted(expected_schems | optional_schems)

    os.makedirs(csv_output_folder, exist_ok=True)
    os.makedirs(csv_counts_folder, exist_ok=True)
    os.makedirs(csv_weights_folder, exist_ok=True)

    replacements = []

    # Update the loop to process both required and optional schematics
    for schem_file in all_schems:  # Keep output order consistent
        input_path = os.path.join(theme_folder, schem_file)
        output_path = os.path.join(csv_output_folder, os.path.splitext(schem_file)[0] + ".csv")

        if not os.path.exists(input_path):
            if schem_file in expected_schems:
                print(f"❌ Missing required file: {schem_file}")
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
        print(f"✅ Exported: {os.path.relpath(output_path, base_folder)}")

    for file in os.listdir(csv_output_folder):
        if not file.lower().endswith(".csv"):
            continue

        filename_base = os.path.splitext(file)[0].lower()
        if not filename_base.startswith("processor"):
            continue

        try:
            processor_num = int(filename_base.replace("processor", ""))
        except ValueError:
            continue

        processor_base = f"wotr:processor_block_{processor_num}"

        input_csv = os.path.join(csv_output_folder, file)
        counts_csv = os.path.join(csv_counts_folder, f"Processor{processor_num}_blockCounts.csv")
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

        # Verify the first block in each column matches the expected processor block
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

        with open(counts_csv, "w", newline="") as f:
            writer = csv.writer(f)  # Corrected file object reference
            writer.writerow(["Column", "ProcessorType", "BlockCounts"])
            for column in sorted(column_block_counts):
                suffix = column_suffixes[column] if column < len(column_suffixes) else ""
                processor_type = processor_base + suffix
                block_counts = column_block_counts[column]
                block_counts.pop(processor_type, None)  # Remove the processor block from the block counts
                writer.writerow([column, processor_type, json.dumps(block_counts)])

        with open(weights_csv, "w", newline="") as f:
            writer = csv.writer(f)  # Corrected file object reference
            writer.writerow(["Column", "ProcessorType", "BlockWeights"])
            for column in sorted(column_block_counts):
                suffix = column_suffixes[column] if column < len(column_suffixes) else ""
                processor_type = processor_base + suffix
                block_counts = filter_blocks_to_ignore(dict(column_block_counts[column]), ignored_blocks)
                weights = normalize_weights(block_counts)
                writer.writerow([column, processor_type, json.dumps(weights)])

        print(f"✅ Exported: {counts_csv}")
        print(f"✅ Exported: {weights_csv}")

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
                except json.JSONDecodeError:
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

    return replacements

# Function: process_csv_to_json
# Purpose: Main function to process CSV data into JSON format
# Input: Path to CSV file and output JSON file
# Output: JSON file containing processed data
def process_csv_to_json(csv_file_path, json_file_path):
    theme_name, target = select_theme_and_target()
    if not theme_name or not target:
        print("No theme or target selected. Exiting.")
        sys.exit()

    theme_folder = os.path.join(base_folder, theme_name)
    csv_output_folder = os.path.join(theme_folder, "Blockcsv")
    csv_counts_folder = os.path.join(theme_folder, "BlockCounts")
    csv_weights_folder = os.path.join(theme_folder, "BlockWeights")

    processor_replacements = process_schematics(theme_folder, csv_output_folder, csv_counts_folder, csv_weights_folder)
    
    

    # Additional logic from theme_json_generator
    selected_features = show_checklist_popup(target)
    if selected_features is None:
        print("No selections made, exiting.")
        sys.exit()

    try:
        endnote = []
        for feature, rarity in selected_features.items():
            if rarity is not None:
                if feature == "mushroom":
                    endnote.append({"processor_type": "wotr:mushrooms", "rarity": rarity})
                elif feature == "vines":
                    endnote.append({"processor_type": "wotr:vines", "rarity": rarity})
                elif feature == "chest":
                    endnote.append({
                        "processor_type": "wotr:rift_chests",
                        "base_loot_table": "wotr:chests/",
                        "rarity": rarity,
                        "chest_types": [{"chest_type": "wooden", "weight": 1}]
                    })

        if "attachments" in selected_features:
            for attachment in selected_features["attachments"]:
                if attachment["name"]:
                    attachment_data = {
                        "processor_type": "wotr:attachment",
                        "requires_sides": int(attachment["sides"] if attachment["sides"].strip() else 0),
                        "requires_up": bool(attachment["up"]),
                        "requires_down": bool(attachment["down"]),
                        "rarity": float(attachment["rarity"] if attachment["rarity"].strip() else 0),
                        "blockstate": {
                            "Name": attachment["name"],
                            "Properties": {
                                attachment["property_1"]: attachment["value_1"]
                                for property, value in [
                                    (attachment["property_1"], attachment["value_1"]),
                                    (attachment["property_2"], attachment["value_2"])
                                ]
                                if property and value
                            }
                        }
                    }
                    endnote.append(attachment_data)

        final_output = {
            "processors": [
                {
                    "processor_type": "wotr:spot_gradient",
                    "noise_scale_x": selected_features.get("noise_scale_x", 0.075),
                    "noise_scale_y": selected_features.get("noise_scale_y", 0.075),
                    "noise_scale_z": selected_features.get("noise_scale_z", 0.075),
                    "replacements": processor_replacements,
                    
                },
                *endnote
            ]
        }

        # Generate JSON file name based on target and theme name
        json_file_path = f"{target}_{theme_name}.json"

        with open(json_file_path, 'w', encoding='utf-8') as jsonfile:
            json.dump(final_output, jsonfile, indent=4)

        print(f"JSON data processed and saved to {json_file_path}")
    except Exception as e:
        print(f"Error saving JSON file: {e}")

# Example usage section
# Demonstrates how to call the main function with example file paths
# Example usage
csv_file = 'processor_theme_sheet.csv'
json_file = ''
process_csv_to_json(csv_file, json_file)

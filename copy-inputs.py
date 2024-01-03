# Each folder 'day*' may contain a file named 'input.txt'. What I want is to copy
# them to the folder 'data', changing its name to 'day*-input.txt'

import os
import shutil

# Get the current working directory
cwd = os.getcwd()

# Get the list of folders
folders = [folder for folder in os.listdir(cwd) if folder.startswith("day")]
folders.sort()

# Create the folder 'data' if it doesn't exist
if not os.path.exists("data"):
    os.mkdir("data")

# Copy the files (if they exist)
for folder in folders:
    if os.path.exists(f"{folder}/input.txt"):
        shutil.copy(f"{folder}/input.txt", f"data/{folder}-input.txt")

🖼 As Advance IT Image Cleaner

A Python GUI tool to clean image metadata and batch convert images to HEIC,
with multithreading, logging, and progress tracking.


✨ Features

🧹 Metadata Cleaner → Removes all hidden EXIF/metadata from images for privacy & security

🔄 HEIC Converter → Converts JPG, PNG, BMP, TIFF → .HEIC format with high compression & quality

⚡ Multithreaded Processing → Faster batch conversion using multiple CPU cores

📂 Smart Folder Processing → Skips folders with fewer than X images (configurable)

⏸ Pause / Resume → Pause & resume ongoing conversions

⏹ Stop / Cancel → Cancel running batch safely

📊 Live Progress & ETA → Real-time progress bar with estimated time remaining

📝 Detailed Logs → GUI log window + external log file (conversion_log.txt)

🎨 User-Friendly GUI → Modern Tkinter interface with clean layout

🔒 Safe & Reliable → Cleans metadata without altering visible image content

Install required dependencies:

pip install -r requirements.txt

▶️ Usage

Run the application with:

python converter_gui.py


Click Browse Folder → Select input folder

Adjust Minimum Images per Folder if needed

Click Start Convert

Monitor progress in the log window & progress bar

📌 Converted images will be saved inside the output/ directory,
preserving folder structure.

🛠 Tech Stack

Python

Tkinter
 (GUI)

Pillow
 (Image processing)

pillow-heif
 (HEIC support)

ThreadPoolExecutor
 (Parallelism)

📜 License
Copyright (c) 2025 Eklas Mahmud

✍️ Author
Eklas Mahmud
💼 As Advance IT
🔗 GitHub Profile
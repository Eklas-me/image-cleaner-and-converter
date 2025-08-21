"""
As Advance IT Image Cleaner
Copyright (c) 2025 Eklas Mahmud
All rights reserved.

This software is developed by Eklas Mahmud. Unauthorized copying,
modification, or distribution of this software is strictly prohibited.
"""
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from tkinter import Tk, Label, Button, filedialog, Text, Scrollbar, END, ttk, messagebox
from PIL import Image
import pillow_heif
from datetime import datetime, timedelta

# Register HEIF plugin
pillow_heif.register_heif_opener()

# ===== Global variables =====
INPUT_DIR = ""
OUTPUT_DIR = "output"
LOG_FILE = "conversion_log.txt"
stop_flag = False
pause_flag = threading.Event()  # Pause/Resume flag

# Auto detect workers (reserve 2 cores for smooth system)
MAX_WORKERS = min(4, max(1, os.cpu_count() - 2))

# ===== GUI setup =====
root = Tk()
root.title("As Advance IT Image Cleaner")
root.geometry("850x700")

# ===== Input folder selection (on one horizontal line) =====
folder_frame = ttk.Frame(root)
folder_frame.pack(pady=5)

Label(folder_frame, text="Select Input Folder:").pack(side="left", padx=5)
folder_label = Label(folder_frame, text="No folder selected", fg="blue")
folder_label.pack(side="left", padx=5)

# ===== Minimum images per folder (horizontal) =====
min_frame = ttk.Frame(root)
min_frame.pack(pady=5)

Label(min_frame, text="Minimum Images per Folder:").pack(side="left", padx=5)
min_images_spinbox = ttk.Spinbox(min_frame, from_=1, to=100, width=5)
min_images_spinbox.set(6)  # default = 6
min_images_spinbox.pack(side="left", padx=5)

# Log display
log_text = Text(root, height=30, width=100)
log_text.pack(fill="both", expand=True, padx=10, pady=10)

scrollbar = Scrollbar(log_text)
scrollbar.pack(side="right", fill="y")
log_text.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=log_text.yview)

progress = ttk.Progressbar(root, orient="horizontal", length=800, mode="determinate")
progress.pack(pady=10)

# ===== Buttons in a horizontal frame =====
button_frame = ttk.Frame(root)
button_frame.pack(pady=10, padx=10, anchor="center")

browse_btn = Button(button_frame, text="Browse Folder", bg="#4B9CD3", fg="white", width=15)
start_btn = Button(button_frame, text="Start Convert", bg="green", fg="white", width=15)
pause_btn = Button(button_frame, text="Pause", bg="orange", fg="white", width=15)
stop_btn = Button(button_frame, text="Stop / Cancel", bg="red", fg="white", width=15)

browse_btn.pack(side="left", padx=10)
start_btn.pack(side="left", padx=10)
pause_btn.pack(side="left", padx=10)
stop_btn.pack(side="left", padx=10)

# ===== Watermark =====
copyright_label = Label(
    root,
    text="© 2025 Eklas Mahmud. All rights reserved.",
    fg="gray",
    font=("Arial", 10, "italic")
)
copyright_label.pack(pady=5)

# ===== Helper functions =====
def log_message(msg: str, flush_file=True):
    """Insert log to GUI & optionally write to file."""
    log_text.insert(END, msg + "\n")
    log_text.see(END)
    if flush_file:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(msg + "\n")

def browse_folder():
    global INPUT_DIR
    folder = filedialog.askdirectory()
    if folder:
        INPUT_DIR = folder
        folder_label.config(text=folder)
    else:
        messagebox.showwarning("Warning", "No folder selected!")

browse_btn.config(command=browse_folder)

def gather_images(input_folder, min_images):
    images = []
    skipped_folders = []
    processed_folders = []

    for root_dir, _, files in os.walk(input_folder):
        folder_images = [
            file for file in files
            if file.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".tiff"))
        ]

        if len(folder_images) >= min_images:
            processed_folders.append((root_dir, len(folder_images)))
            for file in folder_images:
                input_file = os.path.join(root_dir, file)
                relative_path = os.path.relpath(root_dir, INPUT_DIR)
                output_folder = os.path.join(OUTPUT_DIR, relative_path)
                os.makedirs(output_folder, exist_ok=True)
                images.append((input_file, output_folder, file))
        else:
            if folder_images:
                skipped_folders.append((root_dir, len(folder_images)))

    return images, processed_folders, skipped_folders

def clean_and_convert(image_path, output_folder, file_name):
    try:
        while pause_flag.is_set():
            time.sleep(0.2)

        img = Image.open(image_path)
        data = list(img.getdata())
        clean_img = Image.new(img.mode, img.size)
        clean_img.putdata(data)

        base_name = os.path.splitext(file_name)[0]
        heic_file = os.path.join(output_folder, f"{base_name}.heic")
        clean_img.save(heic_file, format="HEIF", quality=95)

        return True, f"✅ Converted & Metadata removed: {image_path} → {heic_file}"

    except Exception as e:
        return False, f"❌ Error: {image_path}: {e}"

# ===== Main processing =====
def process_images():
    global stop_flag
    stop_flag = False

    if not INPUT_DIR:
        messagebox.showwarning("Warning", "Please select an input folder first!")
        return

    try:
        min_images = int(min_images_spinbox.get())
    except ValueError:
        messagebox.showerror("Error", "Invalid number in minimum images field!")
        return

    all_images, processed_folders, skipped_folders = gather_images(INPUT_DIR, min_images)

    preview_msg = (
        f"{len(processed_folders)} folders have ({min_images}+ images) and will be processed.\n"
        f"{len(skipped_folders)} folders have less than {min_images} images and will be skipped.\n\n"
        "Do you want to continue?"
    )
    if not messagebox.askyesno("Preview & Confirmation", preview_msg):
        return

    start_btn.config(state="disabled")
    browse_btn.config(state="disabled")
    stop_btn.config(state="normal")
    pause_btn.config(state="normal")

    log_text.delete(1.0, END)
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write("=== Image Conversion Log ===\n")
        f.write("Started at: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n\n")

    total = len(all_images)
    if total == 0:
        log_message("⚠️ No eligible images found in selected folder!")
        start_btn.config(state="normal")
        browse_btn.config(state="normal")
        stop_btn.config(state="disabled")
        pause_btn.config(state="disabled")
        return

    success_count = 0
    error_count = 0
    progress["maximum"] = total
    progress["value"] = 0
    start_time = time.time()

    log_message(f"🚀 Starting conversion using {MAX_WORKERS} workers...")

    BATCH_SIZE = 20
    LOG_BATCH = 5

    for batch_start in range(0, total, BATCH_SIZE):
        batch_images = all_images[batch_start: batch_start + BATCH_SIZE]
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {executor.submit(clean_and_convert, img_in, output_folder, file_name): (img_in, output_folder, file_name)
                       for (img_in, output_folder, file_name) in batch_images}

            batch_results = []
            for idx, future in enumerate(as_completed(futures), start=1 + batch_start):
                if stop_flag:
                    log_message("\n⏹ Conversion stopped by user!")
                    break

                ok, msg = future.result()
                batch_results.append((ok, msg))

                if idx % LOG_BATCH == 0 or idx == total:
                    # Batch update GUI log
                    for r_ok, r_msg in batch_results:
                        log_message(r_msg, flush_file=False)
                    batch_results.clear()

                    # Progress & ETA
                    progress["value"] = idx
                    elapsed = time.time() - start_time
                    avg_time = elapsed / idx
                    remaining = avg_time * (total - idx)
                    eta = str(timedelta(seconds=int(remaining)))
                    log_text.insert(END, f"Progress: {idx}/{total} ({idx/total*100:.1f}%), ETA: {eta}\n")
                    log_text.see(END)
                    log_text.update_idletasks()

                if ok:
                    success_count += 1
                else:
                    error_count += 1

    # ===== Summary =====
    log_message("\n📊 Summary Report")
    log_message(f"   ✅ Success: {success_count}")
    log_message(f"   ❌ Errors : {error_count}")
    log_message(f"   📁 Output saved in: {os.path.abspath(OUTPUT_DIR)}")

    log_message("\n📂 Folder Summary")
    log_message(f"   Processed folders: {len(processed_folders)}")
    for folder, count in processed_folders:
        log_message(f"      ✔ {folder} ({count} images)")

    log_message(f"\n   Skipped folders: {len(skipped_folders)}")
    for folder, count in skipped_folders:
        log_message(f"      ✖ {folder} ({count} images)")

    log_message("\n🎉 Done!")

    start_btn.config(state="normal")
    browse_btn.config(state="normal")
    stop_btn.config(state="disabled")
    pause_btn.config(state="disabled")

# ===== Button actions =====
def start_thread():
    threading.Thread(target=process_images, daemon=True).start()

def stop_conversion():
    global stop_flag
    stop_flag = True

def toggle_pause():
    if not pause_flag.is_set():
        pause_flag.set()
        pause_btn.config(text="Resume", bg="blue")
        log_message("⏸ Paused...")
    else:
        pause_flag.clear()
        pause_btn.config(text="Pause", bg="orange")
        log_message("▶️ Resumed...")

start_btn.config(command=start_thread)
stop_btn.config(command=stop_conversion)
pause_btn.config(command=toggle_pause)
stop_btn.config(state="disabled")
pause_btn.config(state="disabled")

root.mainloop()

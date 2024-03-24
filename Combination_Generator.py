import os
import shutil
from itertools import combinations
import random
import uuid
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw, ImageOps
from io import BytesIO
import requests
import webbrowser
import threading
import configparser
import math
import urllib.request
import urllib.error


def copy_files_to_new_folder(file_combination, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    for file_path in file_combination:
        shutil.copy(file_path, output_folder)


def get_combination_size(file_combination):
    return sum(os.path.getsize(file) for file in file_combination if os.path.isfile(file))


def format_size(size_in_bytes):
    mb_size = size_in_bytes / (1024 * 1024)
    gb_size = mb_size / 1024

    if gb_size >= 1:
        return f"{gb_size:.2f} GB"
    else:
        return f"{mb_size:.2f} MB"


def show_popup_message(message):
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo("Operation Complete", message)
    root.lift()
    root.attributes('-topmost', True)
    root.after_idle(root.attributes, '-topmost', False)


class ToolTip:
    def __init__(self, widget, description):
        self.widget = widget
        self.tooltip = None
        self.description = description
        self.widget.bind("<Enter>", self.on_enter)
        self.widget.bind("<Leave>", self.on_leave)

    def on_enter(self, event=None):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 40

        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")

        label = tk.Label(self.tooltip, text=self.description, background="#ffffe0", relief="solid", borderwidth=1)
        label.pack(ipadx=1)

    def on_leave(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

MAX_RETRIES = 5
BASE_DELAY = 3  # Initial delay in seconds

class CombinationGeneratorApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Combination Generator by M0VER")

        self.set_icon_from_url("https://static.wixstatic.com/media/4db758_094b6a28cfb848f9b5d05dfd5e9627f3~mv2.png/v1/fit/w_138,h_114,q_90/4db758_094b6a28cfb848f9b5d05dfd5e9627f3~mv2.webp")

        screen_width = master.winfo_screenwidth()
        screen_height = master.winfo_screenheight()
        window_width = 500
        window_height = 470
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        self.master.geometry(f"{window_width}x{window_height}+{x}+{y}")

        self.config_file = "config.ini"
        self.load_config()

        self.request_counter = 0  # Counter to track the number of requests made

        self.input_folder_label = tk.Label(
            master, text="Input Folder:")
        self.input_folder_label.grid(
            row=0, column=0, padx=10, pady=10, sticky="e")

        self.input_folder_var = tk.StringVar(
            value=self.config.get("Paths", "InputFolder", fallback=""))
        self.input_folder_entry = tk.Entry(
            master, textvariable=self.input_folder_var, width=40)
        self.input_folder_entry.grid(
            row=0, column=1, padx=10, pady=10, columnspan=2, sticky="w")

        self.input_folder_button = tk.Button(
            master, text="Browse", command=self.browse_input_folder, cursor="hand2")
        self.input_folder_button.grid(row=0, column=3, padx=10, pady=10)

        self.output_folder_label = tk.Label(
            master, text="Output Folder:")
        self.output_folder_label.grid(
            row=1, column=0, padx=10, pady=10, sticky="e")

        self.output_folder_var = tk.StringVar(
            value=self.config.get("Paths", "OutputFolder", fallback=""))
        self.output_folder_entry = tk.Entry(
            master, textvariable=self.output_folder_var, width=40)
        self.output_folder_entry.grid(
            row=1, column=1, padx=10, pady=10, columnspan=2, sticky="w")

        self.output_folder_button = tk.Button(
            master, text="Browse", command=self.browse_output_folder, cursor="hand2")
        self.output_folder_button.grid(row=1, column=3, padx=10, pady=10)

        self.r_label = tk.Label(
            master, text="Files per Combination:")
        self.r_label.grid(row=2, column=1, padx=10, pady=10, sticky="e")

        self.r_var = tk.IntVar(value=self.config.get(
            "Settings", "FilesPerCombination", fallback=2))
        self.r_entry = tk.Entry(
            master, textvariable=self.r_var, width=10)
        self.r_entry.grid(row=2, column=2, padx=5, pady=10, sticky="w")

        self.status_label = tk.Label(
            master, text="", font=("Helvetica", 10), fg="black")
        self.status_label.grid(row=8, column=0, columnspan=4, pady=5)

        self.size_label = tk.Label(
            master, text="Estimated Output Size: 0.00 MB", font=("Helvetica", 10), fg="black")
        self.size_label.grid(row=3, column=0, columnspan=4, pady=5)

        self.combination_label = tk.Label(
            master, text="Combination Calculator", font=("Helvetica", 14, "underline"), fg="blue", cursor="hand2")
        self.combination_label.grid(row=5, column=0, columnspan=4, pady=5)
        ToolTip(self.combination_label, "Calculate the number of combinations (C(n, r))")
        self.combination_label.bind(
            "<Button-1>", lambda event: self.open_combination_calculator())

        self.generate_button = tk.Button(
            master, text="Generate Combinations", font=("Helvetica", 10), cursor="hand2", command=self.run_process_thread)
        self.generate_button.grid(row=6, column=0, columnspan=4, pady=10)
        ToolTip(self.generate_button, "Start the process to generate combinations")

        self.stop_button = tk.Button(
            master, text="Stop Process", font=("Helvetica", 10), cursor="hand2", command=self.stop_process)
        self.stop_button.grid(row=7, column=0, columnspan=4, pady=5)
        ToolTip(self.stop_button, "Stop the running process")

        self.display_round_image()

        self.signature_label = tk.Label(
            master, text="Designed & Created by: M0VER", font=("Helvetica", 10), fg="gray")
        self.signature_label.grid(row=15, column=0, columnspan=4, pady=5)

        self.stop_process_flag = False
        self.process_cancelled_flag = False
        master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_enter_button(self, description):
        self.status_label.config(text=description)

    def on_leave_button(self):
        self.status_label.config(text="")

    def browse_input_folder(self):
        folder = filedialog.askdirectory()
        self.input_folder_var.set(folder)

    def browse_output_folder(self):
        folder = filedialog.askdirectory()
        self.output_folder_var.set(folder)

    def open_combination_calculator(self):
        input_folder = self.input_folder_var.get()
        output_folder = self.output_folder_var.get()

        if not input_folder or not output_folder:
            messagebox.showwarning("Warning", "Please choose both Input and Output folders.")
            return

        n = len(os.listdir(input_folder))
        r = self.r_var.get()
        combination_count = math.comb(n, r)
        message = f"Number of combinations (C(n, r)): {combination_count}"
        messagebox.showinfo("Combination Calculator", message)

    def generate_combinations(self):
        input_folder = self.input_folder_var.get()
        output_base_folder = self.output_folder_var.get()
        r = self.r_var.get()

        if not input_folder or not output_base_folder:
            messagebox.showwarning("Warning", "Please choose both Input and Output folders.")
            return

        files = [os.path.join(input_folder, file) for file in os.listdir(
            input_folder) if os.path.isfile(os.path.join(input_folder, file))]

        if len(files) < r:
            show_popup_message(
                "There are not enough files in the input folder to create combinations.")
            return

        random.shuffle(files)

        max_combinations = math.comb(len(files), r)
        combinations_of_files = list(combinations(files, r))

        for index, file_combination in enumerate(combinations_of_files, start=1):
            if self.stop_process_flag:
                self.status_label.config(text="Process Stopped")
                self.process_cancelled_flag = True
                break

            folder_name = str(uuid.uuid4())
            output_folder = os.path.join(output_base_folder, folder_name)
            copy_files_to_new_folder(file_combination, output_folder)
            print(f"Combination {index} copied to {output_folder}")

            if index >= max_combinations:
                break

        if not self.stop_process_flag:
            if not self.process_cancelled_flag:
                show_popup_message("Operation completed! Made by M0VER.")
            else:
                show_popup_message("Process cancelled! Made by M0VER")

        self.stop_process_flag = False
        self.process_cancelled_flag = False
        self.status_label.config(text="")
        self.size_label.config(text="Estimated Output Size: 0.00 MB")

    def display_round_image(self):
        image_url = "https://static.wixstatic.com/media/4db758_14e6d6ac8107470d8136d8fbda34c56e~mv2.png/v1/fit/w_256,h_256,q_90/4db758_14e6d6ac8107470d8136d8fbda34c56e~mv2.webp"
        retries = 0
        while retries < MAX_RETRIES:
            try:
                with urllib.request.urlopen(image_url) as response:
                    image_data = response.read()
                image = Image.open(BytesIO(image_data))
                image = image.resize((100, 100))
                image = ImageOps.fit(
                    image, (100, 100), method=0, bleed=0.0, centering=(0.5, 0.5))
                mask = Image.new("L", (100, 100), 0)
                draw = ImageDraw.Draw(mask)
                draw.ellipse((0, 0, 100, 100), fill=255)
                image.putalpha(mask)
                photo = ImageTk.PhotoImage(image)

                image_label = tk.Label(
                    self.master, image=photo, cursor="hand2")
                image_label.photo = photo
                image_label.grid(row=9, column=3, padx=10, pady=10, sticky="se")

                image_label.bind("<Enter>", lambda event: self.change_cursor("hand2"))
                image_label.bind("<Leave>", lambda event: self.change_cursor(""))
                image_label.bind("<Button-1>", lambda event: self.open_url(
                    "https://www.nexusmods.com/users/105540373?tab=user+files"))

                self.request_counter += 1
                break
            except urllib.error.URLError as e:
                retries += 1
                time.sleep(BASE_DELAY * retries)
        else:
            print("Failed to download round image: Max retries exceeded")

    def set_icon_from_url(self, icon_url):
        try:
            retries = 0
            while retries < MAX_RETRIES:
                response = requests.get(icon_url)
                if response.status_code == 200:
                    icon_data = response.content
                    img = Image.open(BytesIO(icon_data))
                    img = img.resize((32, 32))
                    photo = ImageTk.PhotoImage(img)
                    self.master.tk.call(
                        'wm', 'iconphoto', self.master._w, photo)
                    break
                else:
                    retries += 1
                    time.sleep(BASE_DELAY * retries)
            else:
                print("Failed to download icon: Max retries exceeded")
        except Exception as e:
            print(f"Failed to set icon: {e}")

    def change_cursor(self, cursor_type):
        self.master.config(cursor=cursor_type)

    def open_url(self, url):
        webbrowser.open_new(url)

    def stop_process(self):
        if self.status_label.cget("text") == "Processing...":
            self.stop_process_flag = True
            self.status_label.config(text="Stopping Process...")
            self.display_stop_message()
        else:
            messagebox.showwarning("Warning", "No process is currently running.")

    def display_stop_message(self):
        stop_message = "Process Cancelled"
        messagebox.showinfo("Process Cancelled", stop_message)

    def run_process_thread(self):
        self.status_label.config(text="Processing...")

        threading.Thread(target=self.generate_combinations).start()

    def load_config(self):
        self.config = configparser.ConfigParser()
        self.config.read(self.config_file)

    def save_config(self):
        if not self.config.has_section("Paths"):
            self.config.add_section("Paths")

        if not self.config.has_section("Settings"):
            self.config.add_section("Settings")

        self.config.set("Paths", "InputFolder", self.input_folder_var.get())
        self.config.set("Paths", "OutputFolder", self.output_folder_var.get())
        self.config.set(
            "Settings", "FilesPerCombination", str(self.r_var.get()))

        with open(self.config_file, "w") as configfile:
            self.config.write(configfile)

    def on_closing(self):
        self.save_config()
        self.master.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = CombinationGeneratorApp(root)
    root.mainloop()

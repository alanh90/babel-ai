import tkinter as tk
from io import BytesIO
from tkinter import filedialog, simpledialog
import win32clipboard
from PIL import Image, ImageTk
from PIL import ImageGrab
import numpy as np
from imagebabelgen import ImageBabelGenerator
import os
import threading

class ImageBabelGUI:
    def __init__(self, master):
        self.master = master
        master.title("Image Babel Generator")

        self.resampling_filter = Image.LANCZOS  # Default resampling filter
        self.randomness_threshold = 0.7  # Default randomness threshold

        # Create an instance of the ImageBabelGenerator with default values
        self.generator = ImageBabelGenerator(width=4, height=4, color_depth=2)

        # Create menu bar
        self.menu_bar = tk.Menu(master)
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="New", command=self.new_settings)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)

        master.config(menu=self.menu_bar)

        # Filter selection dropdown
        self.filter_var = tk.StringVar(value="Lanczos")
        self.filter_dropdown = tk.OptionMenu(master, self.filter_var, "Nearest", "Bilinear", "Bicubic", "Lanczos",
                                             command=self.change_filter)
        self.filter_dropdown.pack()

        # Create GUI elements
        self.canvas = tk.Canvas(master, width=400, height=400, bg="white")
        self.canvas.pack()

        # Slider initialization with dynamic maximum value
        self.slider = tk.Scale(self.master, from_=0, to=self.get_max_slider_value(), orient=tk.HORIZONTAL,
                               command=self.update_image_from_slider)
        self.slider.pack(fill=tk.X, expand=True)

        # Navigation buttons
        navigation_frame = tk.Frame(master)
        navigation_frame.pack()

        self.button_prev = tk.Button(navigation_frame, text="Previous", command=self.previous_image)
        self.button_prev.pack(side=tk.LEFT)

        self.button_next = tk.Button(navigation_frame, text="Next", command=self.next_image)
        self.button_next.pack(side=tk.LEFT)

        self.fast_next_frame = tk.Frame(navigation_frame)
        self.fast_next_frame.pack(side=tk.LEFT)

        self.fast_next_entry = tk.Entry(self.fast_next_frame, width=5)
        self.fast_next_entry.insert(tk.END, "100")  # Set default value to 100
        self.fast_next_entry.pack(side=tk.LEFT)

        self.button_fast_next = tk.Button(self.fast_next_frame, text="Fast Next", command=self.fast_next)
        self.button_fast_next.pack(side=tk.LEFT)

        # Image generation buttons
        generation_frame = tk.Frame(master)
        generation_frame.pack()

        self.button_find_nonrandom = tk.Button(generation_frame, text="Find Next Non-Random", command=self.find_next_nonrandom)
        self.button_find_nonrandom.pack(side=tk.LEFT)

        self.button_save = tk.Button(generation_frame, text="Save Image", command=self.save_image)
        self.button_save.pack(side=tk.LEFT)

        self.button_copy = tk.Button(generation_frame, text="Copy Image", command=self.copy_image)
        self.button_copy.pack(side=tk.LEFT)

        # Image ID display
        self.image_id_label = tk.Label(master, text="Image ID:")
        self.image_id_label.pack()

        self.image_id_text = tk.Text(master, height=1)
        self.image_id_text.pack(fill=tk.X)

        # Show the settings dialog on startup
        self.new_settings()

    def update_image(self, image):
        # Calculate the aspect ratio of the image
        width, height = image.size
        aspect_ratio = width / height

        # Calculate the dimensions to fit the canvas while maintaining the aspect ratio
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        if aspect_ratio > 1:
            # Image is wider than tall
            scaled_width = canvas_width
            scaled_height = int(scaled_width / aspect_ratio)
        else:
            # Image is taller than wide or square
            scaled_height = canvas_height
            scaled_width = int(scaled_height * aspect_ratio)

        # Resize the image to fit the canvas using the selected resampling filter
        image = image.resize((scaled_width, scaled_height), self.resampling_filter)

        image = image.convert("RGB")  # Convert the image to RGB mode

        photo = ImageTk.PhotoImage(image)
        self.canvas.delete("all")
        self.canvas.create_image(canvas_width // 2, canvas_height // 2, anchor=tk.CENTER, image=photo)
        self.canvas.image = photo

    def update_image_from_slider(self, slider_value):
        image_index = int(float(slider_value) / self.slider["to"] * (self.generator.get_total_images() - 1))
        image = self.generator.get_image_at_index(image_index)
        self.update_image(image)
        self.update_image_id(image_index)

    def previous_image(self):
        self.generator.previous_image()
        self.update_image(self.generator.current_image)
        self.update_slider()
        self.update_image_id(self.generator.image_iterator.current_index)

    def next_image(self):
        self.generator.generate_image()
        self.update_image(self.generator.current_image)
        self.update_slider()
        self.update_image_id(self.generator.image_iterator.current_index)

    def fast_next(self):
        try:
            fast_next_steps = self.fast_next_entry.get()
            if not fast_next_steps:
                fast_next_steps = "100"  # Use default value if entry is empty
            fast_next_steps = int(fast_next_steps)
            if fast_next_steps <= 0:
                raise ValueError
            for _ in range(fast_next_steps):
                self.generator.generate_image()
            self.update_image(self.generator.current_image)
            self.update_slider()
            self.update_image_id(self.generator.image_iterator.current_index)
        except ValueError:
            tk.messagebox.showerror("Invalid Input", "Please enter a positive integer for fast next steps.")

    def find_next_nonrandom(self):
        nonrandom_index = self.generator.image_iterator.find_next_nonrandom_index(self.randomness_threshold)
        if nonrandom_index is not None:
            image = self.generator.get_image_at_index(nonrandom_index)
            self.update_image(image)
            self.update_slider_to_index(nonrandom_index)
            self.update_image_id(nonrandom_index)
        else:
            tk.messagebox.showinfo("No Non-Random Image", "No non-random image found.")

    def new_settings(self):
        dialog = tk.Toplevel(self.master)
        dialog.title("Image Settings")

        tk.Label(dialog, text="Enter the image width:").grid(row=0, column=0)
        width_entry = tk.Entry(dialog)
        width_entry.insert(tk.END, str(self.generator.width))
        width_entry.grid(row=0, column=1)

        tk.Label(dialog, text="Enter the image height:").grid(row=1, column=0)
        height_entry = tk.Entry(dialog)
        height_entry.insert(tk.END, str(self.generator.height))
        height_entry.grid(row=1, column=1)

        tk.Label(dialog, text="Enter the color depth:").grid(row=2, column=0)
        color_depth_entry = tk.Entry(dialog)
        color_depth_entry.insert(tk.END, str(self.generator.color_depth))
        color_depth_entry.grid(row=2, column=1)

        def confirm_settings():
            width = int(width_entry.get())
            height = int(height_entry.get())
            color_depth = int(color_depth_entry.get())
            self.generator.set_parameters(width, height, color_depth)
            self.generator.image_iterator = self.generator._generate_image_iterator()
            self.generator.current_image = self.generator.generate_image()
            self.update_image(self.generator.current_image)
            self.update_slider()
            self.update_image_id(self.generator.image_iterator.current_index)
            dialog.destroy()

        def import_image():
            file_path = filedialog.askopenfilename()
            if file_path:
                image = Image.open(file_path)
                image = image.convert("L")  # Convert to black and white
                image = image.quantize(self.generator.color_depth)  # Reduce color depth
                image = image.resize(
                    (int(width_entry.get()), int(height_entry.get())))  # Resize to specified resolution
                image_id = self.generator.get_image_id(image)
                self.generator.image_iterator.current_index = self.generator.image_iterator.get_index_from_id(image_id)
                self.generator.current_image = image
                self.update_image(image)
                self.update_slider()
                self.update_image_id(self.generator.image_iterator.current_index)
                dialog.destroy()

        confirm_button = tk.Button(dialog, text="Confirm", command=confirm_settings)
        confirm_button.grid(row=3, column=0)

        import_button = tk.Button(dialog, text="Import Image", command=import_image)
        import_button.grid(row=3, column=1)

        dialog.transient(self.master)
        dialog.grab_set()

    def save_image(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png")])
        if file_path:
            self.generator.current_image.save(file_path, "PNG")

    def copy_image(self):
        image = self.generator.current_image
        output = BytesIO()
        image.convert("RGB").save(output, "BMP")
        data = output.getvalue()[14:]
        output.close()
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
        win32clipboard.CloseClipboard()

    def update_slider(self):
        self.slider.set(self.generator.image_iterator.current_index)

    def update_slider_to_index(self, index):
        self.slider.set(index)

    def update_image_id(self, index):
        image_id = self.generator.image_iterator.get_id_from_index(index)
        self.image_id_text.delete("1.0", tk.END)
        self.image_id_text.insert(tk.END, str(image_id))

    def get_max_slider_value(self):
        # Ensure we have a valid integer value for the slider's maximum
        return max(0, self.generator.get_total_images() - 1)

    def change_filter(self, selected_filter):
        filters = {
            "Nearest": Image.NEAREST,
            "Bilinear": Image.BILINEAR,
            "Bicubic": Image.BICUBIC,
            "Lanczos": Image.LANCZOS
        }

        self.resampling_filter = filters[selected_filter]
        self.update_image(self.generator.current_image)
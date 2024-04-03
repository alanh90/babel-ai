import tkinter as tk
from tkinter import filedialog, simpledialog
from PIL import Image, ImageTk
import numpy as np
from imagebabelgen import ImageBabelGenerator
import os

class ImageBabelGUI:
    def __init__(self, master):
        self.master = master
        master.title("Image Babel Generator")

        self.randomness_threshold = 0.7  # Default randomness threshold

        # Create an instance of the ImageBabelGenerator with default values
        self.generator = ImageBabelGenerator(width=4, height=4, color_depth=2)

        # Create menu bar
        self.menu_bar = tk.Menu(master)
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="New", command=self.new_settings)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        master.config(menu=self.menu_bar)

        # Create GUI elements
        self.canvas = tk.Canvas(master, width=400, height=400)
        self.canvas.pack()

        self.slider = tk.Scale(master, from_=0, to=int(self.generator.get_total_images()) - 1, orient=tk.HORIZONTAL,
                               command=self.update_image, length=400)
        self.slider.pack(fill=tk.X, expand=True)

        # Navigation buttons
        navigation_frame = tk.Frame(master)
        navigation_frame.pack()

        self.button_step_prev = tk.Button(navigation_frame, text="Step Prev", command=self.step_prev)
        self.button_step_prev.pack(side=tk.LEFT)

        self.button_step_next = tk.Button(navigation_frame, text="Step Next", command=self.step_next)
        self.button_step_next.pack(side=tk.LEFT)

        self.button_fast_forward = tk.Button(navigation_frame, text="Fast Forward", command=self.fast_forward)
        self.button_fast_forward.pack(side=tk.LEFT)

        # Image generation buttons
        generation_frame = tk.Frame(master)
        generation_frame.pack()

        self.button_auto = tk.Button(generation_frame, text="Auto", command=self.toggle_auto)
        self.button_auto.pack(side=tk.LEFT)

        self.button_save_nonrandom = tk.Button(generation_frame, text="Skip to Non-Random", command=self.skip_to_nonrandom)
        self.button_save_nonrandom.pack(side=tk.LEFT)

        self.button_save = tk.Button(generation_frame, text="Save Image", command=self.save_image)
        self.button_save.pack(side=tk.LEFT)

        # Additional options
        options_frame = tk.Frame(master)
        options_frame.pack()

        self.label_step_size = tk.Label(options_frame, text="Step Size:")
        self.label_step_size.pack(side=tk.LEFT)
        self.entry_step_size = tk.Entry(options_frame)
        self.entry_step_size.insert(tk.END, "1")
        self.entry_step_size.pack(side=tk.LEFT)
        self.entry_step_size.bind("<Return>", self.update_step_size)

        self.label_threshold = tk.Label(options_frame, text="Randomness Threshold:")
        self.label_threshold.pack(side=tk.LEFT)
        self.entry_threshold = tk.Entry(options_frame)
        self.entry_threshold.insert(tk.END, "0.7")
        self.entry_threshold.pack(side=tk.LEFT)

        self.button_toggle_filter = tk.Button(options_frame, text="Toggle Filter", command=self.toggle_filter)
        self.button_toggle_filter.pack(side=tk.LEFT)

        self.auto_increment = False
        self.step_size = 1
        self.resampling_filter = Image.LANCZOS

        # Show the settings dialog on startup
        self.new_settings()

    def update_image(self, index):
        try:
            image = self.generator.generate_image(index)

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

            photo = ImageTk.PhotoImage(image)
            self.canvas.delete("all")
            self.canvas.create_image(canvas_width // 2, canvas_height // 2, anchor=tk.CENTER, image=photo)
            self.canvas.image = photo
        except ValueError as e:
            print(f"Error: {str(e)}")

    def step_prev(self):
        current_index = self.generator.current_index
        new_index = str(int(current_index) - self.step_size).zfill(len(current_index))
        if int(new_index) >= 0:
            self.generator.current_index = new_index
            self.update_image(new_index)

    def step_next(self):
        current_index = self.generator.current_index
        new_index = str(int(current_index) + self.step_size).zfill(len(current_index))
        if int(new_index) < int(self.generator.get_total_images()):
            self.generator.current_index = new_index
            self.update_image(new_index)

    def fast_forward(self):
        current_index = self.generator.current_index
        fast_forward_step = self.step_size * 100  # Adjust the factor as needed
        new_index = str(int(current_index) + fast_forward_step).zfill(len(current_index))
        if int(new_index) < int(self.generator.get_total_images()):
            self.generator.current_index = new_index
            self.update_image(new_index)

    def toggle_auto(self):
        self.auto_increment = not self.auto_increment
        if self.auto_increment:
            self.button_auto.config(text="Stop")
            self.auto_generate()
        else:
            self.button_auto.config(text="Auto")

    def auto_generate(self):
        if self.auto_increment:
            self.step_next()
            self.master.after(100, self.auto_generate)  # Adjust the delay as needed

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
            self.slider.config(to=int(self.generator.get_total_images()) - 1)
            update_image_after_dialog(0)
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
                self.generator.current_index = image_id
                update_image_after_dialog(image_id)
                dialog.destroy()

        def update_image_after_dialog(index):
            self.update_image(index)

        confirm_button = tk.Button(dialog, text="Confirm", command=confirm_settings)
        confirm_button.grid(row=3, column=0)

        import_button = tk.Button(dialog, text="Import Image", command=import_image)
        import_button.grid(row=3, column=1)

        dialog.transient(self.master)
        dialog.grab_set()

    def toggle_filter(self):
        if self.resampling_filter == Image.LANCZOS:
            self.resampling_filter = Image.NEAREST
            self.button_toggle_filter.config(text="Filter: Nearest")
        elif self.resampling_filter == Image.NEAREST:
            self.resampling_filter = Image.BILINEAR
            self.button_toggle_filter.config(text="Filter: Bilinear")
        else:
            self.resampling_filter = Image.LANCZOS
            self.button_toggle_filter.config(text="Filter: Lanczos")
        self.update_image(self.generator.current_index)

    def update_step_size(self, event):
        try:
            self.step_size = int(self.entry_step_size.get())
        except ValueError:
            pass

    def save_image(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".png")
        if file_path:
            image = self.generator.generate_image(self.generator.current_index)
            image.save(file_path)

    def skip_to_nonrandom(self):
        threshold = float(self.entry_threshold.get())
        image = self.generator.find_next_nonrandom_image(threshold)
        if image is not None:
            self.generator.current_index = self.generator.get_image_id(image)
            self.update_image(self.generator.current_index)
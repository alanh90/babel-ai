import tkinter as tk
from tkinter import filedialog, simpledialog
from PIL import Image, ImageTk
import numpy as np
from imagebabelgen import ImageBabelGenerator
import os
import threading

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

        # Slider initialization with dynamic maximum value
        self.slider = tk.Scale(self.master, from_=0, to=self.get_max_slider_value(), orient=tk.HORIZONTAL,
                               command=self.update_image_from_slider)
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

        self.label_threshold = tk.Label(options_frame, text="Randomness Threshold:")
        self.label_threshold.pack(side=tk.LEFT)
        self.entry_threshold = tk.Entry(options_frame)
        self.entry_threshold.insert(tk.END, "0.7")
        self.entry_threshold.pack(side=tk.LEFT)

        self.button_toggle_filter = tk.Button(options_frame, text="Toggle Filter", command=self.toggle_filter)
        self.button_toggle_filter.pack(side=tk.LEFT)

        self.auto_increment = False
        self.resampling_filter = Image.LANCZOS

        self.image_generation_thread = None
        self.stop_image_generation = False

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

        photo = ImageTk.PhotoImage(image)
        self.canvas.delete("all")
        self.canvas.create_image(canvas_width // 2, canvas_height // 2, anchor=tk.CENTER, image=photo)
        self.canvas.image = photo

    def update_image_from_slider(self, slider_value):
        if self.image_generation_thread is None or not self.image_generation_thread.is_alive():
            self.stop_image_generation = False
            self.image_generation_thread = threading.Thread(target=self.estimate_image_from_slider, args=(int(slider_value),))
            self.image_generation_thread.start()

    def estimate_image_from_slider(self, slider_position):
        total_images = self.get_max_slider_value() + 1
        image_index = int(slider_position / total_images * self.generator.image_iterator.total_combinations)
        pixel_combination = self.generator.image_iterator.get_pixel_combination(image_index)
        image = self.generator.image_iterator._pixel_combination_to_image(pixel_combination)
        self.generator.current_image = image
        if not self.stop_image_generation:
            self.master.after(0, self.update_image, image)

    # The purpose of the step_prev function is to go back to the previous image
    def step_prev(self):
        try:
            self.generator.current_image = self.generator.generate_image()
            self.update_image(self.generator.current_image)
            self.slider.set(self.generator.image_iterator.current_index)
        except StopIteration:
            pass

    # The purpose of the step_next function is to go to the next image
    def step_next(self):
        try:
            self.generator.current_image = self.generator.generate_image()
            self.update_image(self.generator.current_image)
            self.slider.set(self.generator.image_iterator.current_index)
        except StopIteration:
            pass

    # This is meant to skip images
    def fast_forward(self):
        for _ in range(100):  # Adjust the number as needed
            try:
                self.generator.current_image = self.generator.generate_image()
            except StopIteration:
                break
        self.update_image(self.generator.current_image)
        self.slider.set(self.generator.image_iterator.current_index)

    def toggle_auto(self):
        self.auto_increment = not self.auto_increment
        if self.auto_increment:
            self.button_auto.config(text="Stop")
            self.auto_generate()
        else:
            self.button_auto.config(text="Auto")

    # This is supposed to automatically increment to the next image so you can actively see the image changing
    def auto_generate(self):
        if self.auto_increment:
            try:
                self.generator.current_image = self.generator.generate_image()
                self.update_image(self.generator.current_image)
                self.slider.set(self.generator.image_iterator.current_index)
                self.master.after(100, self.auto_generate)  # Adjust the delay as needed
            except StopIteration:
                self.auto_increment = False
                self.button_auto.config(text="Auto")

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
            self.stop_image_generation = True
            if self.image_generation_thread is not None:
                self.image_generation_thread.join()
            width = int(width_entry.get())
            height = int(height_entry.get())
            color_depth = int(color_depth_entry.get())
            self.generator.set_parameters(width, height, color_depth)
            self.generator.image_iterator = self.generator._generate_image_iterator()
            self.generator.current_image = self.generator.generate_image()
            self.update_image(self.generator.current_image)
            self.slider.config(to=self.get_max_slider_value())
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
                self.generator.image_iterator = iter([self.generator.image_iterator._pixel_combination_to_image(image_id)])
                self.generator.current_image = self.generator.generate_image()
                self.update_image(self.generator.current_image)
                self.slider.config(to=self.get_max_slider_value())
                dialog.destroy()

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
        self.update_image(self.generator.current_image)

    def save_image(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".png")
        if file_path:
            self.generator.current_image.save(file_path)

    def skip_to_nonrandom(self):
        threshold = float(self.entry_threshold.get())
        image_index = self.generator.image_iterator.find_next_nonrandom_index(threshold)
        if image_index is not None:
            pixel_combination = self.generator.image_iterator.get_pixel_combination(image_index)
            image = self.generator.image_iterator._pixel_combination_to_image(pixel_combination)
            self.generator.current_image = image
            self.update_image(image)
            self.slider.set(image_index)

    def get_max_slider_value(self):
        # Ensure we have a valid integer value for the slider's maximum
        return max(0, self.generator.image_iterator.total_combinations - 1)
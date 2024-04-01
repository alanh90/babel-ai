import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import numpy as np
from imagebabelgen import ImageBabelGenerator
import os


class ImageBabelGUI:
    def __init__(self, master):
        self.master = master
        master.title("Image Babel Generator")

        # Create an instance of the ImageBabelGenerator
        self.generator = ImageBabelGenerator(width=4, height=4, color_depth=2)

        # Create GUI elements
        self.canvas = tk.Canvas(master, width=400, height=400)
        self.canvas.pack()

        self.slider = tk.Scale(master, from_=0, to=self.generator.get_total_images() - 1, orient=tk.HORIZONTAL,
                               command=self.update_image)
        self.slider.pack()

        self.button_frame = tk.Frame(master)
        self.button_frame.pack()

        self.button_prev = tk.Button(self.button_frame, text="Previous", command=self.prev_image)
        self.button_prev.pack(side=tk.LEFT)

        self.button_next = tk.Button(self.button_frame, text="Next", command=self.next_image)
        self.button_next.pack(side=tk.LEFT)

        self.button_step_prev = tk.Button(self.button_frame, text="Step Prev", command=self.step_prev)
        self.button_step_prev.pack(side=tk.LEFT)

        self.button_step_next = tk.Button(self.button_frame, text="Step Next", command=self.step_next)
        self.button_step_next.pack(side=tk.LEFT)

        self.button_auto = tk.Button(self.button_frame, text="Auto", command=self.toggle_auto)
        self.button_auto.pack(side=tk.LEFT)

        self.button_import = tk.Button(self.button_frame, text="Import Image", command=self.import_image)
        self.button_import.pack(side=tk.LEFT)

        self.button_save = tk.Button(self.button_frame, text="Save Image", command=self.save_image)
        self.button_save.pack(side=tk.LEFT)

        self.label_width = tk.Label(master, text="Width:")
        self.label_width.pack()
        self.entry_width = tk.Entry(master)
        self.entry_width.pack()

        self.label_height = tk.Label(master, text="Height:")
        self.label_height.pack()
        self.entry_height = tk.Entry(master)
        self.entry_height.pack()

        self.label_color_depth = tk.Label(master, text="Color Depth:")
        self.label_color_depth.pack()
        self.entry_color_depth = tk.Entry(master)
        self.entry_color_depth.pack()

        self.button_generate = tk.Button(master, text="Generate Images", command=self.generate_images)
        self.button_generate.pack()

        self.label_step_size = tk.Label(master, text="Step Size:")
        self.label_step_size.pack()
        self.entry_step_size = tk.Entry(master)
        self.entry_step_size.insert(tk.END, "1")
        self.entry_step_size.pack()
        self.entry_step_size.bind("<Return>", self.update_step_size)

        self.button_fast_forward = tk.Button(self.button_frame, text="Fast Forward", command=self.fast_forward)
        self.button_fast_forward.pack(side=tk.LEFT)

        self.button_save_nonrandom = tk.Button(self.button_frame, text="Save Non-Random", command=self.save_nonrandom)
        self.button_save_nonrandom.pack(side=tk.LEFT)

        self.label_threshold = tk.Label(master, text="Randomness Threshold:")
        self.label_threshold.pack()
        self.entry_threshold = tk.Entry(master)
        self.entry_threshold.insert(tk.END, "0.7")
        self.entry_threshold.pack()

        self.auto_increment = False
        self.step_size = 1

        # Display the first image
        self.update_image(0)

    def fast_forward(self):
        current_index = self.slider.get()
        fast_forward_step = self.step_size * 100  # Adjust the factor as needed
        if current_index + fast_forward_step < self.generator.get_total_images():
            self.slider.set(current_index + fast_forward_step)

    def save_nonrandom(self):
        threshold = float(self.entry_threshold.get())
        image = self.generator.find_next_nonrandom_image(threshold)
        if image is not None:
            self.update_image(self.generator.current_index)
            self.save_image()

    def update_image(self, index):
        image = self.generator.generate_image(int(index))
        photo = ImageTk.PhotoImage(image)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=photo)
        self.canvas.image = photo

    def prev_image(self):
        current_index = self.slider.get()
        if current_index > 0:
            self.slider.set(current_index - 1)

    def next_image(self):
        current_index = self.slider.get()
        if current_index < self.generator.get_total_images() - 1:
            self.slider.set(current_index + 1)

    def step_prev(self):
        current_index = self.slider.get()
        if current_index - self.step_size >= 0:
            self.slider.set(current_index - self.step_size)

    def step_next(self):
        current_index = self.slider.get()
        if current_index + self.step_size < self.generator.get_total_images():
            self.slider.set(current_index + self.step_size)

    def toggle_auto(self):
        self.auto_increment = not self.auto_increment
        if self.auto_increment:
            self.button_auto.config(text="Stop")
            self.auto_generate()
        else:
            self.button_auto.config(text="Auto")

    def auto_generate(self):
        if self.auto_increment:
            current_index = self.slider.get()
            if current_index + self.step_size < self.generator.get_total_images():
                self.slider.set(current_index + self.step_size)
                self.master.after(100, self.auto_generate)  # Adjust the delay as needed
            else:
                self.auto_increment = False
                self.button_auto.config(text="Auto")

    def update_step_size(self, *args):
        try:
            self.step_size = int(self.entry_step_size.get())
        except ValueError:
            pass

    def import_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            image = Image.open(file_path)
            image = image.convert("L")  # Convert to grayscale
            image = image.resize((self.generator.width, self.generator.height))
            image_id = self.generator.get_image_id(image)
            self.slider.set(image_id)

    def save_image(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".png")
        if file_path:
            image = self.generator.generate_image(self.slider.get())
            image.save(file_path)

    def generate_images(self):
        width = int(self.entry_width.get())
        height = int(self.entry_height.get())
        color_depth = int(self.entry_color_depth.get())
        self.generator.set_parameters(width, height, color_depth)
        self.slider.config(to=self.generator.get_total_images() - 1)
        self.update_image(0)
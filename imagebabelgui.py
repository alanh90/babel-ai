import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import numpy as np
from imagebabelgen import ImageBabelGenerator


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

        self.button_import = tk.Button(self.button_frame, text="Import Image", command=self.import_image)
        self.button_import.pack(side=tk.LEFT)

        # Display the first image
        self.update_image(0)

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

    def import_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            image = Image.open(file_path)
            image = image.convert("L")  # Convert to grayscale
            image = image.resize((self.generator.width, self.generator.height))
            image_id = self.generator.get_image_id(image)
            self.slider.set(image_id)


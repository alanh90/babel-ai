from PIL import Image
import numpy as np
import itertools

class ImageBabelGenerator:
    def __init__(self, width, height, color_depth):
        self.width = width
        self.height = height
        self.color_depth = color_depth
        self.total_images = color_depth ** (width * height)
        self.image_iterator = self._generate_image_iterator()
        self.current_image = None
        self.current_array = None

    def _generate_image_iterator(self):
        pixel_values = range(self.color_depth)
        pixel_combinations = itertools.product(pixel_values, repeat=self.width * self.height)
        return (self._pixel_combination_to_array(combination) for combination in pixel_combinations)

    def _pixel_combination_to_array(self, pixel_combination):
        image_array = np.array(pixel_combination, dtype=np.uint8).reshape(self.height, self.width)
        return image_array

    def _array_to_image(self, image_array):
        image_data = image_array.flatten()
        image_data = [int(value / (self.color_depth - 1) * 255) for value in image_data]
        image_data = bytearray(image_data)
        return Image.frombytes('L', (self.width, self.height), bytes(image_data))

    def generate_image(self):
        try:
            self.current_array = next(self.image_iterator)
            self.current_image = self._array_to_image(self.current_array)
        except StopIteration:
            self.current_image = None
            self.current_array = None
        return self.current_image

    def get_total_images(self):
        return self.total_images

    def get_image_id(self, image):
        pixels = np.array(image.getdata(), dtype=np.uint8)
        pixel_values = (pixels / 255 * (self.color_depth - 1)).astype(np.uint8)
        return tuple(pixel_values)

    def set_parameters(self, width=None, height=None, color_depth=None):
        if width is not None:
            self.width = width
        if height is not None:
            self.height = height
        if color_depth is not None:
            self.color_depth = color_depth
        self.total_images = self.color_depth ** (self.width * self.height)
        self.image_iterator = self._generate_image_iterator()
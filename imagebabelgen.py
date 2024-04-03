from PIL import Image
import numpy as np
import itertools

class ImageIterator:
    def __init__(self, width, height, color_depth):
        self.width = width
        self.height = height
        self.color_depth = color_depth
        self.total_combinations = color_depth ** (width * height)
        self.current_index = 0
        self.pixel_combination_generator = self._generate_pixel_combinations()

    def _generate_pixel_combinations(self):
        pixel_values = range(self.color_depth)
        return itertools.product(pixel_values, repeat=self.width * self.height)

    def __iter__(self):
        return self

    def __next__(self):
        if self.current_index >= self.total_combinations:
            raise StopIteration
        try:
            pixel_combination = next(self.pixel_combination_generator)
        except StopIteration:
            self.pixel_combination_generator = self._generate_pixel_combinations()
            pixel_combination = next(self.pixel_combination_generator)
        self.current_index += 1
        return pixel_combination

    def __len__(self):
        return self.total_combinations

    def get_pixel_combination(self, index):
        if index >= self.total_combinations:
            raise IndexError("Index out of range")
        pixel_combination_generator = self._generate_pixel_combinations()
        for _ in range(index):
            next(pixel_combination_generator)
        return next(pixel_combination_generator)

    def is_random_image(self, index, entropy_threshold=5.0):
        image = self._pixel_combination_to_image(self.get_pixel_combination(index))
        entropy = self._calculate_entropy(image)
        return entropy >= entropy_threshold

    def _pixel_combination_to_image(self, pixel_combination):
        image_data = [pixel_value for pixel_value in pixel_combination]
        image_data = [int(value / (self.color_depth - 1) * 255) for value in image_data]
        image_data = bytearray(image_data)
        return Image.frombytes('L', (self.width, self.height), bytes(image_data))

    def _calculate_entropy(self, image):
        pixels = np.array(image)
        _, counts = np.unique(pixels, return_counts=True)
        probabilities = counts / counts.sum()
        entropy = -np.sum(probabilities * np.log2(probabilities))
        return entropy

    def find_next_nonrandom_index(self, entropy_threshold=5.0):
        for i in range(self.current_index, len(self.pixel_combinations)):
            if not self.is_random_image(i, entropy_threshold):
                return i
        return None

class ImageBabelGenerator:
    def __init__(self, width, height, color_depth):
        self.width = width
        self.height = height
        self.color_depth = color_depth
        self.image_iterator = self._generate_image_iterator()
        self.current_image = None

    def _generate_image_iterator(self):
        return ImageIterator(self.width, self.height, self.color_depth)

    def generate_image(self):
        try:
            pixel_combination = next(self.image_iterator)
            self.current_image = self.image_iterator._pixel_combination_to_image(pixel_combination)
        except StopIteration:
            self.current_image = None
        return self.current_image

    def get_total_images(self):
        return self.color_depth ** (self.width * self.height)

    def get_image_id(self, image):
        pixels = list(image.getdata())
        pixel_values = [int(value / 255 * (self.color_depth - 1)) for value in pixels]
        return tuple(pixel_values)

    def set_parameters(self, width=None, height=None, color_depth=None):
        if width is not None:
            self.width = width
        if height is not None:
            self.height = height
        if color_depth is not None:
            self.color_depth = color_depth
        self.image_iterator = self._generate_image_iterator()
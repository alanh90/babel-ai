import numpy as np
from PIL import Image
import base64


class ImageBabelGenerator:
    def __init__(self, width, height, color_depth):
        self.width = width
        self.height = height
        self.color_depth = color_depth
        self.total_images = self.color_depth ** (self.width * self.height)
        self.current_index = "0" * (self.width * self.height)

    def generate_image(self, index=None):
        if index is not None:
            self.current_index = str(index)
        image = self._index_to_image(self.current_index)
        self.current_index = self._increment_index(self.current_index)
        return image

    def _index_to_image(self, index):
        expected_length = self.width * self.height
        if len(index) != expected_length:
            # Return a default or error image
            return Image.new('L', (self.width, self.height), 0)

        max_val = self.color_depth - 1
        image_data = np.zeros((self.height, self.width), dtype=np.uint8)

        for y in range(self.height):
            for x in range(self.width):
                pixel_value = int(index[x + y * self.width]) % self.color_depth
                image_data[y, x] = int(pixel_value / max_val * 255)

        return Image.fromarray(image_data)

    def _image_to_index(self, image):
        pixels = np.array(image) // (255 // (self.color_depth - 1))
        index = "".join(str(d) for d in pixels.flatten())
        return index

    def _increment_index(self, index):
        incremented = int(index) + 1
        if incremented >= self.total_images:
            incremented = 0
        return str(incremented).zfill(len(index))

    def _calculate_entropy(self, image):
        pixels = np.array(image)
        _, counts = np.unique(pixels, return_counts=True)
        probabilities = counts / counts.sum()
        entropy = -np.sum(probabilities * np.log2(probabilities))
        return entropy

    def is_random_image(self, index, entropy_threshold=5.0):
        image = self._index_to_image(index)
        entropy = self._calculate_entropy(image)
        return entropy >= entropy_threshold

    def find_next_nonrandom_image(self, entropy_threshold=5.0):
        current_index = self._increment_index(self.current_index)
        while current_index != self.current_index:
            if not self.is_random_image(current_index, entropy_threshold):
                self.current_index = current_index
                return self._index_to_image(current_index)
            current_index = self._increment_index(current_index)
        return None

    def get_image_id(self, image):
        index = self._image_to_index(image)
        return index

    def set_parameters(self, width=None, height=None, color_depth=None):
        if width is not None:
            self.width = width
        if height is not None:
            self.height = height
        if color_depth is not None:
            self.color_depth = color_depth
        self.total_images = self.color_depth ** (self.width * self.height)

    def get_total_images(self):
        return str(self.total_images)

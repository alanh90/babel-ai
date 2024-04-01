import sys

import numpy as np
import scipy
from PIL import Image
import base64

class ImageBabelGenerator:
    def __init__(self, width, height, color_depth):
        self.width = width
        self.height = height
        self.color_depth = color_depth
        # Adjust total_images calculation for very high color depths
        self.total_images = self.calculate_total_images()
        self.current_index = 0

    def calculate_total_images(self):
        try:
            total_images = pow(self.color_depth, self.width * self.height)
            if total_images > sys.maxsize:
                print("Warning: Total image count exceeds the maximum size.")
                return sys.maxsize  # or another appropriate large but manageable number
            return total_images
        except OverflowError:
            print("Error: Total image count calculation overflowed.")
            return sys.maxsize  # or handle it appropriately

    def generate_image(self, index=None):
        if index is not None:
            try:
                index = int(index)
            except ValueError:
                raise ValueError("Index value is invalid.")
            if index >= self.total_images:
                raise ValueError("Index exceeds the total number of images.")
            self.current_index = index
        else:
            self.current_index = np.random.randint(0, self.total_images)

        return self._index_to_image(self.current_index)

    def calculate_total_images(self):
        # Handle potential overflow for large numbers
        return pow(self.color_depth, self.width * self.height)

    def generate_image(self, index=None):
        if index is not None:
            self.current_index = index
        else:
            self.current_index = np.random.randint(0, self.total_images)
        return self._index_to_image(self.current_index)

    def _index_to_image(self, index):
        # Efficient conversion of index to image representation for variable color depths
        max_val = self.color_depth - 1
        # Create an empty array for the image
        image_data = np.zeros((self.height, self.width), dtype=np.uint8)

        for y in range(self.height):
            for x in range(self.width):
                # Calculate pixel value based on the index and color depth
                pixel_value = (index // (self.color_depth ** (x + y * self.width))) % self.color_depth
                image_data[y, x] = int(pixel_value / max_val * 255)

        return Image.fromarray(image_data)

    def _image_to_index(self, image):
        pixels = np.array(image) // (255 // (self.color_depth - 1))
        digits = ''.join(str(d) for d in pixels.flatten())
        index = self._digits_to_index(digits)
        return index

    def _index_to_string_id(self, index):
        """
        Convert a numerical index to a base-64 encoded string ID.
        """
        digits = np.base_repr(index, base=self.color_depth)
        digits = digits.zfill(self.width * self.height)
        binary_data = ''.join(format(int(d), '08b') for d in digits)
        string_id = base64.b64encode(binary_data.encode()).decode()
        return string_id

    def _string_id_to_index(self, string_id):
        """
        Convert a base-64 encoded string ID to a numerical index.
        """
        binary_data = base64.b64decode(string_id).decode()
        digits = [int(binary_data[i:i+8], 2) for i in range(0, len(binary_data), 8)]
        index = int(''.join(str(d) for d in digits), base=self.color_depth)
        return index

    def _increment_index(self, index):
        digits = self._index_to_digits(index)
        digits = str(int(digits) + 1)
        return self._digits_to_index(digits)

    def _index_to_digits(self, index):
        return ''.join(str(int(d) % self.color_depth) for d in index)

    def _digits_to_index(self, digits):
        return ''.join(str(d) for d in digits)

    def _calculate_entropy(self, image):
        """
        Calculate the Shannon entropy of an image, which is a measure of randomness.
        """
        pixels = np.array(image)
        _, counts = np.unique(pixels, return_counts=True)
        probabilities = counts / counts.sum()
        entropy = scipy.stats.entropy(probabilities)
        return entropy

    def find_next_nonrandom_image(self, entropy_threshold=5.0):
        """
        Find the next image that has an entropy below the given threshold.
        """
        current_index = self.current_index
        while True:
            image = self._index_to_image(current_index)
            entropy = self._calculate_entropy(image)
            if entropy < entropy_threshold:
                self.current_index = current_index
                return image
            current_index = self._increment_index(current_index)
            if current_index >= self.total_images:  # Stop if we reach the total number of images.
                break
        return None

    def _compare_indices(self, index1, index2):
        if len(index1) < len(index2):
            return -1
        elif len(index1) > len(index2):
            return 1
        else:
            if index1 < index2:
                return -1
            elif index1 > index2:
                return 1
            else:
                return 0

    def get_image_id(self, image):
        """
        Get the index (ID) of a given image in the sequence of all possible images.
        """
        index = self._image_to_index(image)
        return index

    def get_image_string_id(self, image):
        """
        Get the base-64 encoded string ID of a given image.
        """
        index = self._image_to_index(image)
        string_id = self._index_to_string_id(index)
        return string_id

    def generate_image_from_string_id(self, string_id):
        """
        Generate an image from a base-64 encoded string ID.
        """
        index = self._string_id_to_index(string_id)
        image = self._index_to_image(index)
        return image

    def set_parameters(self, width=None, height=None, color_depth=None):
        if width is not None:
            self.width = width
        if height is not None:
            self.height = height
        if color_depth is not None:
            self.color_depth = color_depth
        self.total_images = self.calculate_total_images()

    def get_total_images(self):
        """
        Return the total number of images that can be generated with the current settings.
        """
        return self.total_images

    def is_random_noise(self, image, threshold=0.7):
        """
        Check if an image is considered random noise based on a threshold.
        """
        pixels = np.array(image) // (255 // (self.color_depth - 1))
        unique_pixels = np.unique(pixels)
        randomness = len(unique_pixels) / (self.width * self.height)
        return randomness > threshold

    def is_mirrored(self, image):
        """
        Check if an image is mirrored horizontally or vertically.
        """
        pixels = np.array(image)
        h_flipped = np.fliplr(pixels)
        v_flipped = np.flipud(pixels)
        return np.array_equal(pixels, h_flipped) or np.array_equal(pixels, v_flipped)
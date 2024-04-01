import numpy as np
from PIL import Image
import base64

class ImageBabelGenerator:
    def __init__(self, width, height, color_depth):
        self.width = width
        self.height = height
        self.color_depth = color_depth
        self.total_images = self.color_depth ** (self.width * self.height)
        self.current_index = 0

    def generate_image(self, index=None):
        """
        Generate the image corresponding to the given index.
        If no index is provided, use the current index.
        """
        if index is not None:
            self.current_index = np.int64(index)
        image = self._index_to_image(self.current_index)
        self.current_index += 1  # Move to the next image for subsequent call
        return image

    def _index_to_image(self, index):
        """
        Convert a numerical index into an image based on the generator's settings.
        This function maps the index to a unique image configuration.
        """
        # Convert the index to a base-color_depth number
        digits = np.base_repr(index, base=self.color_depth)
        # Pad the digits with zeros to match the total number of pixels
        digits = digits.zfill(self.width * self.height)
        # Reshape the digits into a 2D array
        pixels = np.array([int(d) for d in digits]).reshape((self.height, self.width))
        # Create an image from the pixel values
        image = Image.fromarray(np.uint8(pixels * (255 // (self.color_depth - 1))))
        return image

    def _image_to_index(self, image):
        """
        Convert an image to its corresponding index in the sequence of all possible images.
        """
        pixels = np.array(image) // (255 // (self.color_depth - 1))
        digits = ''.join(str(d) for d in pixels.flatten())
        index = np.int64(digits, base=self.color_depth)
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
        """
        Update the image generator parameters.
        """
        if width is not None:
            self.width = width
        if height is not None:
            self.height = height
        if color_depth is not None:
            self.color_depth = color_depth
        self.total_images = self.color_depth ** (self.width * self.height)

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

    def find_next_nonrandom_image(self, threshold=0.7):
        current_index = self.current_index
        while current_index < self.total_images:
            image = self._index_to_image(current_index)
            if not self.is_random_noise(image, threshold):
                self.current_index = current_index
                return image
            current_index += 1
        return None
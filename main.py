from PIL import Image
from ImageBabelGenerator import ImageBabelGenerator

# Create an instance of the ImageBabelGenerator
generator = ImageBabelGenerator(width=4, height=4, color_depth=2)

# Generate and display the first 10 images
for i in range(10):
    image = generator.generate_image()
    print(f"Image {i + 1}:")
    image.show()

# Get the total number of possible images
total_images = generator.get_total_images()
print(f"\nTotal possible images: {total_images}")

# Import an existing image
existing_image = Image.open("example_image.png")
existing_image = existing_image.convert("L")  # Convert to grayscale
existing_image = existing_image.resize((4, 4))  # Resize to match the generator's dimensions

# Get the ID of the existing image
image_id = generator.get_image_id(existing_image)
print(f"\nID of the existing image: {image_id}")

# Check if the existing image is random noise
is_noise = generator.is_random_noise(existing_image)
print(f"Is the existing image random noise? {is_noise}")

# Check if the existing image is mirrored
is_mirrored = generator.is_mirrored(existing_image)
print(f"Is the existing image mirrored? {is_mirrored}")

# Update the generator's parameters
generator.set_parameters(width=5, height=5, color_depth=3)
print(f"\nUpdated total possible images: {generator.get_total_images()}")
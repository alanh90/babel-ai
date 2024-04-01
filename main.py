import tkinter as tk
from imagebabelgui import ImageBabelGUI

# Create the main window
root = tk.Tk()
root.title("Image Babel Generator")

# Create an instance of the ImageBabelGUI
gui = ImageBabelGUI(root)

# Start the main event loop
root.mainloop()
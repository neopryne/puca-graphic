from PIL import Image
from math import sqrt
from math import ceil
import tkinter as tk
from tkinter import filedialog
import cProfile

#the unlicense for now.

def bitstring_to_bytes(s):
    return int(s, 2).to_bytes((len(s) + 7) // 8, byteorder='big')

#Ok I either need terminators or length declarations.
#For getting around compression, I'll need to be less granular.  Maybe rgb = on or off for each pixel, three bits.
def encode(zip_file_path, image_path):
    # Read the zip file as binary data
    with open(zip_file_path, 'rb') as file:
        zip_data = file.read()

        # Convert zip data to binary format
        binary_data = ''.join(format(byte, '08b') for byte in zip_data)
        #I should be doing both of these streamed.

        # Calculate the number of pixels needed
        num_pixels = ceil(len(binary_data) / (3 * 8))  # 3 bytes per pixel
        width = ceil(sqrt(num_pixels))  # Square root rounded up
        height = ceil((num_pixels) / width)
        image_size = (width, height)

        print(num_pixels)
        print(width)
        print(height)

        #3Meg -> 1Mil pixels

        # Create a new image with the determined size
        encoded_image = Image.new('RGB', image_size)

        # Embed the binary data into the image
        pixels = []
        index = 0
        for i in range(width):
            for j in range(height):
                # Get the next 3 bits of binary data
                if index < len(binary_data):
                    r = int(binary_data[index:index + 8], 2)
                    index += 8
                else:
                    r = 0  # Padding with zeros if binary data ends prematurely
                if index < len(binary_data):
                    g = int(binary_data[index:index + 8], 2)
                    index += 8
                else:
                    g = 0
                if index < len(binary_data):
                    b = int(binary_data[index:index + 8], 2)
                    index += 8
                else:
                    b = 0
                pixels.append((r, g, b))

        encoded_image.putdata(pixels)

        # Save the encoded image
        encoded_image.save(image_path, 'PNG')


def decode(image_path, zip_file_path):
    # Load the encoded image
    encoded_image = Image.open(image_path)
    i = 0
    #todo add a pixel counter to the decode because it takes a long time for files over like a meg.
    #todo also make this faster because wow.  It's going to take like an hour for a 12 meg file.

    binary_data = ''.join(format(pixel[0], '08b') + format(pixel[1], '08b') + format(pixel[2], '08b') for pixel in encoded_image.getdata())

    # Convert binary data back to bytes
    bytes_data = bytes(int(binary_data[i:i+8], 2) for i in range(0, len(binary_data), 8))

    # Write the decompressed data to a zip file
    with open(zip_file_path, 'wb') as file:
        file.write(bytes_data)

#encoding original filename would be nice, required for public release.

#encode("Jabberwocky.txt", "test.png")
#decode("test.png", "output.txt")

#togpt Image compression algorithms often remove subtle data from files.


def get_text_after_last_dot(text):
    last_slash_index = text.rfind('.')
    # If no forward slash is found, return empty string
    if last_slash_index == -1:
        return ""
    return text[last_slash_index + 1:]

KEY_SOURCE_FULL_PATH = "source_full_path"
KEY_SOURCE_FILENAME = "source_filename" #this includes the leading slash, so /filename.
KEY_SOURCE_FOLDER = "source_folder"
KEY_SOURCE_EXTENSION = "source_extension"
KEY_EMBEDDED_EXTENSION = "embedded_extension"

begin_embed_extension = "(."
end_embed_extension = ")"

global_strings = {KEY_SOURCE_FILENAME: "", KEY_SOURCE_FOLDER: "", KEY_SOURCE_EXTENSION: "", KEY_SOURCE_FULL_PATH: "",
                  KEY_EMBEDDED_EXTENSION: ""}

def embedded_extension():
    stored = global_strings[KEY_EMBEDDED_EXTENSION]
    if stored == "":
        return "txt" #default to txt
    return stored


def encode_pressed():
    #for this to work, embedded extension must be non-null
    # Placeholder for encode button press action
    print("Encode button pressed " + global_strings[KEY_SOURCE_FILENAME])
    print("E " + global_strings[KEY_SOURCE_EXTENSION])
    outfilepath = global_strings[KEY_SOURCE_FOLDER] + global_strings[KEY_SOURCE_FILENAME] + begin_embed_extension +\
                  global_strings[KEY_SOURCE_EXTENSION] + end_embed_extension + ".png"
    print(outfilepath)
    encode(global_strings[KEY_SOURCE_FULL_PATH], outfilepath)


def decode_pressed():
    # Placeholder for decode button press action
    decode_file_name = global_strings[KEY_SOURCE_FOLDER] + global_strings[KEY_SOURCE_FILENAME] +\
                       embedded_extension()
    print("Decode button pressed " + decode_file_name)
    decode(global_strings[KEY_SOURCE_FULL_PATH], decode_file_name)

def browse_file():
    # Open a file dialog to select a file
    file_path = filedialog.askopenfilename()
    entry.delete(0, tk.END)  # Clear the text box
    entry.insert(tk.END, file_path)  # Insert the selected file path into the text box
    last_slash_index = file_path.rfind('/')
    last_dot_index = file_path.rfind('.')
    last_lparen_index = file_path.rfind(begin_embed_extension)
    last_rparen_index = file_path.rfind(end_embed_extension)
    if last_rparen_index == -1 or last_lparen_index == -1:
        global_strings[KEY_EMBEDDED_EXTENSION] = ""
        global_strings[KEY_SOURCE_FILENAME] = file_path[last_slash_index:last_dot_index]
    else:
        global_strings[KEY_EMBEDDED_EXTENSION] = file_path[last_lparen_index + 1:last_rparen_index]
        global_strings[KEY_SOURCE_FILENAME] = file_path[last_slash_index:last_lparen_index]
        print("EE: " + global_strings[KEY_EMBEDDED_EXTENSION])
    last_dot_index = file_path.rfind('.')
    if last_slash_index == -1 or last_dot_index == -1:
        #error message
        print("invalid path")
        return
    global_strings[KEY_SOURCE_FULL_PATH] = file_path
    global_strings[KEY_SOURCE_FOLDER] = file_path[:last_slash_index]
    global_strings[KEY_SOURCE_EXTENSION] = file_path[last_dot_index + 1:]
    print("Source folder: " + global_strings[KEY_SOURCE_FOLDER])
    print("Source filename: " + global_strings[KEY_SOURCE_FILENAME])
    print("Source extension: " + global_strings[KEY_SOURCE_EXTENSION])
    print("Embedded extension: " + global_strings[KEY_EMBEDDED_EXTENSION])


# Create the main window
root = tk.Tk()
root.title("Puca in Graphic")

# Create buttons
encode_button = tk.Button(root, text="Encode Here", command=encode_pressed)
decode_button = tk.Button(root, text="Decode Here", command=decode_pressed)
browse_button = tk.Button(root, text="Browse", command=browse_file)

# Create text box
entry = tk.Entry(root, width=50)

# Place buttons and text box in the window
encode_button.grid(row=0, column=0, padx=5, pady=5)
decode_button.grid(row=0, column=1, padx=5, pady=5)
entry.grid(row=1, column=0, columnspan=2, padx=5, pady=5)
browse_button.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

# Start the Tkinter event loop
root.mainloop()


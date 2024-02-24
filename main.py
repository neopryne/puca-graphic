from PIL import Image
from math import sqrt
from math import ceil
import zlib


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

        # Calculate the number of pixels needed
        num_pixels = ceil(len(binary_data) / (3 * 8))  # 3 bytes per pixel
        width = ceil(sqrt(num_pixels))  # Square root rounded up
        height = ceil((num_pixels) / width)
        image_size = (width, height)

        print(num_pixels)
        print(width)
        print(height)

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


    # Extract data from the red channel of each pixel
    # wait why are we casting this to a char?  This should create bytes to start with.
    # Extract data from the image pixels
    binary_data = ''
    for pixel in encoded_image.getdata():
        binary_data += format(pixel[0], '08b')  # Red channel
        binary_data += format(pixel[1], '08b')  # Green channel
        binary_data += format(pixel[2], '08b')  # Blue channel

    # Convert binary data back to bytes
    bytes_data = bytes(int(binary_data[i:i+8], 2) for i in range(0, len(binary_data), 8))

    #binary_data = ''.join([chr(pixel[0]) for pixel in encoded_image.getdata()])


    # doesn't this need to convert the binary date to something else?  maybe encode does that..

    # Decompress the binary data
    #decompressed_data = zlib.decompress(binary_data.encode())

    # Write the decompressed data to a zip file
    with open(zip_file_path, 'wb') as file:
        file.write(bytes_data)


encode("Tom Knight and the Lisp Machine.txt", "test.png")
decode("test.png", "output.txt")

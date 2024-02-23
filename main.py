from PIL import Image
import zlib


def encode(zip_file_path, image_path):
    # Read the zip file as binary data
    with open(zip_file_path, 'rb') as file:
        zip_data = file.read()

    # Compress the zip data
    compressed_data = zlib.compress(zip_data)

    # Convert compressed data to binary format
    binary_data = ''.join(format(byte, '08b') for byte in compressed_data)

    # Determine the size of the image needed to accommodate the binary data
    width = 1
    height = ((len(binary_data) + 2)) + 1  # 3 bytes per pixel  no idiot you only use one
    print(height)
    image_size = (width, height)

    # Create a new image with the determined size
    encoded_image = Image.new('RGB', image_size)

    # Embed the binary data into the image
    pixels = []
    for i in range(len(binary_data)):
        pixels.append((ord(binary_data[i]), 0, 0))  # Only use the red channel to embed data
        #print(i)
    encoded_image.putdata(pixels)

    # Save the encoded image
    encoded_image.save(image_path, 'PNG')


def decode(image_path, zip_file_path):
    # Load the encoded image
    encoded_image = Image.open(image_path)

    # Extract data from the red channel of each pixel
    binary_data = ''.join([chr(pixel[0]) for pixel in encoded_image.getdata()])

    # Decompress the binary data
    decompressed_data = zlib.decompress(binary_data.encode())

    # Write the decompressed data to a zip file
    with open(zip_file_path, 'wb') as file:
        file.write(decompressed_data)


encode("test.zip", "test.png")
encode("test.png", "results.zip")

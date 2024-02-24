from PIL import Image
import zlib


def bitstring_to_bytes(s):
    return int(s, 2).to_bytes((len(s) + 7) // 8, byteorder='big')

def encode(zip_file_path, image_path):
    # Read the zip file as binary data
    with open(zip_file_path, 'rb') as file:
        zip_data = file.read()

    # Convert zip data to binary format
    binary_data = ''.join(format(byte, '08b') for byte in zip_data)

    # Determine the size of the image needed to accommodate the binary data
    width = 1
    height = len(binary_data) #+ 2 // 3)) + 1  # 3 bytes per pixel  no idiot you only use one
    print(height)
    image_size = (width, height)

    # Create a new image with the determined size
    encoded_image = Image.new('RGB', image_size)

    # Embed the binary data into the image
    pixels = []
    for i in range(len(binary_data)):
        #this only chooses between 49 and 48. I could get way better results by using the entire red channel.
        #print(ord(binary_data[i]))
        pixels.append((ord(binary_data[i]), 0, 0))  # Only use the red channel to embed data
        #print(i)
    encoded_image.putdata(pixels)

    # Save the encoded image
    encoded_image.save(image_path, 'PNG')


def decode(image_path, zip_file_path):
    # Load the encoded image
    encoded_image = Image.open(image_path)


    # Extract data from the red channel of each pixel
    # wait why are we casting this to a char?  This should create bytes to start with.
    binary_data = ''.join([chr(pixel[0]) for pixel in encoded_image.getdata()])


    # doesn't this need to convert the binary date to something else?  maybe encode does that..

    # Decompress the binary data
    #decompressed_data = zlib.decompress(binary_data.encode())

    # Write the decompressed data to a zip file
    with open(zip_file_path, 'wb') as file:
        file.write(bitstring_to_bytes(binary_data.encode()))


encode("test.txt", "test.png")
decode("test.png", "results.txt")

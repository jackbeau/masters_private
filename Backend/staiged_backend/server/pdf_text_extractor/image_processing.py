from PIL import Image, ImageDraw
import numpy as np


def crop_and_fill_image(image, top_left, bottom_right):
    # Get the width and height of the image
    width, height = image.shape[1], image.shape[0]

    # Ensure the coordinates are within the valid range
    top_left = (max(0, top_left[0]), max(0, top_left[1]))
    bottom_right = (min(width - 1, bottom_right[0]),
                    min(height - 1, bottom_right[1]))

    # Create a mask image
    mask = Image.new("L", (width, height), 0)
    draw = ImageDraw.Draw(mask)
    draw.rectangle([top_left, bottom_right], fill=255)

    # Apply the mask to the image
    result = Image.new("RGB", (width, height), (255, 255, 255))
    result.paste(Image.fromarray(image), mask=mask)

    return np.array(result)


def get_max_coordinates(image_path):
    # Open the image
    image = Image.open(image_path)

    # Get the width and height of the image
    width, height = image.size

    # Maximal coordinates
    max_x = width - 1
    max_y = height - 1

    return max_x, max_y

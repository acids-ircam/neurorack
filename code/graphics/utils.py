# -*- coding: utf-8 -*-


import time
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
        
_WHITE = (255, 255, 255)
_GREEN = (0, 255, 0)
_BLUE = (0, 0, 255)
_RED = (255, 0, 0)

def draw_rotated_text(image, text, position, angle, font=None, fill=_WHITE):
    if (font is None):
        # Load default font.
        font = ImageFont.load_default()
    # Get rendered font width and height.
    draw = ImageDraw.Draw(image)
    width, height = draw.textsize(text, font=font)
    # Create a new image with transparent background to store the text.
    textimage = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    # Render the text.
    textdraw = ImageDraw.Draw(textimage)
    textdraw.text((0, 0), text, font=font, fill=fill)
    # Rotate the text image.
    rotated = textimage.rotate(angle, expand=1)
    # Paste the text into the image, using it as a mask for transparency.
    image.paste(rotated, position, rotated)
    
def draw_animated_gif(disp, image_file, width, height):
    # Load an image.
    print('Loading gif: {}...'.format(image_file))
    image = Image.open(image_file)
    frame = 0
    while True:
        try:
            image.seek(frame)
            disp.display(image.resize((width, height)))
            frame += 1
            time.sleep(0.05)
        except EOFError:
            frame = 0
    
# Draw some shapes
def draw_rectangle(image, x, y, width, height, outline=_WHITE, fill=_WHITE):
    # Get draw object in image
    draw = ImageDraw.Draw(image)
    # Draw a purple rectangle with yellow outline.
    draw.rectangle((x, y, width, height), outline=outline, fill=fill)

def draw_ellipse(image, x, y, width, height, outline=_WHITE, fill=_WHITE):
    # Get draw object in image
    draw = ImageDraw.Draw(image)
    # Draw a blue ellipse with a green outline.
    draw.ellipse((x, y, width, height), outline=outline, fill=fill)

def draw_lines(image, x, y, width, height, fill=_WHITE):
    # Get draw object in image
    draw = ImageDraw.Draw(image)
    # Draw a white X.
    draw.line((x, y, height, width), fill=fill)

def draw_triangle(image, a, b, c, outline=_WHITE, fill=_WHITE):
    # Get draw object in image
    draw = ImageDraw.Draw(image)
    # Draw a cyan triangle with a black outline.
    draw.polygon([a, b, c], outline=outline, fill=fill)
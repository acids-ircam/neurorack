# -*- coding: utf-8 -*-


import time
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
        
_WHITE = (255, 255, 255)
_GREEN = (0, 255, 0)
_BLUE = (0, 0, 255)
_RED = (255, 0, 0)

"""
Create an image that fits into screen properties
"""
def get_resized_image(filename, width, height, ratio=0):
    image = Image.open(filename)
    # Scale the image to the smaller screen dimension
    image_ratio = image.width / image.height
    screen_ratio = width / height
    if screen_ratio < image_ratio:
        scaled_width = image.width * height // image.height
        scaled_height = height
    else:
        scaled_width = width
        scaled_height = image.height * width // image.width
    if (ratio > 0):
        scaled_width = (scaled_width * ratio)
        scaled_height = (scaled_height * ratio)
        image = image.resize((scaled_width, scaled_height), Image.BICUBIC)
        image = image.crop((0, 0, scaled_width, scaled_height))
        return image
    image = image.resize((scaled_width, scaled_height), Image.BICUBIC)
    # Crop and center the image
    x = scaled_width // 2 - width // 2
    y = scaled_height // 2 - height // 2
    image = image.crop((x, y, x + width, y + height))
    # Return image.
    return image
    
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
    
# Draw some shapes
def draw_rectangle(image, x, y, width, height, outline=_WHITE, fill=_WHITE):
    # Get draw object in image
    draw = ImageDraw.Draw(image)
    # Draw a purple rectangle with yellow outline.
    draw.rectangle((x, y, width, height), outline=outline, fill=fill)
    
# Draw some shapes
def draw_rounded_rectangle(image, x, y, width, height, radius=2, outline=_WHITE, fill=_WHITE):
    # Get draw object in image
    draw = ImageDraw.Draw(image)
    # Draw a purple rectangle with yellow outline.
    draw.rounded_rectangle((x, y, width, height), radius=radius, outline=outline, fill=fill)

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

def __drawScrollArrows(self):
    """
        Handles drawing of the Scroll Arrows for the menu as needed
    """
    if self.__scrollDown: 
        self.__draw.polygon([
            (self.__width-5, self.__height-10),
            (self.__width-15, self.__height-10),
            (self.__width-10, self.__height-5)
        ], fill=self.__navigationColor, outline=self.__navigationColor)
    if self.__scrollUp:
        self.__draw.polygon([
            (self.__width-5, 10),
            (self.__width-15, 10),
            (self.__width-10, 5)
        ], fill=self.__navigationColor, outline=self.__navigationColor)
    
"""

# Set of reminders from the PIL documentation

# Create thumbnail
with Image.open(infile) as im:
    im.thumbnail(size)
    im.save(outfile, "JPEG")
    
# Copying a subrectangle from an image
box = (100, 100, 400, 400)
region = im.crop(box)

# Processing a subrectangle, and pasting it back
region = region.transpose(Image.ROTATE_180)
im.paste(region, box)

PIL.Image.blend(im1, im2, alpha)[source]
Creates a new image by interpolating between two input images, using a constant alpha.:
out = image1 * (1.0 - alpha) + image2 * alpha

PIL.Image.effect_mandelbrot(size, extent, quality)[source]
Generate a Mandelbrot set covering the given extent.

PIL.Image.composite(image1, image2, mask)[source]
Create composite image by blending images using a transparency mask.
Parameters
image1 – The first image.
image2 – The second image. Must have the same mode and size as the first image.
mask – A mask image. This image can have mode “1”, “L”, or “RGBA”, and must have the same size as the other two images.

Image.resize(size, resample=3, box=None, reducing_gap=None)[source]
Returns a resized copy of this image.

Example: Draw Partial Opacity Text
# draw text, half opacity
d.text((10,10), "Hello", font=fnt, fill=(255,255,255,128))
# draw text, full opacity
d.text((10,60), "World", font=fnt, fill=(255,255,255,255))

Example: Draw Multiline Text
# draw multiline text
d.multiline_text((10,10), "Hello\nWorld", font=fnt, fill=(0, 0, 0))

PIL.ImageOps.pad(image, size, method=3, color=None, centering=(0.5, 0.5))[source]
Returns a sized and padded version of the image, expanded to fill the requested aspect ratio and size.

PIL.ImageOps.fit(image, size, method=3, bleed=0.0, centering=(0.5, 0.5))[source]
Returns a sized and cropped version of the image, cropped to the requested aspect ratio and size.
"""

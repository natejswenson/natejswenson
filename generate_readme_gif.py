#!/usr/bin/env python3
"""
Generate animated GIF for GitHub README with typing effect and colored shapes.
"""

from PIL import Image, ImageDraw, ImageFont
import os

# Configuration
WIDTH = 800
HEIGHT = 400
BACKGROUND_COLOR = (255, 255, 255)
TEXT_COLOR = (0, 0, 0)
FONT_SIZE = 20
TYPING_SPEED = 2  # frames per character
PAUSE_AT_END = 30  # frames to pause at end before looping

# Shape colors (red, yellow, teal, blue, repeating)
SHAPE_COLORS = [
    (223, 0, 36),    # #df0024 red
    (243, 195, 0),   # #f3c300 yellow
    (0, 171, 159),   # #00ab9f teal
    (46, 109, 180),  # #2e6db4 blue
]

# Content lines
LINES = [
    "nate swenson:",
    "▲ Operations Engineer @ goodleap",
    "■ AI Enthusiast",
    "✖ Contious Learner",
    "● experieced coder in js and python",
    "../interested-in"
    "▲ fitnessstem"
    "■ STEM (for kids)",
    "✖ coding",
    "../connect-with-me"
    "■ linkedin.com/in/natejswenson",
    "✖ natejswenson.github.io/my-resume",
    "● natejswenson.com"
]

# Shapes (circle, triangle, square, X)
SHAPES = ["●", "▲", "■", "✖"]

def get_font(size):
    """Try to load a monospace font, fallback to default."""
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
        "/System/Library/Fonts/Courier.dfont",
        "/usr/share/fonts/truetype/ubuntu/UbuntuMono-R.ttf",
    ]

    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                return ImageFont.truetype(font_path, size)
            except:
                pass

    # Fallback to default
    return ImageFont.load_default()

def draw_text_with_colored_shapes(draw, text, x, y, font, line_index):
    """Draw text with the first character (shape) in color, rest in black."""
    if not text:
        return

    # Get the shape color for this line
    color_index = line_index % len(SHAPE_COLORS)
    shape_color = SHAPE_COLORS[color_index]

    # Draw the shape (first character) in color
    shape = text[0]
    draw.text((x, y), shape, fill=shape_color, font=font)

    # Calculate width of the shape character to position the rest
    shape_bbox = draw.textbbox((x, y), shape, font=font)
    shape_width = shape_bbox[2] - shape_bbox[0]

    # Draw the rest of the text in black
    if len(text) > 1:
        draw.text((x + shape_width, y), text[1:], fill=TEXT_COLOR, font=font)

def create_frames():
    """Generate all frames for the animation."""
    frames = []
    font = get_font(FONT_SIZE)

    # Start with terminal prompt
    prompt = "$ whoami"
    line_height = 30
    start_y = 40

    # Calculate total characters to type
    total_chars = sum(len(line) for line in LINES)

    current_line_index = 0
    current_char_index = 0

    # Generate typing frames
    for frame_num in range(total_chars * TYPING_SPEED):
        img = Image.new('RGB', (WIDTH, HEIGHT), BACKGROUND_COLOR)
        draw = ImageDraw.Draw(img)

        # Draw prompt
        draw.text((20, start_y), prompt, fill=TEXT_COLOR, font=font)

        # Draw completed lines
        for i in range(current_line_index):
            y_pos = start_y + line_height * (i + 1)
            draw_text_with_colored_shapes(draw, LINES[i], 20, y_pos, font, i)

        # Draw current line being typed
        if current_line_index < len(LINES):
            y_pos = start_y + line_height * (current_line_index + 1)
            current_text = LINES[current_line_index][:current_char_index]
            draw_text_with_colored_shapes(draw, current_text, 20, y_pos, font, current_line_index)

        frames.append(img)

        # Update character position every TYPING_SPEED frames
        if frame_num % TYPING_SPEED == 0:
            current_char_index += 1
            if current_line_index < len(LINES) and current_char_index > len(LINES[current_line_index]):
                current_line_index += 1
                current_char_index = 0

    # Add pause frames at the end
    final_img = Image.new('RGB', (WIDTH, HEIGHT), BACKGROUND_COLOR)
    draw = ImageDraw.Draw(final_img)
    draw.text((20, start_y), prompt, fill=TEXT_COLOR, font=font)

    for i, line in enumerate(LINES):
        y_pos = start_y + line_height * (i + 1)
        draw_text_with_colored_shapes(draw, line, 20, y_pos, font, i)

    for _ in range(PAUSE_AT_END):
        frames.append(final_img.copy())

    return frames

def main():
    print("Generating animated GIF...")
    frames = create_frames()

    # Save as animated GIF
    output_path = "output.gif"
    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        duration=50,  # milliseconds per frame
        loop=0  # loop forever
    )

    print(f"✓ Generated {output_path}")
    print(f"  Total frames: {len(frames)}")
    print(f"  Size: {WIDTH}x{HEIGHT}")

if __name__ == "__main__":
    main()

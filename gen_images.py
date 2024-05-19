from PIL import Image, ImageDraw

def create_shape(shape, filename, color):
    # Define the size of each box
    box_size = 60
    # Calculate image size based on the shape dimensions
    width = max(x for x, y in shape) * box_size + box_size
    height = max(y for x, y in shape) * box_size + box_size
    
    # Create a new image with a transparent background
    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # Draw each box in the shape
    for (x, y) in shape:
        top_left = (x * box_size, y * box_size)
        bottom_right = (top_left[0] + box_size, top_left[1] + box_size)
        draw.rectangle([top_left, bottom_right], fill=color)
    
    # Save the image as a PNG file
    image.save(filename)

# Define shapes using coordinates (x, y)
shapes = {
    "tavern": [(0, 0)],
    "stable": [(0, 0), (1, 0)],
    "inn": [(0, 0), (1, 0), (0, 1)],
    "square": [(0, 0), (1, 0), (0, 1), (1, 1)],
}

# Create and save each shape
for shape_name, shape_coords in shapes.items():
    create_shape(shape_coords, f"r_{shape_name}.png", "red")

for shape_name, shape_coords in shapes.items():
    create_shape(shape_coords, f"b_{shape_name}.png", "black")
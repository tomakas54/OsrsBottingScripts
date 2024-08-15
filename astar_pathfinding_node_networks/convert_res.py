from PIL import Image

def change_image_resolution(input_image_path, output_image_path, new_width, new_height):
    try:
        # Open an image file
        with Image.open(input_image_path) as img:
            # Print the original size
            print(f"Original image size: {img.size}")

            # Resize image
            img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # Save the resized image
            img_resized.save(output_image_path)

            # Print the new size
            print(f"Resized image saved as: {output_image_path}")
            print(f"New image size: {img_resized.size}")

    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
input_image_path = 'osrs_map_merged.png'  # Path to your input image
output_image_path = 'osrs_map_merged_output.png'  # Path to save the resized image
new_width = int(12000/4)  # Desired width
new_height = int(7250/4) # Desired height

change_image_resolution(input_image_path, output_image_path, new_width, new_height)
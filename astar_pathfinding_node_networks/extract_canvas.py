import base64
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
from PIL import Image
from PIL import ImageDraw


def osrs_canvas_scrape():
    options = Options()
    user = "i7 8700" # change this to your windows username
    options.add_argument("user-data-dir=C:\\Users\\" + user + "\\AppData\\Local\\Google\\Chrome\\User Data\\Profile 1")
    driver = webdriver.Chrome(executable_path=r"C:\Users\\" + user + "\\Downloads\chromedriver.exe", chrome_options=options)
    driver.set_window_size(10000, 10000)
    driver.get("https://www.osrsmap.net/")
    canvas = driver.find_element_by_id("map")
    time.sleep(1.5)
    driver.find_element_by_id("show-labels").click()
    # get the canvas as a PNG base64 string
    time.sleep(1.5)
    x = 1000
    i = 1
    while x < 4500:
        y = 2500
        b = 1
        while y < 4500:
            driver.get("https://www.osrsmap.net/#area=main&x=" + str(x) + "&y=" + str(y) + "&zoom=100")
            time.sleep(0.1)
            canvas_base64 = driver.execute_script("return arguments[0].toDataURL('image/png').substring(21);", canvas)
            # decode
            canvas_png = base64.b64decode(canvas_base64)
            # save to a file
            with open(r"images/osrs_map_canvas_" + str(i) + "_" + str(b) + ".png", 'wb') as f:
                f.write(canvas_png)
            y += 200
            b += 1
        x += 600
        i += 1

def crop_black_bars(image_path, output_path):
    """
    Crop black bars from an image.

    :param image_path: Path to the input image
    :param output_path: Path to save the cropped image
    """
    # Open the image
    img = Image.open(image_path)
    img = img.convert("RGB")  # Convert to RGB to ensure consistent color data
    
    # Get image dimensions
    width, height = img.size

    # Find non-black bounding box
    bbox = img.getbbox()

    # Crop the image to the bounding box
    cropped_img = img.crop(bbox)
    
    # Save the cropped image
    cropped_img.save(output_path)
    print(f"Cropped image saved to {output_path}")

print('*** Program Started ***')
image_name_output = '02_create_blank_image_01.png'
mode = 'RGB' # for color image “L” (luminance) for greyscale images, “RGB” for true color images, and “CMYK” for pre-press images.
size = (12000, 7250)
color = (0, 0, 0)
im = Image.new(mode, size, color)
im.save(image_name_output )

#im.show()


img0 = Image.open(r"02_create_blank_image_01.png")

x = 2
x_pos = 0
while x < 6:

    y = 9
    y_pos = 0
    while y > 0:
        img = Image.open(r"astar_pathfinding_node_networks/images/osrs_map_canvas_" + str(x) + "_" + str(y) + ".png")
        img0.paste(img, (x_pos, y_pos))
        y_pos += 800
        print("x:", x, " | y:", y)
        y -= 1
    x_pos += 2400
    x += 1
print('*** Program Ended ***')
img0.save("osrs_map_merged.png")
# Example usage
image_path = 'osrs_map_merged.png'  # Replace with the path to your image
output_path = 'osrs_map_merged.png'  # Replace with the desired output path
crop_black_bars(image_path, output_path)
#img0.show()

#test_url()
#osrs_canvas_scrape()

import cv2
import numpy as np
import random
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.window_utils import *

def take_screenshot(hwnd):
    # Take a screenshot of the specified region
    screenshot, left, top, width, height = get_window_screenshot(hwnd)
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    screenshot_path = 'screenshot.png'
    cv2.imwrite(screenshot_path, screenshot)
    # print(f"Screenshot saved to {screenshot_path}")
    return screenshot_path

def preprocess_image(image):
    # Set all pixels that don't have a green channel value of 255 to black
    mask = image[:, :, 1] == 255
    preprocessed_image = np.zeros_like(image)
    preprocessed_image[mask] = image[mask]
    return preprocessed_image

def template_match(source_image_path, template_image_path, threshold=0.8, roi=None, scale_factor=1.0):
    """
    Perform template matching and draw bounding boxes around detected matches with optional ROI and scaling.
    
    Parameters:
    - source_image_path: Path to the source image.
    - template_image_path: Path to the template image.
    - threshold: Matching score threshold for detecting matches.
    - roi: Region of interest as a tuple (x, y, w_roi, h_roi). If None, the whole image is used.
    - scale_factor: Factor to scale bounding box size. Values > 1.0 enlarge, values < 1.0 shrink.
    
    Returns:
    - List of random coordinates within the bounding boxes of detected matches.
    """
    # Read the source image and the template image
    source_image = cv2.imread(source_image_path)
    template_image = cv2.imread(template_image_path)
    
    if source_image is None:
        print(f"Error: Unable to load source image from {source_image_path}")
        return None
    
    if template_image is None:
        print(f"Error: Unable to load template image from {template_image_path}")
        return None

    # Convert images to grayscale
    source_gray = cv2.cvtColor(source_image, cv2.COLOR_BGR2GRAY)
    template_gray = cv2.cvtColor(template_image, cv2.COLOR_BGR2GRAY)

    # Get the dimensions of the template image
    template_w, template_h = template_gray.shape[::-1]

    # Define the region of interest (ROI) if provided
    if roi:
        x, y, w_roi, h_roi = roi
        source_gray = source_gray[y:y + h_roi, x:x + w_roi]
        original_image = source_image[y:y + h_roi, x:x + w_roi]
    else:
        original_image = source_image

    # Perform template matching
    res = cv2.matchTemplate(source_gray, template_gray, cv2.TM_CCOEFF_NORMED)
    
    # Find locations where the matching score is above the threshold
    loc = np.where(res >= threshold)
    
    matches = []
    for pt in zip(*loc[::-1]):  # Switch columns and rows
        if roi:
            pt = (pt[0] + roi[0], pt[1] + roi[1])
        
        # Adjust the bounding box size based on the scale factor
        x1, y1 = pt
        x2, y2 = x1 + template_w, y1 + template_h
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        width = (x2 - x1) * scale_factor
        height = (y2 - y1) * scale_factor
        
        # Ensure width and height are positive
        width = max(width, 1)
        height = max(height, 1)
        
        # Calculate new bounding box corners
        x1 = int(center_x - width / 2)
        y1 = int(center_y - height / 2)
        x2 = int(center_x + width / 2)
        y2 = int(center_y + height / 2)
        
        matches.append((x1, y1, x2, y2))
        cv2.rectangle(original_image, (x1, y1), (x2, y2), (0, 255, 0), 2)

    # Save the result image with rectangles drawn around matches
    result_image_path = 'result.png'
    cv2.imwrite(result_image_path, original_image)
    # print(f"Matching completed. Result saved to {result_image_path}")

    # Generate random coordinates within each bounding box
    random_coordinates = []
    for (x1, y1, x2, y2) in matches:
        rand_x = random.randint(x1, x2)
        rand_y = random.randint(y1, y2)
        random_coordinates.append((rand_x, rand_y))
        # print(f"Random coordinate within bounding box ({x1}, {y1}, {x2}, {y2}): ({rand_x}, {rand_y})")
    
    return random_coordinates

def template_match_multiple(source_image_path, template_image_paths, threshold=0.8, roi=None, scale_factor=1.0):
    """
    Perform template matching with multiple templates and draw bounding boxes around detected matches
    with optional ROI and scaling.
    
    Parameters:
    - source_image_path: Path to the source image.
    - template_image_paths: List of paths to the template images.
    - threshold: Matching score threshold for detecting matches.
    - roi: Region of interest as a tuple (x, y, w_roi, h_roi). If None, the whole image is used.
    - scale_factor: Factor to scale bounding box size. Values > 1.0 enlarge, values < 1.0 shrink.
    
    Returns:
    - List of random coordinates within the bounding boxes of detected matches.
    """
    # Read the source image
    source_image = cv2.imread(source_image_path)
    
    if source_image is None:
        print(f"Error: Unable to load source image from {source_image_path}")
        return None

    # Convert source image to grayscale
    source_gray = cv2.cvtColor(source_image, cv2.COLOR_BGR2GRAY)

    # Define the region of interest (ROI) if provided
    if roi:
        x, y, w_roi, h_roi = roi
        source_gray = source_gray[y:y + h_roi, x:x + w_roi]
        original_image = source_image[y:y + h_roi, x:x + w_roi]
    else:
        original_image = source_image

    matches = []

    # Loop over all template image paths
    for template_image_path in template_image_paths:
        # Read the template image
        template_image = cv2.imread(template_image_path)
        
        if template_image is None:
            print(f"Error: Unable to load template image from {template_image_path}")
            continue

        # Convert template image to grayscale
        template_gray = cv2.cvtColor(template_image, cv2.COLOR_BGR2GRAY)

        # Get the dimensions of the template image
        template_w, template_h = template_gray.shape[::-1]

        # Perform template matching
        res = cv2.matchTemplate(source_gray, template_gray, cv2.TM_CCOEFF_NORMED)
        
        # Find locations where the matching score is above the threshold
        loc = np.where(res >= threshold)
        
        for pt in zip(*loc[::-1]):  # Switch columns and rows
            if roi:
                pt = (pt[0] + roi[0], pt[1] + roi[1])
            
            # Adjust the bounding box size based on the scale factor
            x1, y1 = pt
            x2, y2 = x1 + template_w, y1 + template_h
            center_x = (x1 + x2) / 2
            center_y = (y1 + y2) / 2
            width = (x2 - x1) * scale_factor
            height = (y2 - y1) * scale_factor
            
            # Ensure width and height are positive
            width = max(width, 1)
            height = max(height, 1)
            
            # Calculate new bounding box corners
            x1 = int(center_x - width / 2)
            y1 = int(center_y - height / 2)
            x2 = int(center_x + width / 2)
            y2 = int(center_y + height / 2)
            
            matches.append((x1, y1, x2, y2))
            cv2.rectangle(original_image, (x1, y1), (x2, y2), (0, 255, 0), 2)

    # Save the result image with rectangles drawn around matches
    result_image_path = 'result.png'
    cv2.imwrite(result_image_path, original_image)
    #print(f"Matching completed. Result saved to {result_image_path}")

    # Generate random coordinates within each bounding box
    random_coordinates = []
    for (x1, y1, x2, y2) in matches:
        rand_x = random.randint(x1, x2)
        rand_y = random.randint(y1, y2)
        random_coordinates.append((rand_x, rand_y))
        #print(f"Random coordinate within bounding box ({x1}, {y1}, {x2}, {y2}): ({rand_x}, {rand_y})")
    
    return random_coordinates

def merge_close_boxes(boxes, threshold=10):
    if not boxes:
        return []

    def box_distance(box1, box2):
        x_min1, y_min1, x_max1, y_max1 = box1
        x_min2, y_min2, x_max2, y_max2 = box2

        dx = max(0, max(x_min1, x_min2) - min(x_max1, x_max2))
        dy = max(0, max(y_min1, y_min2) - min(y_max1, y_max2))

        return max(dx, dy)

    def merge_two_boxes(box1, box2):
        x_min1, y_min1, x_max1, y_max1 = box1
        x_min2, y_min2, x_max2, y_max2 = box2

        x_min = min(x_min1, x_min2)
        y_min = min(y_min1, y_min2)
        x_max = max(x_max1, x_max2)
        y_max = max(y_max1, y_max2)

        return (x_min, y_min, x_max, y_max)

    merged_boxes = []
    used = [False] * len(boxes)

    for i in range(len(boxes)):
        if used[i]:
            continue

        current_box = boxes[i]
        x_min, y_min, x_max, y_max = current_box
        has_merge = True

        while has_merge:
            has_merge = False
            for j in range(len(boxes)):
                if i != j and not used[j]:
                    other_box = boxes[j]
                    if box_distance(current_box, other_box) <= threshold:
                        current_box = merge_two_boxes(current_box, other_box)
                        used[j] = True
                        has_merge = True

        merged_boxes.append(current_box)
        used[i] = True

    return merged_boxes

def template_match_digits(source_image_path, template_image_paths, roi=None, threshold=0.8):
    # Read the source image
    source_image = cv2.imread(source_image_path)
    
    if source_image is None:
        print(f"Error: Unable to load source image from {source_image_path}")
        return None

    # If ROI is specified, crop the source image to the ROI
    if roi is not None:
        x, y, w, h = roi
        source_image = source_image[y:y+h, x:x+w]

    # Preprocess source image
    source_image = preprocess_image(source_image)
    source_gray = cv2.cvtColor(source_image, cv2.COLOR_BGR2GRAY)

    all_matches = []

    for template_image_path in template_image_paths:
        # Read the template image
        template_image = cv2.imread(template_image_path)
        
        if template_image is None:
            print(f"Error: Unable to load template image from {template_image_path}")
            continue

        # Preprocess template image
        template_image = preprocess_image(template_image)
        template_gray = cv2.cvtColor(template_image, cv2.COLOR_BGR2GRAY)

        # Get the dimensions of the template image
        w, h = template_gray.shape[::-1]

        # Perform template matching
        res = cv2.matchTemplate(source_gray, template_gray, cv2.TM_CCOEFF_NORMED)
        
        # Find locations where the matching score is above the threshold
        loc = np.where(res >= threshold)
        
        matches = []
        for pt in zip(*loc[::-1]):  # Switch columns and rows
            matches.append((pt[0], pt[1], pt[0] + w, pt[1] + h))

        # Add matches to all_matches
        all_matches.extend(matches)

    # Merge close matches into single bounding boxes
    merged_boxes = merge_close_boxes(all_matches, threshold=10)  # Adjust threshold if needed
    # Draw merged bounding boxes on the image
    for (x_min, y_min, x_max, y_max) in merged_boxes:
        cv2.rectangle(source_image, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)

    # Save the result image with rectangles drawn around matches
    result_image_path = 'result.png'
    cv2.imwrite(result_image_path, source_image)
    # print(f"Matching completed. Result saved to {result_image_path}")

    return merged_boxes



if __name__ == "__main__":
    # Take a screenshot of the whole screen
    hwnd = findWindow_runelite('GIMGrupiokas')

    while True:
        screenshot_path = take_screenshot(hwnd)
        # Example usage
        source_image_path = screenshot_path  # Use the screenshot as the source image
        
        # List of template image paths from 1 to 9
        template_image_paths = [f'../assets/{i}.png' for i in range(1, 10)]

        # Define ROI as (x, y, width, height)
        roi = (358, 285, 90, 35)  # Adjust these values as needed

        matches = template_match_digits(source_image_path, template_image_paths, roi=roi, threshold=0.9)
  

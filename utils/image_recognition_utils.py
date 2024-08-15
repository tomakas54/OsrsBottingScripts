import cv2
import numpy as np
import random
import os
import glob
from rich.console import Console
from rich.traceback import install
from typing import List, Tuple, Optional
from utils import window_utils

console = Console()
install()
# Add a helper function to verify if the path exists]

class ImageRecognition:
    def __init__(self) -> None:
        self.screenshot_manager = window_utils.ScreenshotManager()
        self.screenshot_path = window_utils.ScreenshotManager().get_screenshot_path()
    

    def load_image(self, image_path: str, preprocess: bool = False) -> np.ndarray:
        """
        Load an image from the specified path and optionally preprocess it.
        
        Parameters:
        - image_path: Path to the image.
        - preprocess: Whether to preprocess the image.
        
        Returns:
        - image: The loaded (and optionally preprocessed) image.
        
        Raises:
        - FileNotFoundError: If the image cannot be loaded.
        """
        image = cv2.imread(image_path)
        if image is None:
            raise FileNotFoundError(f"Unable to load image from {image_path}")
        if preprocess:
            image = self.preprocess_image(image)
        return image

    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess the image by creating a mask where the green channel is 255 
        and setting those pixels in the output image.
        
        Parameters:
        - image: The input image.
        
        Returns:
        - preprocessed_image: The preprocessed image.
        """
        mask = image[:, :, 1] == 255
        preprocessed_image = np.zeros_like(image)
        preprocessed_image[mask] = image[mask]
        return preprocessed_image

    def generate_random_b_box_coord(self, matches: List[Tuple[int, int, int, int]]) -> List[Tuple[int, int]]:
        """
        Generate random coordinates within the bounding boxes.
        
        Parameters:
        - matches: List of bounding boxes as (x1, y1, x2, y2).
        
        Returns:
        - List of random coordinates within the bounding boxes.
        """
        random_coordinates = []
        for (x1, y1, x2, y2) in matches:
            rand_x = random.randint(x1, x2)
            rand_y = random.randint(y1, y2)
            random_coordinates.append((rand_x, rand_y))
        return random_coordinates

    def shrink_boxes(self, boxes: List[Tuple[int, int, int, int]], scaling_factor: float) -> List[Tuple[int, int, int, int]]:
        """
        Shrink bounding boxes by the given scaling factor.
        
        Parameters:
        - boxes: List of bounding boxes as (x_min, y_min, x_max, y_max).
        - scaling_factor: Factor by which to shrink the boxes (e.g., 0.8 will shrink the boxes to 80% of their size).
        
        Returns:
        - shrunk_boxes: List of shrunk bounding boxes.
        """
        shrunk_boxes = []
        for x_min, y_min, x_max, y_max in boxes:
            width = x_max - x_min
            height = y_max - y_min
            center_x = x_min + width // 2
            center_y = y_min + height // 2
            
            new_width = width * scaling_factor
            new_height = height * scaling_factor
            
            half_width = new_width // 2
            half_height = new_height // 2
            
            new_x_min = int(center_x - half_width)
            new_y_min = int(center_y - half_height)
            new_x_max = int(center_x + half_width)
            new_y_max = int(center_y + half_height)
            
            shrunk_boxes.append((new_x_min, new_y_min, new_x_max, new_y_max))
        
        return shrunk_boxes

    def template_match(self, template_image_path: str, threshold: float = 0.8, roi: Optional[Tuple[int, int, int, int]] = None, scaling_factor: float = 1.0) -> List[Tuple[int, int, int, int]]:
        """
        Perform template matching on the source image to find occurrences of the template image.
        
        Parameters:
        - template_image_path: Path to the template image.
        - threshold: Matching threshold.
        - roi: Region of interest as a tuple (x, y, width, height). If None, the whole image is used.
        - scaling_factor: Scaling factor to shrink the boxes.
        
        Returns:
        - matches: List of coordinates of matched regions as (x1, y1, x2, y2).
        """
        # Reload the screenshot to ensure we're using the most recent one
        self.screenshot_manager.take_screenshot()
        source_image = self.load_image(self.screenshot_path)
        template_image = self.load_image(template_image_path)
        source_gray = cv2.cvtColor(source_image, cv2.COLOR_BGR2GRAY)
        template_gray = cv2.cvtColor(template_image, cv2.COLOR_BGR2GRAY)
        template_w, template_h = template_gray.shape[::-1]

        if roi:
            x, y, w, h = roi
            source_gray = source_gray[y:y + h, x:x + w]
            source_image = source_image[y:y + h, x:x + w]

        res = cv2.matchTemplate(source_gray, template_gray, cv2.TM_CCOEFF_NORMED)
        loc = np.where(res >= threshold)

        matches = []
        for pt in zip(*loc[::-1]):
            if roi:
                pt = (pt[0] + roi[0], pt[1] + roi[1])
            x1, y1, x2, y2 = pt[0], pt[1], pt[0] + template_w, pt[1] + template_h
            matches.append((x1, y1, x2, y2))

        if scaling_factor < 1.0:
            matches = self.shrink_boxes(matches, scaling_factor)

        for (x1, y1, x2, y2) in matches:
            cv2.rectangle(source_image, (x1, y1), (x2, y2), (0, 255, 0), 1)

        result_image_path = 'result.png'
        cv2.imwrite(result_image_path, source_image)
        return matches

    def template_match_multiple(self,template_image_paths: List[str], threshold: float = 0.8, roi: Optional[Tuple[int, int, int, int]] = None, scaling_factor: float = 1.0) -> List[Tuple[int, int, int, int]]:
        """
        Perform template matching on the source image to find occurrences of multiple template images.
        
        Parameters:
        - source_image_path: Path to the source image.
        - template_image_paths: List of paths to the template images.
        - threshold: Matching threshold.
        - roi: Region of interest as a tuple (x, y, width, height). If None, the whole image is used.
        - scaling_factor: Scaling factor to shrink the boxes.
        
        Returns:
        - matches: List of coordinates of matched regions as (x1, y1, x2, y2).
        """
        self.screenshot_manager.take_screenshot()
        source_image = self.load_image(self.screenshot_path)
        source_gray = cv2.cvtColor(source_image, cv2.COLOR_BGR2GRAY)

        if roi:
            x, y, w, h = roi
            source_gray = source_gray[y:y + h, x:x + w]
            source_image = source_image[y:y + h, x:x + w]

        all_matches = []
        
        for template_image_path in template_image_paths:
            template_image = self.load_image(template_image_path)
            template_gray = cv2.cvtColor(template_image, cv2.COLOR_BGR2GRAY)
            template_w, template_h = template_gray.shape[::-1]

            res = cv2.matchTemplate(source_gray, template_gray, cv2.TM_CCOEFF_NORMED)
            loc = np.where(res >= threshold)

            matches = []
            for pt in zip(*loc[::-1]):
                if roi:
                    pt = (pt[0] + roi[0], pt[1] + roi[1])
                x1, y1, x2, y2 = pt[0], pt[1], pt[0] + template_w, pt[1] + template_h
                matches.append((x1, y1, x2, y2))
            
            if scaling_factor < 1.0:
                matches = self.shrink_boxes(matches, scaling_factor)
            
            all_matches.extend(matches)
        
        # Draw rectangles on the source image
        for (x1, y1, x2, y2) in all_matches:
            cv2.rectangle(source_image, (x1, y1), (x2, y2), (0, 255, 0), 1)
        
        result_image_path = 'result.png'
        cv2.imwrite(result_image_path, source_image)
        
        return all_matches

    def template_match_multiple_folder(self,template_directory: str, threshold: float = 0.8, roi: Optional[Tuple[int, int, int, int]] = None, scaling_factor: float = 1.0) -> List[Tuple[int, int, int, int]]:
        """
        Perform template matching for multiple template images found in a specified directory on the source image.
        
        Parameters:
        - source_image_path: Path to the source image.
        - template_directory: Directory path containing template images (all .png files will be used).
        - threshold: Matching threshold.
        - roi: Region of interest as a tuple (x, y, width, height). If None, the whole image is used.
        - scaling_factor: Factor by which to shrink the bounding boxes (default is 1.0, meaning no shrinking).
        
        Returns:
        - all_matches: List of coordinates of matched regions from all templates, optionally shrunk.
        """
        all_matches = []
        
        # Find all .png files in the specified directory
        template_image_paths = glob.glob(os.path.join(template_directory, '*.png'))
        
        for template_image_path in template_image_paths:
            console.log(template_image_path)
            matches = self.template_match(template_image_path, threshold, roi)
            all_matches.extend(matches)

        if scaling_factor < 1.0:
            all_matches = self.shrink_boxes(all_matches, scaling_factor)

        return all_matches

    def merge_close_boxes(boxes: List[Tuple[int, int, int, int]], threshold: int = 10) -> List[Tuple[int, int, int, int]]:
        """
        Merge close bounding boxes into a single bounding box.
        
        Parameters:
        - boxes: List of bounding boxes as (x_min, y_min, x_max, y_max).
        - threshold: Distance threshold for merging boxes.
        
        Returns:
        - merged_boxes: List of merged bounding boxes.
        """
        def box_distance(box1: Tuple[int, int, int, int], box2: Tuple[int, int, int, int]) -> int:
            x_min1, y_min1, x_max1, y_max1 = box1
            x_min2, y_min2, x_max2, y_max2 = box2
            dx = max(0, max(x_min1, x_min2) - min(x_max1, x_max2))
            dy = max(0, max(y_min1, y_min2) - min(y_max1, y_max2))
            return max(dx, dy)

        def merge_two_boxes(box1: Tuple[int, int, int, int], box2: Tuple[int, int, int, int]) -> Tuple[int, int, int, int]:
            x_min1, y_min1, x_max1, y_max1 = box1
            x_min2, y_min2, x_max2, y_max2 = box2
            return min(x_min1, x_min2), min(y_min1, y_min2), max(x_max1, x_max2), max(y_max1, y_max2)

        merged_boxes = []
        used = [False] * len(boxes)

        for i, current_box in enumerate(boxes):
            if used[i]:
                continue
            has_merge = True
            while has_merge:
                has_merge = False
                for j, other_box in enumerate(boxes):
                    if i != j and not used[j] and box_distance(current_box, other_box) <= threshold:
                        current_box = merge_two_boxes(current_box, other_box)
                        used[j] = True
                        has_merge = True
            merged_boxes.append(current_box)
            used[i] = True

        return merged_boxes

    def template_match_digits(self,template_image_paths: List[str], roi: Optional[Tuple[int, int, int, int]] = None, threshold: float = 0.8) -> List[Tuple[int, int, int, int]]:
        """
        Perform template matching for digit templates on the source image and merge close bounding boxes.
        
        Parameters:
        - source_image_path: Path to the source image.
        - template_image_paths: List of paths to template images.
        - roi: Region of interest as a tuple (x, y, width, height). If None, the whole image is used.
        - threshold: Matching threshold.
        
        Returns:
        - merged_boxes: List of merged bounding boxes after template matching.
        """
        self.screenshot_manager.take_screenshot()
        source_image = self.load_image(self.screenshot_path)
        if roi:
            x, y, w, h = roi
            source_image = source_image[y:y + h, x:x + w]
        
        all_matches = self.template_match_multiple(template_image_paths, threshold, roi)
        merged_boxes = self.merge_close_boxes(all_matches, threshold=10)
        
        for x_min, y_min, x_max, y_max in merged_boxes:
            cv2.rectangle(source_image, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)

        result_image_path = 'result.png'
        cv2.imwrite(result_image_path, source_image)
        return merged_boxes

if __name__ == "__main__":
    bank = ImageRecognition('screenshot.png')
    bank.template_match('assets/bank_items.png')

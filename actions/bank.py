import time
import random
import sys
import os
from rich.console import Console
from rich.traceback import install
from typing import List, Tuple

# Import local modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import coordinates_utils, image_recognition_utils, hardware_inputs, constants
from simpy.library import io
from simpy.library.global_vals import *

install()
console = Console()

class Bank:
    def __init__(self):
        self.coordinates_utils = coordinates_utils.Coordinates()
        self.image_recognition_utils = image_recognition_utils.ImageRecognition()
        self.pin_entered = False

    def enter_pin(self) -> None:
        pin_matches = self.image_recognition_utils.template_match('assets/bank_pin_flag.png', threshold=0.8)
        if pin_matches:
            time.sleep(random.uniform(0.33, 0.89))
            with open("account_data.txt", "r") as f:
                pin = f.readlines()[3].strip()
            hardware_inputs.Write(pin)
            time.sleep(random.uniform(1, 2))
            self.pin_entered = True
        else:
            self.pin_entered = True
            console.log('NO PIN NEEDED')

    def set_quantity(self, quantity: int) -> None:
        if not self.open_bank():
            console.log("Failed to open bank")
            return

        quantity_mapping = {
            1: 'assets/quantity_1.png',
            5: 'assets/quantity_5.png',
            10: 'assets/quantity_10.png',
        }

        if quantity in quantity_mapping:
            asset = quantity_mapping[quantity]
        elif quantity >= 28:
            asset = 'assets/quantity_all.png'
        else:
            asset = 'assets/quantity_x.png'

        quantity_coords = self.get_coordinates(asset)
        if not quantity_coords:
            console.log(f"Failed to find quantity button for {quantity}")
            return

        if asset != 'assets/quantity_x.png':
            self.coordinates_utils.click_coordinates(quantity_coords[0])
        else:
            self.set_custom_quantity(quantity_coords[0], quantity)

    def set_custom_quantity(self, coords: Tuple[int, int], quantity: int) -> None:
        self.coordinates_utils.click_coordinates(coords, 'right')
        custom_quantity_coords = self.get_coordinates('assets/custom_quantity_text.png')
        if not custom_quantity_coords:
            console.log("Failed to find custom quantity input")
            return

        io.wind_mouse(custom_quantity_coords[0][0], custom_quantity_coords[0][1], speed=0.2)
        hardware_inputs.Click('left')
        time.sleep(random.uniform(0.5, 1))
        hardware_inputs.Write(str(quantity))
        hardware_inputs.PressButton('enter')

    def is_in_bank(self) -> bool:
        bank_item_coords = self.get_coordinates('assets/in_bank_flag.png')
        return bool(bank_item_coords)

    def open_bank(self) -> bool:
        bank_coords = self.coordinates_utils.find_color_coordinates(constants.COLORS["pink"])
        if len(bank_coords) > 0:
            self.coordinates_utils.click_coordinates(self.coordinates_utils.pick_random_coordinate(bank_coords))
            return True
        return False

    def bank_inventory(self) -> None:
        if not self.is_in_bank():
            if not self.open_bank():
                console.log("Failed to open bank")
                return
            if not self.pin_entered:
                self.enter_pin()

        bank_item_coords = self.get_coordinates('assets/bank_items.png')
        if bank_item_coords:
            self.coordinates_utils.click_coordinates(bank_item_coords[0])
        else:
            console.log('NO BANK ITEM COORDINATES')

    def take_item(self, template_path: str) -> bool:
        if not self.is_in_bank():
            console.log('NOT IN BANK')
            return True

        bank_roi = (*constants.RELATIVE_COORDS['bank'], *constants.ROI_SIZES['bank'])
        item_coords = self.get_coordinates(template_path, roi=bank_roi)
        if not item_coords:
            console.log(f"Failed to find item: {template_path}")
            return True

        self.coordinates_utils.click_coordinates(item_coords[0])
        time.sleep(random.uniform(0.5, 0.7))

        no_items_matches = self.get_coordinates('assets/choose.png', roi=bank_roi)
        if no_items_matches:
            console.log('ZERO ITEM QUANTITY')
            return True
        return False

    def get_coordinates(self, asset: str, roi: Tuple[int, int, int, int] = None, scaling_factor: float = 0.8) -> List[Tuple[int, int]]:
        return self.image_recognition_utils.generate_random_b_box_coord(
            self.image_recognition_utils.template_match(asset, threshold=0.8, roi=roi, scaling_factor=scaling_factor)
        )

if __name__ == "__main__":
    bank = Bank()
    bank.bank_inventory()
    bank.set_quantity(14)
    bank.take_item('assets/bow_string.png')
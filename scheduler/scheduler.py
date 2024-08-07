import time
import os
import sys
from typing import Callable, Optional
from datetime import datetime

# Add necessary directories to sys.path
sys.path.extend([
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..')),
    os.path.join(os.path.dirname(__file__), '..', 'actions')
])

from utils.break_utils import generate_botting_time
from actions.fishing import FishingBot  # Import the FishingBot class

class BotScheduler:
    def __init__(self, bot_class, status_file: str = 'script_status.txt'):
        self.bot_class = bot_class
        self.status_file = status_file
        self.script_failed = False

    def get_script_status(self) -> str:
        if not os.path.exists(self.status_file):
            return 'success'
        with open(self.status_file, 'r') as file:
            return file.read().strip()

    def run_bot_script(self) -> None:
        try:
            bot_instance = self.bot_class()
            bot_instance.fish()  # Assuming the main method is called 'fish'
        except Exception as e:
            print(f"An error occurred: {e}")
            self.script_failed = True

    def sleep_until_next_run(self, hours: int) -> None:
        next_start_time = generate_botting_time(hours)
        sleep_duration = max(0, next_start_time - time.time())
        
        if sleep_duration > 0:
            print(f"Scheduler sleeping until {datetime.fromtimestamp(next_start_time)}")
            print(f"Sleep duration: {sleep_duration / 60:.2f} minutes")
            time.sleep(sleep_duration)
        else:
            print("Generated start time is in the past. Starting immediately.")

    def run(self) -> None:
        while not self.script_failed:
            self.run_bot_script()
            
            if self.get_script_status() == 'failed':
                print("Script failed. Stopping the scheduler.")
                break
            
            self.sleep_until_next_run(1)  # Sleep for at least 1 hour

def main():
    scheduler = BotScheduler(FishingBot)
    scheduler.run()

if __name__ == "__main__":
    main()
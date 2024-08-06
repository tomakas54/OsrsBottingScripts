import time
import os
import sys

# Append the parent directory of the current file to the sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
actions_dir = os.path.join(os.path.dirname(__file__), '..', 'actions')
sys.path.append(actions_dir)

print("Current working directory:", os.getcwd())
print("Python path:", sys.path)
from utils.break_utils import generate_botting_time
from actions.stun_alch import stun_alch
from actions.fishing import fish

def get_script_status():
    if not os.path.exists('script_status.txt'):
        return 'success'
    with open('script_status.txt', 'r') as file:
        status = file.read().strip()
    return status

def run_bot_script():
    global script_failed
    try:
        #stun_alch('assets/curse.png', 'assets/fletch_lvl.png', 'assets/alch.png', 'assets/longbow_note.png')
        fish()
    except Exception as e:
        print(f"An error occurred: {e}")
        script_failed = True

def main():
    global script_failed
    script_failed = False
    
    while not script_failed:
        # Run the bot script
        run_bot_script()
        
        # Check script status
        script_status = get_script_status()
        if script_status == 'failed':
            print("Script failed. Stopping the scheduler.")
            break
        
        # Generate next start time
        next_start_time_epoch = generate_botting_time(1)  # Ensuring the bot waits at least 30 minutes
        print(next_start_time_epoch)
        
        # Calculate sleep duration
        sleep_duration = next_start_time_epoch - time.time()
        print(sleep_duration)
        if sleep_duration > 0:
            print(f"Scheduler sleeping for {sleep_duration / 60:.2f} minutes.")
            time.sleep(sleep_duration)
        else:
            print("Generated start time is in the past. Starting immediately.")

if __name__ == "__main__":
    main()

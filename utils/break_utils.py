import time
import random
def generate_botting_time(min_time):
    # Generate a random time to stop in seconds, ensuring it's between min_time hours and 6 hours (21600 seconds)
    stop_time_seconds = random.uniform(min_time * 3600, 21600)
    # Get the current time
    current_time_seconds = time.time()
    # Calculate the stop time in seconds since the epoch
    stop_time_epoch = current_time_seconds + stop_time_seconds
    # Convert the stop time to a readable format
    stop_time_readable = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(stop_time_epoch))
    print('BOTTING TILL: ' + stop_time_readable)
    return stop_time_epoch


def take_a_break(min_dur,max_dur):
    """Take a break for a random duration between 5 to 10 minutes."""
    break_duration = random.uniform(min_dur,max_dur)  # 5 to 10 minutes in seconds
    print(f"Taking a break for {break_duration / 60:.2f} minutes.")
    time.sleep(break_duration)
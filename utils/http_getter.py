import requests
import time
import json

def get_game_data(category):
    url = f"http://localhost:8080/{category}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check for HTTP errors
        
        data = response.json()
        
        return data
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None

def export_to_json(data, filename='live_data.json'):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)
    print(f"Data exported to {filename}")
if __name__ == "__main__":
    while True:
        export_to_json(get_game_data('objects'))
        export_to_json(get_game_data('events'),'live_data_events.json')
        time.sleep(0.5)

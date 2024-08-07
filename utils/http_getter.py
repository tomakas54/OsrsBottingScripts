import requests
import time

def get_game_data():
    url = "http://localhost:8080/inv"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check for HTTP errors
        
        data = response.json()
        
        return data
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None

def main():
    retry_count = 0
    max_retries = 5
    base_delay = 2  # base delay in seconds

    while True:
        game_data = get_game_data()
        if game_data:
            print("Game Data Retrieved Successfully:")
            print(game_data)
            #print(game_data['game tick'])
            #print(game_data['health'])
            #print(game_data['npc name'])
            retry_count = 0   #Reset retry count on success
        else:
            retry_count += 1
            if retry_count > max_retries:
                print("Max retries exceeded. Exiting.")
                break
            delay = base_delay * (2 ** (retry_count - 1))
            print(f"Failed to retrieve game data. Retrying in {delay} seconds.")
            time.sleep(delay)
            continue  # Skip the regular sleep

        time.sleep(0.6)

if __name__ == "__main__":
    main()

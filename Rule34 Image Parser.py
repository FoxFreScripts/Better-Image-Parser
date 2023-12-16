import os
import json
import threading
import httpx
from urllib.parse import urljoin
from art import text2art
from colorama import Fore, Style, init
import sys
import ssl
import time
from tqdm import tqdm
import shutil

# Define retry settings
retry_delay = 5  # seconds
max_retries = 3

# Ignore SSL certificate verification
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# Function to clear the console
def clear_console():
    # Clear the console for Windows, Linux, and macOS
    os.system('cls' if os.name == 'nt' else 'clear')

# Initialize colorama
init()

# Print a smaller cool text banner
banner_text = text2art("Image Parser", font='small')
print(banner_text)

# ANSI escape codes for yellowish-orange color
warning_color = Fore.YELLOW
error_color = Fore.RED
success_color = Fore.GREEN
reset_color = Style.RESET_ALL

# Request settings
websites = {
    "Rule34": {
        "endpoint_url": "https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&tags=%s&json=1&limit=%s&pid=%s",
        "headers": {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
        }
    },
    "ATFBooru": {
        "endpoint_url": "https://booru.allthefallen.moe/posts.json?tags=%s&limit=%s&page=%s",
        "headers": {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
            "api-key": "PAAvBsBYKHpXKBEyPBKwre4t"  # Replace with your ATFBooru API key
        }
    },
    "Danbooru": {
        "endpoint_url": "https://danbooru.donmai.us/posts.json?tags=%s&limit=%s&page=%s",
        "headers": {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",  # Replace with your user agent
            "api-key": "6EpZTiQdx9Cw95MdvJFYMMdP"  # Replace with your Danbooru API key
        }
    }
}

# Function to choose the website
def choose_website():
    total_downloads = [0]  # Add this line to initialize total_downloads

    while True:
        print(f"{success_color}Choose the website:{reset_color}")
        print("1. TEST")
        print(f"{error_color}2. TEST (Slower due to API usage){reset_color}")
        print("3. TEST (clean images)")
        choice = input("Enter the number of the website (or any other key to reset options): ")
        if choice == "1":
            return "Rule34"
        elif choice == "2":
            try:
                return "ATFBooru"
            except httpx.HTTPError as e:
                print(f"Error during request: {e}. Retrying...")
        elif choice == "3":
            return "Danbooru"
        else:
            print(f"{warning_color}Invalid choice. Resetting to the beginning.{reset_color}")
            restart_script(total_downloads)



# Function to handle Rule34 response
def handle_rule34_response(response, limit, save_folder, total_downloads):
    try:
        json_data = response.json()

        if not isinstance(json_data, list):
            print(f"Invalid response structure. Expected a list.")
            return

        relevant_posts = [post for post in json_data if 'file_url' in post]

        file_urls = [post['file_url'] for post in relevant_posts]

        if file_urls:
            if 'video' in tags:
                videos_folder = os.path.join(save_folder, 'videos')
                download_files_threaded(file_urls[:limit], videos_folder, limit, total_downloads)
            else:
                download_files_threaded(file_urls[:limit], save_folder, limit, total_downloads)
        else:
            restart_script(total_downloads)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {str(e)}")
        restart_script(total_downloads)

# Function to handle ATFBooru response
def handle_danbooru_response(response, limit, save_folder, total_downloads):
    try:
        json_data = response.json()

        if not isinstance(json_data, list):
            print(f"Invalid response structure. Expected a list.")
            return

        relevant_posts = [post for post in json_data if 'file_url' in post]

        file_urls = [post['file_url'] for post in relevant_posts]

        if file_urls:
            if 'video' in tags:
                videos_folder = os.path.join(save_folder, 'videos')
                download_files_threaded(file_urls[:limit], videos_folder, limit, total_downloads)
            else:
                download_files_threaded(file_urls[:limit], save_folder, limit, total_downloads)
        else:
            restart_script(total_downloads)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {str(e)}")
        restart_script(total_downloads)

def handle_atfbooru_response(response, limit, save_folder, total_downloads):
    try:
        json_data = response.json()

        if not isinstance(json_data, list):
            print(f"Invalid response structure. Expected a list.")
            return

        relevant_posts = [post for post in json_data if 'file_url' in post]

        file_urls = [post['file_url'] for post in relevant_posts]

        if file_urls:
            if 'video' in tags:
                videos_folder = os.path.join(save_folder, 'videos')
                download_files_threaded(file_urls[:limit], videos_folder, limit, total_downloads)
            else:
                download_files_threaded(file_urls[:limit], save_folder, limit, total_downloads)
        else:
            restart_script(total_downloads)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {str(e)}")
        restart_script(total_downloads)


# Function to create subfolders for tags
def create_tag_subfolders(tags):
    for tag in tags:
        tag_folder = os.path.join(os.getcwd(), 'PO_N', tag)
        if not os.path.exists(tag_folder):
            os.makedirs(tag_folder)

        # Check if 'video' is in tags
        if 'video' in tags:
            videos_folder = os.path.join(tag_folder, 'videos')
            if not os.path.exists(videos_folder):
                os.makedirs(videos_folder)



def download_files_threaded_atfbooru(url_list, save_folder, limit, total_downloads):
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    threads = []
    for url in url_list[:limit]:
        thread = threading.Thread(target=download_file, args=(url, save_folder, total_downloads))
        threads.append(thread)
        thread.start()

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

# Function to download files using multithreading
def download_files_threaded(url_list, save_folder, limit, total_downloads):
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    threads = []
    for url in url_list[:limit]:
        thread = threading.Thread(target=download_file, args=(url, save_folder, total_downloads))
        threads.append(thread)
        thread.start()

    # Wait for all threads to finish
    for thread in threads:
        thread.join()



# Function to download file with progress update
def download_file(url, save_folder, total_downloads):
    try:
        if isinstance(url, list):
            # If url is a list, take the first element
            url = url[0]

        file_name = url.split("/")[-1]

        # Create subfolders for tags
        create_tag_subfolders(tags)

        tag_folder = os.path.join(os.getcwd(), 'PO_N', tags[0])

        if 'video' in tags and file_name.lower().endswith(('.mp4', '.webm')):
            videos_folder = os.path.join(tag_folder, 'videos')
            if not os.path.exists(videos_folder):
                os.makedirs(videos_folder)
            file_path = os.path.join(videos_folder, file_name)
        else:
            file_path = os.path.join(tag_folder, file_name)

        if os.path.exists(file_path):
            return  # Skip download if the file already exists

        # Use tqdm to create a progress bar without additional messages
        with tqdm(total=100, desc=f"Downloading {file_name}", unit="%", leave=False, position=0, dynamic_ncols=True) as pbar:
            with httpx.stream("GET", url) as response:
                if response.status_code == 200:
                    total_size = int(response.headers.get('content-length', 1))
                    downloaded_size = 0

                    with open(file_path, 'wb') as file:
                        for chunk in response.iter_bytes():
                            file.write(chunk)
                            downloaded_size += len(chunk)
                            pbar.update(int(downloaded_size * 100 / total_size - pbar.n))

                    total_downloads[0] += 1
                else:
                    print(f"Failed to download file: {file_name}. Status code: {response.status_code}")

    except Exception as e:
        print(f"Error downloading file: {str(e)}")




# Function to download files using multithreading
def download_files_threaded(url_list, save_folder, limit, total_downloads):
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    threads = []
    for url in url_list[:limit]:
        thread = threading.Thread(target=download_file, args=(url, save_folder, total_downloads))
        threads.append(thread)
        thread.start()

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

# Function to restart the script
def restart_script(total_downloads=None, desired_amount=None):
    if total_downloads is not None and desired_amount is not None and total_downloads[0] >= desired_amount:
        print("\nDone downloading!")
        sys.exit()
    else:
        # Print a message before restarting the script
        print("\nRestarting the script...\n")
        time.sleep(3)

        # Restart the script on Windows
        if os.name == 'nt':
            clear_console()
            os.system('cls' if os.name == 'nt' else 'clear')
            os.system('python "{}"'.format(__file__))
        else:
            # Restart on non-Windows systems
            os.execl(sys.executable, sys.executable, *sys.argv)




# Print warnings with yellowish-orange color
print(f"{error_color}I am a menace to society :3{reset_color}")
print(f"\n{warning_color}WARNING: Please be cautious with the number of files you choose to download.{reset_color}")
print(f"{warning_color}This script downloads files very quickly. To stop downloading, simply close the console.{reset_color}")

# Prompt the user to choose the website
selected_website = choose_website()

# Read tags from tags.json
with open('tags.json', 'r') as tags_file:
    tags_data = json.load(tags_file)
    tags = tags_data.get(selected_website, [])


# Create subfolders for tags
create_tag_subfolders(tags)


# Create a folder for each tag within the 'PO_N' folder
for tag in tags:
    tag_folder = os.path.join(os.getcwd(), 'PO_N', tag)
    if not os.path.exists(tag_folder):
        os.makedirs(tag_folder)

    # Check if 'video' is in the tags
    if 'video' in tags:
        videos_folder = os.path.join(tag_folder, 'videos')
        if not os.path.exists(videos_folder):
            os.makedirs(videos_folder)

# Create a string with all the tags with either "+" or "-" for the selected website
formatted_tags = "".join("+" + i for i in tags)

order_preference = input("Do you want to download files randomly or in sequence? (yes/no): ").lower()
random_order = order_preference == 'yes'
order_message = "randomly" if random_order else "sequentially"
print(f"Downloading files {order_message}...")

# Define the limit variable
while True:
    limit_input = input("Enter the number of files to download: ")
    if limit_input.isdigit():
        limit = int(limit_input)
        break
    else:
        print(f"{Fore.RED}Invalid input. Please enter a valid number.{Style.RESET_ALL}")

# Fetch more file links using the selected website's endpoint URL and formatted tags
website_settings = websites[selected_website]

# Define an HTTPX client with an adapter that ignores SSL verification and increase timeout
client = httpx.Client(http2=True, verify=False, timeout=120)  # Adjust the timeout value as needed (in seconds)

# Fetching files from ATFBooru might take some time
if selected_website == "ATFBooru":
    print(f"{warning_color}Fetching files might take some time. Please be patient.{reset_color}")

offset = 0
total_downloads = [0]
while total_downloads[0] < limit:
    retries = 0

    while retries < max_retries:
        try:
            response = client.get(website_settings["endpoint_url"] % (formatted_tags, limit, offset), headers=website_settings["headers"])
            if response.status_code == 200:
                # Handle the response based on the selected website
                if selected_website == "Rule34":
                    handle_rule34_response(response, limit, os.path.join(os.getcwd(), 'PO_N', tags[0]), total_downloads)
                elif selected_website == "ATFBooru":
                    handle_atfbooru_response(response, limit, os.path.join(os.getcwd(), 'PO_N', tags[0]), total_downloads)
                elif selected_website == "Danbooru":
                    handle_danbooru_response(response, limit, os.path.join(os.getcwd(), 'PO_N', tags[0]), total_downloads)
                break  # Break out of the loop if successful
            else:
                print(f"Failed to fetch data. Status code: {response.status_code}. Retrying...")
                retries += 1
        except Exception as e:
            print(f"Error during request: {str(e)}. Retrying...")
            retries += 1
            time.sleep(retry_delay)

    # Increment offset for the next batch of files
    offset += limit

# Close the HTTPX client
client.close()

# Restart the script
restart_script(total_downloads)

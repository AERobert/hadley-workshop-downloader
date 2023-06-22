import os
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
from downloader_parser import create_parser
from mp4_to_mp3 import convert_mp4_to_mp3  

# Create argument parser
parser = create_parser()
args = parser.parse_args()

# Fetch the HTML content of the webpage
url = args.url
try:
    response = requests.get(url)
    response.raise_for_status()
except requests.RequestException as e:
    print(f"Error fetching the webpage: {e}")
    exit(1)

html_content = response.text

# Parse HTML and find the video URL
soup = BeautifulSoup(html_content, 'html.parser')
video_container = soup.find('div', class_='workshop')

if video_container is None:
    print("No video container found")
    exit(1)

video_element = video_container.find('video')

if video_element is None:
    print("No video element found")
    exit(1)

source_element = video_element.find('source')

if not source_element:
    print("No source element found.")
    exit(1)

video_url = source_element.get('src')

if not video_url:
    print("No video URL found")
    exit(1)

# Determine the output file name
if args.output:
    output_file = args.output
else:
    output_file = os.path.basename(urlparse(video_url).path)

# Download the video
try:
    video_response = requests.get(video_url, stream=True)
    video_response.raise_for_status()
except requests.RequestException as e:
    print(f"Error fetching the video: {e}")
    exit(1)

with open(output_file, 'wb') as f:
    for chunk in video_response.iter_content(chunk_size=8192):
        f.write(chunk)

print(f"Video downloaded successfully as {output_file}")

# Convert to MP3 if the -a flag is set
if args.audio:
    convert_mp4_to_mp3(output_file)

import os
import argparse
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
from downloader_parser import parse_arguments
from mp4_to_mp3 import convert_mp4_to_mp3


def extract_video_link(url):
    """Finds the video source url from the specified webpage"""
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

    return video_url


def determine_output_file_name(video_url, output_arg):
    if output_arg:
        return output_arg
    else:
        return os.path.basename(urlparse(video_url).path)


def download_mp4_from_url(video_url, output_file):
    """Downloads video from the given URL to the specified output file"""
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


def convert_to_mp3_if_needed(output_file, audio_flag):
    if audio_flag:
        convert_mp4_to_mp3(output_file)


if __name__ == "__main__":
    # Parse command line arguments
    args = parse_arguments()

    # Loop through each URL and download/convert the video
    for i, url in enumerate(args.url):
        # Extract video link
        video_url = extract_video_link(url)

        # Determine output file name
        output_file = determine_output_file_name(video_url, args.output[i] if args.output else None)

        # Download MP4 from URL
        download_mp4_from_url(video_url, output_file)

        # Convert to MP3 if needed
        convert_to_mp3_if_needed(output_file, args.audio)

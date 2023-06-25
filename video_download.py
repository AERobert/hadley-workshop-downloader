import os
import subprocess
from pathlib import Path
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from downloader_parser import parse_arguments


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


def get_workshop_series_urls(url):
    """
    Retrieves a list of URLs leading to the pages for each workshop in a series.

    Args:
        url (str): The URL of the webpage containing the workshop information.

    Returns:
        list: A list of URLs for each workshop in the series.

    Raises:
        requests.exceptions.RequestException: If an error occurs while making the HTTP request.
        ValueError: If the specified URL is invalid or the required elements are not found.
    """
    parsed_url = urlparse(url)
    try:
        # Make an HTTP GET request to the specified URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for any HTTP errors

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the div with the id "block-workshops"
        workshop_div = soup.find('div', id='block-workshops')
        if workshop_div is None:
            raise ValueError('Could not find the workshop div with id "block-workshops"')

        # Find all h3 elements within the workshop div
        h3_elements = workshop_div.find_all('h3')

        # Extract the href attribute from each <a> element and store it in a list
        workshop_urls = []
        for h3_element in h3_elements:
            anchor_element = h3_element.find('a')
            if anchor_element is not None and 'href' in anchor_element.attrs:
                full_url = f"{parsed_url.scheme}://{parsed_url.netloc}{anchor_element['href']}"
                workshop_urls.append(full_url)

        return workshop_urls

    except requests.exceptions.RequestException as e:
        # Handle any network-related errors
        raise e

    except Exception as e:
        # Handle any other exceptions, including BeautifulSoup parsing errors
        raise ValueError(f'An error occurred: {str(e)}')


def determine_output_file_name(video_url, output_arg, directory=None):
    """
    Determines the output file name based on the video URL and --output argument.
    If --directory argument is provided, it prefixes the directory to the file name.
    """
    file_name = output_arg if output_arg else Path(urlparse(video_url).path).name
    if directory:
        directory_path = Path(directory)
        directory_path.mkdir(parents=True, exist_ok=True)
        return str(directory_path / file_name)
    else:
        return str(Path(file_name))


def download_mp4_from_url(video_url, output_file, show_progress_bar=False):
    """Downloads video from the given URL to the specified output file"""
    try:
        video_response = requests.get(video_url, stream=True)
        video_response.raise_for_status()
        total_size = int(video_response.headers.get('content-length', 0))
    except requests.RequestException as e:
        print(f"Error fetching the video: {e}")
        exit(1)

    # Progress bar setup
    if show_progress_bar:
        progress_bar = tqdm(total=total_size, unit='iB', unit_scale=True)

    with open(output_file, 'wb') as f:
        for chunk in video_response.iter_content(chunk_size=8192):
            f.write(chunk)
            if show_progress_bar:
                progress_bar.update(len(chunk))

    if show_progress_bar:
        progress_bar.close()

    print(f"Video downloaded successfully as {output_file}")


from pathlib import Path
import subprocess

def convert_mp4_to_mp3(input_file, output_dir=None, delete=True):
    """
    Convert an MP4 file to MP3 format using ffmpeg.

    Parameters:
    - input_file: str
        Path to the input .mp4 file to be converted.
    - output_dir: str, optional
        Directory where the converted .mp3 file should be saved.
        If None, the current working directory will be used.
    - delete: bool, optional
        If True, deletes the original .mp4 file after successful conversion.
        Default is True.

    Returns:
    - None

    Raises:
    - FileNotFoundError: If the input_file does not exist.
    - ValueError: If the input_file is not a .mp4 file.
    - Exception: For any other unexpected errors.
    """

    # Check if the input file exists
    input_file_path = Path(input_file)
    if not input_file_path.exists():
        raise FileNotFoundError(f"The input file '{input_file}' does not exist.")

    # Check if the input file is a .mp4 file
    if not input_file_path.suffix.lower() == '.mp4':
        raise ValueError("The input file must be a .mp4 file.")

    # If output_dir is None, set it to the current working directory
    if output_dir is None:
        output_dir = Path.cwd()
    else:
        output_dir = Path(output_dir)
        # Create output directory if not exists
        output_dir.mkdir(parents=True, exist_ok=True)

    # Prepare output file path
    output_file = output_dir / (input_file_path.stem + '.mp3')

    # Run ffmpeg to convert .mp4 to .mp3
    try:
        subprocess.run(['ffmpeg', '-hide_banner', '-y', '-i', str(input_file_path), '-vn', '-acodec', 'libmp3lame', '-ac', '2', '-ab', '160k', '-ar', '48000', str(output_file)], check=True)
    except subprocess.CalledProcessError as e:
        raise Exception("Error while converting file using ffmpeg.") from e

    # Delete the original file if delete parameter is True
    if delete:
        try:
            input_file_path.unlink()
        except OSError as e:
            raise Exception("Error while deleting the original file.") from e


def convert_to_mp3_if_needed(output_file, audio_flag, output_directory):
    if audio_flag:
        convert_mp4_to_mp3(output_file, output_dir=output_directory)


if __name__ == "__main__":
    # Parse command line arguments
    args = parse_arguments()


    # Loop through each series URL
    for series_url in args.series:
        # Get workshop URLs from series
        workshop_urls = get_workshop_series_urls(series_url)
        # Loop through each workshop URL and download/convert
        for workshop_url in workshop_urls:
            # Extract video link
            video_url = extract_video_link(workshop_url)
            # Determine output file name
            output_file = determine_output_file_name(video_url, None, directory=args.directory)
            # Download MP4 from URL
            download_mp4_from_url(video_url, output_file, show_progress_bar=args.progress_bar)
            # Convert to MP3 if needed
            convert_to_mp3_if_needed(output_file, args.audio, args.directory)

    for i, url in enumerate(args.url):
        # Extract video link
        video_url = extract_video_link(url)

        # Determine output file name
        output_file = determine_output_file_name(video_url, args.output[i] if args.output else None, directory=args.directory)

        # Download MP4 from URL
        download_mp4_from_url(video_url, output_file, show_progress_bar=args.progress_bar)

        # Convert to MP3 if needed
        convert_to_mp3_if_needed(output_file, args.audio, args.directory)

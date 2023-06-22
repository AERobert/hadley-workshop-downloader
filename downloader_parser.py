import argparse
from urllib.parse import urlparse

def create_parser():
    """Create an argument parser for the video downloader script."""
    
    parser = argparse.ArgumentParser(description="Download video from a webpage and optionally convert it to MP3.")
    
    # URL argument
    parser.add_argument(
        '-u', '--url',
        type=str,
        required=True,
        help="URL of the webpage containing the video to be downloaded."
    )
    
    # Output file name argument
    parser.add_argument(
        '-o', '--output',
        type=str,
        default=None,
        help="Desired name for the downloaded video file. If not specified, the source link's basename will be used."
    )
    
    # Convert to MP3 flag
    parser.add_argument(
        '-a', '--audio',
        action='store_true',
        help="If set, convert the downloaded MP4 file to MP3 audio."
    )
    
    return parser

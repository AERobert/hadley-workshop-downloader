import argparse

def create_parser():
    """Create an argument parser for the video downloader script."""
    
    parser = argparse.ArgumentParser(description="Download video from a webpage and optionally convert it to MP3.")
    
    # URL argument
    parser.add_argument(
        '-u', '--url',
        type=str,
        required=True,
        help="URL(s) of the webpage containing the video to be downloaded.",
        nargs='+'
    )
    
    # Output file name argument
    parser.add_argument(
        '-o', '--output',
        type=str,
        default=None,
        help="Desired name for the downloaded video file. If not specified, the source link's basename will be used.",
        nargs='*'
    )
    
    # Convert to MP3 flag
    parser.add_argument(
        '-a', '--audio',
        action='store_true',
        help="If set, convert the downloaded MP4 file to MP3 audio."
    )
    
    return parser

def parse_arguments():
    """Parse command line arguments and perform basic validation."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Basic validation
    if args.output and len(args.url) < len(args.output):
        parser.error("The number of specified output file names exceeds the number of input URLs provided.")
    
    return args

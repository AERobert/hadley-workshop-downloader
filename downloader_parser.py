import argparse

def create_parser():
    """Create an argument parser for the video downloader script."""
    
    parser = argparse.ArgumentParser(description="Download video from a webpage and optionally convert it to MP3.")
    
    # URL argument
    parser.add_argument(
        '-u', '--url',
        type=str,
        default=[],
        help="URL(s) of the webpage containing the video to be downloaded.",
        nargs='+'
    )
    
    # Add series option
    parser.add_argument(
        '-s', '--series',
        type=str,
        default=[],
        help="URL(s) of the webpages containing a series of videos to be downloaded.",
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
    
    # Add --directory argument
    parser.add_argument(
        '-d', '--directory',
        type=str,
        help="Specify the directory where the output files will be saved.",
        required=False
    )
    
    # Convert to MP3 flag
    parser.add_argument(
        '-a', '--audio',
        action='store_true',
        help="If set, convert the downloaded MP4 file to MP3 audio."
    )
    
    # progress bar flag
    parser.add_argument(
        '-p', '--progress-bar',
        action='store_true',
        help="If set, show a progress bar during video download."
    )
    
    return parser

def parse_arguments():
    """Parse command line arguments and perform basic validation."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Basic validation
    
    if not args.url and not args.series:
        parser.error("You must provide at least one of --url or --series.")
    
    if args.url and args.output and len(args.url) < len(args.output):
        parser.error("The number of specified output file names exceeds the number of input URLs provided.")
    
    return args

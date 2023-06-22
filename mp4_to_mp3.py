import os
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
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"The input file '{input_file}' does not exist.")

    # Check if the input file is a .mp4 file
    if not input_file.lower().endswith('.mp4'):
        raise ValueError("The input file must be a .mp4 file.")

    # If output_dir is None, set it to the current working directory
    if output_dir is None:
        output_dir = os.getcwd()
    # Create output directory if not exists
    elif not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Prepare output file path
    output_file = os.path.join(output_dir, os.path.splitext(os.path.basename(input_file))[0] + '.mp3')

    # Run ffmpeg to convert .mp4 to .mp3
    try:
        subprocess.run(['ffmpeg', '-hide_banner', '-y', '-i', input_file, '-vn', '-acodec', 'libmp3lame', '-ac', '2', '-ab', '160k', '-ar', '48000', output_file], check=True)
    except subprocess.CalledProcessError as e:
        raise Exception("Error while converting file using ffmpeg.") from e

    # Delete the original file if delete parameter is True
    if delete:
        try:
            os.remove(input_file)
        except OSError as e:
            raise Exception("Error while deleting the original file.") from e

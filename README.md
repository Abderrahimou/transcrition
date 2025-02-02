# YouTube Video Transcriber using Wit.ai

This project is a Python-based tool that transcribes the audio from a YouTube video using the Wit.ai speech recognition API.

## Features

- Fetches the audio from a YouTube video.
- Sends the audio to Wit.ai for transcription.
- Displays the transcribed text output.

## Requirements

Before running the script, you need to install the following Python packages:

- `youtube-dl` or `yt-dlp` (to download YouTube videos)
- `requests` (to interact with the Wit.ai API)
- `ffmpeg` (for audio extraction)

You can install them using `pip`:

```bash
pip install youtube-dl requests ffmpeg-python

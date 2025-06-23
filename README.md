# WorkTimeTracker

This project downloads noise videos from YouTube, converts them into short seamless loops and plays them continuously. It can be useful for creating background ambience during work or study sessions.

## Requirements

Install dependencies from `requirements.txt`:

```bash
pip install -r requirements.txt
```

`ffmpeg` is also required and should be available in your `PATH`.

## Usage

Adjust `pipeline_config.yaml` to set the list of YouTube URLs and output file names. Then run:

```bash
python main.py
```

The script will download audio, prepare a loop for each target and start playback.

Press `Ctrl+C` to stop playback.

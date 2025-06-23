from pathlib import Path
from yt_dlp import YoutubeDL


def download(url: str, dst: Path) -> None:
    """Download audio from YouTube into the given file."""
    dst = Path(dst)
    opts = {
        "format": "bestaudio/best",
        "outtmpl": str(dst),
        "quiet": True,
        "noplaylist": True,
    }
    with YoutubeDL(opts) as ydl:
        ydl.download([url])

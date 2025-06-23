#!/usr/bin/env python3
"""
make_loopable.py  —  готовит аудиофайл к бесшовному повтору.

❱❱  python make_loopable.py input.mp3 \
        --output pink_noise_loop.ogg \
        --start-trim 120   --end-trim 120 \
        --crossfade 2000   --format ogg
"""

import argparse
from pathlib import Path

from pydub import AudioSegment   # pip install pydub
# pydub использует FFmpeg. Убедись, что ffmpeg в PATH.

def make_loopable(
    src: Path,
    dst: Path,
    start_trim: float = 120.0,
    end_trim: float = 120.0,
    crossfade_ms: int = 2000,
    out_format: str = "ogg",
    bitrate: str | None = None,
) -> None:
    """Обрезает шум и кросс-фейдит конец с началом."""
    audio = AudioSegment.from_file(src)

    trimmed = audio[start_trim * 1000 : len(audio) - end_trim * 1000]

    # Делаем «копия + crossfade» и оставляем только первую половину
    loopable = trimmed.append(trimmed, crossfade=crossfade_ms)[: len(trimmed)]

    export_kwargs = {}
    if bitrate:
        export_kwargs["bitrate"] = bitrate

    loopable.export(dst, format=out_format, **export_kwargs)
    print(f"✅  Exported loopable file → {dst}  ({out_format})")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prepare seamless loop from long noise file")
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", "-o", type=Path)
    parser.add_argument("--start-trim", type=float, default=120.0, metavar="SEC",
                        help="Сколько секунд отрезать от начала (default: 120)")
    parser.add_argument("--end-trim", type=float, default=120.0, metavar="SEC",
                        help="Сколько секунд отрезать от конца (default: 120)")
    parser.add_argument("--crossfade", type=int, default=2000, metavar="MS",
                        help="Длина кросс-фейда в мс (default: 2000)")
    parser.add_argument("--format", default="ogg", choices=["ogg", "mp3", "wav", "flac"],
                        help="Формат вывода (default: ogg)")
    parser.add_argument("--bitrate", default=None,
                        help="Битрейт для сжатых форматов, напр. '192k'")

    args = parser.parse_args()
    output_path = args.output or args.input.with_stem(args.input.stem + "_loop").with_suffix("." + args.format)

    make_loopable(
        src=args.input,
        dst=output_path,
        start_trim=args.start_trim,
        end_trim=args.end_trim,
        crossfade_ms=args.crossfade,
        out_format=args.format,
        bitrate=args.bitrate,
    )

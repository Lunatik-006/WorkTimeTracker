#!/usr/bin/env python3
# prepare_loop.py
"""
Конвертирует длинный WEBM → WAV (lossless), обрезает «хвосты», делает
cross-fade и сохраняет короткий loop-ready файл (OGG/FLAC/WAV/MP3).

❱  python prepare_loop.py big_noise.webm \
        --output pink_noise_loop.ogg \
        --loop-length 30          # длительность готового лупа, cек
        --start-trim 120 --end-trim 120  # убрать начало/конец
        --crossfade 2000          # cross-fade, мс
        --format ogg              # ogg|flac|wav|mp3
"""

import argparse, subprocess, tempfile
from pathlib import Path
from pydub import AudioSegment   # pip install pydub

FFMPEG = "ffmpeg"                # ffmpeg должен быть в PATH

def webm_to_wav(src: Path) -> Path:
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    subprocess.run(
        [FFMPEG, "-y", "-i", str(src), "-c:a", "pcm_s16le", "-ar", "48000", tmp.name],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return Path(tmp.name)

def make_loop(audio: AudioSegment, loop_len: int, crossfade_ms: int) -> AudioSegment:
    # нарезаем нужный кусок
    if len(audio) > loop_len * 1000:
        start = (len(audio) - loop_len * 1000) // 2
        audio = audio[start : start + loop_len * 1000]

    # дублируем + cross-fade → отрезаем до loop_len
    loop = audio.append(audio, crossfade=crossfade_ms)[: len(audio)]
    return loop

if __name__ == "__main__":
    ap = argparse.ArgumentParser("prepare_loop")
    ap.add_argument("input", type=Path)
    ap.add_argument("--output", "-o", type=Path)
    ap.add_argument("--loop-length", type=int, default=30, help="секунд")
    ap.add_argument("--start-trim", type=float, default=120)
    ap.add_argument("--end-trim", type=float, default=120)
    ap.add_argument("--crossfade", type=int, default=2000, metavar="MS")
    ap.add_argument("--format", default="ogg", choices=["ogg", "flac", "wav", "mp3"])
    ap.add_argument("--bitrate", default=None, help="например 192k для mp3/ogg")
    args = ap.parse_args()

    src = args.input
    if src.suffix.lower() == ".webm":
        src = webm_to_wav(src)

    audio = AudioSegment.from_file(src)
    trimmed = audio[args.start_trim*1000 : len(audio)-args.end_trim*1000]

    loop = make_loop(trimmed, args.loop_length, args.crossfade)

    out = args.output or args.input.with_stem(args.input.stem+"_loop").with_suffix("."+args.format)
    export_kw = {"format": args.format}
    if args.bitrate: export_kw["bitrate"] = args.bitrate
    loop.export(out, **export_kw)
    print("✅  Loop saved →", out)

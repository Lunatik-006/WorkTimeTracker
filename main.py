#!/usr/bin/env python3
# main.py
"""
Полный цикл: YouTube → loop-ready ogg → бесшовное воспроизведение.
Настройки задаются в CONFIG (ниже) или в external_config.py / config.yaml.
"""

# ──────────────────────────────────────────────────────────
# ░░ 1. КОНФИГ ЧЕРЕЗ YAML  ░░
# ──────────────────────────────────────────────────────────
import yaml
from pathlib import Path

yaml_path = Path(__file__).with_name("pipeline_config.yaml")
if not yaml_path.exists():
    raise FileNotFoundError("pipeline_config.yaml not found")

with open(yaml_path, "r", encoding="utf-8") as f:
    CFG_YAML = yaml.safe_load(f)

COMMON = CFG_YAML["common"]
TARGETS = CFG_YAML["targets"]
# ──────────────────────────────────────────────────────────
# ░░ 2. ИМПОРТ ЛОКАЛЬНЫХ МОДУЛЕЙ  ░░
# ──────────────────────────────────────────────────────────
sys.path.append(str(Path(__file__).parent))   # чтобы импортировать соседние скрипты

from download_audio import download
from prepare_loop import webm_to_wav, make_loop   # функции взяты из скрипта № 1
from prepare_loop import AudioSegment             # pydub
from play_loop import play_loop

# ──────────────────────────────────────────────────────────
# ░░ 3. PIPELINE  ░░
# ──────────────────────────────────────────────────────────
def run_pipeline(cfg):
    url          = cfg["youtube_url"]
    raw_path     = cfg["raw_file"]
    loop_path    = cfg["loop_file"]

    # 1) DOWNLOAD --------------------------------------------------------------
    if not raw_path.exists():
        print("⬇️  Downloading audio …")
        download(url, raw_path)
    else:
        print("📂  Using cached", raw_path)

    # 2) PREPARE LOOP ----------------------------------------------------------
    print("🎛  Preparing loop …")
    # webm → wav
    wav_path = webm_to_wav(raw_path)
    audio    = AudioSegment.from_file(wav_path)

    p = cfg["prepare"]
    trimmed = audio[p["start_trim"]*1000 : len(audio)-p["end_trim"]*1000]
    loop    = make_loop(trimmed, p["loop_length"], p["crossfade"])

    export_kw = {"format": p["format"]}
    if p["bitrate"]: export_kw["bitrate"] = p["bitrate"]
    loop.export(loop_path, **export_kw)
    print("✅  Loop ready →", loop_path)

    # 3) PLAY LOOP -------------------------------------------------------------
    print("▶️  Starting playback … (Ctrl-C to stop)")
    play_loop(str(loop_path), cfg["play"]["volume"])

# ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    try:
        for target in TARGETS:
            cfg = {
                "youtube_url": target["youtube_url"],
                "raw_file":    Path(target["raw_file"]),
                "loop_file":   Path(target["loop_file"]),
                "prepare": {
                    "loop_length": COMMON["loop_length"],
                    "start_trim":  COMMON["start_trim"],
                    "end_trim":    COMMON["end_trim"],
                    "crossfade":   COMMON["crossfade"],
                    "format":      COMMON["format"],
                    "bitrate":     COMMON["bitrate"],
                },
                "play": {
                    "volume":      COMMON["volume"],
                },
            }
            run_pipeline(cfg)
    except KeyboardInterrupt:
        print("\n🛑  Stopped by user.")

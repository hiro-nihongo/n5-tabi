# -*- coding: utf-8 -*-
"""
audio/ 内の .wav を配布用の軽い .mp3 に一括変換するスクリプト
(教材は .mp3 を優先して読みます。1語あたり約10〜15KBになります)

必要なもの: ffmpeg (https://ffmpeg.org/ / Macは brew install ffmpeg / Winは公式サイト)
使い方:     python convert_mp3.py
"""
import pathlib
import shutil
import subprocess
import sys

SRC = pathlib.Path("audio")

if shutil.which("ffmpeg") is None:
    sys.exit("ffmpeg が見つかりません。インストールしてから再実行してください。")
if not SRC.exists():
    sys.exit("audio/ フォルダがありません。先に voicevox_generate.py を実行してください。")

wavs = sorted(SRC.glob("*.wav"))
if not wavs:
    sys.exit("audio/ に .wav がありません。")

total = 0
for wav in wavs:
    mp3 = wav.with_suffix(".mp3")
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav),
         "-ac", "1", "-b:a", "64k", str(mp3)],
        check=True,
    )
    total += mp3.stat().st_size
    print(f"OK  {mp3.name}  ({mp3.stat().st_size//1024} KB)")

print(f"\n完了: {len(wavs)}ファイル / 合計 {total/1024/1024:.2f} MB")
print("mp3ができたら .wav は削除して構いません(配布サイズ削減のため推奨)。")

# -*- coding: utf-8 -*-
"""
VOICEPEAK 一括音声生成スクリプト(Mac用 / Unit 0 + Unit 1)
==========================================================
使い方:
  1. このファイルを n5-tabi フォルダに入れる
  2. ターミナルで cd で n5-tabi フォルダに入る(READMEのSTEP 1と同じ)
  3. まず自分のナレーター名を確認:
       /Applications/voicepeak.app/Contents/MacOS/voicepeak --list-narrator
  4. 下の NARRATOR = "..." を表示された名前に書き換える(このファイルを
     テキストエディタで開いて書き換えて保存)
  5. 実行:
       python3 voicepeak_generate.py
  6. audio/ に u0_00.wav 〜 u1_69.wav ができる → python3 convert_mp3.py

注意:
  - VOICEPEAKのコマンドラインは同時に1つしか動かせないため、1語ずつ順番に
    生成します。110語で10〜20分ほどかかりますが放置でOKです。
  - 途中で止めても大丈夫。再実行すると「まだ無いファイルだけ」作ります。
  - アクセントが違う語は、VOICEPEAKの「辞書」に読みとアクセントを登録して
    から、そのwavを削除して再実行してください(辞書が効いた音で作り直されます)。
"""

import os
import pathlib
import subprocess
import sys
import time

# VOICEPEAKは文字コード変換の初期化にロケール設定が必要。
# 未設定だと iconv_open is not supported で落ちるため、ここで必ず設定する。
os.environ.setdefault("LANG", "ja_JP.UTF-8")
os.environ["LANG"] = "ja_JP.UTF-8"
os.environ["LC_ALL"] = "ja_JP.UTF-8"

# ===== 設定(ここだけ自分の環境に合わせる)=====
VOICEPEAK = "/Applications/voicepeak.app/Contents/MacOS/voicepeak"
NARRATOR = "Japanese Male Child"   # ← --list-narrator で出た名前に書き換える
SPEED = "60"                     # 50〜200(100が標準。学習用に少しゆっくり)

OUT_DIR = pathlib.Path("audio")

# ---- Unit 0: カタカナ語ブースト(HTMLのWORDS配列と同じ順番であること!) ----
UNIT0 = [
    "コーヒー", "テレビ", "ホテル", "タクシー", "コンビニ", "パソコン",
    "レストラン", "カメラ", "バス", "エレベーター", "デパート", "スーパー",
    "プール", "パン", "ジュース", "ペン", "ノート", "ボールペン",
    "スプーン", "フォーク", "ナイフ", "コップ", "シャツ", "ネクタイ",
    "スカート", "ズボン", "コート", "テスト", "クラス", "プレゼント",
    "パーティー", "ギター", "スポーツ", "ドア", "テーブル", "ベッド",
    "トイレ", "アパート", "ラジオ", "ニュース",
]

# ---- Unit 1: すうじとじかん(HTMLのWORDS配列と同じ順番であること!) ----
UNIT1 = [
    "ゼロ", "いち", "に", "さん", "よん", "ご", "ろく", "なな", "はち", "きゅう",
    "じゅう", "ひゃく", "せん", "いちまん", "えん", "ばんごう",
    "いちじ、にじ、さんじ", "ごふん、じゅっぷん", "はん", "じかん",
    "ごぜん", "ごご", "あさ", "ひる", "よる", "ばん", "ゆうがた", "いま",
    "まいにち", "まいあさ", "まいばん", "なんじ", "いつ",
    "にちようび", "げつようび", "かようび", "すいようび", "もくようび",
    "きんようび", "どようび", "ようび", "しゅうまつ",
    "いちがつ", "にがつ", "さんがつ", "しがつ", "ごがつ", "ろくがつ",
    "しちがつ", "はちがつ", "くがつ", "じゅうがつ", "じゅういちがつ", "じゅうにがつ",
    "きょう", "あした", "きのう", "おととい", "あさって",
    "こんしゅう", "らいしゅう", "せんしゅう", "こんげつ", "らいげつ", "せんげつ",
    "ことし", "らいねん", "きょねん", "たんじょうび", "カレンダー",
]

# 生成後に必ず耳でアクセント確認してほしい語
ACCENT_CHECK = [
    "コーヒー", "エレベーター", "パーティー", "ノート", "スーパー",
    "いちじ、にじ、さんじ", "ごふん、じゅっぷん", "しがつ", "しちがつ", "くがつ",
    "きのう", "あした", "きょう", "ことし", "きょねん", "おととい", "あさって",
]


def synthesize(text: str, out_path: pathlib.Path) -> None:
    """VOICEPEAKのコマンドラインで1語を合成してwav保存する。"""
    subprocess.run(
        [VOICEPEAK,
         "-s", text,
         "-n", NARRATOR,
         "-o", str(out_path),
         "--speed", SPEED],
        check=True,
        capture_output=True,
        timeout=120,
        env=os.environ,   # LANGを設定した環境をVOICEPEAKに渡す
    )


def run(unit_name: str, words: list) -> None:
    for i, text in enumerate(words):
        out = OUT_DIR / f"{unit_name}_{i:02d}.wav"
        if out.exists():
            print(f"SKIP {out.name}  {text} (作成済み)", flush=True)
            continue
        try:
            synthesize(text, out)
            flag = "  ← ★要アクセント確認" if text in ACCENT_CHECK else ""
            print(f"OK  {out.name}  {text}{flag}", flush=True)
        except subprocess.TimeoutExpired:
            print(f"NG  {out.name}  {text}  (時間切れ。VOICEPEAKが応答しません)", flush=True)
        except subprocess.CalledProcessError as e:
            msg = (e.stderr or b"").decode("utf-8", "ignore")[:120]
            print(f"NG  {out.name}  {text}  ({msg})", flush=True)
        except Exception as e:
            print(f"NG  {out.name}  {text}  ({e})", flush=True)
        time.sleep(0.5)  # 同時実行1つ制限があるため少し待つ


if __name__ == "__main__":
    if not pathlib.Path(VOICEPEAK).exists():
        sys.exit(
            "VOICEPEAKが見つかりません。\n"
            "アプリの場所が違う場合は、このファイル冒頭の VOICEPEAK = の行を修正してください。"
        )
    OUT_DIR.mkdir(exist_ok=True)
    print("音声生成をはじめます(最初の1語が出るまで少し待ってください)…", flush=True)
    print(f"ナレーター: {NARRATOR} / 速度: {SPEED}", flush=True)
    print("=== 動作テスト(1語) ===", flush=True)
    try:
        synthesize("こんにちは", OUT_DIR / "_test.wav")
        print("テストOK。VOICEPEAKは正常に動いています。本番を開始します。\n", flush=True)
        (OUT_DIR / "_test.wav").unlink(missing_ok=True)
    except Exception as e:
        sys.exit(
            f"\nテストに失敗しました: {e}\n"
            "→ ターミナルで先に  export LANG=ja_JP.UTF-8  を打ってから、\n"
            "   もう一度 python3 voicepeak_generate.py を実行してください。\n"
            "   ナレーター名がVOICEPEAKの表示と完全に一致しているかも確認してください。"
        )
    print("=== Unit 0 (40語) ===", flush=True)
    run("u0", UNIT0)
    print("=== Unit 1 (70語) ===", flush=True)
    run("u1", UNIT1)
    print("\n完了。次は python3 convert_mp3.py でmp3に変換してください。", flush=True)
    print("★印の語はNHKアクセント辞典/OJADと照合し、違っていたらVOICEPEAKの")
    print("  辞書に登録 → 該当wavを削除 → このスクリプトを再実行、で直せます。")

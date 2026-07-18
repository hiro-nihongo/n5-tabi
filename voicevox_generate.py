# -*- coding: utf-8 -*-
"""
VOICEVOX 一括音声生成スクリプト(Unit 0 / Unit 1 用)
====================================================
使い方:
  1. VOICEVOX(https://voicevox.hiroshiba.jp/)をインストールして起動しておく
     ※起動中はローカルAPI http://127.0.0.1:50021 が使える
  2. python voicevox_generate.py を実行
  3. audio/ フォルダに u0_00.wav 〜 u1_69.wav が生成される
  4. audio/ フォルダを教材HTMLと同じ場所に置く
     (教材は audio/uX_XX.mp3 → .wav → 端末TTS の順に探します)

アクセントについて:
  VOICEVOXは辞書ベースで単語アクセントを付けるため、端末TTSより大幅に正確です。
  ただし下の ACCENT_CHECK に挙げた語は、生成後に必ず耳で確認し、
  気になる場合は VOICEVOX の GUI で同じ語を入力し、
  「アクセント」タブで核の位置を修正してから書き出して差し替えてください。
  確認の基準には NHK日本語発音アクセント新辞典 か OJAD
  (http://www.gavo.t.u-tokyo.ac.jp/ojad/)を使ってください。

配布時の注意:
  VOICEVOXの各キャラクター音声には利用規約があります(多くは「VOICEVOX:キャラ名」
  のクレジット表記で商用可)。学校配布前に使用キャラクターの規約を確認してください。
"""

import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

HOST = "http://127.0.0.1:50021"
SPEAKER = 3        # 3 = ずんだもん(ノーマル)。VOICEVOXの /speakers で一覧確認可
SPEED = 0.9        # 学習用に少しゆっくり
OUT_DIR = Path("audio")

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

# 生成後に必ず耳でアクセント確認してほしい語(誤りやすい・特に重要)
ACCENT_CHECK = [
    "コーヒー", "エレベーター", "パーティー", "ノート", "スーパー",
    "いちじ、にじ、さんじ", "ごふん、じゅっぷん", "しがつ", "しちがつ", "くがつ",
    "きのう", "あした", "きょう", "ことし", "きょねん", "おととい", "あさって",
]


def synthesize(text: str, out_path: Path) -> None:
    """VOICEVOXエンジンで1語を合成してwav保存する。"""
    # 1) 音声クエリ生成(この段階で辞書アクセントが付く)
    q_url = f"{HOST}/audio_query?text={urllib.parse.quote(text)}&speaker={SPEAKER}"
    with urllib.request.urlopen(urllib.request.Request(q_url, method="POST")) as res:
        query = json.loads(res.read())

    query["speedScale"] = SPEED
    query["postPhonemeLength"] = 0.3   # 語尾の余韻を少し

    # 2) 合成
    s_url = f"{HOST}/synthesis?speaker={SPEAKER}"
    req = urllib.request.Request(
        s_url,
        data=json.dumps(query).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as res:
        out_path.write_bytes(res.read())


def run(unit_name: str, words: list) -> None:
    for i, text in enumerate(words):
        out = OUT_DIR / f"{unit_name}_{i:02d}.wav"
        try:
            synthesize(text, out)
            flag = "  ← ★要アクセント確認" if text in ACCENT_CHECK else ""
            print(f"OK  {out.name}  {text}{flag}")
        except Exception as e:
            print(f"NG  {out.name}  {text}  ({e})")
        time.sleep(0.1)


if __name__ == "__main__":
    OUT_DIR.mkdir(exist_ok=True)
    print("=== Unit 0 (40語) ===")
    run("u0", UNIT0)
    print("=== Unit 1 (70語) ===")
    run("u1", UNIT1)
    print("\n完了。audio/ フォルダを教材HTMLと同じ場所に置いてください。")
    print("★印の語はNHKアクセント辞典/OJADと照合し、必要ならVOICEVOXのGUIで")
    print("  アクセント核を修正して同名ファイルに書き出し直してください。")

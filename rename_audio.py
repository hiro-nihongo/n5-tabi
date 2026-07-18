# -*- coding: utf-8 -*-
"""
Audacityで分割したwavを、教材が読める u0_00.wav 形式に一括リネームする
=====================================================================
Audacityの「複数ファイルの書き出し」は 01, 02... と1始まりで番号を振るため、
教材が期待する 00 始まりの連番(u0_00, u0_01, ...)に付け替えます。

使い方:
  1. 分割したwavだけを1つのフォルダに入れる(他のファイルは入れない)
       例: デスクトップに split_u0 フォルダを作り、その中に分割wavを置く
  2. このスクリプトを n5-tabi フォルダに置く
  3. ターミナルで n5-tabi に cd した状態で、フォルダとユニット記号を指定して実行:

       python3 rename_audio.py ~/Desktop/split_u0 u0
       python3 rename_audio.py ~/Desktop/split_u1 u1

  4. 中身が u0_00.wav 〜 の連番に変わる。数が正しいか表示で確認する。
  5. 確認できたら、それらを n5-tabi/audio/ に移動する。

安全のため:
  - いきなり本番リネームせず、まず「こう変わる」という予定を表示します。
  - 内容を見て問題なければ、もう一度 yes と打つと実際に変更します。
"""

import os
import pathlib
import sys

def main():
    if len(sys.argv) != 3:
        sys.exit(
            "使い方: python3 rename_audio.py <分割wavのフォルダ> <ユニット記号>\n"
            "例:     python3 rename_audio.py ~/Desktop/split_u0 u0"
        )

    folder = pathlib.Path(os.path.expanduser(sys.argv[1]))
    unit = sys.argv[2]

    if not folder.is_dir():
        sys.exit(f"フォルダが見つかりません: {folder}")

    # wavファイルを名前順に並べる(Audacityの 01,02... 順を尊重)
    wavs = sorted([p for p in folder.iterdir()
                   if p.suffix.lower() == ".wav"],
                  key=lambda p: p.name)

    if not wavs:
        sys.exit(f"{folder} に .wav がありません。")

    # リネーム予定を作る
    plan = []
    for i, src in enumerate(wavs):
        dst = folder / f"{unit}_{i:02d}.wav"
        plan.append((src, dst))

    print(f"対象フォルダ: {folder}")
    print(f"見つかった .wav: {len(wavs)} 個\n")
    print("--- リネーム予定(最初の5件と最後の2件)---")
    preview = plan[:5] + ([("...", "...")] if len(plan) > 7 else []) + plan[-2:] if len(plan) > 7 else plan
    for src, dst in preview:
        if src == "...":
            print("   ...")
        else:
            print(f"   {src.name}  →  {dst.name}")

    print(f"\n合計 {len(plan)} 個を {unit}_00.wav 〜 {unit}_{len(plan)-1:02d}.wav に変更します。")
    ans = input("実行してよいですか? yes と打つと実行します: ").strip().lower()
    if ans != "yes":
        print("中止しました。変更していません。")
        return

    # 衝突を避けるため、いったん一時名にしてから最終名へ(2段階)
    tmp = []
    for i, (src, _) in enumerate(plan):
        t = folder / f"__tmp_{i:03d}.wav"
        src.rename(t)
        tmp.append(t)
    for t, (_, dst) in zip(tmp, plan):
        t.rename(dst)

    print(f"\n完了。{len(plan)} 個を {unit}_00.wav 形式にリネームしました。")
    print(f"中身を確認して、問題なければ {folder} のwavを n5-tabi/audio/ に移動してください。")


if __name__ == "__main__":
    main()

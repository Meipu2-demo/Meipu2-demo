# ===== Credit =====
# プロジェクト名: Meipu2
# URL:
# ライセンス: UnKnown
# 著作権者: 広島市立大学
# 著者: K.Mera
#
# 以下のコードはUnKnownに従って利用し、Huyu2239が改変しています。
# 2025/07/18
# ===== Credit =====

"""
学習済の機械学習モデルを使用し，指定されたWAVファイルに対して感情ラベルを出力するプログラム
"""

import glob

import pandas as pd
import opensmile
from sklearn.preprocessing import StandardScaler
import joblib
import os


def detect_emotion_label(wav_file_path):
    smile = opensmile.Smile(
        feature_set=opensmile.FeatureSet.eGeMAPSv02,
        feature_level=opensmile.FeatureLevel.Functionals,
    )
    feature0_test = smile.process_file(wav_file_path)
    standard_features = pd.read_csv(
        os.environ["MEIPU_ROOT_PATH"] + "/core/standardvoice.csv",
        index_col=["file", "start", "end"],
    )
    dummy = pd.concat([standard_features, feature0_test], ignore_index=False)

    scaler = StandardScaler()
    feature_test = scaler.fit_transform(dummy)[-1]
    model = joblib.load(
        os.environ["MEIPU_ROOT_PATH"] + "/core/train8_11_lgbm.pkl"
    )
    rout = model.predict([feature_test])
    dictation = {
        "other": 0,
        "alarmed": 1,
        "angry": 2,
        "calmness": 3,
        "contempt": 4,
        "delight": 5,
        "disgust": 6,
        "fear": 7,
        "pleased": 8,
        "relax": 9,
        "sad": 10,
        "sleepy": 11,
    }
    return rout[0], dictation[rout[0]]


if __name__ == "__main__":
    # Recordフォルダにあるwavファイルを読み込んで、感情ラベルを出力する
    # cd ~/Meipu2-demo
    # python core/main.py
    all_wav_files = glob.glob(os.environ["MEIPU_ROOT_PATH"] + "/Record/*.wav")
    for sample_wav_file in sorted(all_wav_files):
        print(f"Detecting {sample_wav_file}\nResult: ", end="")
        result = detect_emotion_label(sample_wav_file)
        print(result)

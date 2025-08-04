import socket
import glob
import os

from main import detect_emotion_label


# 感情に対応する日本語の辞書
emotion_dict = {
    "alarmed": "不安",
    "angry": "怒り",
    "calmness": "冷静",
    "contempt": "軽蔑",
    "delight": "嬉しい",
    "disgust": "嫌悪",
    "fear": "恐れ",
    "pleased": "楽しい",
    "relax": "リラックス",
    "sad": "悲しい",
    "sleepy": "疲れた",
}


def connect(host: str, port: int):
    _socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    _socket.settimeout(30)
    _socket.connect((host, port))
    return _socket


def detect_emotion():
    latest_wav_file_path = sorted(
        glob.glob(os.environ["MEIPU_ROOT_PATH"] + "/Record/*.wav")
    )[-1]
    label, num = detect_emotion_label(latest_wav_file_path)
    line = emotion_dict.get(label, "other")
    print(label, num, line)


def main():
    # juliusのサーバーに接続
    print("Starting client...")
    _socket = connect(host="127.0.0.1", port=10500)
    print("開始します")

    # 1000回イベントを受け取る
    for _ in range(1000):
        message_recv = _socket.recv(1024).decode("utf-8")
        if message_recv.startswith("<ENDRECOG/>"):
            detect_emotion()

    # 接続を閉じる
    try:
        _socket.shutdown(socket.SHUT_RDWR)
        _socket.close()
    except:
        pass


if __name__ == "__main__":
    main()

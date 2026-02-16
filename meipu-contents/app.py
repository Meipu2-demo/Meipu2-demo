import os
import pathlib
import queue
import random
import socket
import sys
import threading
import time

import emoji
from google.cloud import speech

from meipu import (
    Gemini,
    connect_julius,
    drain_julius_socket,
    generate_response_run,
    send_julius_command,
    transcribe_file,
    wait_for_julius_recogout,
    wait_till_synth_event_stop,
)

sys.stdin.reconfigure(encoding="utf-8")
sys.stdout.reconfigure(encoding="utf-8")
sys.path.append("../")
from core.main import detect_emotion_label

# Todo: configファイルに移動
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = (
    os.environ["MEIPU_ROOT_PATH"] + "/credentials.json"
)

ASR_RESUME_GUARD_SEC = 0.4
JULIUS_DRAIN_SEC = 0.5


# 感情に対応する日本語の辞書
EMOTION_DICT = {
    "other": "",
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

EMOTION_EMOJI_DICT = {
    "other": "",
    "alarmed": ":face_screaming_in_fear:",
    "angry": ":anger_symbol:",
    "calmness": "",
    "contempt": ":expressionless_face:",
    "delight": ":smiling_face_with_heart-eyes:",
    "disgust": ":expressionless_face:",
    "fear": ":face_screaming_in_fear:",
    "pleased": ":smiling_face_with_heart-eyes:",
    "relax": ":smiling_face_with_heart-eyes:",
    "sad": ":crying_face:",
    "sleepy": ":crying_face:",
}


def get_latest_wav_file_after(record_path: pathlib.Path, after_timestamp: float):
    latest_path = None
    latest_mtime = after_timestamp
    for wav_path in record_path.glob("*.wav"):
        try:
            mtime = wav_path.stat().st_mtime
        except OSError:
            continue
        if mtime > latest_mtime:
            latest_mtime = mtime
            latest_path = wav_path
    return str(latest_path) if latest_path else None


def pause_asr(julius_socket: socket.socket):
    send_julius_command(julius_socket, "TERMINATE")


def synth_once(voice: str, content: str):
    print(f"SYNTH_START|uka|{voice}|{content}")
    wait_till_synth_event_stop()


def resume_asr_with_guard(julius_socket: socket.socket):
    time.sleep(ASR_RESUME_GUARD_SEC)
    drain_julius_socket(julius_socket, JULIUS_DRAIN_SEC)
    send_julius_command(julius_socket, "RESUME")
    return time.time()


def main():
    julius_socket = connect_julius(host="127.0.0.1", port=10500)
    input_queue = queue.Queue()
    output_queue = queue.Queue()
    stt_client = speech.SpeechClient()
    record_path = pathlib.Path(os.environ["MEIPU_ROOT_PATH"]).joinpath("Record")

    first_assistant_content_list = [
        "こんにちは、人間と話せるなんて嬉しいです！🥰",
        "こんにちは、今日はいい天気ですね",
        "こんにちは、今日の朝ご飯は何を食べましたか？",
        "こんにちは、今日のお仕事はどうでしたか？",
        "こんにちは、今日のお休みはどう過ごしましたか？",
    ]
    first_assistant_content = random.choice(first_assistant_content_list)
    gemini_client = Gemini(first_assistant_content)

    # 字幕
    print("CAPTION_SETSTYLE|meipu-font|NotoSansJPwithEmoji.ttf|1,0.5,0,1|1,1,1,1,4|0,0,0,0.6,6|0,0,0,0")
    print(f"CAPTION_START|agent_context_log|meipu-font|{first_assistant_content}|3.0|CENTER|0.2|{30*60*15}")
    # モーション
    print("MOTION_ADD|uka|base|../contents/uka/motion/01_happy.vmd")
    pause_asr(julius_socket)
    synth_once("mei_voice_happy", first_assistant_content)
    listening_since = resume_asr_with_guard(julius_socket)

    print("MOTION_ADD|uka|base|../contents/motions/wait/01_Wait_b.vmd")
    print("CAPTION_STOP|agent_context_log")

    # エージェントの応答を生成するスレッドを起動
    thread1 = threading.Thread(target=generate_response_run, args=(gemini_client, input_queue, output_queue))
    thread1.start()

    user_utterance = ""
    while user_utterance != "おわり":
        # juliusが認識するまで待機
        try:
            if wait_for_julius_recogout(julius_socket) is None:
                continue
        except Exception:
            continue

        # 音声ファイルを取得
        latest_wav_file_path = get_latest_wav_file_after(record_path, listening_since)
        if latest_wav_file_path is None:
            continue

        # 音声ファイルを文字起こし
        user_utterance = transcribe_file(stt_client, latest_wav_file_path)
        if user_utterance is None:
            continue

        # 音声ファイルから感情を抽出
        label, _emotion_enum = detect_emotion_label(latest_wav_file_path)

        # 感情に対応するemojiを取得
        raw_emoji = EMOTION_EMOJI_DICT.get(label, "")
        user_emotion_emoji = emoji.emojize(raw_emoji) if raw_emoji else ""

        # ユーザーの入力を処理
        user_input = user_utterance + user_emotion_emoji
        print(f"CAPTION_START|user_context_log|meipu-font|{user_utterance + f'【{EMOTION_DICT[label]}】'}|1.0|RIGHT|0.8|{30*60*15}")
        input_queue.put(user_input)

        # エージェントの応答を処理
        spoke_any = False
        while True:
            assistant_content = output_queue.get()
            if assistant_content == "***END***":
                break

            # 返答emojiに含まれる感情を抽出し、それに応じて音声とmotionを変更
            output_sentence = emoji.demojize(assistant_content)
            voice_dict = {
                ":anger_symbol:": "mei_voice_angry",
                ":pouting_face:": "mei_voice_angry",
                ":expressionless_face:": "mei_voice_angry",
                ":unamused_face:": "mei_voice_angry",
                ":face_with_rolling_eyes:": "mei_voice_angry",
                ":face_screaming_in_fear:": "mei_voice_sad",
                ":two_hearts:": "mei_voice_happy",
                ":red_heart:": "mei_voice_happy",
                ":smiling_face_with_hearts:": "mei_voice_happy",
                ":smiling_face_with_heart-eyes:": "mei_voice_happy",
                ":crying_face:": "mei_voice_sad",
                ":loudly_crying_face:": "mei_voice_sad",
                ":astonished_face:": "mei_voice_normal",
                ":red_exclamation_mark:": "mei_voice_normal",
            }
            voice = "mei_voice_normal"
            for key, value in voice_dict.items():
                if key in output_sentence:
                    voice = value
                    break

            motion_dict = {
                ":anger_symbol:": "33_angry",
                ":pouting_face:": "33_angry",
                ":expressionless_face:": "21_disgust",
                ":unamused_face:": "21_disgust",
                ":face_with_rolling_eyes:": "21_disgust",
                ":face_screaming_in_fear:": "34_sad",
                ":two_hearts:": "01_happy",
                ":red_heart:": "01_happy",
                ":smiling_face_with_hearts:": "01_happy",
                ":smiling_face_with_heart-eyes:": "01_happy",
                ":crying_face:": "34_sad",
                ":loudly_crying_face:": "34_sad",
                ":astonished_face:": "08_surprise",
                ":red_exclamation_mark:": "08_surprise",
            }
            motion = "00_normal"
            for key, value in motion_dict.items():
                if key in output_sentence:
                    motion = value
                    break

            if not spoke_any:
                pause_asr(julius_socket)
                spoke_any = True

            print(f"MOTION_ADD|uka|base|../contents/uka/motion/{motion}.vmd")
            print(f"CAPTION_START|agent_context_log|meipu-font|{assistant_content}|3.0|CENTER|0.2|{30*60*15}")
            synth_once(voice, assistant_content)
            print("MOTION_ADD|uka|base|../contents/motions/wait/01_Wait_b.vmd")

        if spoke_any:
            listening_since = resume_asr_with_guard(julius_socket)

        print("CAPTION_STOP|user_context_log")
        print("CAPTION_STOP|agent_context_log")

        # 古い音声ファイルを削除
        wav_file_list = sorted([str(_path) for _path in record_path.glob("*.wav")])
        if len(wav_file_list) > 10:
            for file in wav_file_list[:-10]:
                print(f"Deleting {file}")
                os.remove(file)

    thread1.join()

    try:
        julius_socket.shutdown(socket.SHUT_RDWR)
        julius_socket.close()
    except Exception:
        pass


if __name__ == "__main__":
    main()

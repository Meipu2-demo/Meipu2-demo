import re
import sys
import socket
import io
import time

from google.cloud import speech


def generate_response_run(gemini_client, input_queue, output_queue):
    """
    ユーザーの発言を受け取り、応答を生成する
    """
    while True:
        user_input = input_queue.get()
        print(f"認識: {user_input}", file=sys.stderr)
        queue = gemini_client.play_response(user_input)
        for item in queue:
            output_queue.put(item)
        input_queue.task_done()


def transcribe_file(STT_client, speech_file):
    """音声ファイルをGoogle Speech-to-Text APIで文字起こしする"""
    with io.open(speech_file, "rb") as audio_file:
        content = audio_file.read()

    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="ja-JP",
    )
    response = STT_client.recognize(config=config, audio=audio)
    return str(response.results[0].alternatives[0].transcript) if response.results else None


def connect_julius(host: str, port: int):
    """
    juliusのサーバーに接続する
    """
    _socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    _socket.settimeout(60 * 15)
    _socket.connect((host, port))
    return _socket


def send_julius_command(_socket: socket.socket, command: str):
    """
    juliusモジュールコマンドを送信する
    """
    _socket.sendall(f"{command.strip().upper()}\n".encode("utf-8"))


def wait_for_julius_recogout(_socket: socket.socket):
    """
    juliusから<RECOGOUT>を受け取るまで待機する
    """
    recv_buffer = ""
    while True:
        chunk = _socket.recv(4096).decode("utf-8", errors="ignore")
        if not chunk:
            return None
        recv_buffer += chunk
        if len(recv_buffer) > 16384:
            recv_buffer = recv_buffer[-16384:]
        if "<RECOGOUT>" in recv_buffer:
            return recv_buffer


def drain_julius_socket(_socket: socket.socket, drain_sec: float = 0.5):
    """
    juliusソケットに残っている受信データを破棄する
    """
    old_timeout = _socket.gettimeout()
    _socket.settimeout(0.0)
    drain_until = time.monotonic() + drain_sec
    try:
        while time.monotonic() < drain_until:
            try:
                chunk = _socket.recv(4096)
                if not chunk:
                    break
            except (BlockingIOError, socket.timeout):
                time.sleep(0.01)
    finally:
        _socket.settimeout(old_timeout)


def wait_till_synth_event_stop():
    """
    音声合成が終わるまで待機する
    """
    while True:
        instr = input().strip()
        if not instr:
            break
        if re.findall("^SYNTH_EVENT_STOP", instr):
            break

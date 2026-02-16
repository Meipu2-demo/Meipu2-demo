import os
import re
import sys
import google.generativeai as genai


GEMINI_MESSAGE_HISTORY_MAX = 5
GEMINI_MODEL = 'gemma-3-27b-it'


class Gemini:
    def __init__(self, first_assistant_content=None):
        genai.configure(api_key=os.environ["MEIPU_GEMINI_API_KEY"])
        self.gemini_messages = []
        self.gemini_model = genai.GenerativeModel(GEMINI_MODEL)
        en_prompt = """
        You are my friend. You are a girl.
        Consider the emotion icon at the end of my messages when responding.
        End your responses with 0 or more emotion icons that reflect your current feeling,
        using 🥰 for happiness, 💢 for anger, 😱 for fear, and 😭 for sadness.
        Keep responses concise, within 2 sentences, and avoid bullet points.
        Tailor language and tone to match my emotional state.
        Respond in Japanese, aiming for a natural, empathetic conversation.
        Use emotion icons after each sentence when possible.
        Do not use periods at the end of sentences.
        """
        ja_prompt = """
        あなたは私の友人です．
        私の発言の末尾に付いているアイコンは私の気持ちを表しています．
        あなたは私の気持ちを考慮して応答してください．
        あなたの応答の末尾には必ずあなたの気持ちを表すアイコンを付けてください．
        あなたが嬉しい気持ちの時は🥰，怒っている気持ちの時は💢，
        怖い気持ちの時は😱，悲しい気持ちの時は😭のアイコンを付けてください．
        応答は必ず２文以内にしてください．箇条書きは使わないでください．
        """
        self.gemini_messages.append({"role": "user", "parts": [en_prompt]})
        if first_assistant_content:
            self.gemini_messages.append({"role": "model", "parts": [first_assistant_content]})

    def play_response(self, user_input):
        queue = []
        self.gemini_messages.append({"role": "user", "parts": [user_input]})

        try:
            completion = self.gemini_model.generate_content(self.gemini_messages)
        except Exception as e:
            print(f"gemini: Failed to connect to Gemini API: {e}", file=sys.stderr)
            del self.gemini_messages[-1]
            return
    
        completion_text = re.sub(r'[\n\r]+', '', completion.text) 
        self.gemini_messages.append({"role": "model", "parts": [completion_text]})

        if len(self.gemini_messages) > GEMINI_MESSAGE_HISTORY_MAX * 2 + 1:
            self.gemini_messages.pop(1)
            self.gemini_messages.pop(1)
        
        # 絵文字または句読点ごとに文を分割してキューに追加
        emoji_chars = r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\u2600-\u26FF\u2700-\u27BF\U0001F900-\U0001F9FF\U0001FA70-\U0001FAFF]'
        punctuation = r'[、。！？]'
        pattern = f'.*?(?:{emoji_chars}|{punctuation})|.+$'
        sentences = re.findall(pattern, completion_text)
        for sentence in sentences:
            if sentence:
                queue.append(sentence)

        queue.append("***END***")
        print(f"返答: {completion_text}", file=sys.stderr)
        return queue

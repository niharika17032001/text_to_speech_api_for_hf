# app.py

import gradio as gr
import requests

from model_handler import call_model_with_timeout

ref_audio_url = "https://github.com/AI4Bharat/IndicF5/raw/refs/heads/main/prompts/PAN_F_HAPPY_00002.wav"
ref_audio_path = "PAN_F_HAPPY_00002.wav"
with open(ref_audio_path, "wb") as f:
    f.write(requests.get(ref_audio_url).content)


def synthesize_speech(text, ref_audio, ref_text):
    if not ref_audio:
        return "⛔ Please upload a reference WAV file", None

    # ref_audio is already a file path
    status, output_path = call_model_with_timeout(text, ref_audio, ref_text)
    return status, output_path


iface = gr.Interface(
    fn=synthesize_speech,
    inputs=[
        gr.Textbox(label="Input Text", value="यह एक परीक्षण वाक्य है।"),
        gr.Audio(type="filepath", label="Reference Audio", value="PAN_F_HAPPY_00002.wav"),
        gr.Textbox(label="Reference Text",
                   value="ਇੱਕ ਗ੍ਰਾਹਕ ਨੇ ਸਾਡੀ ਬੇਮਿਸਾਲ ਸੇਵਾ ਬਾਰੇ ਦਿਲੋਂਗਵਾਹੀ ਦਿੱਤੀ ਜਿਸ ਨਾਲ ਸਾਨੂੰ ਅਨੰਦ ਮਹਿਸੂਸ ਹੋਇਆ।"),
    ],
    outputs=[
        gr.Textbox(label="Status"),
        gr.Audio(label="Synthesized Output")
    ],
    title="Speech Synthesis Demo",
    description="Provide input text, a reference audio sample, and its corresponding text to synthesize new speech."
)

iface.launch()

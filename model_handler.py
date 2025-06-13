# model_handler.py

import threading
import logging
import requests
import os
import shutil
from gradio_client import Client, handle_file
from colorama import init, Fore, Style

import story

# Initialize colorama for Windows console color support
init(autoreset=True)

# --- Custom colored log formatter for full-line coloring ---
class FullColorFormatter(logging.Formatter):
    COLORS = {
        logging.DEBUG: Fore.CYAN,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.MAGENTA
    }

    def format(self, record):
        base_message = super().format(record)
        color = self.COLORS.get(record.levelno, "")
        return f"{color}{base_message}{Style.RESET_ALL}"

# Setup logger
formatter = FullColorFormatter("%(asctime)s [%(levelname)s] %(message)s")

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

file_handler = logging.FileHandler("model_handler.log", mode="w", encoding="utf-8")
file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))

logging.basicConfig(
    level=logging.INFO,
    handlers=[console_handler, file_handler]
)

client = Client("ai4bharat/IndicF5")

def call_model_with_timeout(text, ref_audio_path, ref_text="", timeout=3600):
    result = {"status": None, "audio_url": None}

    def run():
        try:
            logging.info("Calling model with text: %s", text)
            audio_url = client.predict(
                text,
                handle_file(ref_audio_path),
                ref_text,
                api_name="/synthesize_speech"
            )
            result["status"] = "success"
            result["audio_url"] = audio_url
            logging.info("Model call successful. Audio URL: %s", audio_url)
        except Exception as e:
            result["status"] = f"error: {e}"
            logging.error("Model call failed with error: %s", e)

    thread = threading.Thread(target=run)
    thread.start()
    thread.join(timeout)

    if thread.is_alive():
        logging.error("Model call timed out after %s seconds", timeout)
        return "Timed out", None

    if result["status"] == "success":
        audio_url = result["audio_url"]
        try:
            output_path = "voices/output.wav"
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            logging.info("Handling audio download/copy from: %s", audio_url)
            if audio_url.startswith("http"):
                audio_response = requests.get(audio_url)
                with open(output_path, "wb") as f:
                    f.write(audio_response.content)
                logging.info("Audio downloaded from URL and saved as %s", output_path)
            elif os.path.exists(audio_url):
                shutil.copy(audio_url, output_path)
                logging.info("Audio copied from local path to %s", output_path)
            else:
                raise FileNotFoundError(f"Audio file not found at {audio_url}")
            return "Success", output_path
        except Exception as e:
            logging.error("Error downloading or copying audio: %s", e)
            return f"Download error: {e}", None
    else:
        logging.error("Model call failed: %s", result["status"])
        return result["status"], None


def main(text = "यह एक परीक्षण वाक्य है।"):
    ref_audio_url = "https://github.com/AI4Bharat/IndicF5/raw/refs/heads/main/prompts/PAN_F_HAPPY_00002.wav"
    ref_audio_path = "PAN_F_HAPPY_00002.wav"
    logging.info("Downloading reference audio from %s", ref_audio_url)
    try:
        with open(ref_audio_path, "wb") as f:
            f.write(requests.get(ref_audio_url).content)
        logging.info("Reference audio saved as %s", ref_audio_path)
    except Exception as e:
        logging.error("Failed to download reference audio: %s", e)
        return


    ref_text = "ਇੱਕ ਗ੍ਰਾਹਕ ਨੇ ਸਾਡੀ ਬੇਮਿਸਾਲ ਸੇਵਾ ਬਾਰੇ ਦਿਲੋਂਗਵਾਹੀ ਦਿੱਤੀ ਜਿਸ ਨਾਲ ਸਾਨੂੰ ਅਨੰਦ ਮਹਿਸੂਸ ਹੋਇਆ।"

    if not os.path.exists(ref_audio_path):
        logging.error("Reference audio not found.")
        return "Please upload a reference WAV file", None

    status, output_path = call_model_with_timeout(text, ref_audio_path, ref_text)
    logging.info("Final Status: %s", status)

    if output_path:
        logging.info("Output audio path: %s", output_path)
    else:
        logging.warning("No output audio file was generated.")

    return status, output_path


if __name__ == "__main__":
    text=story.story
    main(text)

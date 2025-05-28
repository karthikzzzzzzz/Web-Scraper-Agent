import requests
from dotenv import load_dotenv
import os

load_dotenv()

class DeepgramTranscriber:
    def __init__(self):
        self.api_key = os.getenv("DEEPGRAM_KEY")
        self.url = "https://api.deepgram.com/v1/listen?punctuate=true&language=en-US"
        self.headers = {
            "Authorization": f"Token {self.api_key}"
        }

    def transcribe(self, file_path: str) -> str | None:
        """
        Transcribes a webm audio file using Deepgram API.

        Args:
            file_path (str): Path to the webm audio file.

        Returns:
            str | None: Transcript text if successful, else None.
        """
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return None

        with open(file_path, "rb") as audio_file:
            response = requests.post(self.url, headers=self.headers, data=audio_file)

        if response.status_code == 200:
            result = response.json()
            transcript = (
                result.get("results", {})
                      .get("channels", [{}])[0]
                      .get("alternatives", [{}])[0]
                      .get("transcript", "")
            )
            print("Transcript:", transcript)
            return transcript
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None

transcript_obj = DeepgramTranscriber()
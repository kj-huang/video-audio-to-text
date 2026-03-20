# Video/Audio to Text

Transcribe audio and video files to text using [OpenAI's Whisper API](https://platform.openai.com/docs/guides/speech-to-text), with optional ChatGPT-powered summarization.

This tool extracts speech from media files and produces a text transcript. It can optionally generate a concise summary using ChatGPT, saving you the manual step of copying the transcript into ChatGPT.

Based on the approach described in this article:
[Developing an Audio Summarization Tool with ChatGPT and Python for Fast Knowledge Digest](https://medium.com/kjh-new-tech-update/developing-an-audio-summarization-tool-with-chatgpt-and-python-for-fast-knowledge-digest-58fcf4995156)

## Prerequisites

- Python 3.9+
- An [OpenAI API key](https://platform.openai.com/api-keys)
- [FFmpeg](https://ffmpeg.org/download.html) installed on your system (required by pydub for audio processing)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/kj-huang/video-audio-to-text.git
   cd video-audio-to-text
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set your OpenAI API key:
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```

## Usage

Transcribe an audio file:
```bash
python index.py audio.wav
```

Transcribe a video file (extracts audio automatically):
```bash
python index.py video.mp4
```

Transcribe and summarize:
```bash
python index.py audio.wav --summarize
```

Specify output file:
```bash
python index.py audio.wav -o transcript.txt
```

All options:
```bash
python index.py --help
```

## How It Works

1. If the input is a video file, audio is extracted using moviepy
2. The audio is split into chunks to stay within Whisper API limits (25MB per request)
3. Each chunk is sent to OpenAI's Whisper API for transcription
4. The transcript is written to an output file
5. Optionally, the transcript is sent to ChatGPT for summarization

## License

This project is licensed under the [GPL-3.0 License](LICENSE).

---

Fork this project or give it a star if you like it!

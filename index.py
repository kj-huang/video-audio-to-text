import argparse
import os
import sys
import tempfile
from pathlib import Path

from openai import OpenAI
from pydub import AudioSegment
from tqdm import tqdm

VIDEO_EXTENSIONS = {".mp4", ".mkv", ".avi", ".mov", ".webm", ".flv"}
AUDIO_EXTENSIONS = {".wav", ".mp3", ".flac", ".ogg", ".m4a", ".aac"}


def extract_audio_from_video(video_path: str) -> str:
    """Extract audio from a video file and return path to a temporary wav file."""
    try:
        from moviepy import VideoFileClip
    except ImportError:
        print("Error: moviepy is required for video files. Install it with: pip install moviepy")
        sys.exit(1)

    print(f"Extracting audio from {video_path}...")
    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    tmp.close()
    clip = VideoFileClip(video_path)
    clip.audio.write_audiofile(tmp.name, verbose=False, logger=None)
    clip.close()
    return tmp.name


def chunk_audio(audio_path: str, chunk_duration_s: int) -> list[AudioSegment]:
    """Split audio file into chunks of the given duration."""
    audio = AudioSegment.from_file(audio_path)
    chunk_ms = chunk_duration_s * 1000
    chunks = [audio[i:i + chunk_ms] for i in range(0, len(audio), chunk_ms)]
    return chunks


def transcribe_chunks(client: OpenAI, chunks: list[AudioSegment], model: str) -> str:
    """Transcribe audio chunks using the Whisper API."""
    texts = []
    for chunk in tqdm(chunks, desc="Transcribing"):
        tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        tmp.close()
        try:
            chunk.export(tmp.name, format="wav")
            with open(tmp.name, "rb") as audio_file:
                transcript = client.audio.transcriptions.create(
                    model=model,
                    file=audio_file,
                )
            texts.append(transcript.text)
        finally:
            os.unlink(tmp.name)
    return " ".join(texts)


def summarize_text(client: OpenAI, text: str, model: str) -> str:
    """Summarize transcript using the ChatGPT API."""
    print("Generating summary...")
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant. Summarize the following transcript concisely."},
            {"role": "user", "content": text},
        ],
    )
    return response.choices[0].message.content


def main():
    parser = argparse.ArgumentParser(
        description="Transcribe audio/video files to text using OpenAI Whisper, with optional ChatGPT summarization."
    )
    parser.add_argument("input_file", help="Path to the audio or video file")
    parser.add_argument("-o", "--output", default="recognized.txt", help="Output text file (default: recognized.txt)")
    parser.add_argument("-s", "--summarize", action="store_true", help="Summarize the transcript using ChatGPT")
    parser.add_argument("--model", default="whisper-1", help="Whisper model to use (default: whisper-1)")
    parser.add_argument("--summary-model", default="gpt-4o-mini", help="ChatGPT model for summarization (default: gpt-4o-mini)")
    parser.add_argument("--chunk-size", type=int, default=300, help="Chunk duration in seconds (default: 300)")
    args = parser.parse_args()

    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"Error: File not found: {args.input_file}")
        sys.exit(1)

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable is not set.")
        print("Get your API key at https://platform.openai.com/api-keys")
        sys.exit(1)

    client = OpenAI(api_key=api_key)
    temp_audio = None

    try:
        # Extract audio from video if needed
        suffix = input_path.suffix.lower()
        if suffix in VIDEO_EXTENSIONS:
            temp_audio = extract_audio_from_video(str(input_path))
            audio_path = temp_audio
        elif suffix in AUDIO_EXTENSIONS:
            audio_path = str(input_path)
        else:
            print(f"Error: Unsupported file format '{suffix}'.")
            print(f"Supported formats: {', '.join(sorted(VIDEO_EXTENSIONS | AUDIO_EXTENSIONS))}")
            sys.exit(1)

        # Chunk and transcribe
        chunks = chunk_audio(audio_path, args.chunk_size)
        print(f"Processing {len(chunks)} chunk(s)...")
        transcript = transcribe_chunks(client, chunks, args.model)

        # Write output
        with open(args.output, "w") as f:
            f.write(transcript)
            if args.summarize:
                summary = summarize_text(client, transcript, args.summary_model)
                f.write("\n\n--- Summary ---\n\n")
                f.write(summary)

        print(f"Done! Output saved to {args.output}")

    finally:
        if temp_audio and os.path.exists(temp_audio):
            os.unlink(temp_audio)


if __name__ == "__main__":
    main()

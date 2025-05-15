import os
import moviepy.editor as mp
import speech_recognition as sr
from pydub import AudioSegment
import video_audio_db

def extract_audio_from_video(video_path: str, audio_output_path: str = "extracted_audio.wav") -> str:
    """
    Extracts audio from a video file and saves it as a WAV file.

    Args:
        video_path (str): Path to the input video file.
        audio_output_path (str): Path to save the extracted audio file.

    Returns:
        str: Path to the saved audio file.
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    video = mp.VideoFileClip(video_path)
    audio = video.audio
    if audio is None:
        raise ValueError("No audio track found in the video.")

    audio.write_audiofile(audio_output_path, logger=None)
    print(f"Audio extracted and saved to {audio_output_path}")
    return audio_output_path


def convert_audio_to_wav(audio_path: str, wav_output_path: str = "converted_audio.wav") -> str:
    """
    Converts audio file to WAV format if not already WAV.

    Args:
        audio_path (str): Path to the input audio file.
        wav_output_path (str): Path to save the WAV audio file.

    Returns:
        str: Path to the WAV audio file.
    """
    if audio_path.lower().endswith(".wav"):
        return audio_path

    audio = AudioSegment.from_file(audio_path)
    audio.export(wav_output_path, format="wav")
    print(f"Audio converted to WAV and saved to {wav_output_path}")
    return wav_output_path


def transcribe_audio(audio_path: str) -> str:
    """
    Transcribes speech from an audio file to text using Google's speech recognition.

    Args:
        audio_path (str): Path to the WAV audio file.

    Returns:
        str: Transcribed text.
    """
    recognizer = sr.Recognizer()

    with sr.AudioFile(audio_path) as source:
        # For long audio, consider chunking here
        audio_data = recognizer.record(source)

    try:
        print("Transcribing audio...")
        text = recognizer.recognize_google(audio_data)
        print("Transcription complete.")
        return text
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
        return ""
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
        return ""


def save_text_to_file(text: str, output_path: str = "transcription.txt") -> None:
    """
    Saves the transcribed text to a file.

    Args:
        text (str): Text to save.
        output_path (str): Path to the output text file.
    """
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"Transcribed text saved to {output_path}")


def main():
  import argparse

  parser = argparse.ArgumentParser(
    description="Extract audio from video, transcribe it, and save text for bias analysis.")
  parser.add_argument("video_path", help="Path to the input video file")
  parser.add_argument("--audio_output", default="extracted_audio.wav", help="Path to save extracted audio (wav format)")
  parser.add_argument("--text_output", default="transcription.txt", help="Path to save transcribed text")

  args = parser.parse_args()

  try:
    # Ensure DB table exists
    video_audio_db.create_table()

    audio_path = extract_audio_from_video(args.video_path, args.audio_output)
    wav_audio_path = convert_audio_to_wav(audio_path)
    transcription = transcribe_audio(wav_audio_path)
    if transcription:
      save_text_to_file(transcription, args.text_output)
      # Insert transcription into DB
      video_audio_db.insert_transcription(os.path.basename(args.video_path), transcription)
    else:
      print("No transcription available to save.")
  except Exception as e:
    print(f"Error: {e}")


if __name__ == "__main__":
  main()

import yt_dlp
from pydub import AudioSegment
from wit import Wit
import os
import time
from datetime import datetime

def download_audio(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'downloaded_audio.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '256',
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        audio_filename = ydl.prepare_filename(info).replace('.webm', '.mp3').replace('.m4a', '.mp3')
    return audio_filename, info.get('title', 'Unknown Title')

def split_audio(audio_path, chunk_length_ms=15000):
    audio = AudioSegment.from_file(audio_path)
    chunks = []
    
    for i in range(0, len(audio), chunk_length_ms):
        chunk = audio[i:i + chunk_length_ms]
        chunk_name = f"chunk_{i//1000}.mp3"
        chunk.export(chunk_name, format="mp3", parameters=["-ac", "1"])
        chunks.append((chunk_name, i // 1000))  # Store chunk filename and start time in seconds
    
    return chunks

def transcribe_audio(api_key, audio_chunks, language="ar"):
    client = Wit(api_key)
    transcript_with_timestamps = []
    
    for i, (chunk, start_time) in enumerate(audio_chunks):
        try:
            with open(chunk, 'rb') as f:
                print(f"Processing chunk {i+1} of {len(audio_chunks)}...")
                response = client.speech(f, {'Content-Type': 'audio/mpeg'})
                text = response.get('text', '')
                if text:
                    minutes, seconds = divmod(start_time, 60)
                    transcript_with_timestamps.append(f"[{minutes:02}:{seconds:02}] {text}")
            time.sleep(2)
        except Exception as e:
            print(f"Error on chunk {i+1}: {str(e)}")
        finally:
            if os.path.exists(chunk):
                os.remove(chunk)
    
    return transcript_with_timestamps

def save_transcript(transcript, video_title, language):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"transcript_{timestamp}.txt"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"Video Title: {video_title}\n")
        f.write(f"Language: {language}\n")
        f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("\n=== Transcript with Timestamps ===\n\n")
        f.write("\n".join(transcript))
    
    return filename

def main(url, api_key, language="ar"):
    audio_file = None
    try:
        print("Downloading audio...")
        audio_file, video_title = download_audio(url)
        
        print("Processing and splitting audio...")
        chunks = split_audio(audio_file)
        
        print(f"Transcribing audio in language: {language}...")
        transcript = transcribe_audio(api_key, chunks, language)
        
        output_file = save_transcript(transcript, video_title, language)
        print(f"\nTranscript saved to: {output_file}")
        
        return transcript
    
    except Exception as e:
        return f"Error: {str(e)}"
    finally:
        if audio_file and os.path.exists(audio_file):
            os.remove(audio_file)

if __name__ == "__main__":
    video_url = input("Enter video URL: ")
    api_key = input("Enter your Wit.ai Server Access Token: ")
    language = input("Enter language code (e.g., 'ar' for Arabic, 'en' for English): ").lower() or "ar"
    
    transcript = main(video_url, api_key, language)
    print("\nTranscript:")
    print("\n".join(transcript))

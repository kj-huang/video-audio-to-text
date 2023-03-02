import speech_recognition as sr 
import moviepy.editor as mp
from pydub import AudioSegment

# uncomment this area if you want to get the audio file in videos
# clip = mp.VideoFileClip(r"test.mp4")
# clip.audio.write_audiofile(r"converted.wav")

# Split the audio file into smaller chunks to avoid memory issues
audio_file = AudioSegment.from_file("converted.wav", format="wav")
chunk_size = 10 * 1000
chunks = []
for i in range(0, len(audio_file), chunk_size):
    chunks.append(audio_file[i:i+chunk_size])

# Create a Recognizer instance and transcribe each chunk
r = sr.Recognizer()
result_text = ""
for chunk in chunks:
    with sr.AudioFile(chunk.export(format="wav")) as audio:
        audio_data = r.record(audio)
        result_text += r.recognize_google(audio_data) + " "


# exporting the result to a file, then you can put the text file to ChatGPT to get summary
with open('recognized.txt',mode ='w') as file:
   file.write("Result:")
   file.write("\n")
   file.write(result_text)
   print("done!")
  
 # Or you can integrate with ChatGPT api if you are lazy copy paste the result.

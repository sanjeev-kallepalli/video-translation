from openai import OpenAI
from dotenv import load_dotenv
import os
import openai
import whisper
import io
from tools.prompt import base_prompt
from pydub import AudioSegment


load_dotenv('.env')
# print(os.getenv('OPENAI_API_KEY'))
# print(os.getenv('TRANSCRIBE_MODEL'))
# print(os.getenv('RESPONSE_MODEL'))
openai.api_key = os.getenv('OPENAI_API_KEY')


# without timestamps
def transcribe_audio(audio_path):

    client = OpenAI()

    audio_file = open(audio_path, "rb")
    transcription = client.audio.transcriptions.create(
        model=os.getenv('TRANSCRIBE_MODEL'),
        file=audio_file
    )
    audio_file.close()
    return transcription.text


def transcribe_audio_with_timestamps(audio_path):
    audio = whisper.load_audio(audio_path)
    model = whisper.load_model("base")
    result = whisper.transcribe(model, audio)
    return result


def timestamped_transcription(audio_path, base_prompt=base_prompt):
     # get accurate text using gpt-4o-transcribe
    fine_text = transcribe_audio(audio_path)
    # get timestamps using whisper
    result = transcribe_audio_with_timestamps(audio_path)

    timeline_text = "\n".join([f"{segment['text']} {segment['start']} {segment['end']}" for segment in result['segments']])
    raw_fine_text = ".\n".join(fine_text.split('.'))
    user_input = timeline_text + "\n\n" + raw_fine_text

    client = OpenAI()
    response = client.responses.create(
    model=os.getenv('RESPONSE_MODEL'),
    input=base_prompt + [
        {
            "role": "user",
            "content": [
                {
                    "type": "input_text",
                    "text": user_input
          }
      ]
    }
  ],
    text={"format": {"type": "text"}},
    reasoning={},
    tools=[],
    temperature=0.8,
    max_output_tokens=2048,
    top_p=1,
    store=True
    )
    return response.output[0].content[0].text


def get_length_of_audio(audio_segment):
    
    audio_length_seconds = len(audio_segment) / 1000.0
    return audio_length_seconds


def add_muted_audio(audio_start, audio_end):
    duration = float(audio_end) - float(audio_start)
    if duration<=0:
        duration = 0.01
    muted_segment = AudioSegment.silent(duration=duration * 900)
    return muted_segment


def text_to_speech_with_timestamps(text, audio_start, audio_end):
    try:
        # Step 1: Generate audio from text using OpenAI's TTS

        client = OpenAI()
        audio_buffer = io.BytesIO()
        with client.audio.speech.with_streaming_response.create(
            model=os.getenv('TTS_MODEL'),
            input=text,
            voice='alloy',
            instructions="You are a polite chef. Speak clearly and naturally."
        ) as response:
            for chunk in response.iter_bytes():
                audio_buffer.write(chunk)
        audio_buffer.seek(0)
        # 2. Capture the length of the audio file (in seconds)
        audio_segment = AudioSegment.from_file(audio_buffer, format="mp3")
        audio_length_seconds = get_length_of_audio(audio_segment)  # duration in seconds
        # Step 3: Add muted audio segment before the actual audio.
        silence_duration = (float(audio_end) - float(audio_start) - audio_length_seconds) * 1000
        # print(f"{text}, {audio_start}, {audio_end}, {silence_duration/1000}, {audio_length_seconds}")
        if silence_duration >0:
            silence = AudioSegment.silent(duration=silence_duration)
            audio_buffer = audio_segment + silence    
            return audio_buffer
        return audio_segment
    except Exception as e:
        print(f"Error in text_to_speech_with_timestamps: {e}")


def get_timestamp_adjusted_audio(translated_text, translated_audio_path):
    # add 10ms muted audio at the start
    audio_fl = add_muted_audio('0.0', '0.01')                           

    for idx in range(len(translated_text)):
        try:
            temp_audio_fl = text_to_speech_with_timestamps(
                translated_text[idx]['text'],
                translated_text[idx]['start_time'],
                translated_text[idx]['end_time']
            )
            length_of_temp_audio = get_length_of_audio(temp_audio_fl)
            print(f"Processing index {idx}: {translated_text[idx]['text']}, audio span: {length_of_temp_audio}, " +
                  f"start: {translated_text[idx]['start_time']}, end: {translated_text[idx]['end_time']}")
            if idx < len(translated_text) - 1:
                spawn_end_time = translated_text[idx+1]['start_time']
            else:
                spawn_end_time = str(float(translated_text[idx]['end_time']) + 0.1)
            muted_audio = add_muted_audio(
                translated_text[idx]['end_time'],
                spawn_end_time
            )
            audio_fl = audio_fl + temp_audio_fl + muted_audio
            
        except Exception as e:
            print(f"Error processing index {idx}: {e}")
            continue
    audio_fl.export(translated_audio_path, format="mp3")
    return f"audio saved to {translated_audio_path}"
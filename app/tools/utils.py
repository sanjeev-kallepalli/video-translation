import os
import shutil
import time
import asyncio
from googletrans import Translator


def save_upload_file(upload_file, destination_folder="output"):
    # Use provided filename or fallback to original upload filename
    target_filename = upload_file.filename
    destination_path = os.path.join(destination_folder, target_filename)

    # Rewind the file and write it to the outputs/ directory
    upload_file.file.seek(0)
    with open(destination_path, "wb") as out_file:
        shutil.copyfileobj(upload_file.file, out_file)

    return destination_path


async def translate_text(text, dest='en'):
    translator = Translator()
    translation = await translator.translate(text, dest=dest)
    return translation.text


# en English, hi Hindi, es Spanish
async def to_desired_text_translation(lang_text, dest='en'):
    try:
        desired_lang_text = await translate_text(lang_text, dest=dest)
        time.sleep(1)  # Adding a delay to avoid rate limiting issues with the translator
        return desired_lang_text
    except Exception as e:
        return f"An error occurred: {e}"
    

async def timestamped_target_text(timestamped_text, dest='en'):
     
    timestamped_texts = timestamped_text.split('\n')
    desired_lang_text = []
    for text in timestamped_texts[1:]:
        text = text.strip()
        splits = text.split(' ')
        if len(splits)>=3:
            start_time = splits[-2]
            end_time = splits[-1]
            temp = {}
            temp['text'] = await to_desired_text_translation(' '.join(splits[:-2]), dest=dest)
            temp['start_time'] = start_time
            temp['end_time'] = end_time
            desired_lang_text.append(temp)
    return desired_lang_text


def seconds_to_srt_time(seconds):
    hours = int(float(seconds) // 3600)
    minutes = int((float(seconds) % 3600) // 60)
    secs = int(float(seconds) % 60)
    millis = int((float(seconds) - int(float(seconds))) * 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"


def generate_subtitle_file(translated_text, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        for idx, entry in enumerate(translated_text):
            start_time = seconds_to_srt_time(entry['start_time'])
            end_time = seconds_to_srt_time(entry['end_time'])
            text = entry['text']
            f.write(f"{idx + 1}\n")
            f.write(f"{start_time} --> {end_time}\n")
            f.write(f"{text}\n\n")
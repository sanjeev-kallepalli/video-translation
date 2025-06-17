from tools.audio_operations import timestamped_transcription, get_timestamp_adjusted_audio
from tools.utils import timestamped_target_text, generate_subtitle_file
from tools.video_operations import extract_audio, replace_audio, add_subtitles
import asyncio


async def run_workflow(video_path, audio_path, translated_audio_path, output_video_path, subtitles_srt_path, desired_language):
    """ Executes all operations in sequence for translating video from one language to another """
    # Step 1 extract audio from video and store it in audio_path
    extract_audio(video_path, audio_path)
    # Step 2 use audio_path to get the timestamped text
    timestamped_text = timestamped_transcription(audio_path)
    # Step 3 use timestamped text and translate to desired language
    translated_text = await timestamped_target_text(timestamped_text, dest=desired_language)
    # Step 4: Process the loaded translated text and generate audio with timestamps
    get_timestamp_adjusted_audio(translated_text, translated_audio_path)
    # Step 5
    replace_audio(video_path, translated_audio_path, output_video_path)
    # step 6: Generate subtitle file
    generate_subtitle_file(translated_text, subtitles_srt_path)
    #Step 7: Add subtitles to the video
    output_video_path = add_subtitles(output_video_path, subtitles_srt_path)
    
    return output_video_path
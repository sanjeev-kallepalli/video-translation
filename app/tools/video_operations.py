from moviepy import VideoFileClip
import ffmpeg


def extract_audio(video_path, output_audio_path):
    clip = VideoFileClip(video_path)
    clip.audio.write_audiofile(output_audio_path)


def replace_audio(original_video_path, new_audio_path, output_video_path):
    video_stream = ffmpeg.input(original_video_path)
    audio_stream = ffmpeg.input(new_audio_path)
    ffmpeg.output(video_stream.video, audio_stream.audio, 
                  output_video_path, vcodec='copy', acodec='aac', 
                  strict='experimental').run(overwrite_output=True)
    

def add_subtitles(output_video_path, subtitles_srt_path):
    try:
        file_name = f"final_{output_video_path.split('/')[-1]}"
        output_directory = '/'.join(output_video_path.split('/')[:-1])
        
        ffmpeg.input(output_video_path).output(output_directory + '/' + file_name, vf=f"subtitles={subtitles_srt_path}:force_style='Fontsize=36'").run()
        print(f"Subtitles added successfully to {output_directory + '/' + file_name}")
        return output_directory + '/' + file_name
    except ffmpeg.Error as e:
        print(f"An error occurred: {e.stderr.decode()}")
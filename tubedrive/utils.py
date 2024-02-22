import os
from pathlib import Path
from typing import List

from moviepy.editor import VideoFileClip
from moviepy.video.compositing.concatenate import concatenate_videoclips

from .models import VideoMp4


def create_file_if_not_exists(path: str):
    fle = Path(path)
    fle.touch(exist_ok=True)


def create_dir_if_not_exists(path: str):
    if not os.path.exists(path):
        os.makedirs(path)


def list_mp4_files_recursively(directory) -> list:
    result = []
    for root, dirs, files in os.walk(directory, topdown=True):
        dirs[:] = [d for d in dirs if d not in ['.tubedrive']]
        for file in files:
            if file.endswith(".mp4"):
                result.append(os.path.join(root, file))
    return result


def get_all_videos_mp4(files: list) -> List[VideoMp4]:
    result = []
    end_time_s = 0
    for file_path in files:
        file_clip = VideoFileClip(file_path)
        start_time_s = end_time_s
        end_time_s += file_clip.duration
        video_mp4 = VideoMp4(
            path=file_path,
            length_s=file_clip.duration,
            start_time_s=int(start_time_s),
            end_time_s=int(end_time_s),
        )
        result.append(video_mp4)
    return result


def concatenate_videos(video_clip_paths, output_path, method="compose"):
    """Concatenates several video files into one video file
    and save it to `output_path`. Note that extension (mp4, etc.) must be added to `output_path`
    `method` can be either 'compose' or 'reduce':
        `reduce`: Reduce the quality of the video to the lowest quality on the list of `video_clip_paths`.
        `compose`: type help(concatenate_videoclips) for the info"""
    # create VideoFileClip object for each video file
    clips = [VideoFileClip(c) for c in video_clip_paths]
    if method == "reduce":
        # calculate minimum width & height across all clips
        min_height = min([c.h for c in clips])
        min_width = min([c.w for c in clips])
        # resize the videos to the minimum
        clips = [c.resize(newsize=(min_width, min_height)) for c in clips]
        # concatenate the final video
        final_clip = concatenate_videoclips(clips)
    elif method == "compose":
        # concatenate the final video with the compose method provided by moviepy
        final_clip = concatenate_videoclips(clips, method="compose")
    # write the output video file
    final_clip.write_videofile(output_path)

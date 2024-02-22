import os
import sqlite3
from typing import List

from skinny_orm.sqlite_orm import SqliteOrm

from tubedrive.models import YoutubeVideo, VideoMp4, get_new_uuid
from tubedrive.utils import list_mp4_files_recursively, get_all_videos_mp4, concatenate_videos
from tubedrive.youtube_helper import YoutubeHelper

#CWD = os.getcwd()
CWD = 'C:\\Users\\amaya\\PycharmProjects\\tubedrive\\inputs'


def main():
    print(f"Current working dir: {CWD}")
    db_con = sqlite3.connect(f'{CWD}/tubedrive.db')
    orm = SqliteOrm(connection=db_con)

    files = list_mp4_files_recursively(directory=CWD)
    youtube_video_id = get_new_uuid()
    all_videos_mp4: List[VideoMp4] = get_all_videos_mp4(files, youtube_video_id)

    if len(all_videos_mp4) == 0:
        return

    concatenate_videos(files, output_path=f'{CWD}/concatenated.mp4')

    youtube_helper = YoutubeHelper()
    youtube_video: YoutubeVideo = youtube_helper.upload_video(youtube_video_id, f'{CWD}/concatenated.mp4')
    youtube_video.id = youtube_video_id
    orm.insert(youtube_video)
    orm.bulk_insert(all_videos_mp4)

    os.remove(f"{CWD}/concatenated.mp4")

    for video_mp4 in all_videos_mp4:
        with open(video_mp4.link_path, mode="w") as f:
            f.write(f'<script>window.location = "{youtube_video.url}?t={video_mp4.start_time_s}";</script>')
        os.remove(video_mp4.path)


if __name__ == '__main__':
    main()

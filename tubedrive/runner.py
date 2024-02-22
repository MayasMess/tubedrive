import logging
import os
import sqlite3
import sys
import time
from typing import List
import shutil
import typer
from skinny_orm.sqlite_orm import SqliteOrm

from .models import YoutubeVideo, VideoMp4, GcpClientSecret
from .utils import list_mp4_files_recursively, get_all_videos_mp4, create_dir_if_not_exists
from .youtube_helper import YoutubeHelper

CWD = os.getcwd()
TUBEDRIVE_PATH = os.path.join(CWD, '.tubedrive')
UPLOADED_PATH = os.path.join(TUBEDRIVE_PATH, '.uploaded')
create_dir_if_not_exists(TUBEDRIVE_PATH)
create_dir_if_not_exists(UPLOADED_PATH)
LIMIT_UPLOADS = 5
SLEEP_TIME = 10

logger: logging.Logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(name)s %(levelname)s - %(message)s',
    datefmt='%d-%m-%y %H:%M:%S',
    handlers=[logging.FileHandler(f'{TUBEDRIVE_PATH}/logs.log')]
)
logger.addHandler(logging.StreamHandler(sys.stdout))

app = typer.Typer()


@app.command()
def run(
        secret_path: str = typer.Option("", help="The path to your gcp client secret json file."),
        mock: bool = typer.Option(False, help="If true, mock the youtube upload to not use the api")
):
    logger.info(f"Running on directory: {CWD}")
    db_con = sqlite3.connect(f'{TUBEDRIVE_PATH}/tubedrive.db')
    orm = SqliteOrm(connection=db_con)

    gcp_client_secret = orm.select(GcpClientSecret).first()
    logger.info(f"Found gcp client secret path: {gcp_client_secret}")
    if gcp_client_secret is None:
        if not secret_path:
            secret_path = typer.prompt("What's the path of your gcp client secret json file ?")
        gcp_client_secret = GcpClientSecret(path=secret_path)
        orm.insert(gcp_client_secret)
    else:
        if secret_path:
            gcp_client_secret.path = secret_path
            logger.info(f"Updating gcp client secret: {gcp_client_secret}")
            orm.update(gcp_client_secret).using(GcpClientSecret.id)
    logger.info(f"gcp client secret: {gcp_client_secret}")

    video_uploaded_count = 0
    while True:

        if video_uploaded_count == LIMIT_UPLOADS:
            logger.info("Limit upload done!")
            break

        files = list_mp4_files_recursively(directory=CWD)
        all_videos_mp4: List[VideoMp4] = get_all_videos_mp4(files)[:1]  # Limiting to one video per run for now

        if len(all_videos_mp4) == 0:
            time.sleep(SLEEP_TIME)
            continue

        youtube_helper = YoutubeHelper(gcp_client_secret.path)
        for video_mp4 in all_videos_mp4:
            logger.info(f"Working with video {video_mp4.path}")
            youtube_video: YoutubeVideo = youtube_helper.upload_video(
                video_mp4.filename, f'{CWD}/{video_mp4.filename}', mock)
            video_uploaded_count += 1
            orm.insert(youtube_video)
            logger.info(f'{video_mp4.filename} uploaded => {youtube_video.url}')

            with open(video_mp4.link_path, mode="w") as f:
                f.write(f'<script>window.location = "{youtube_video.url}";</script>')

            logger.info(f"Move from {video_mp4.path} to {UPLOADED_PATH}/{video_mp4.filename}")
            shutil.move(video_mp4.path, f"{UPLOADED_PATH}/{video_mp4.filename}")

        orm.bulk_insert(all_videos_mp4)
        time.sleep(SLEEP_TIME)

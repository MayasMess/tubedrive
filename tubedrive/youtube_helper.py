import os

import google_auth_oauthlib.flow
import googleapiclient
from dotenv import load_dotenv
import googleapiclient.discovery
from googleapiclient.http import MediaFileUpload

from tubedrive.models import YoutubeVideo

load_dotenv()


class YoutubeHelper:
    YOUTUBE_UPLOAD_SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
    YOUTUBE_API_SERVICE_NAME = "youtube"
    YOUTUBE_API_VERSION = "v3"
    CLIENT_SECRET_FILE = os.getenv("yt_json_credentials")

    def __init__(self):
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            self.CLIENT_SECRET_FILE, self.YOUTUBE_UPLOAD_SCOPES)
        credentials = flow.run_local_server(port=8083)
        self.youtube = googleapiclient.discovery.build(
            self.YOUTUBE_API_SERVICE_NAME, self.YOUTUBE_API_VERSION, credentials=credentials)

    def upload_video(self, video_name: str, video_path: str) -> YoutubeVideo:
        request = self.youtube.videos().insert(
            part="snippet,status",
            body={
                "snippet": {
                    "categoryId": "22",
                    "description": "",
                    "title": video_name
                },
                "status": {
                    "privacyStatus": "private"
                }
            },
            media_body=MediaFileUpload(video_path)
        )
        response = request.execute()
        print(response)
        return YoutubeVideo(
            name=response["snippet"]["title"],
            path=video_path,
            url=f"vnd.youtube:{response['id']}"
        )

import os
import pickle

import google_auth_oauthlib.flow
import googleapiclient
import googleapiclient.discovery
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
from models import YoutubeVideo


class YoutubeHelper:
    YOUTUBE_UPLOAD_SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
    YOUTUBE_API_SERVICE_NAME = "youtube"
    YOUTUBE_API_VERSION = "v3"

    def __init__(self, gcp_client_secret_path: str, credentials_file: str = ".tubedrive/token.pickle"):
        # os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
        # flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        #     gcp_client_secret_path, self.YOUTUBE_UPLOAD_SCOPES)
        # credentials = flow.run_local_server(port=8083)

        credentials = None
        # Check if the credentials file exists and load it
        if os.path.exists(credentials_file):
            with open(credentials_file, "rb") as token:
                credentials = pickle.load(token)

        # If there are no valid credentials available, then either refresh the token or log in.
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            else:
                flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                    gcp_client_secret_path, self.YOUTUBE_UPLOAD_SCOPES)
                credentials = flow.run_local_server(port=8083)
            # Save the credentials for the next run
            with open(credentials_file, "wb") as token:
                pickle.dump(credentials, token)

        self.youtube = googleapiclient.discovery.build(
            self.YOUTUBE_API_SERVICE_NAME, self.YOUTUBE_API_VERSION, credentials=credentials)

    def upload_video(self, video_name: str, video_path: str, mock: bool = False) -> YoutubeVideo:
        if mock:
            return YoutubeVideo(video_name, video_path, 'this is a mock url')
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

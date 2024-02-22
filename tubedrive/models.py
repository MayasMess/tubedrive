from dataclasses import dataclass, field
import uuid
from pathlib import Path


def get_new_uuid() -> str:
    return str(uuid.uuid4())


@dataclass
class GcpClientSecret:
    path: str
    id: str = field(default_factory=get_new_uuid)


@dataclass
class VideoMp4:
    path: str
    length_s: int
    start_time_s: int
    end_time_s: int
    id: str = field(default_factory=get_new_uuid)
    youtube_id: str = None

    @property
    def link_path(self) -> str:
        return self.path.replace('.mp4', '.html')

    @property
    def filename(self) -> str:
        return Path(self.path).name


@dataclass
class YoutubeVideo:
    name: str
    path: str
    url: str
    id: str = field(default_factory=get_new_uuid)


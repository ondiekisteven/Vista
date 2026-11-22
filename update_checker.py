import json
import re
from urllib.error import URLError
from urllib.request import Request, urlopen

from packaging.version import InvalidVersion, Version
from PySide6.QtCore import QObject, Signal

from app_version import APP_VERSION


RELEASE_API_URL = "https://api.github.com/repos/ondiekisteven/Vista/releases/latest"


def get_latest_release():
    request = Request(
        RELEASE_API_URL,
        headers={
            "Accept": "application/vnd.github+json",
        },
    )
    with urlopen(request, timeout=8) as response:
        release = json.loads(response.read().decode("utf-8"))

    tag = release.get("tag_name", "")
    release_url = release.get("html_url", "")
    if not tag or not release_url:
        raise ValueError("GitHub returned an incomplete release")

    current = re.sub(r"^[vV]", "", APP_VERSION)
    latest = re.sub(r"^[vV]", "", tag)
    try:
        update_available = Version(latest) > Version(current)
    except InvalidVersion as error:
        raise ValueError("The app or release version is invalid") from error

    return tag, release_url, update_available


class UpdateCheckWorker(QObject):
    finished = Signal(str, str, bool)
    failed = Signal(str)

    def run(self):
        try:
            tag, url, available = get_latest_release()
            self.finished.emit(tag, url, available)
        except (URLError, TimeoutError, ValueError, json.JSONDecodeError) as error:
            self.failed.emit(str(error))

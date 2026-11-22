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
            "User-Agent": "Vista-update-checker",
        },
    )
    with urlopen(request, timeout=8) as response:
        print(response.read().decode("utf-8"))
        release = json.loads(response.read().decode("utf-8"))


get_latest_release()
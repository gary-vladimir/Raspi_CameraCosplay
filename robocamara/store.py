"""Captured photos with a time-to-live.

Each photo gets an unguessable token (its URL), is served only by that token,
and is deleted from the Pi automatically when its 10-minute timer runs out.
The store is shared between the capture loop and the web server, so it is
thread-safe.
"""
import os
import secrets
import shutil
import threading
import time
from dataclasses import dataclass

from . import config


@dataclass
class Photo:
    token: str
    path: str
    created: float
    expires: float


class PhotoStore:
    def __init__(self, ttl=config.PHOTO_TTL_SECONDS, directory=config.PHOTOS_DIR):
        self._ttl = ttl
        self._dir = str(directory)
        self._photos = {}
        self._latest = None
        self._lock = threading.Lock()
        self._reset_dir()

    def _reset_dir(self):
        # Never keep photos across restarts (privacy + clean slate).
        shutil.rmtree(self._dir, ignore_errors=True)
        os.makedirs(self._dir, exist_ok=True)

    def add(self, src_path) -> Photo:
        """Adopt a freshly captured file and return its Photo record."""
        token = secrets.token_urlsafe(16)
        now = time.time()
        dest = os.path.join(self._dir, token + ".jpg")
        shutil.move(str(src_path), dest)
        photo = Photo(token, dest, now, now + self._ttl)
        with self._lock:
            self._photos[token] = photo
            self._latest = token
        return photo

    def get(self, token):
        with self._lock:
            return self._photos.get(token)

    def latest(self):
        with self._lock:
            return self._photos.get(self._latest) if self._latest else None

    def remaining(self, token) -> int:
        photo = self.get(token)
        if not photo:
            return 0
        return max(0, int(photo.expires - time.time()))

    def cleanup(self):
        """Delete any photos whose timer has run out."""
        now = time.time()
        with self._lock:
            expired = [t for t, p in self._photos.items() if now >= p.expires]
            for token in expired:
                photo = self._photos.pop(token)
                try:
                    os.remove(photo.path)
                except OSError:
                    pass
                if self._latest == token:
                    self._latest = None

    def run_cleanup_loop(self):
        while True:
            self.cleanup()
            time.sleep(config.CLEANUP_INTERVAL_SECONDS)

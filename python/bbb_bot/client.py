"""High level client that mirrors the Go ``Client`` type.

The client wraps :class:`ApiClient` and exposes a small subset of the
functionality offered by the Go implementation.  It is intended as a starting
point for a more complete port and demonstrates how the Go design maps to
Python.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .api import ApiClient


@dataclass
class Client:
    """Represents a BigBlueButton client connection."""

    api: ApiClient
    join_url: Optional[str] = None

    @classmethod
    def from_config(cls, api_url: str, secret: str, sha: str = "SHA256") -> "Client":
        return cls(ApiClient(api_url, secret, sha))

    # ------------------------------------------------------------------
    def create(self, meeting_id: str, name: str, moderator_pw: str, attendee_pw: str) -> None:
        self.api.create(meeting_id, name, moderator_pw, attendee_pw)

    def join(self, meeting_id: str, full_name: str, password: str) -> str:
        self.join_url = self.api.join(meeting_id, full_name, password)
        return self.join_url

    def end(self, meeting_id: str, password: str) -> None:
        self.api.end(meeting_id, password)

    def leave(self) -> None:
        """Placeholder for future WebSocket disconnect logic."""
        self.join_url = None

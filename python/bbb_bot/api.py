"""Minimal BigBlueButton API client.

This module ports a subset of the Go API helper from this repository into
Python.  It focuses on constructing request URLs with the appropriate
checksum and performing HTTP GET requests.  Only the actions required for a
basic bot (``create``, ``join`` and ``end``) are implemented, but the class is
extensible and mirrors the behaviour of the Go implementation.
"""

from __future__ import annotations

import hashlib
import urllib.parse
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Dict, Optional

import requests


# Supported hashing algorithms
SHA1 = "SHA1"
SHA256 = "SHA256"


@dataclass
class ApiClient:
    """Helper for interacting with the BigBlueButton HTTP API."""

    url: str
    secret: str
    sha: str = SHA256

    def __post_init__(self) -> None:
        if not (self.url.startswith("http://") or self.url.startswith("https://")):
            raise ValueError("url has the wrong format. It should look like https://example.com/api/")
        if not self.url.endswith("/"):
            self.url += "/"
        if not self.url.endswith("api/"):
            self.url += "api/"
        if self.sha not in {SHA1, SHA256}:
            self.sha = SHA256

    # ------------------------------------------------------------------
    # URL helpers
    def _build_params(self, params: Dict[str, str]) -> str:
        encoded = [
            f"{urllib.parse.quote_plus(k)}={urllib.parse.quote_plus(v)}"
            for k, v in params.items()
        ]
        return "&".join(encoded)

    def _checksum(self, action: str, param_str: str) -> str:
        data = f"{action}{param_str}{self.secret}".encode()
        if self.sha == SHA1:
            return hashlib.sha1(data).hexdigest()
        return hashlib.sha256(data).hexdigest()

    def build_url(self, action: str, params: Optional[Dict[str, str]] = None) -> str:
        params = params or {}
        param_str = self._build_params(params)
        checksum = self._checksum(action, param_str)
        if param_str:
            return f"{self.url}{action}?{param_str}&checksum={checksum}"
        return f"{self.url}{action}?checksum={checksum}"

    # ------------------------------------------------------------------
    # Request helpers
    def _request(self, action: str, params: Dict[str, str]) -> ET.Element:
        url = self.build_url(action, params)
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return ET.fromstring(response.content)

    # ------------------------------------------------------------------
    # High level API methods
    def create(self, meeting_id: str, name: str, moderator_pw: str, attendee_pw: str) -> ET.Element:
        params = {
            "meetingID": meeting_id,
            "name": name,
            "moderatorPW": moderator_pw,
            "attendeePW": attendee_pw,
        }
        return self._request("create", params)

    def end(self, meeting_id: str, password: str) -> ET.Element:
        params = {"meetingID": meeting_id, "password": password}
        return self._request("end", params)

    def join(self, meeting_id: str, full_name: str, password: str) -> str:
        params = {
            "meetingID": meeting_id,
            "fullName": full_name,
            "password": password,
        }
        xml = self._request("join", params)
        # The join API returns an URL element on success.
        url = xml.findtext("url")
        if not url:
            raise RuntimeError("join response did not contain a URL")
        return url

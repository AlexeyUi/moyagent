""" GTTS Voice. """
from __future__ import annotations

import os

# import gtts
# from playsound import playsound

from .base import VoiceBase


class GTTSVoice(VoiceBase):
    """GTTS Voice отключён (заглушка без реального TTS)."""

    def _setup(self) -> None:
        pass

    def _speech(self, text: str, voice_id: int = 0) -> bool:
        """Заглушка: ничего не делает и всегда возвращает True."""
        return True


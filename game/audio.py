import math
from array import array
from pathlib import Path

import pygame


class AudioManager:
    """Локальные эффекты и заранее сгенерированные реплики персонажей."""

    def __init__(self, root: Path):
        self.root = root
        self.voice_dir = root / "assets" / "audio" / "voices"
        self.master_volume = 0.65
        self.sfx_volume = 0.75
        self.voice_volume = 0.85
        self.enabled = False
        self.sfx = {}
        self.voice_cache = {}
        self.last_voice = None
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)
            self.enabled = True
            self._build_sounds()
        except pygame.error:
            self.enabled = False

    @staticmethod
    def _sound(notes, duration=0.12, volume=0.35, tempo=1.0):
        sample_rate = 44100
        samples = array("h")
        for frequency in notes:
            count = max(1, int(sample_rate * duration * tempo))
            for index in range(count):
                envelope = min(1.0, index / 500, (count - index) / 1200)
                value = math.sin(2 * math.pi * frequency * index / sample_rate) * envelope * volume
                samples.append(int(value * 32767))
        return pygame.mixer.Sound(buffer=samples.tobytes())

    def _build_sounds(self):
        self.sfx = {
            "click": self._sound([280], 0.045, 0.22),
            "success": self._sound([440, 660, 880], 0.09, 0.28),
            "error": self._sound([180, 130], 0.13, 0.30),
        }

    @staticmethod
    def _set_volume(sound, volume):
        sound.set_volume(max(0.0, min(1.0, volume)))

    def play(self, name):
        if not self.enabled or name not in self.sfx:
            return
        sound = self.sfx[name]
        self._set_volume(sound, self.master_volume * self.sfx_volume)
        sound.play()

    def _load_voice(self, voice_key, action=None):
        filename = f"result_{action}.wav" if action else f"dialog_{voice_key}.wav"
        path = self.voice_dir / filename
        if not path.exists():
            return None
        if path not in self.voice_cache:
            try:
                self.voice_cache[path] = pygame.mixer.Sound(str(path))
            except pygame.error:
                self.voice_cache[path] = None
        return self.voice_cache[path]

    def speak(self, message, voice_key=None, action=None):
        """Проигрывает готовую реплику персонажа и запоминает её для повтора."""
        if not message:
            return
        self.last_voice = (message, voice_key, action)
        if not self.enabled:
            return
        sound = self._load_voice(voice_key, action) if voice_key else None
        if sound is None:
            base = 230 + (sum(ord(char) for char in message) % 100)
            sound = self._sound([base, base + 35, base + 70, base + 35], 0.075, 0.22, 0.9)
        self._set_volume(sound, self.master_volume * self.voice_volume)
        sound.play()

    def repeat_voice(self):
        if self.last_voice:
            self.speak(*self.last_voice)

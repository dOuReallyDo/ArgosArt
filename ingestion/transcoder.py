"""Smart Transcoder — Conversione automatica formati non supportati.

Risolve il pain point #1 di he.Art:
- HEIC → JPG (immagini iPhone)
- MOV → MP4 (video iPhone)
- WebM/AVI/MKV → MP4
- Resize se >150MB
- Normalizzazione audio per Whisper (16kHz mono)

Basato su FFmpeg + Pillow. Zero dipendenze cloud.
"""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

from core.logging import logger

# ── Configuration ──────────────────────────────────────────────
MAX_VIDEO_SIZE_MB = 150
MAX_IMAGE_SIZE_PX = 4096
TARGET_AUDIO_SR = 16000
TARGET_AUDIO_CHANNELS = 1


class Transcoder:
    """Converte automaticamente file in formati supportati dalla piattaforma."""

    async def transcode_if_needed(self, file_path: Path) -> Path:
        """Check if file needs transcoding, convert if so.

        Returns: Path to the (possibly transcoded) file.
        """
        suffix = file_path.suffix.lower()
        name = file_path.name

        # ── HEIC → JPG ──
        if suffix in (".heic", ".heif"):
            return await self._heic_to_jpg(file_path)

        # ── MOV → MP4 ──
        if suffix == ".mov":
            return await self._mov_to_mp4(file_path)

        # ── Non-MP4 video → MP4 ──
        if suffix in (".avi", ".mkv", ".webm", ".flv", ".wmv", ".divx", ".xvid"):
            return await self._to_mp4(file_path)

        # ── Audio con sample rate errato → 16kHz mono ──
        if suffix in (".wav", ".mp3", ".flac", ".m4a", ".aac", ".ogg"):
            return await self._normalize_audio(file_path)

        # ── RAW fotografici → JPG ──
        if suffix in (".cr2", ".nef", ".arw", ".dng", ".raf", ".rw2", ".orf"):
            return await self._raw_to_jpg(file_path)

        return file_path

    # ── Image Conversions ───────────────────────────────────────

    async def _heic_to_jpg(self, file_path: Path) -> Path:
        """Convert HEIC/HEIF to JPEG."""
        logger.info(f"🔄 Converting HEIC: {file_path.name}")
        try:
            from PIL import Image
            import pillow_heif

            pillow_heif.register_heif_opener()
            img = Image.open(str(file_path))
            img = img.convert("RGB")
            img = self._resize_if_large(img)

            out = file_path.with_suffix(".jpg")
            img.save(str(out), "JPEG", quality=90)
            logger.success(f"✅ HEIC→JPG: {file_path.name} ({file_path.stat().st_size:_d}B → {out.stat().st_size:_d}B)")
            return out
        except ImportError:
            logger.warning("pillow-heif not installed. HEIC files will fail.")
            return file_path

    async def _raw_to_jpg(self, file_path: Path) -> Path:
        """Convert RAW camera files to JPEG."""
        logger.info(f"🔄 Converting RAW: {file_path.name}")
        try:
            out = file_path.with_suffix(".jpg")
            subprocess.run(
                ["ffmpeg", "-i", str(file_path), "-q:v", "2", "-y", str(out)],
                capture_output=True, timeout=30, check=True,
            )
            logger.success(f"✅ RAW→JPG: {file_path.name}")
            return out
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.warning(f"RAW conversion failed for {file_path.name}")
            return file_path

    # ── Video Conversions ───────────────────────────────────────

    async def _mov_to_mp4(self, file_path: Path) -> Path:
        """Convert MOV to MP4 with H.264 codec."""
        return await self._to_mp4(file_path, codec="libx264")

    async def _to_mp4(self, file_path: Path, codec: str = "libx264") -> Path:
        """Generic video → MP4 conversion."""
        logger.info(f"🔄 Converting video to MP4: {file_path.name}")
        try:
            out = file_path.with_suffix(".mp4")
            # Get video size
            size_mb = file_path.stat().st_size / (1024 * 1024)

            if size_mb > MAX_VIDEO_SIZE_MB:
                # Reduce bitrate to fit 150MB
                target_bitrate = int((MAX_VIDEO_SIZE_MB * 8192) / self._get_duration(file_path)) - 128
                target_bitrate = max(target_bitrate, 500)
                cmd = [
                    "ffmpeg", "-i", str(file_path),
                    "-c:v", codec, "-b:v", f"{target_bitrate}k",
                    "-c:a", "aac", "-b:a", "128k",
                    "-movflags", "+faststart", "-y", str(out),
                ]
            else:
                cmd = [
                    "ffmpeg", "-i", str(file_path),
                    "-c:v", codec,
                    "-c:a", "aac", "-b:a", "128k",
                    "-movflags", "+faststart", "-y", str(out),
                ]

            subprocess.run(cmd, capture_output=True, timeout=120, check=True)
            logger.success(f"✅ Video→MP4: {file_path.name}")
            return out
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            logger.warning(f"Video conversion failed: {e}")
            return file_path

    # ── Audio Normalization ─────────────────────────────────────

    async def _normalize_audio(self, file_path: Path) -> Path:
        """Normalize audio to 16kHz mono WAV for Whisper."""
        try:
            # Check if already 16kHz mono
            info = self._get_audio_info(file_path)
            if info.get("sample_rate") == 16000 and info.get("channels") == 1:
                return file_path

            logger.info(f"🔄 Normalizing audio: {file_path.name}")
            out = file_path.with_suffix(".wav")
            subprocess.run([
                "ffmpeg", "-i", str(file_path),
                "-acodec", "pcm_s16le",
                "-ar", str(TARGET_AUDIO_SR),
                "-ac", str(TARGET_AUDIO_CHANNELS),
                "-y", str(out),
            ], capture_output=True, timeout=60, check=True)
            logger.success(f"✅ Audio normalized: {file_path.name}")
            return out
        except (subprocess.CalledProcessError, FileNotFoundError):
            return file_path

    # ── Helpers ─────────────────────────────────────────────────

    @staticmethod
    def _get_duration(file_path: Path) -> float:
        """Get video/audio duration in seconds."""
        try:
            result = subprocess.run([
                "ffprobe", "-v", "quiet", "-print_format", "json",
                "-show_format", str(file_path),
            ], capture_output=True, text=True, timeout=10)
            import json
            info = json.loads(result.stdout)
            return float(info.get("format", {}).get("duration", 30))
        except Exception:
            return 30  # Default assumption

    @staticmethod
    def _get_audio_info(file_path: Path) -> dict:
        try:
            result = subprocess.run([
                "ffprobe", "-v", "quiet", "-print_format", "json",
                "-show_streams", str(file_path),
            ], capture_output=True, text=True, timeout=10)
            import json
            info = json.loads(result.stdout)
            streams = info.get("streams", [])
            audio = [s for s in streams if s.get("codec_type") == "audio"]
            if audio:
                return {
                    "sample_rate": int(audio[0].get("sample_rate", 0)),
                    "channels": int(audio[0].get("channels", 0)),
                }
        except Exception:
            pass
        return {}

    @staticmethod
    def _resize_if_large(img, max_size: int = MAX_IMAGE_SIZE_PX):
        """Resize image if any side exceeds max_size."""
        w, h = img.size
        if w > max_size or h > max_size:
            ratio = min(max_size / w, max_size / h)
            new_size = (int(w * ratio), int(h * ratio))
            logger.info(f"  Resizing image: {w}x{h} → {new_size[0]}x{new_size[1]}")
            return img.resize(new_size, resample=img.LANCZOS if hasattr(img, 'LANCZOS') else 3)
        return img


# Singleton
transcoder = Transcoder()

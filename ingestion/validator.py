"""Validator — Checklist automatica materiali richiesti per candidatura.

Dal documento he.Art x AI: verifica che una candidatura includa tutti i materiali
richiesti dal bando prima di accettarla.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from core.logging import logger


@dataclass
class ValidationResult:
    """Result of a candidacy validation."""
    passed: bool = True
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    missing_items: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "passed": self.passed,
            "errors": self.errors,
            "warnings": self.warnings,
            "missing_items": self.missing_items,
        }


class CandidacyValidator:
    """Valida che una candidatura soddisfi tutti i requisiti del bando."""

    # Requisiti standard per ogni tipo di bando
    STANDARD_REQUIREMENTS = {
        "musical_performer": {
            "video_performance": {"min_count": 1, "max_size_mb": 150, "format": "mp4"},
            "cv_pdf": {"format": "pdf"},
            "photo_portrait": {"format": "jpg"},
            "photo_full_body": {"format": "jpg"},
        },
        "attore_cinema": {
            "cv_pdf": {"format": "pdf"},
            "photo_portrait": {"format": "jpg"},
            "showreel_link": {},
        },
        "ballerino": {
            "video_danza": {"min_count": 1, "max_size_mb": 150, "format": "mp4"},
            "cv_pdf": {"format": "pdf"},
            "photo_portrait": {"format": "jpg"},
        },
    }

    async def validate(
        self,
        files: list[Path],
        job_type: str,
        custom_requirements: Optional[dict] = None,
    ) -> ValidationResult:
        """Validate a set of files against job requirements.

        Args:
            files: List of uploaded file paths
            job_type: Type of job (musical_performer, attore_cinema, ballerino, etc.)
            custom_requirements: Optional custom requirement overrides

        Returns:
            ValidationResult with errors/warnings
        """
        result = ValidationResult()
        reqs = custom_requirements or self.STANDARD_REQUIREMENTS.get(
            job_type, self._default_requirements()
        )

        # Check each required item
        for item_name, item_reqs in reqs.items():
            found = self._find_matching_files(files, item_name, item_reqs)
            if not found:
                result.errors.append(f"Mancante: {item_name}")
                result.missing_items.append(item_name)
                result.passed = False
            else:
                for f in found:
                    warnings = self._check_file_quality(f, item_name, item_reqs)
                    result.warnings.extend(warnings)

        # Check format compatibility
        for f in files:
            if not self._is_supported_format(f):
                result.errors.append(f"Formato non supportato: {f.name}")
                result.passed = False

        logger.info(
            f"Validation {job_type}: {'PASSED' if result.passed else 'FAILED'} "
            f"({len(result.errors)} errors, {len(result.warnings)} warnings)"
        )

        return result

    @staticmethod
    def _find_matching_files(files: list[Path], item_name: str, reqs: dict) -> list[Path]:
        """Find files matching a required item."""
        target_format = reqs.get("format", "")
        matching = []
        for f in files:
            suffix = f.suffix.lower().lstrip(".")
            if target_format and suffix in (target_format, target_format.lstrip(".")):
                matching.append(f)
            elif not target_format:
                matching.append(f)
        return matching

    @staticmethod
    def _check_file_quality(file_path: Path, item_name: str, reqs: dict) -> list[str]:
        """Check individual file quality against requirements."""
        warnings = []
        max_size = reqs.get("max_size_mb")
        if max_size:
            actual_mb = file_path.stat().st_size / (1024 * 1024)
            if actual_mb > max_size:
                warnings.append(
                    f"File troppo grande: {file_path.name} ({actual_mb:.1f}MB > {max_size}MB)"
                )
        return warnings

    @staticmethod
    def _is_supported_format(file_path: Path) -> bool:
        """Check if file format is supported by he.Art platform."""
        suffix = file_path.suffix.lower()
        supported_video = {".mp4"}
        supported_image = {".jpg", ".jpeg", ".png", ".pdf"}
        supported_docs = {".pdf", ".docx", ".txt"}
        return suffix in (supported_video | supported_image | supported_docs)

    @staticmethod
    def _default_requirements() -> dict:
        """Default minimal requirements."""
        return {
            "cv_pdf": {"format": "pdf"},
            "photo_portrait": {"format": "jpg"},
        }

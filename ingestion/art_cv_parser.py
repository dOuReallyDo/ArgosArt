"""CV Parser Artistico — Estrazione strutturata da CV di artisti (PDF).

Gestisce CV di performer, attori, cantanti, ballerini con estrazione di:
- Dati fisici (altezza, peso, occhi, capelli, taglie, scarpe)
- Dati vocali (timbro, range, registro)
- Skills (danza, canto, recitazione, sport, strumenti musicali)
- Esperienze professionali (produzioni, ruoli, registi)
- Formazione (accademie, masterclass, workshop)
- Lingue e dialetti
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ArtistProfile:
    """Profilo strutturato di un artista estratto dal CV."""

    # Identità
    full_name: str = ""
    birth_date: str = ""
    birth_place: str = ""
    email: str = ""
    phone: str = ""
    residence: str = ""
    domicile: str = ""

    # Dati fisici
    height_cm: str = ""
    weight_kg: str = ""
    eyes: str = ""
    hair: str = ""
    measurements: str = ""  # Es: "88-70-88"
    jacket_size: str = ""
    pants_size: str = ""
    shoe_size: str = ""
    scenic_age: str = ""  # Età scenica, es. "17-28 anni"

    # Dati vocali
    voice_type: str = ""  # Soprano, Tenore, Baritono, etc.
    voice_range: str = ""  # Es. "G2-B4"
    vocal_subtype: str = ""  # Drammatico, Lirico, Leggero
    vocal_technique: str = ""  # Belt, Legit, Mix

    # Skills
    dance_styles: list[str] = field(default_factory=list)
    sports: list[str] = field(default_factory=list)
    instruments: list[str] = field(default_factory=list)
    acting_skills: list[str] = field(default_factory=list)

    # Formazione
    education: list[str] = field(default_factory=list)
    masterclasses: list[str] = field(default_factory=list)
    certifications: list[str] = field(default_factory=list)

    # Esperienze
    theatre_experiences: list[dict] = field(default_factory=list)
    tv_cinema_experiences: list[dict] = field(default_factory=list)
    other_experiences: list[str] = field(default_factory=list)

    # Lingue
    languages: list[dict] = field(default_factory=list)  # [{name, level}]
    dialects: list[str] = field(default_factory=list)

    # Link
    showreel_urls: list[str] = field(default_factory=list)
    social_links: list[str] = field(default_factory=list)
    website: str = ""

    # Availability
    available_national: bool = False
    available_international: bool = False
    driving_license: str = ""

    # Raw text for embedding
    raw_text: str = ""

    def to_searchable_text(self) -> str:
        """Genera un testo ricercabile semanticamente per l'embedding."""
        parts = [
            f"Artista: {self.full_name}",
            f"Voce: {self.voice_type} {self.voice_subtype}".strip(),
            f"Range vocale: {self.voice_range}" if self.voice_range else "",
            f"Tecnica vocale: {self.vocal_technique}" if self.vocal_technique else "",
            f"Altezza: {self.height_cm}" if self.height_cm else "",
            f"Età scenica: {self.scenic_age}" if self.scenic_age else "",
            f"Occhi: {self.eyes}, Capelli: {self.hair}" if self.eyes else "",
            f"Taglie: {self.measurements}" if self.measurements else "",
            f"Scarpe: {self.shoe_size}" if self.shoe_size else "",
            f"Danza: {', '.join(self.dance_styles)}" if self.dance_styles else "",
            f"Sport: {', '.join(self.sports)}" if self.sports else "",
            f"Strumenti: {', '.join(self.instruments)}" if self.instruments else "",
            f"Lingue: {', '.join(l['name'] + ' ' + l['level'] for l in self.languages)}" if self.languages else "",
            f"Dialetti: {', '.join(self.dialects)}" if self.dialects else "",
            f"Formazione: {'; '.join(self.education[:5])}" if self.education else "",
            f"Esperienze: {'; '.join(e.get('production','') for e in self.theatre_experiences[:5])}" if self.theatre_experiences else "",
            f"Disponibilità: {'Nazionale' if self.available_national else ''} {'Internazionale' if self.available_international else ''}".strip(),
        ]
        return "\n".join(p for p in parts if p.strip())

    def to_tags(self) -> list[str]:
        """Genera tag per il profilo artista."""
        tags = []
        if self.voice_type:
            tags.append(self.voice_type.lower().replace(" ", "_"))
        if self.vocal_subtype:
            tags.append(self.vocal_subtype.lower().replace(" ", "_"))
        if self.voice_range:
            tags.append(f"range_{self.voice_range.replace(' ', '')}")
        tags.extend(f"danza_{s.lower().replace(' ', '_')}" for s in self.dance_styles)
        tags.extend(f"sport_{s.lower().replace(' ', '_')}" for s in self.sports)
        tags.extend(f"strumento_{s.lower().replace(' ', '_')}" for s in self.instruments)
        tags.extend(f"lingua_{l['name'].lower()}" for l in self.languages)
        tags.extend(f"dialetto_{d.lower()}" for d in self.dialects)
        if self.height_cm:
            tags.append(f"altezza_{self.height_cm.replace(' ','')}")
        return tags


class ArtistCVParser:
    """Parser specializzato per CV artistici in formato PDF.

    Estrae informazioni strutturate usando pattern recognition
    su CV di performer/attori/cantanti/ballerini.
    """

    async def parse(self, file_path: Path, raw_text: str = "") -> ArtistProfile:
        """Parse a CV PDF into a structured ArtistProfile."""
        import asyncio

        loop = asyncio.get_running_loop()

        def _parse():
            if not raw_text:
                import pdfplumber
                with pdfplumber.open(str(file_path)) as pdf:
                    texts = []
                    for page in pdf.pages:
                        t = page.extract_text()
                        if t:
                            texts.append(t)
                    raw_text = "\n".join(texts)
            return self._extract_profile(raw_text)

        profile = await loop.run_in_executor(None, _parse)
        return profile

    def _extract_profile(self, text: str) -> ArtistProfile:
        """Estrae tutte le informazioni dal testo del CV."""
        p = ArtistProfile(raw_text=text)
        text_lower = text.lower()

        # ── Nome ──
        p.full_name = self._extract_name(text)

        # ── Contatti ──
        p.email = self._extract_email(text)
        p.phone = self._extract_phone(text)

        # ── Nascita/Residenza ──
        p.birth_date = self._extract_birth_date(text)
        p.birth_place = self._extract_birth_place(text)
        p.residence = self._extract_pattern(text, r"(?:residenza|domicilio)[:\s]+([^,\n]+)", default="")

        # ── Dati fisici ──
        p.height_cm = self._extract_height(text)
        p.weight_kg = self._extract_weight(text)
        p.eyes = self._extract_eyes(text)
        p.hair = self._extract_hair(text)
        p.measurements = self._extract_measurements(text)
        p.shoe_size = self._extract_shoe_size(text)
        p.scenic_age = self._extract_scenic_age(text)
        p.jacket_size = self._extract_jacket_size(text)
        p.pants_size = self._extract_pants_size(text)

        # ── Dati vocali ──
        p.voice_type = self._extract_voice_type(text)
        p.voice_range = self._extract_voice_range(text)
        p.vocal_subtype = self._extract_vocal_subtype(text, p.voice_type)
        p.vocal_technique = self._extract_vocal_technique(text)

        # ── Skills ──
        p.dance_styles = self._extract_dance_styles(text)
        p.sports = self._extract_sports(text)
        p.instruments = self._extract_instruments(text)

        # ── Lingue ──
        p.languages = self._extract_languages(text)
        p.dialects = self._extract_dialects(text)

        # ── Formazione ──
        p.education = self._extract_education(text)
        p.masterclasses = self._extract_masterclasses(text)

        # ── Esperienze ──
        p.theatre_experiences = self._extract_theatre(text)
        p.tv_cinema_experiences = self._extract_tv_cinema(text)

        # ── Disponibilità ──
        p.available_national = "nazionale" in text_lower or "territorio nazionale" in text_lower
        p.available_international = "internazionale" in text_lower
        p.driving_license = self._extract_driving_license(text)

        # ── Link ──
        p.showreel_urls = self._extract_urls(text)
        p.social_links = self._extract_social(text)

        return p

    # ── Pattern Extractors ──────────────────────────────────────

    @staticmethod
    def _extract_pattern(text: str, pattern: str, default: str = "") -> str:
        m = re.search(pattern, text, re.IGNORECASE)
        return m.group(1).strip() if m and m.group(1) else default

    @staticmethod
    def _extract_name(text: str) -> str:
        """Estrae il nome — tipicamente le prime righe in maiuscolo."""
        lines = text.strip().split("\n")
        for line in lines[:5]:
            stripped = line.strip()
            # Skip non-name lines
            if any(kw in stripped.lower() for kw in ["cv", "curriculum", "profilo", "dati personal", "contatti"]):
                continue
            # Names are usually short all-uppercase or title case
            words = stripped.split()
            if 2 <= len(words) <= 4 and all(w[0].isupper() for w in words if w.isalpha()):
                return stripped
        return ""

    @staticmethod
    def _extract_email(text: str) -> str:
        m = re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", text)
        return m.group(0).strip() if m else ""

    @staticmethod
    def _extract_phone(text: str) -> str:
        m = re.search(r"(?:\+39\s?)?\d{3}[\s-]?\d{3}[\s-]?\d{4}", text)
        return m.group(0).strip() if m else ""

    @staticmethod
    def _extract_birth_date(text: str) -> str:
        patterns = [
            r"nata?(?:\s+il)?\s+(\d{2}[/-]\d{2}[/-]\d{2,4})",
            r"data\s+di\s+nascita[:\s]+(\d{2}[/-]\d{2}[/-]\d{2,4})",
        ]
        for pat in patterns:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                return m.group(1)
        return ""

    @staticmethod
    def _extract_birth_place(text: str) -> str:
        m = re.search(r"(?:nata?(?:\s+a)?|nato(?:\s+a)?)\s+([A-ZÀ-Ü][a-zà-ü]+(?:\s+[A-ZÀ-Ü][a-zà-ü]+)?)", text, re.IGNORECASE)
        if not m:
            m = re.search(r"(?:Foggia|Roma|Milano|Torino|Padova|Napoli|Firenze|Bologna|Genova|Palermo|Cuneo|San Miniato)", text, re.IGNORECASE)
        return m.group(0).strip() if m else ""

    @staticmethod
    def _extract_height(text: str) -> str:
        m = re.search(r"(?:altezza|height)[:\s]*(\d[\d,.]*\s*(?:cm|m|CM|M)?)", text, re.IGNORECASE)
        return m.group(1).strip() if m else ""

    @staticmethod
    def _extract_weight(text: str) -> str:
        m = re.search(r"(?:peso|weight)[:\s]*(\d+[\s]*(?:kg|KG)?)", text, re.IGNORECASE)
        return m.group(1).strip() if m else ""

    @staticmethod
    def _extract_eyes(text: str) -> str:
        colors = ["castani", "castano scuro", "marroni", "celesti", "azzurri", "verdi", "neri", "nocciola"]
        for c in colors:
            if re.search(rf"(?:occhi|eyes)[:\s]*{c}", text, re.IGNORECASE):
                return c
        return ""

    @staticmethod
    def _extract_hair(text: str) -> str:
        colors = ["biondi", "biondo cenere", "castani", "neri", "rossi", "mori", "bianchi"]
        for c in colors:
            if re.search(rf"(?:capelli|hair)[:\s]*{c}", text, re.IGNORECASE):
                return c
        return ""

    @staticmethod
    def _extract_measurements(text: str) -> str:
        m = re.search(r"(?:taglie?|misure?)[:\s]*(\d{2,3}\s*[-–—]\s*\d{2,3}\s*[-–—]\s*\d{2,3})", text, re.IGNORECASE)
        return m.group(1).replace(" ", "") if m else ""

    @staticmethod
    def _extract_shoe_size(text: str) -> str:
        m = re.search(r"(?:scarpa|scarpe|shoe)[:\s]*(\d{2}(?:[.,]\d)?\s*(?:IT|EU|UK|US)?)", text, re.IGNORECASE)
        return m.group(1).strip() if m else ""

    @staticmethod
    def _extract_scenic_age(text: str) -> str:
        m = re.search(r"(?:età\s+scenica|età\s+apparente|scenic\s+age)[:\s]*(\d{1,2}\s*[-–—]\s*\d{1,2}\s*(?:anni)?)", text, re.IGNORECASE)
        return m.group(1).strip() if m else ""

    @staticmethod
    def _extract_jacket_size(text: str) -> str:
        m = re.search(r"(?:giacca|jacket)[:\s]*([A-Za-z0-9/]+)", text, re.IGNORECASE)
        return m.group(1).strip() if m else ""

    @staticmethod
    def _extract_pants_size(text: str) -> str:
        m = re.search(r"(?:pantaloni?|pants)[:\s]*(\d{2,3}[/.]?\d{0,2})", text, re.IGNORECASE)
        return m.group(1).strip() if m else ""

    @staticmethod
    def _extract_voice_type(text: str) -> str:
        voice_types = [
            "Soprano", "Mezzosoprano", "Contralto",
            "Tenore", "Baritono", "Basso",
            "Sopranista", "Controtenore",
        ]
        text_lower = text.lower()
        for vt in voice_types:
            if vt.lower() in text_lower:
                # Check for subtype like "Soprano Drammatico"
                subtype_match = re.search(rf"{vt}\s+([A-Za-zÀ-Ü]+)", text, re.IGNORECASE)
                return vt
        return ""

    @staticmethod
    def _extract_voice_range(text: str) -> str:
        m = re.search(r"(?:range|estensione|registro)[:\s]*([A-G][#b]?\d\s*[-–—]\s*[A-G][#b]?\d)", text, re.IGNORECASE)
        if not m:
            m = re.search(r"([A-G][#b]?\d\s*[-–—]\s*[A-G][#b]?\d)", text)
        return m.group(1).replace(" ", "") if m else ""

    @staticmethod
    def _extract_vocal_subtype(text: str, voice_type: str) -> str:
        if not voice_type:
            return ""
        subtypes = ["Drammatico", "Lirico", "Leggero", "Spinto", "Assoluto", "Coloratura"]
        for st in subtypes:
            if st.lower() in text.lower():
                return st
        return ""

    @staticmethod
    def _extract_vocal_technique(text: str) -> str:
        techniques = ["belt", "legit", "mix", "falsetto", "growl", "scream", "vibrato"]
        for t in techniques:
            if t in text.lower():
                return t
        return ""

    @staticmethod
    def _extract_dance_styles(text: str) -> list[str]:
        dance_keywords = [
            "moderno", "contemporaneo", "contemporanea", "jazz", "hip hop", "hip-hop",
            "funky", "caraibico", "caraibica", "burlesque", "orientale", "balletto",
            "classica", "tip tap", "valzer", "espressiva", "teatrodanza",
            "latino americano", "salsa", "tango", "flamenco", "break dance",
            "pole dance", "aerial", "acro dance",
        ]
        found = []
        text_lower = text.lower()
        for d in dance_keywords:
            if d in text_lower:
                found.append(d)
        return found

    @staticmethod
    def _extract_sports(text: str) -> list[str]:
        sport_keywords = [
            "pallavolo", "pattinaggio", "acrobatica", "nuoto", "equitazione",
            "scherma", "combattimento scenico", "atletica", "calcio", "basket",
            "skate", "boxe", "ginnastica", "arti marziali", "yoga", "pilates",
            "arrampicata", "sci", "snowboard", "surf",
        ]
        found = []
        text_lower = text.lower()
        for s in sport_keywords:
            if s in text_lower:
                found.append(s)
        return found

    @staticmethod
    def _extract_instruments(text: str) -> list[str]:
        instr_keywords = [
            "chitarra", "pianoforte", "batteria", "basso", "violino",
            "ukulele", "sassofono", "tromba", "flauto", "arpa",
            "violoncello", "fisarmonica", "tastiera",
        ]
        found = []
        text_lower = text.lower()
        for ins in instr_keywords:
            if ins in text_lower:
                found.append(ins)
        return found

    @staticmethod
    def _extract_languages(text: str) -> list[dict]:
        results = []
        # Pattern: "Lingua: Livello" or "Lingua - Livello"
        matches = re.findall(
            r"(?:inglese|english|francese|french|spagnolo|spanish|tedesco|german|italiano|italian)\s*[:–—-]*\s*(?:livello\s*)?([A-C][12]|madrelingua|avanzato|intermedio|base|bilingual)",
            text, re.IGNORECASE
        )
        # Also try explicit sections
        lang_section = re.search(r"(?:lingue|languages)[:\s]*(.*?)(?:\n\n|\n[A-Z]{2,}|$)", text, re.IGNORECASE | re.DOTALL)
        if lang_section:
            section_text = lang_section.group(1)
            lang_pairs = re.findall(
                r"(inglese|english|francese|french|spagnolo|spanish|tedesco|german|italiano|italian|portoghese|portuguese|cinese|chinese)\s*[-:–—]*\s*(madrelingua|bilingual|[A-C][12]|avanzato|intermedio|base)",
                section_text, re.IGNORECASE
            )
            for name, level in lang_pairs:
                level_clean = level.lower().replace("avanzato", "B2").replace("intermedio", "B1").replace("base", "A1")
                results.append({"name": name, "level": level_clean})

        if not results:
            # Fallback
            for lang in ["inglese", "francese", "spagnolo", "tedesco"]:
                m = re.search(rf"{lang}[:\s]*([A-C][12]|avanzato|intermedio|base)", text, re.IGNORECASE)
                if m:
                    level = m.group(1).lower().replace("avanzato","B2").replace("intermedio","B1").replace("base","A1")
                    results.append({"name": lang, "level": level})

        return results

    @staticmethod
    def _extract_dialects(text: str) -> list[str]:
        dialects = [
            "romano", "napoletano", "toscano", "milanese", "siciliano",
            "veneto", "pugliese", "sardo", "calabrese", "ligure",
            "piemontese", "lombardo", "emiliano", "umbro", "marchigiano",
            "abruzzese", "laziale", "ciociaro",
        ]
        found = []
        text_lower = text.lower()
        for d in dialects:
            if d in text_lower:
                found.append(d)
        return found

    @staticmethod
    def _extract_education(text: str) -> list[str]:
        schools = []
        patterns = [
            r"(?:diploma(?:to|ta)|laurea(?:to|ta)|certificat[oa])\s+(?:presso|in|come)\s+(.+?)(?:\n|$|\.)",
            r"(?:accademia|scuola|istituto|conservatorio|università)\s+(?:di\s+)?(.+?)(?:\n|$|\.)",
        ]
        for pat in patterns:
            for m in re.finditer(pat, text, re.IGNORECASE):
                schools.append(m.group(0).strip())
        return schools

    @staticmethod
    def _extract_masterclasses(text: str) -> list[str]:
        masters = []
        for m in re.finditer(r"(?:masterclass|workshop|stage|corso)\s+(?:con|di|presso)\s+(.+?)(?:\n|$|\.)", text, re.IGNORECASE):
            masters.append(m.group(0).strip())
        return masters

    @staticmethod
    def _extract_theatre(text: str) -> list[dict]:
        """Extract theatre/musical experiences."""
        experiences = []
        # Pattern: "Production" regia di "Director"
        matches = re.findall(
            r"[«""]([^»""]+)[»""]\s*,?\s*regia\s+(?:di\s+)?([^,\n]+)",
            text
        )
        for production, director in matches:
            experiences.append({
                "production": production.strip(),
                "director": director.strip(),
                "type": "theatre",
            })
        # Also match unquoted productions
        matches2 = re.findall(
            r"([A-ZÀ-Ü][^,\n]{3,60}?),\s*regia\s+(?:di\s+)?([^,\n]{3,40})",
            text
        )
        for production, director in matches2:
            if not any(e["production"] == production.strip() for e in experiences):
                experiences.append({
                    "production": production.strip(),
                    "director": director.strip(),
                    "type": "theatre",
                })
        return experiences

    @staticmethod
    def _extract_tv_cinema(text: str) -> list[dict]:
        experiences = []
        matches = re.findall(
            r"(?:ruolo|coprotagonista|protagonista)(?:\s+di\s+puntata)?\s+(?:in|nel)\s+([^,\n]+?)(?:,|\s+regia\s+(?:di\s+)?([^,\n]+))?",
            text, re.IGNORECASE
        )
        for production, director in matches:
            experiences.append({
                "production": production.strip(),
                "director": (director or "").strip(),
                "type": "tv_cinema",
            })
        return experiences

    @staticmethod
    def _extract_urls(text: str) -> list[str]:
        urls = re.findall(r"https?://[^\s\n]+", text)
        return [u.strip() for u in urls if len(u) > 10]

    @staticmethod
    def _extract_social(text: str) -> list[str]:
        socials = []
        handles = re.findall(r"@\w[\w.]*", text)
        return handles

    @staticmethod
    def _extract_driving_license(text: str) -> str:
        m = re.search(r"patente\s+(?:di\s+)?(?:tipo\s+)?([AB][\s,AB]*)", text, re.IGNORECASE)
        return m.group(1).strip() if m else ""

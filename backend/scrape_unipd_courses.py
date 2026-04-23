import argparse
import csv
import re
import sys
import time
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from urllib.parse import parse_qs, urljoin, urlparse

import requests
from bs4 import BeautifulSoup, Tag


DEFAULT_OUTPUT_PATH = Path("/home/atul-nayak/book/unipd_courses_scraped.csv")
DEFAULT_ACADEMIC_YEAR = "2025"
CONNECT_TIMEOUT_SECONDS = 10
READ_TIMEOUT_SECONDS = 60
MAX_FETCH_ATTEMPTS = 3
COURSE_CATALOGUE_API_URL = "https://unipd.coursecatalogue.cineca.it/api/v1/corsi"

# Official UniPd entry pages collected from the public course catalogue.
SEED_URLS = [
    "https://www.unipd.it/corsi-laurea",
    "https://www.unipd.it/corsi-laurea-lingua-inglese",
    "https://www.unipd.it/corsi-laurea-magistrale-lingua-inglese",
    "https://www.scienzeumane.unipd.it/corsi/corsi-di-laurea",
    "https://www.scienzeumane.unipd.it/en/corsi-di-laurea-magistrale-ciclo-unico",
    "https://www.medicinachirurgia.unipd.it/corsi-di-laurea-magistrale-ciclo-unico",
    "https://www.medicinachirurgia.unipd.it/offerta-formativa/corsi-di-laurea-magistrale-ciclo-unico",
    "https://www.agrariamedicinaveterinaria.unipd.it/corsi/corsi-di-laurea-magistrale-ciclo-unico",
]

ALLOWED_HOST_SUFFIXES = ("unipd.it",)
DISALLOWED_PATH_FRAGMENTS = (
    "ante-riforma",
    "disattivati",
    "archivio",
    "archivi",
    "archived",
)

GENERIC_SUBJECT_LABELS = {
    "elenco insegnamenti",
    "descrizione del percorso formativo",
    "collegamenti utili",
    "approfondimento",
    "curricula",
    "programma",
    "programmi",
    "course units",
    "programme structure",
}

YEAR_PATTERN = re.compile(r"\b([1-6])(?:\s*[°ºo]\s*anno|\s*year)\b", re.IGNORECASE)
PROGRAM_PREFIX_PATTERN = re.compile(
    r"^(Corso di laurea magistrale in|Corso di laurea in|Single-cycle degree in|Master['’]s degree in|Bachelor['’]s degree in)\s+",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class CourseRecord:
    department: str
    program: str
    year: str
    subject: str


class UniPdCourseScraper:
    def __init__(self, academic_year: str, crawl_delay: float = 0.15):
        self.academic_year = academic_year
        self.crawl_delay = crawl_delay
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (X11; Linux x86_64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/126.0.0.0 Safari/537.36"
                )
            }
        )

    def scrape(self) -> list[CourseRecord]:
        records: set[CourseRecord] = set()
        payload = self._fetch_json(f"{COURSE_CATALOGUE_API_URL}?anno={self.academic_year}")
        courses = list(self._iter_catalogue_courses(payload))
        print(f"Discovered {len(courses)} candidate course entries.")

        for index, course in enumerate(courses, start=1):
            records.update(self._extract_records_from_course(course))
            if index % 25 == 0:
                print(f"Processed {index}/{len(courses)} course entries...")

        return sorted(
            records,
            key=lambda item: (item.department.lower(), item.program.lower(), item.year, item.subject.lower()),
        )

    def _fetch_json(self, url: str) -> object:
        text = self._fetch_text(url)
        if not text:
            return []
        return requests.models.complexjson.loads(text)

    def _iter_catalogue_courses(self, node: object) -> Iterable[dict]:
        if isinstance(node, dict):
            if node.get("cdsCod") and node.get("percorsi"):
                yield node
            for value in node.values():
                yield from self._iter_catalogue_courses(value)
            return

        if isinstance(node, list):
            for item in node:
                yield from self._iter_catalogue_courses(item)

    def _extract_records_from_course(self, course: dict) -> set[CourseRecord]:
        department = self._extract_catalogue_department_name(course)
        program = self._build_catalogue_program_name(course)
        records: set[CourseRecord] = set()

        for percorso in course.get("percorsi", []):
            percorso_name = self._clean_text(percorso.get("des_it") or percorso.get("des_en") or "")
            percorso_suffix = ""
            if percorso_name and percorso_name.upper() != "PERCORSO COMUNE":
                percorso_suffix = f" - {percorso_name}"

            for year_entry in percorso.get("anni", []):
                year = str(year_entry.get("anno", "")).strip()
                if not year:
                    continue

                for insegnamento_group in year_entry.get("insegnamenti", []):
                    for attivita in insegnamento_group.get("attivita", []):
                        subject = self._normalize_subject(
                            attivita.get("des_it") or attivita.get("des_en") or ""
                        )
                        if not subject:
                            continue

                        records.add(
                            CourseRecord(
                                department=department,
                                program=f"{program}{percorso_suffix}",
                                year=year,
                                subject=subject,
                            )
                        )

        return records

    def _build_catalogue_program_name(self, course: dict) -> str:
        course_code = self._clean_text(course.get("cdsCod") or "")
        course_name = self._clean_text(course.get("des_it") or course.get("des_en") or "")
        if course_code and course_name:
            return f"[{course_code}] {course_name}"
        return course_name or course_code or "[UNKNOWN] Unknown course"

    def _extract_catalogue_department_name(self, course: dict) -> str:
        structures = course.get("strutture") or []
        for structure in structures:
            if structure.get("respDidFlg") == 1:
                name = self._clean_text(structure.get("descrizione_it") or structure.get("descrizione_en") or "")
                if name:
                    return name

        for structure in structures:
            name = self._clean_text(structure.get("descrizione_it") or structure.get("descrizione_en") or "")
            if name:
                return name

        category = self._clean_text(course.get("categoria_des_it") or course.get("categoria_des_en") or "")
        if category:
            return category
        return "University of Padua"

    def _discover_course_urls(self) -> set[str]:
        queue = list(SEED_URLS)
        visited: set[str] = set()
        discovered_detail_urls: set[str] = set()

        while queue:
            url = queue.pop(0)
            normalized_url = self._normalize_url(url)
            if normalized_url in visited:
                continue
            visited.add(normalized_url)

            html = self._fetch_text(normalized_url)
            if not html:
                continue

            soup = BeautifulSoup(html, "html.parser")
            for anchor in soup.find_all("a", href=True):
                href = anchor.get("href", "").strip()
                candidate_url = self._normalize_url(urljoin(normalized_url, href))
                if not self._is_allowed_url(candidate_url):
                    continue
                if self._looks_like_course_detail_url(candidate_url):
                    discovered_detail_urls.add(candidate_url)
                elif self._looks_like_catalogue_page(candidate_url) and candidate_url not in visited:
                    queue.append(candidate_url)

        return {
            url for url in discovered_detail_urls if self._matches_academic_year(url)
        }

    def _scrape_course_page(self, url: str) -> set[CourseRecord]:
        html = self._fetch_text(url)
        if not html:
            return set()

        soup = BeautifulSoup(html, "html.parser")
        query_params = parse_qs(urlparse(url).query)
        course_code = query_params.get("key", ["UNKNOWN"])[0].strip().upper()

        program_name = self._extract_program_name(soup)
        if not program_name:
            raise ValueError("Could not determine program name")
        full_program_name = f"[{course_code}] {program_name}"

        department = self._extract_department_name(soup, query_params)
        subjects_by_year = self._extract_subjects_by_year(soup)
        if not subjects_by_year:
            return set()

        records: set[CourseRecord] = set()
        for year, subjects in subjects_by_year.items():
            for subject in subjects:
                records.add(
                    CourseRecord(
                        department=department,
                        program=full_program_name,
                        year=year,
                        subject=subject,
                    )
                )
        return records

    def _fetch_text(self, url: str) -> str:
        last_error: Exception | None = None
        for attempt in range(1, MAX_FETCH_ATTEMPTS + 1):
            try:
                response = self.session.get(
                    url,
                    timeout=(CONNECT_TIMEOUT_SECONDS, READ_TIMEOUT_SECONDS),
                )
                response.raise_for_status()
                time.sleep(self.crawl_delay)
                return response.text
            except requests.RequestException as exc:
                last_error = exc
                print(
                    f"Fetch attempt {attempt}/{MAX_FETCH_ATTEMPTS} failed for {url}: {exc}",
                    file=sys.stderr,
                )
                if attempt < MAX_FETCH_ATTEMPTS:
                    time.sleep(min(2**attempt, 5))

        print(f"Skipping URL after repeated failures: {url}", file=sys.stderr)
        if last_error:
            print(f"Final error: {last_error}", file=sys.stderr)
        return ""

    def _extract_program_name(self, soup: BeautifulSoup) -> str:
        heading_candidates = []
        for selector in ("h1", "h2", "title"):
            heading_candidates.extend(soup.select(selector))

        for node in heading_candidates:
            text = self._clean_text(node.get_text(" ", strip=True))
            if not text:
                continue
            if "università di padova" in text.lower():
                text = text.split("|", 1)[0].strip()
            if text.lower().startswith(("corso di laurea", "single-cycle degree", "master", "bachelor")):
                cleaned = PROGRAM_PREFIX_PATTERN.sub("", text).strip(" :-")
                if cleaned:
                    return cleaned

        meta_title = soup.find("meta", attrs={"property": "og:title"})
        if meta_title and meta_title.get("content"):
            text = self._clean_text(meta_title["content"].split("|", 1)[0])
            if text:
                return text

        return ""

    def _extract_department_name(self, soup: BeautifulSoup, query_params: dict[str, list[str]]) -> str:
        page_text = soup.get_text("\n", strip=True)
        for label in ("Strutture di riferimento", "Scuola", "School", "Dipartimento", "Department"):
            extracted = self._extract_value_after_label(page_text, label)
            if extracted:
                return extracted

        school_code = query_params.get("scuola", [""])[0].upper()
        school_map = {
            "AG": "School of Agricultural Sciences and Veterinary Medicine",
            "AV": "School of Agricultural Sciences and Veterinary Medicine",
            "EP": "School of Economics and Political Science",
            "GI": "Law School",
            "IN": "School of Engineering",
            "ME": "School of Medicine",
            "PS": "School of Psychology",
            "SC": "School of Science",
            "SU": "School of Human and Social Sciences and Cultural Heritage",
        }
        return school_map.get(school_code, "University of Padua")

    def _extract_subjects_by_year(self, soup: BeautifulSoup) -> dict[str, set[str]]:
        heading = self._find_subjects_heading(soup)
        if heading is None:
            return {}

        subjects_by_year: dict[str, set[str]] = defaultdict(set)
        current_year = ""

        for node in heading.find_all_next():
            if node == heading:
                continue
            if not isinstance(node, Tag):
                continue

            if node.name and re.fullmatch(r"h[1-6]", node.name):
                heading_text = self._clean_text(node.get_text(" ", strip=True)).lower()
                if node is not heading and heading_text in GENERIC_SUBJECT_LABELS:
                    break

            node_text = self._clean_text(node.get_text(" ", strip=True))
            if not node_text:
                continue

            year_match = YEAR_PATTERN.search(node_text)
            if year_match and len(node_text) < 60:
                current_year = year_match.group(1)
                continue

            for subject in self._extract_subject_names_from_node(node):
                subjects_by_year[current_year].add(subject)

        return {year: values for year, values in subjects_by_year.items() if values}

    def _find_subjects_heading(self, soup: BeautifulSoup) -> Tag | None:
        for node in soup.find_all(re.compile(r"^h[1-6]$")):
            text = self._clean_text(node.get_text(" ", strip=True)).lower()
            if "elenco insegnamenti" in text or "course units" in text or "programme structure" in text:
                return node
        return None

    def _extract_subject_names_from_node(self, node: Tag) -> set[str]:
        subjects: set[str] = set()

        if node.name == "li":
            candidate = self._normalize_subject(node.get_text(" ", strip=True))
            if candidate:
                subjects.add(candidate)
            return subjects

        if node.name in {"a", "button", "summary"}:
            candidate = self._normalize_subject(node.get_text(" ", strip=True))
            if candidate:
                subjects.add(candidate)
            return subjects

        if node.name == "tr":
            cells = [self._clean_text(cell.get_text(" ", strip=True)) for cell in node.find_all(["td", "th"])]
            candidate = self._pick_subject_candidate(cells)
            if candidate:
                subjects.add(candidate)
            return subjects

        if node.name in {"div", "section", "article"}:
            if node.find(["li", "tr"]):
                return subjects
            candidate = self._normalize_subject(node.get_text(" ", strip=True))
            if candidate:
                subjects.add(candidate)

        return subjects

    def _pick_subject_candidate(self, values: Iterable[str]) -> str | None:
        cleaned_values = [value for value in (self._normalize_subject(value) for value in values) if value]
        if not cleaned_values:
            return None
        cleaned_values.sort(key=len, reverse=True)
        return cleaned_values[0]

    def _normalize_subject(self, value: str) -> str | None:
        value = self._clean_text(value)
        if not value:
            return None

        lower = value.lower()
        if lower in GENERIC_SUBJECT_LABELS:
            return None
        if len(value) < 3 or len(value) > 180:
            return None
        if lower.startswith(("iscriviti", "leggi", "vai al sito", "scopri di più", "news")):
            return None
        if "università di padova" in lower:
            return None
        return value

    def _extract_value_after_label(self, page_text: str, label: str) -> str:
        pattern = re.compile(rf"{re.escape(label)}\s+(.*)")
        match = pattern.search(page_text)
        if not match:
            return ""
        raw = match.group(1).split("\n", 1)[0].strip(" :-")
        return self._clean_text(raw)

    def _looks_like_course_detail_url(self, url: str) -> bool:
        parsed = urlparse(url)
        if "/offerta-didattica/" not in parsed.path:
            return False
        query = parse_qs(parsed.query)
        return {"key", "ordinamento", "tipo"}.issubset(query.keys())

    def _looks_like_catalogue_page(self, url: str) -> bool:
        parsed = urlparse(url)
        path = parsed.path.lower()
        if any(fragment in path for fragment in DISALLOWED_PATH_FRAGMENTS):
            return False
        if parsed.query and not self._looks_like_course_detail_url(url):
            return False
        return any(
            marker in path
            for marker in (
                "/corsi-di-laurea",
                "/corsi-di-studio",
                "/corsi-laurea",
                "/corsi-laurea-magistrale",
                "/offerta-formativa",
                "/offerta-didattica",
            )
        )

    def _matches_academic_year(self, url: str) -> bool:
        query = parse_qs(urlparse(url).query)
        return not query.get("ordinamento") or query["ordinamento"][0] == self.academic_year

    def _is_allowed_url(self, url: str) -> bool:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"}:
            return False
        return any(parsed.netloc.endswith(host) for host in ALLOWED_HOST_SUFFIXES)

    def _normalize_url(self, url: str) -> str:
        parsed = urlparse(url)
        if not parsed.scheme:
            return url
        normalized_path = parsed.path.rstrip("/") or "/"
        return parsed._replace(path=normalized_path, fragment="").geturl()

    def _clean_text(self, value: str) -> str:
        return re.sub(r"\s+", " ", value).strip()


def write_csv(records: list[CourseRecord], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["department", "program", "year", "subjects"])
        for record in records:
            writer.writerow([record.department, record.program, record.year, record.subject])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scrape UniPd bachelor/master courses and subjects.")
    parser.add_argument(
        "--academic-year",
        default=DEFAULT_ACADEMIC_YEAR,
        help="Academic year code used in UniPd detail URLs, e.g. 2025.",
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT_PATH),
        help="Output CSV path. Defaults to /home/atul-nayak/book/unipd_courses_scraped.csv",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.15,
        help="Delay between requests in seconds to avoid hammering the UniPd site.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    scraper = UniPdCourseScraper(academic_year=args.academic_year, crawl_delay=args.delay)
    records = scraper.scrape()
    output_path = Path(args.output).expanduser().resolve()
    write_csv(records, output_path)
    print(f"Wrote {len(records)} rows to {output_path}")


if __name__ == "__main__":
    main()

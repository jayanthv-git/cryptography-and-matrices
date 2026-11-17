"""Anonymous survey CSV validation and aggregate-only analysis in memory."""
import csv
import io
from collections import Counter
from backend.core.hill_cipher import CipherError

SCHEMA = {
    "awareness": ["low", "moderate", "high"],
    "encryption_familiarity": ["none", "basic", "confident"],
    "two_factor": ["yes", "no", "unsure"],
    "password_practice": ["unique", "reused", "mixed"],
    "data_protection": ["low", "moderate", "high"],
}
MAX_BYTES = 1_048_576
MAX_ROWS = 1000


def analyze_survey(content: str) -> dict:
    try:
        size = len(content.encode("utf-8")) if isinstance(content, str) else MAX_BYTES + 1
    except UnicodeError as error:
        raise CipherError("CSV must contain valid UTF-8 text without isolated Unicode surrogates.") from error
    if size > MAX_BYTES:
        raise CipherError("CSV must be UTF-8 text no larger than 1 MiB.")
    if "\x00" in content:
        raise CipherError("CSV contains null bytes. Export a UTF-8 CSV file and retry.")
    reader = csv.reader(io.StringIO(content.lstrip("\ufeff")), strict=True)
    try:
        header = next(reader, None)
        if not header:
            raise CipherError("CSV is empty. Include a header and at least one response.")
        header = [value.strip() for value in header]
        if len(set(header)) != len(header):
            raise CipherError("CSV headers must be unique.")
        unknown = [name for name in header if name not in SCHEMA]
        if unknown:
            raise CipherError(f"Unsupported columns: {', '.join(unknown)}. Use only template columns; remove all identifying information.")
        counts = {name: Counter() for name in header}
        missing = Counter()
        total, skipped = 0, 0
        for row in reader:
            if not row or not any(value.strip() for value in row):
                skipped += 1
                continue
            if len(row) != len(header):
                raise CipherError(f"CSV line {reader.line_num}: expected {len(header)} cells, found {len(row)}.")
            total += 1
            if total > MAX_ROWS:
                raise CipherError(f"CSV exceeds {MAX_ROWS} non-empty responses.")
            for name, raw in zip(header, row):
                value = raw.strip().lower()
                if not value:
                    missing[name] += 1
                elif value not in SCHEMA[name]:
                    raise CipherError(f"CSV line {reader.line_num}, {name}: use {', '.join(SCHEMA[name])}, or leave blank.")
                else:
                    counts[name][value] += 1
        if total == 0:
            raise CipherError("No responses found. Add at least one non-empty data row.")
        fields = []
        for name in header:
            answered = total - missing[name]
            categories = [{"label": value, "count": counts[name][value],
                           "percentage": round(counts[name][value] * 100 / answered, 1) if answered else 0.0}
                          for value in SCHEMA[name]]
            fields.append({"name": name, "answered": answered, "missing": missing[name], "categories": categories})
        return {"responses": total, "skipped_empty_rows": skipped, "fields": fields}
    except (csv.Error, UnicodeError) as error:
        raise CipherError(f"Malformed CSV: {error}. Export a UTF-8, comma-delimited file.") from error

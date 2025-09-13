from pathlib import Path
from typing import Iterator

import pandas as pd
import mistune
from io import StringIO

import re

from datetime import datetime


############### fUNCTIONS TO IDENTIFY NOTES TO EXPORT


def traverse_directory(
    root_path: str | Path, pattern: str = "*", skip_dirs: set = None
) -> Iterator[Path]:
    """
    Traverse directory yielding Path objects.

    Args:
        root_path: Directory to traverse
        pattern: File pattern to match (e.g., "*.md" for markdown files)
        skip_dirs: Set of directory names to skip

    Yields:
        Path objects for each matching file
    """

    if isinstance(root_path, str):
        root_path = Path(root_path)

    for item in root_path.rglob(pattern):
        # Skip directories we want to ignore
        if any(part in skip_dirs for part in item.parts):
            continue

        yield item


def find_files_with_tag(files, pattern):
    files_with_match = []
    files_with_error = []
    for file in files:
        try:
            if re.search(pattern, file.read_text(encoding="utf-8")):
                files_with_match.append(file)
        except Exception as e:
            # print(e)
            files_with_error.append(file)
    return files_with_match, files_with_error


############### PROCESSING FILES FUNCTIONS


def convert_to_cloze(text: str, cloze_number: int = 1) -> str:
    """
    Convert ==highlighted text== to Anki cloze format {{c1::highlighted text}}

    Args:
        text: The text to convert
        cloze_number: The cloze deletion number (default: 1)

    Returns:
        Text with converted cloze deletions
    """
    # Pattern to match text between == ==
    # Using non-greedy match .*? to handle multiple highlights in the same line
    pattern = r"==(.+?)=="

    # Replace function to format as cloze
    replacement = f"{{{{c{cloze_number}::\\1}}}}"

    # Replace all matches
    return re.sub(pattern, replacement, text)


def convert_highlight_to_html(text: str, html_tag="mark") -> str:
    """
    Convert ==highlighted text== to Anki cloze format {{c1::highlighted text}}

    Args:
        text: The text to convert
        cloze_number: The cloze deletion number (default: 1)

    Returns:
        Text with converted cloze deletions
    """
    # Pattern to match text between == ==
    # Using non-greedy match .*? to handle multiple highlights in the same line
    pattern = r"==(.+?)=="

    # Replace function to format as cloze
    replacement = f"<{html_tag}>\\1</{html_tag}>"

    # Replace all matches
    return re.sub(pattern, replacement, text)


def clean_table(raw_table: pd.DataFrame) -> pd.DataFrame:
    """Define here the expected schema of the notes.
    Returns:
        _type_: _description_
    """
    STANDARD_COLUMNS = ["Texto", "Contexto", "Traducción", "Notas"]

    return raw_table.set_axis(STANDARD_COLUMNS, axis="columns").assign(
        Texto=lambda df: df["Texto"].apply(convert_to_cloze),
        Traducción=lambda df: df["Traducción"].apply(convert_highlight_to_html),
    )


def process_file(note_file: Path) -> pd.DataFrame:
    print("processing", note_file)
    try:
        tables = pd.read_html(
            StringIO(mistune.html(note_file.read_text(encoding="utf-8")))
        )
    except ValueError as e:
        print(f"Error processing {note_file} with error:", e)
        ### I should return the expected frame?
        return pd.DataFrame()
    # return tables

    clean_tables = []
    for table in tables:
        try:
            clean_tables.append(clean_table(table))
        except Exception as e:
            print(f"Error processing {note_file} with error", e)

    return pd.concat(clean_tables, ignore_index=True)


def save_cards(df: pd.DataFrame, export_dir: Path):
    filename = f"obsidian2anki_export__{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
    try:
        (df.to_csv(export_dir / filename, index=False, header=False))
        print(f"file {filename} succesfully written")
    except Exception as e:
        print("Error saving data", e)


def export_from_obsidian2anki(
    anki_tag_pattern: str, obsidian_dir: str | Path, export_dir: str
):
    print("Begin export from obsidian to anki")
    notes_files = traverse_directory(
        obsidian_dir, pattern="*.md", skip_dirs=[".obsidian"]
    )
    files_with_tag, files_with_error = find_files_with_tag(
        notes_files, anki_tag_pattern
    )
    df = pd.concat([process_file(x) for x in files_with_tag], ignore_index=True)
    save_cards(df, export_dir)

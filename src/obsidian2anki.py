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

def _match_tag_pattern(pattern, text):
    """Check if the exact tag pattern exists in the text.
    
    Args:
        pattern: The tag to look for (e.g., "#anki/export")
        text: The text to search in
        
    Returns:
        bool: True if exact tag is found, False otherwise
    """
    escaped_pattern = re.escape(pattern)
    # Match tag when it:
    # - starts at beginning of line or after whitespace
    # - ends at end of line, or is followed by whitespace or newline
    exact_pattern = f"(?:^|\\s){escaped_pattern}(?:$|\\s|\\n)"
    
    match = re.search(exact_pattern, text)
    return bool(match)

def find_files_with_tag(files, pattern):
    files_with_match = []
    files_with_error = []
    for file in files:
        try:
            if _match_tag_pattern(pattern, file.read_text(encoding="utf-8")):
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

def _standardize_schema(df: pd.DataFrame):
    CORE_COLUMNS = [
        'Texto',
        'Contexto',
        'Traducción',
        'Notas',
    ]

    OPTIONAL_COLUMN = 'Omitir'
    n_columns = len(df.columns)
    if n_columns == 4:
        df = df.assign(**{OPTIONAL_COLUMN: None})
    return (
        df
        .iloc[:, :5]
        .set_axis(CORE_COLUMNS + [OPTIONAL_COLUMN], axis='columns')
    )


def clean_table(df: pd.DataFrame) -> pd.DataFrame:
    """Define here the expected schema of the notes.
    Returns:
        _type_: _description_
    """

    return (
        df
        .pipe(_standardize_schema)
        .loc[lambda df: df['Omitir'].isna()]
        .assign(
            Texto = lambda df: df['Texto'].apply(convert_to_cloze),
            Traducción = lambda df: df['Traducción'].apply(convert_highlight_to_html)
        )
        .iloc[:, :4]
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

    clean_tables = pd.concat(clean_tables, ignore_index=True)
    print(f'Found {clean_tables.shape[0]} notes')
    return clean_tables




def save_cards(df: pd.DataFrame, export_dir: Path, filename:str):
    try:
        (df.to_csv(export_dir / f"{filename}.csv", index=False, header=False))
        print(f"file {filename} succesfully written")
    except Exception as e:
        print("Error saving data", e)


def export_from_obsidian2anki(
    anki_tag_pattern: str, obsidian_dir: str | Path, export_dir: str
):
    print("Begin export from obsidian to anki")
    export_tag = f"obsidian2anki_export__{datetime.now().strftime('%Y%m%d_%H%M')}"
    notes_files = traverse_directory(
        obsidian_dir, pattern="*.md", skip_dirs=[".obsidian"]
    )
    files_with_tag, files_with_error = find_files_with_tag(
        notes_files, anki_tag_pattern
    )
    
    if len(files_with_tag) > 0:
        clean_files = []
        for note_file in files_with_tag:
            try:
                clean_files.append(process_file(note_file))
            except Exception as e:
                print(f"Error processing {note_file} with error:", e) 
        
        if len(clean_files) == 0:
            raise ValueError('No files found')      
        
        df = (
            pd.concat(clean_files, ignore_index=True)
            .assign(
                anki_tag = export_tag
            )
        )        
        save_cards(df, export_dir, export_tag)
    else:
        print('No files found')
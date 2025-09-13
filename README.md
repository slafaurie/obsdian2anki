# Simple Obsidian to anki
A scripts that exports markdown tables to csv which are then imported into anki by:
- Identifying files whose content should be processed via obsidian tags (defined in the main.py as ANKI_PATTERN)
- Parsing markdown tables by first converting them to HTML to read them with pandas
    - Reason? it seems parsing directly from markdown was a bit of a pain. Instead, doing it from HTML is pretty smooth as long as 
    the conversion from markdown to html produces proper HTML tags.
- A further processing to standardize column names and values, this ensures we "translate" to the formatting used in obsidian to what
 the note type in Anki expects. Structure is hard-coded.

## How to run
First, seed the environment variables as shown in `.env.example`. Then, just run `uv run python main.py`. It will generate 
a csv in the export directory. As final task, you must import the csv directly in Anki.

## Next steps?
- Expose main params as arguments to be changed by the user.
- Error trail. As the list of notes to import grows, how to make it easy to identify which notes could not be imported?
- Use LLM to fill up rows with context null? powered

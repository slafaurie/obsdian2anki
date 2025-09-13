if __name__ == "__main__":
    from pathlib import Path
    from src.obsidian2anki import export_from_obsidian2anki
    
    from dotenv import load_dotenv
    import os
    
    load_dotenv()
    
    OBSIDIAN_VAULT = Path(os.getenv("OBSIDIAN_VAULT"))
    EXPORT_DIR = Path(os.getenv("EXPORT_DIR"))
    ANKI_TAG_PATTERN = r'#anki/(\w+)'
    
    export_from_obsidian2anki(
        ANKI_TAG_PATTERN,
        OBSIDIAN_VAULT,
        EXPORT_DIR
    )
    

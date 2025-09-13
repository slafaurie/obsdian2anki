if __name__ == "__main__":
    from pathlib import Path
    from src.obsidian2anki import export_from_obsidian2anki
    
    from dotenv import load_dotenv
    import os
    
    load_dotenv()
    
    OBSIDIAN_VAULT = Path(os.getenv("OBSIDIAN_VAULT"))
    EXPORT_DIR = Path(os.getenv("EXPORT_DIR"))
    
    ANKI_TAG = r'#anki/export'
    
    export_from_obsidian2anki(
        ANKI_TAG,
        OBSIDIAN_VAULT,
        EXPORT_DIR
    )
    

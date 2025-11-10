import matplotlib.font_manager as fm
from pathlib import Path


def register_helvetica_neue():
    # Get path to fonts directory
    base_dir = Path(__file__).parent.parent.parent  # Go up to repo root
    fonts_dir = base_dir / "assets" / "helvetica-neue-5"
    
    if not fonts_dir.exists():
        print(f"Warning: Helvetica Neue fonts directory not found at {fonts_dir}")
        return False
    
    # Register all .otf and .ttf files
    registered_count = 0
    for font_file in fonts_dir.glob("*.otf"):
        try:
            fm.fontManager.addfont(str(font_file))
            registered_count += 1
        except Exception as e:
            print(f"Warning: Could not register font {font_file.name}: {e}")
    
    for font_file in fonts_dir.glob("*.ttf"):
        try:
            fm.fontManager.addfont(str(font_file))
            registered_count += 1
        except Exception as e:
            print(f"Warning: Could not register font {font_file.name}: {e}")
    
    if registered_count > 0:
        print(f"✓ Registered {registered_count} Helvetica Neue font(s)")
        return True
    else:
        print("Warning: No Helvetica Neue fonts were registered")
        return False


# global instance
_fonts_registered = register_helvetica_neue()

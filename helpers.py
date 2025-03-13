def get_language_code(language_str):
    """
    Convert a common language name to its ISO code.
    If the user enters "detect", returns None to allow auto-detection.
    """
    if language_str.lower() == "detect":
        return None
    
    language_mapping = {
        "english": "en",
        "french": "fr",
        "spanish": "es",
        "german": "de",
        "italian": "it",
        "portuguese": "pt",
        # Add additional mappings as needed.
    }
    return language_mapping.get(language_str.lower(), language_str.lower())

def format_timestamp(seconds):
    """
    Convert seconds (float) into an SRT timestamp format (HH:MM:SS,mmm).
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    milliseconds = int((seconds - int(seconds)) * 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{milliseconds:03}"

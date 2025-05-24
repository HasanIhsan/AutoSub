def get_language_code(language_str: str) -> str:
    if language_str.lower() == "detect":
        print("Language detection...")
        return None
    mapping = {
        "english": "en", "french": "fr", "spanish": "es",
        "german": "de",  "italian": "it", "portuguese": "pt"
    }
    return mapping.get(language_str.lower(), language_str.lower())
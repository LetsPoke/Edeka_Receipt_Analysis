def cleanup_name(raw_name: str) -> str:
    """ Standardizes item names by applying text normalization
    1) Convert to a consistent case (e.g. lower).
    2) Replace 'ö'->'oe', 'ü'->'ue', 'ä'->'ae'.
    3) Convert to Title-case or keep lower.
    4) Remove extra spaces
    """
    name = raw_name.lower()
    name = name.replace("ö", "oe").replace("ü", "ue").replace("ä", "ae").replace("ß", "ss")
    name = name.title()
    name = " ".join(name.split())
    return name

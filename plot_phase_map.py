def extract_N(folder):
    try:
        parts = folder.split("_")
        for i, p in enumerate(parts):
            if p == "N":
                return int(parts[i + 1])
    except Exception:
        return None
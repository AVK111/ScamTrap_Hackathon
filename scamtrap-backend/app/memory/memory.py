class ScamPatternMemory:
    _patterns = {}

    @classmethod
    def update(cls, scam_type: str, keywords: list):
        if scam_type not in cls._patterns:
            cls._patterns[scam_type] = {
                "count": 0,
                "keywords": set()
            }

        cls._patterns[scam_type]["count"] += 1
        cls._patterns[scam_type]["keywords"].update(keywords)

    @classmethod
    def is_known_pattern(cls, keywords: list):
        for data in cls._patterns.values():
            if data["count"] >= 2 and any(k in data["keywords"] for k in keywords):
                return True
        return False

    @classmethod
    def dump(cls):
        return cls._patterns

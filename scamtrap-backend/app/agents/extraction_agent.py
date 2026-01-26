import re

class ExtractionAgent:
    def extract(self, text):
        data = []
        data += re.findall(r"[\w.-]+@[\w.-]+", text)
        data += re.findall(r"(https?://[^\s]+)", text)
        return data

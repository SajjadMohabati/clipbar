"""Text transformations matching Transforms.swift."""

from __future__ import annotations
import base64
import json
import urllib.parse
from enum import Enum
from typing import List, Optional


class TextTransform(str, Enum):
    UPPERCASE = "UPPERCASE"
    LOWERCASE = "lowercase"
    CAPITALIZED = "Capitalize Words"
    TRIMMED = "Trim Whitespace"
    REMOVE_EMPTY_LINES = "Remove Empty Lines"
    SORT_LINES = "Sort Lines"
    UNIQUE_LINES = "Remove Duplicate Lines"
    JOIN_LINES = "Join Lines"
    PRETTY_JSON = "Format JSON"
    MINIFY_JSON = "Minify JSON"
    BASE64_ENCODE = "Base64 Encode"
    BASE64_DECODE = "Base64 Decode"
    URL_ENCODE = "URL Encode"
    URL_DECODE = "URL Decode"

    @classmethod
    def groups(cls) -> List[List[TextTransform]]:
        return [
            [cls.UPPERCASE, cls.LOWERCASE, cls.CAPITALIZED],
            [cls.TRIMMED, cls.REMOVE_EMPTY_LINES, cls.SORT_LINES, cls.UNIQUE_LINES, cls.JOIN_LINES],
            [cls.PRETTY_JSON, cls.MINIFY_JSON],
            [cls.BASE64_ENCODE, cls.BASE64_DECODE, cls.URL_ENCODE, cls.URL_DECODE],
        ]

    def apply(self, text: str) -> Optional[str]:
        lines = text.split("\n")
        try:
            if self == TextTransform.UPPERCASE:
                return text.upper()
            elif self == TextTransform.LOWERCASE:
                return text.lower()
            elif self == TextTransform.CAPITALIZED:
                return text.title()
            elif self == TextTransform.TRIMMED:
                trimmed_lines = [line.strip() for line in lines]
                return "\n".join(trimmed_lines).strip()
            elif self == TextTransform.REMOVE_EMPTY_LINES:
                return "\n".join([line for line in lines if line.strip()])
            elif self == TextTransform.SORT_LINES:
                return "\n".join(sorted(lines, key=lambda s: s.casefold()))
            elif self == TextTransform.UNIQUE_LINES:
                seen = set()
                result = []
                for line in lines:
                    if line not in seen:
                        seen.add(line)
                        result.append(line)
                return "\n".join(result)
            elif self == TextTransform.JOIN_LINES:
                non_empty = [line.strip() for line in lines if line.strip()]
                return " ".join(non_empty)
            elif self == TextTransform.PRETTY_JSON:
                parsed = json.loads(text)
                return json.dumps(parsed, indent=2, sort_keys=True, ensure_ascii=False)
            elif self == TextTransform.MINIFY_JSON:
                parsed = json.loads(text)
                return json.dumps(parsed, separators=(',', ':'), ensure_ascii=False)
            elif self == TextTransform.BASE64_ENCODE:
                return base64.b64encode(text.encode("utf-8")).decode("ascii")
            elif self == TextTransform.BASE64_DECODE:
                cleaned = text.strip()
                # Handle padding if needed
                missing_padding = len(cleaned) % 4
                if missing_padding:
                    cleaned += '=' * (4 - missing_padding)
                decoded = base64.b64decode(cleaned.encode("ascii"), validate=True)
                return decoded.decode("utf-8")
            elif self == TextTransform.URL_ENCODE:
                return urllib.parse.quote(text, safe="-._~")
            elif self == TextTransform.URL_DECODE:
                return urllib.parse.unquote(text)
        except Exception:
            return None
        return None

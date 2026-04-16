from typing import Any


class MemoryAnswerCache:
    _cache: dict[str, Any] = {}

    @classmethod
    def get(cls, key: str):
        return cls._cache.get(key)

    @classmethod
    def set(cls, key: str, value: Any):
        cls._cache[key] = value

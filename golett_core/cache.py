from typing import Any, Optional


class InMemoryCache:
    def __init__(self):
        self._cache = {}

    async def get(self, key: str) -> Optional[Any]:
        return self._cache.get(key)

    async def set(self, key: str, value: Any, expire: int = 0):
        self.get_session_id_from_key(key)
        self._cache[key] = value

    async def delete(self, key: str):
        if key in self._cache:
            del self._cache[key]

    def get_session_id_from_key(self, key: str) -> str:
        # Expected format: "history:session_id:limit"
        try:
            return key.split(":")[1]
        except IndexError:
            raise ValueError("Invalid cache key format") 
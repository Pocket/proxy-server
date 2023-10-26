from typing import Optional

import aiohttp


class SessionProvider:
    """Singleton wrapper for an aiohttp ClientSession"""

    __session: Optional[aiohttp.ClientSession] = None

    @classmethod
    def session(cls) -> aiohttp.ClientSession:
        """Get the session singleton, creating it on first call"""

        if cls.__session is None:
            # 30 second timeout
            timeout = aiohttp.ClientTimeout(total=30)

            # Unlimited connection pool size
            connector = aiohttp.TCPConnector(limit=None)

            # Avoid persisting cookies across requests
            cookie_jar = aiohttp.DummyCookieJar()

            cls.__session = aiohttp.ClientSession(
                connector=connector,
                cookie_jar=cookie_jar,
                timeout=timeout,
            )

        return cls.__session

    @classmethod
    async def shutdown(cls) -> None:
        """Close the session and release resources"""

        if cls.__session is None:
            return

        await cls.__session.close()
        cls.__session = None

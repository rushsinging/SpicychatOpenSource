from __future__ import annotations

import json
import uuid
import typing
import redis

from starlette.datastructures import MutableHeaders, Secret
from starlette.requests import HTTPConnection
from starlette.types import ASGIApp, Message, Receive, Scope, Send


class RedisSessionMiddleware:
    def __init__(
        self,
        app: ASGIApp,
        secret_key: str | Secret,
        redis_client: redis.Redis,
        session_cookie: str = "session",
        max_age: int | None = 14 * 24 * 60 * 60,  # 14 days, in seconds
        path: str = "/",
        same_site: typing.Literal["lax", "strict", "none"] = "lax",
        https_only: bool = False,
        domain: str | None = None,
    ) -> None:
        self.app = app
        self.redis_client = redis_client
        self.session_cookie = session_cookie
        self.max_age = max_age
        self.path = path
        self.security_flags = "httponly; samesite=" + same_site
        if https_only:  # Secure flag can be used with HTTPS only
            self.security_flags += "; secure"
        if domain is not None:
            self.security_flags += f"; domain={domain}"

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        # print(f"RedisSessionMiddleware scope: {scope}")
        if scope["type"] not in ("http", "websocket"):  # pragma: no cover
            await self.app(scope, receive, send)
            return

        connection = HTTPConnection(scope)
        initial_session_was_empty = True

        session_id = ""
        # print(f"connection.cookies: {connection.cookies} http_headers: {connection.headers}")
        if self.session_cookie in connection.cookies:
            session_id = connection.cookies[self.session_cookie]
            try:
                data = self.redis_client.get(session_id)
                scope["session"] = json.loads(data) if data else {}
                initial_session_was_empty = False
            except Exception:
                scope["session"] = {}
        else:
            session_id = str(uuid.uuid4())
            scope["session"] = {}

        async def send_wrapper(message: Message) -> None:
            if message["type"] == "http.response.start":
                if scope["session"]:
                    # We have session data to persist.
                    data = json.dumps(scope["session"])
                    self.redis_client.set(session_id, data)
                    headers = MutableHeaders(scope=message)
                    header_value = "{session_cookie}={data}; path={path}; {max_age}{security_flags}".format(
                        session_cookie=self.session_cookie,
                        data=session_id,
                        path=self.path,
                        max_age=f"Max-Age={self.max_age}; " if self.max_age else "",
                        security_flags=self.security_flags,
                    )
                    # print(f"header_value: {header_value}")
                    headers.append("Set-Cookie", header_value)
                elif not initial_session_was_empty:
                    # The session has been cleared.
                    headers = MutableHeaders(scope=message)
                    header_value = "{session_cookie}={data}; path={path}; {expires}{security_flags}".format(
                        session_cookie=self.session_cookie,
                        data="null",
                        path=self.path,
                        expires="expires=Thu, 01 Jan 1970 00:00:00 GMT; ",
                        security_flags=self.security_flags,
                    )
                    headers.append("Set-Cookie", header_value)
            await send(message)

        await self.app(scope, receive, send_wrapper)

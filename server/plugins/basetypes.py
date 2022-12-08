from __future__ import annotations
import asyncio
import aiohttp
import typing
import plugins.configuration
import plugins.database


class Server:
    """Base server class for the suite"""
    config:     'plugins.configuration.Configuration'
    server:     typing.Optional[aiohttp.web.Server]
    data:       'plugins.configuration.InterData'
    handlers:   typing.Dict[str, Endpoint]
    database:   'plugins.database.Database'
    dbpool:     asyncio.Queue


class Endpoint:
    """API end-point function"""
    exec: typing.Callable

    def __init__(self, executor):
        self.exec = executor

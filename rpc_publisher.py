import asyncio
from typing import Union

import tornado.ioloop
import tornado.web
import tornado.websocket
import uuid
from typing import MutableMapping

from aio_pika import Message, connect
from aio_pika.abc import (
    AbstractChannel, AbstractConnection, AbstractIncomingMessage, AbstractQueue,
)


class RPCConnection:
    connection: AbstractConnection
    channel: AbstractChannel
    callback_queue: AbstractQueue
    loop: asyncio.AbstractEventLoop

    def __init__(self, socket) -> None:
        self.futures: MutableMapping[str, asyncio.Future] = {}
        self.loop = asyncio.get_running_loop()




def get_app():
    return tornado.web.Application([(r'/socket', Socket),
                                    (r'/', MainHandler)])

class MainHandler(tornado.web.RequestHandler):
    async def get(self):
        await self.render('index.html')

class Socket(tornado.websocket.WebSocketHandler):
    async def on_message(self, message: Union[str, bytes]):
        print(f'received {message=}')
        self.geocheck = asyncio.create_task(GeoChecker(self).run(message))

    async def open(self, *args: str, **kwargs: str):
        print(f'socket opened from {self.request.remote_ip}')

    def check_origin(self, origin: str) -> bool:
        return True

    def on_close(self) -> None:
        print(f'{self.request.remote_ip} closed connection')
        self.geocheck.cancel()



if __name__ == '__main__':
    try:
        app = get_app()
        app.listen(8888)
        tornado.ioloop.IOLoop.current().start()
    except KeyboardInterrupt:
        tornado.ioloop.IOLoop.current().stop()

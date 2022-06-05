import asyncio
from typing import Union

import tornado.ioloop
import tornado.web
import tornado.websocket

from aio_pika import Message, connect
from aio_pika.abc import AbstractIncomingMessage


def get_app():
    return tornado.web.Application([(r'/socket', Socket),
                                    (r'/', MainHandler)])


class MainHandler(tornado.web.RequestHandler):
    async def get(self):
        await self.render('index.html')


class Socket(tornado.websocket.WebSocketHandler):
    async def open(self, *args: str, **kwargs: str):
        print(f'socket opened from {self.request.remote_ip}')
        self.connection = await connect(
            "amqp://guest:guest@localhost/", loop=asyncio.get_running_loop(),
        )
        self.channel = await self.connection.channel()
        self.callback_queue = await self.channel.declare_queue(exclusive=True)
        await self.callback_queue.consume(self.on_response)

    async def on_response(self, message: AbstractIncomingMessage) -> None:
        # if message.correlation_id is None:
        #     print(f"Bad message {message!r}")
        #     return
        await self.write_message(message.body)

    async def on_message(self, message: Union[str, bytes]):
        print(f'received {message=}')
        await self.channel.default_exchange.publish(
            Message(
                message,
                content_type="application/json",
                reply_to=self.callback_queue.name,
            ),
            routing_key="rpc_queue",
        )

    def check_origin(self, origin: str) -> bool:
        return True

    def on_close(self) -> None:
        print(f'{self.request.remote_ip} closed connection')
        await self.channel.close()
        await self.callback_queue.delete()
        await self.connection.close()


if __name__ == '__main__':
    try:
        app = get_app()
        app.listen(8888)
        tornado.ioloop.IOLoop.current().start()
    except KeyboardInterrupt:
        tornado.ioloop.IOLoop.current().stop()

import asyncio
import logging

from aio_pika import connect
from aio_pika.abc import AbstractIncomingMessage

from checker.geo_checker import GeoChecker


async def check(exchange, message) -> None:
    geochecker = GeoChecker(exchange, message)
    await geochecker.run()


async def main() -> None:
    # Perform connection
    connection = await connect("amqp://guest:guest@localhost/")

    # Creating a channel
    channel = await connection.channel()
    exchange = channel.default_exchange

    # Declaring queue
    queue = await channel.declare_queue("rpc_queue")

    print(" [x] Awaiting RPC requests")

    # Start listening the queue with name 'hello'
    async with queue.iterator() as qiterator:
        message: AbstractIncomingMessage
        async for message in qiterator:
            try:
                async with message.process(requeue=False):
                    assert message.reply_to is not None

                    await check(exchange, message)
                    print("Request complete")
            except Exception:
                logging.exception("Processing error for message %r", message)

if __name__ == "__main__":
    asyncio.run(main())

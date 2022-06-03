import asyncio
from typing import Callable, List
import json

from aio_pika import Message
from aio_pika.abc import AbstractIncomingMessage, AbstractExchange
from dotenv import load_dotenv
from playwright.async_api import async_playwright

from models.base_service import BaseService
from settings import KEY_ORDER
from utils import Utils

load_dotenv()


class GeoChecker:
    def __init__(self, exchange: AbstractExchange, message: AbstractIncomingMessage):
        self.exchange = exchange
        self.message = message

    async def task(self, browser, user_agent, ip, klass: BaseService.__class__):
        service = klass(browser, user_agent)
        await service.task(ip)
        console_dict = {'ip': ip,
                        'data': {
                            service.name: {'country': service.model.country.code,
                                           'city': service.model.city.en}
                        }
                        }
        await self.exchange.publish(
            Message(
                body=json.dumps(console_dict).encode(),
                correlation_id=self.message.correlation_id,
                content_type='application/json'
            ),
            routing_key=self.message.reply_to,
        )
        print(console_dict)

    async def check_ip(self, browser, ip, services: List[BaseService]):
        user_agent = await Utils.get_user_agent()
        task_args = (browser, user_agent, ip)
        await asyncio.gather(
            *[self.task(*task_args, service) for service in services], # noqa
        )
        await self.exchange.publish(
            Message(
                body='проверка завершена'.encode(),
                correlation_id=self.message.correlation_id,
            ),
            routing_key=self.message.reply_to,
        )

    @staticmethod
    def get_active_services() -> List[BaseService]:
        all_services = Utils.get_service_subclasses()
        return [serv for serv in all_services if serv.name in KEY_ORDER.keys()]  # noqa

    @staticmethod
    async def run_sync_parallel(*functions: Callable):
        return await asyncio.gather(
            *[asyncio.to_thread(function) for function in functions]
        )

    async def run(self):
        services = await asyncio.to_thread(self.get_active_services)
        ips = [ip for ip in self.message.body.decode().split('\n') if Utils.is_ipv4(ip)]
        if not ips:
            return
        proxies = Utils.get_proxies(len(ips))
        async with async_playwright() as p:
            for ip in ips:
                proxy = await proxies.__anext__()
                browser = await p.firefox.launch(
                    proxy={'server': f'socks5://{proxy}'}
                )
                await self.check_ip(browser, ip, services)
                await browser.close()
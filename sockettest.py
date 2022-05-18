import asyncio
from typing import Callable, List, Union

import tornado.ioloop
import tornado.web
import tornado.websocket
from dotenv import load_dotenv
from playwright.async_api import async_playwright

from models.service import Service
from settings import KEY_ORDER
from utils import Utils


async def task(browser, user_agent, ip, socket,
               klass: Service.__class__, serv_name):
    service = klass(browser, user_agent)
    await service.task(ip)
    console_dict = {'ip': ip,
                    'data': {
                        serv_name: {'country': service.model.country.code,
                                    'city': service.model.city.en}
                    }
                    }
    await socket.write_message(console_dict)


async def check_ip(browser, ip, services: List[Service], socket):
    user_agent = await Utils.get_user_agent()
    task_args = (browser, user_agent, ip, socket)
    await asyncio.gather(
        *[task(*task_args, service, service.name) for service in services] # noqa
    )


def get_active_services() -> List[Service]:
    all_services = Utils.get_service_subclasses()
    return [serv for serv in all_services if serv.name in KEY_ORDER.keys()] # noqa


async def run_sync_parallel(*functions: Callable):
    return await asyncio.gather(
        *[asyncio.to_thread(function) for function in functions]
    )


async def main(socket, ips):
    """python main.py --ips=5.61.37.207,188.111.11.11"""
    services = await asyncio.to_thread(get_active_services)
    if not ips:
        return
    proxies = Utils.get_proxies(len(ips))
    async with async_playwright() as p:
        for ip in ips:
            proxy = await proxies.__anext__()
            browser = await p.firefox.launch(
                proxy={'server': f'socks5://{proxy}'}
            )
            await check_ip(browser, ip, services, socket)
            await browser.close()


def get_app():
    return tornado.web.Application([(r'/socket', Socket), ])


class Socket(tornado.websocket.WebSocketHandler):
    async def on_message(self, message: Union[str, bytes]):
        print(f'received {message=}')
        await main(self, [message])

    async def open(self, *args: str, **kwargs: str):
        print('socket opened')

    def check_origin(self, origin: str) -> bool:
        return True


if __name__ == '__main__':
    load_dotenv()
    app = get_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()

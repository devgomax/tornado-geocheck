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


class GeoChecker:
    def __init__(self, socket):
        self.ws = socket
        self.queue = asyncio.Queue()

    async def task(self, browser, user_agent, ip, klass: Service.__class__):
        service = klass(browser, user_agent)
        await service.task(ip)
        console_dict = {'ip': ip,
                        'data': {
                            service.name: {'country': service.model.country.code,
                                           'city': service.model.city.en}
                        }
                        }
        await self.ws.write_message(console_dict)
        print(console_dict)

    async def check_ip(self, browser, ip, services: List[Service]):
        user_agent = await Utils.get_user_agent()
        task_args = (browser, user_agent, ip)
        await asyncio.gather(
            *[self.task(*task_args, service) for service in services], # noqa
        )
        await self.ws.write_message('проверка завершена')

    @staticmethod
    def get_active_services() -> List[Service]:
        all_services = Utils.get_service_subclasses()
        return [serv for serv in all_services if serv.name in KEY_ORDER.keys()]  # noqa

    @staticmethod
    async def run_sync_parallel(*functions: Callable):
        return await asyncio.gather(
            *[asyncio.to_thread(function) for function in functions]
        )

    async def run(self, message):
        services = await asyncio.to_thread(self.get_active_services)
        ips = [ip for ip in message.split('\n') if Utils.is_ipv4(ip)]
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
    load_dotenv()
    try:
        app = get_app()
        app.listen(8888)
        tornado.ioloop.IOLoop.current().start()
    except KeyboardInterrupt:
        tornado.ioloop.IOLoop.current().stop()

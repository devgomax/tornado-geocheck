import json
from typing import Callable, List

import asyncio
from dotenv import load_dotenv
from playwright.async_api import async_playwright

from models.base_service import BaseService
from settings import (KEY_ORDER,
                      WRITE_TO_FILE,
                      ONLY_COUNTRY_CODE,
                      LOG_FILENAME)
from utils import Utils


async def task(browser, user_agent, ip, log, console,
               klass: BaseService.__class__, serv_name):
    service = klass(browser, user_agent)
    await service.task(ip)
    log[serv_name] = service.dictionary
    console['data'][serv_name]['country'] = service.model.country.code
    if not ONLY_COUNTRY_CODE:
        console['data'][serv_name]['city'] = service.model.city.en


async def check_ip(browser, ip, services: List[BaseService]):
    log_dict = {}
    console_dict = {'ip': ip,
                    'data': KEY_ORDER}
    user_agent = await Utils.get_user_agent()
    task_args = (browser, user_agent, ip, log_dict, console_dict)
    await asyncio.gather(
        *[task(*task_args, service, service.name) for service in services] # noqa
    )
    if WRITE_TO_FILE:
        await Utils.write_json_log(LOG_FILENAME, log_dict,
                                   asyncio.get_running_loop())
    print(json.dumps(console_dict, indent=2))


def get_active_services() -> List[BaseService]:
    all_services = Utils.get_service_subclasses()
    return [serv for serv in all_services if serv.name in KEY_ORDER.keys()] # noqa


async def run_sync_parallel(*functions: Callable):
    return await asyncio.gather(
        *[asyncio.to_thread(function) for function in functions]
    )


async def main():
    """python main.py 5.61.37.207 socks5 184.170.131.150:1490"""
    services, ips = await run_sync_parallel(get_active_services,
                                            Utils.parse_arguments)
    if not ips:
        return
    proxies = Utils.get_proxies(len(ips))
    async with async_playwright() as p:
        for ip in ips:
            proxy = await proxies.__anext__()
            browser = await p.firefox.launch(
                proxy={'server': f'socks5://{proxy}'}
            )
            await check_ip(browser, ip, services)
            await browser.close()


if __name__ == '__main__':
    load_dotenv()
    asyncio.run(main())

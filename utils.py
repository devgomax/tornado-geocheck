import argparse
import importlib
import json
import os
import random
from ipaddress import ip_address
from typing import List, AsyncGenerator, Tuple, Callable

import aiofiles
import requests

from settings import (DEBUG, REWRITE_LOG_FILE, PROXIES_FILENAME,
                      UA_FILENAME, CURSOR_FILENAME)


class Utils:
    user_agents = []

    @classmethod
    async def __read_ua_file(cls) -> None:
        """Reads user-agents file and saves data into Utils.user_agents
        variable"""
        async with aiofiles.open(os.path.abspath(UA_FILENAME)) as f:
            content = await f.read()
            cls.user_agents = content.split('\n')

    @classmethod
    async def get_user_agent(cls) -> str:
        """Returns a random user_agent string from a list Utils.user_agents"""
        if not cls.user_agents:
            await cls.__read_ua_file()
        return random.choice(cls.user_agents)

    @staticmethod
    def __get_service_filenames() -> List[str]:
        """Returns a list of all filenames without extension where we store
        Service subclasses"""
        filenames = []
        for root, dirs, files in os.walk(os.path.abspath('services')):
            for file in files:
                if file.endswith('.py') and '__init__' not in file:
                    filenames.append(file.replace('.py', ''))
        return filenames

    @classmethod
    def get_service_subclasses(cls) -> List[Callable]:
        """Returns a list of all Service subclasses"""
        classes = []
        filenames = cls.__get_service_filenames()
        for file in filenames:
            module = importlib.import_module(f'services.{file}',
                                             'services').__dict__
            classes.append(list(module.values())[-1])
        return classes

    @staticmethod
    def is_ipv4(ip) -> bool:
        """Checks whether given IP-address is valid IPv4-address"""
        try:
            ip_address(ip)
            return True
        except ValueError:
            return False

    @classmethod
    def is_valid_proxy(cls, proxy) -> bool:
        """Checks whether given proxy is valid by sending a simple request
        with it"""
        proxies = {'http': 'socks5://%s' % proxy,
                   'https': 'socks5://%s' % proxy}
        try:
            requests.get(
                'http://api4ip.info/api/ip/check', proxies=proxies, timeout=4.
            ).raise_for_status()
            return True
        except (requests.exceptions.HTTPError,
                requests.exceptions.Timeout,
                requests.exceptions.ConnectionError) as e:
            if DEBUG:
                print(cls, e)
            return False

    @staticmethod
    async def __get_cursor() -> int:
        """Asynchronously reads file to get the point of a cursor marking the
        start of a line we will get next proxy from"""
        async with aiofiles.open(os.path.abspath(CURSOR_FILENAME)) as f:
            line = await f.readline()
            return int(line.strip())

    @staticmethod
    async def __save_cursor(cursor) -> None:
        """Saves and asynchronously writes a new point of a cursor for the next
        launch of our script"""
        async with aiofiles.open(os.path.abspath(CURSOR_FILENAME), 'w') as f:
            await f.write(str(cursor))

    @classmethod
    async def __get_valid_proxies(cls, cursor, count) -> Tuple[List[str], int]:
        """Returns as many valid proxies as many ips we have to check and a
        point of cursor marking start of the line of proxy for the next
        launch of script"""
        valid_proxies = []
        bad_counter = 0
        async with aiofiles.open(os.path.abspath(PROXIES_FILENAME)) as f:
            await f.seek(cursor)
            while len(valid_proxies) < count:
                if bad_counter == 15:
                    if DEBUG:
                        print(cls.__class__, 'Seems like the proxies are dead')
                    exit(1)
                proxy_line = await f.readline()
                proxy = proxy_line.rstrip('\n')
                if len(proxy) == 0:
                    await f.seek(0)
                    proxy_line = await f.readline()
                    proxy = proxy_line.rstrip('\n')
                if cls.is_valid_proxy(proxy):
                    valid_proxies.append(proxy)
                    bad_counter = 0
                    continue
                bad_counter += 1
            cursor = await f.tell()
        return valid_proxies, cursor

    @classmethod
    async def get_proxies(cls, number) -> AsyncGenerator:
        """Returns AsyncGenerator with given {number} of proxies.
        Usage example:
        proxies = Utils.get_proxies(len(ips))
        proxy = await proxies.__anext__()"""

        cursor = await cls.__get_cursor()
        valid_proxies, cursor = await cls.__get_valid_proxies(cursor, number)
        await cls.__save_cursor(cursor)
        if DEBUG:
            print('Валидные прокси:', valid_proxies)
        for item in valid_proxies:
            yield item

    @classmethod
    def parse_arguments(cls) -> List[str]:
        """Parses commandline arguments to check whether the list of valid
        IPs is given"""
        parser = argparse.ArgumentParser()
        parser.add_argument(
            '--ips', dest='ips', help='comma-separated list of ips',
            required=True, type=str
        )
        args = parser.parse_args().ips.split(',')
        ips = [arg for arg in args if cls.is_ipv4(arg)]
        return ips

    @staticmethod
    async def write_json_log(filename: str, data: dict, loop) -> None:
        """Writes full geodata into json file"""
        async with aiofiles.open(os.path.abspath(filename),
                                 'w' if DEBUG or REWRITE_LOG_FILE else 'a',
                                 loop=loop) as f:
            await f.write(json.dumps(data, indent=2))
            await f.write('\n')

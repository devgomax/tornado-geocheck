from dataclasses import asdict
from typing import Optional

from playwright.async_api._generated import Browser, BrowserContext, Page
from playwright._impl._api_types import TimeoutError, Error

from settings import (DEBUG, TIMEOUT, TO_MULTIPLIER, RETRIES_COUNT,
                      ONLY_COUNTRY_CODE)
from utils import Utils
from .data import IPModel


class Service:
    __slots__ = 'timeout', 'backoff', 'only_country_code', 'browser', \
                'context', 'page', 'tags_to_abort', 'user_agent', \
                'dictionary', 'model', 'tries'

    def __init__(self, browser: Browser, user_agent: str):
        self.timeout = TIMEOUT
        self.backoff = TO_MULTIPLIER
        self.only_country_code = ONLY_COUNTRY_CODE
        self.browser = browser
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.tags_to_abort = ['png', 'svg', 'jpg', 'jpeg', 'woff', 'gif',
                              'woff2', 'css', 'ico']
        self.user_agent = user_agent
        self.dictionary = {'status': '', 'data': {}}
        self.model = IPModel()
        self.tries = 1

    async def handle_requests(self, route, request):
        conditions = map(lambda x: x in request.url, self.tags_to_abort)
        if any(conditions):
            await route.abort()
        else:
            await route.continue_()

    async def prepare_context(self, *args, **kwargs):
        kwargs['user_agent'] = self.user_agent
        kwargs['bypass_csp'] = True
        self.context = await self.browser.new_context(*args, **kwargs)
        self.context.set_default_timeout(self.timeout)
        self.context.set_default_navigation_timeout(self.timeout)

    async def prepare_page(self):
        self.page = await self.context.new_page()
        await self.page.route('**/*', self.handle_requests)

    async def inner_task(self, ip):
        """You must override this function with the logic to fill the fields:
        self.dictionary['status'] - response status (example: '200 OK'),
        self.model - stores gdata from service"""
        ...

    async def task(self, ip):
        try:
            await self.inner_task(ip)
        except (TimeoutError, Error) as e:
            self.user_agent = await Utils.get_user_agent()
            self.dictionary['status'] = '0 Connection Error'
            self.model.traits.ip = ''
            if DEBUG:
                print(self.__class__, e)
        except Exception as exc:
            self.dictionary['status'] = '-1 Parsing Error'
            self.model = IPModel()
            if DEBUG:
                print(self.__class__, exc)
        finally:
            await self.context.close()
            self.tries += 1
            self.timeout *= self.backoff
            self.dictionary['data'] = asdict(self.model)
            if self.dictionary['status'] == '0 Connection Error':
                if self.tries <= RETRIES_COUNT:
                    await self.task(ip)

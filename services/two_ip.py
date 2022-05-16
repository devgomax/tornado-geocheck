import pycountry

from locators.two_ip import Locators
from models.service import Service


class TwoIP(Service):
    name = '2ip'

    async def parse_data(self, locators, ip):
        country_field = await locators.rows.locator('nth=3 >> td >> nth=1 >> a').text_content()
        country = country_field.strip()
        self.model.country.en = country
        self.model.country.code = pycountry.countries.get(name=country).alpha_2
        if self.only_country_code:
            return
        self.model.traits.ip = ip
        isp = await locators.rows.locator('nth=6 >> td >> nth=1').text_content()
        self.model.traits.isp = isp.strip()
        route = await locators.rows.locator('nth=5 >> td >> nth=1').text_content()
        self.model.traits.network = route.strip()
        city_row = await locators.rows.locator('nth=2 >> td >> nth=1').text_content()
        city = city_row.strip()
        self.model.city.ru = city if city != 'Не определен' else ''

    async def inner_task(self, ip):
        self.tags_to_abort += ['vk.com', 'doubleclick', 'google-analytics',
                               'googletag', 'googlead', 'drt/ui', 'mail.ru']
        await self.prepare_context()
        await self.prepare_page()
        locators = Locators(self.page)
        await self.page.goto(f'https://2ip.ru/whois/?ip={ip}')
        self.dictionary['status'] = '200 OK'
        await self.parse_data(locators, ip)

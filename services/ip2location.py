from models.service import Service
from locators.ip2location import Locators


class Ip2Location(Service):
    name = 'ip2location'

    async def parse_data(self, locators):
        cnt_code = await locators.rows.locator('nth=2 >> td').text_content()
        self.model.country.code = cnt_code.strip().split(' ')[-1][1:3]
        if self.only_country_code:
            return
        self.model.traits.ip = await locators.rows.locator('nth=1 >> td >> a').text_content()
        self.model.traits.isp = await locators.rows.locator('nth=6 >> td').text_content()
        self.model.city.en = await locators.rows.locator('nth=4 >> td').text_content()
        self.model.region.en = await locators.rows.locator('nth=3 >> td').text_content()
        self.model.country.en = await locators.rows.locator('nth=2 >> td >> a').text_content()
        self.model.location.zip = await locators.rows.locator('nth=11 >> td').text_content()
        self.model.location.timezone = await locators.rows.locator('nth=26 >> td').text_content()
        location = await locators.rows.locator('nth=5 >> td').text_content()
        lat, long = location.split('(')[0].strip().split(', ')
        self.model.location.latitude = str(lat)
        self.model.location.longitude = str(long)

    async def inner_task(self, ip):
        self.tags_to_abort += ['googletag', 'google-analytics', 'googlead',
                               'doubleclick', 'pagead', 'ads']
        await self.prepare_context()
        await self.prepare_page()
        locators = Locators(self.page)
        await self.page.goto(f'https://www.ip2location.com/demo/{ip}')
        self.dictionary['status'] = '200 OK'
        await self.parse_data(locators)

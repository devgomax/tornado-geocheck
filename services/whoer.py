from locators.whoer import Locators
from models.service import Service


class Whoer(Service):
    name = 'whoer'

    async def parse_data(self, locators, ip):
        country_row = await locators.rows.locator('nth=0 >> div.card__col_value').text_content()
        country_info = country_row.strip().replace(',', '').split(' ')
        cntr_code = country_info[-2][1:3]
        self.model.country.code = cntr_code.strip()
        if self.only_country_code:
            return
        self.model.traits.ip = ip
        isp = await locators.rows.locator('nth=6 >> div.card__col_value').text_content()
        self.model.traits.isp = isp.strip()
        if len(country_info) > 3:
            cntr_en = ' '.join(country_info[:len(country_info) - 2])
        else:
            cntr_en = country_info[0]
        self.model.country.en = cntr_en.strip()
        region = await locators.rows.locator('nth=1 >> div.card__col_value').text_content()
        self.model.region.en = region.strip() if 'N/A' not in region else ''
        city = await locators.rows.locator('nth=2 >> div.card__col_value').text_content()
        self.model.city.en = city.strip() if 'N/A' not in city else ''
        zip = await locators.rows.locator('nth=3 >> div.card__col_value').text_content()
        self.model.location.zip = zip.strip() if 'N/A' not in zip else ''
        timezone = await locators.rows.locator('nth=10 >> div.card__col_value').text_content()
        self.model.location.timezone = timezone.strip()

    async def inner_task(self, ip):
        self.tags_to_abort += ['googletag', 'yandex', 'google-analytics',
                               'doubleclick', 'ads']
        await self.prepare_context()
        await self.prepare_page()
        locators = Locators(self.page)
        await self.page.goto('https://whoer.net/checkwhois')
        self.dictionary['status'] = '200 OK'
        await locators.input.fill(ip)
        await locators.submit_button.click()
        await self.page.wait_for_selector('strong.your-ip')
        await self.parse_data(locators, ip)

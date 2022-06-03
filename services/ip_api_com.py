import re

from models.base_service import BaseService


class IP_API_Com(BaseService):
    name = 'ip_api_com'

    async def parse_data(self, data: dict):
        self.model.country.code = data.get('countryCode', '')
        if self.only_country_code:
            return
        self.model.traits.ip = data.get('query', '')
        self.model.traits.isp = data.get('isp', '')
        self.model.city.en = data.get('city', '')
        self.model.region.en = data.get('regionName', '')
        self.model.region.code = data.get('region', '')
        self.model.country.en = data.get('country', '')
        self.model.continent.code = data.get('continentCode', '')
        self.model.continent.en = data.get('continent', '')
        self.model.location.zip = data.get('zip', '')
        self.model.location.timezone = data.get('timezone', '')
        self.model.location.latitude = str(data.get('lat', ''))
        self.model.location.longitude = str(data.get('lon', ''))

    async def inner_task(self, ip):
        self.tags_to_abort = ['png', 'svg', 'jpg', 'jpeg', 'woff',
                              'woff2', 'css', 'cache', 'ico']
        await self.prepare_context()
        await self.prepare_page()
        regex = re.compile(rf"https://demo\.ip-api\.com/json/{ip}\?.*")
        async with self.page.expect_response(regex) as response_info:
            await self.page.goto(f'https://ip-api.com/#{ip}')
        response = await response_info.value
        self.dictionary['status'] = f'{response.status} {response.status_text}'
        if response.ok:
            data = await response.json()
            await self.parse_data(data)

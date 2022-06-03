import re

from locators.ipregistry import Locators
from models.base_service import BaseService


class IpRegistry(BaseService):
    name = 'ipregistry'

    async def parse_data(self, data: dict):
        self.model.country.code = data.get('location', {}).get('country', {}).get('code', '') or ''
        if self.only_country_code:
            return
        self.model.traits.ip = data.get('ip', '') or ''
        self.model.traits.isp = data.get('connection', {}).get('organization', '') or ''
        self.model.traits.network = data.get('connection', {}).get('route', '') or ''
        self.model.city.en = data.get('location', {}).get('city', '') or ''
        self.model.region.en = data.get('location', {}).get('region', {}).get('name', '') or ''
        self.model.region.code = data.get('location', {}).get('region', {}).get('code', '') or ''
        self.model.country.en = data.get('location', {}).get('country', {}).get('name', '') or ''
        self.model.continent.en = data.get('location', {}).get('continent', {}).get('name', '') or ''
        self.model.continent.code = data.get('location', {}).get('continent', {}).get('code', '') or ''
        self.model.location.zip = data.get('location', {}).get('postal', '') or ''
        self.model.location.latitude = str(
            data.get('location', {}).get('latitude', '')) or ''
        self.model.location.longitude = str(
            data.get('location', {}).get('longitude', '')) or ''
        self.model.location.timezone = data.get('time_zone', {}).get('id', '') or ''

    async def inner_task(self, ip):
        self.tags_to_abort += ['images', 'avatars', 'crisp', 'analytics',
                               'doubleclick', 'photo']
        await self.prepare_context()
        await self.prepare_page()
        locators = Locators(self.page)
        regex = re.compile(rf"https://api\.ipregistry\.co/{ip}\?.*")
        await self.page.goto('https://ipregistry.co/')
        await self.page.wait_for_selector('span:has-text("ip")')
        await locators.input_ip_textarea.fill(ip)
        async with self.page.expect_response(regex) as response_info:
            await locators.submit_button.click()
        response = await response_info.value
        self.dictionary['status'] = f'{response.status} {response.status_text}'
        if response.ok:
            data = await response.json()
            await self.parse_data(data)

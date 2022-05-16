import json
import re

from locators.ipdata import Locators
from models.service import Service


class IpData(Service):
    name = 'ipdata'

    async def parse_data(self, r_json: dict):
        self.model.country.code = r_json.get('country_code', '') or ''
        if self.only_country_code:
            return
        self.model.traits.ip = r_json.get('ip', '') or ''
        self.model.traits.network = r_json.get('asn', {}).get('route', '') or ''
        self.model.traits.isp = r_json.get('asn', {}).get('name', '') or ''
        self.model.city.en = r_json.get('city', '') or ''
        self.model.region.en = r_json.get('region', '') or ''
        self.model.region.code = r_json.get('region_code', '') or ''
        self.model.country.en = r_json.get('country_name', '') or ''
        self.model.continent.en = r_json.get('continent_name', '') or ''
        self.model.continent.code = r_json.get('continent_code', '') or ''
        self.model.location.zip = r_json.get('postal', '') or ''
        self.model.location.latitude = str(r_json.get('latitude', '')) or ''
        self.model.location.longitude = str(r_json.get('longitude', '')) or ''
        self.model.location.timezone = r_json.get('time_zone', {}).get('name', '') or ''

    async def inner_task(self, ip):
        self.tags_to_abort += ['font', 'googletag', 'googleads', 'doubleclick']
        await self.prepare_context()
        await self.prepare_page()
        locators = Locators(self.page)
        regex = re.compile(rf"https://api\.ipdata\.co/{ip}\?.*")
        await self.page.goto('https://ipdata.co')
        await self.page.wait_for_selector('code#demo')
        await locators.input_ip_textarea.fill(ip)
        async with self.page.expect_response(regex) as response_info:
            await locators.submit_button.click()
        response = await response_info.value
        self.dictionary['status'] = f'{response.status} {response.status_text}'
        if response.ok:
            response_raw = await response.body()
            response_str = re.sub(
                re.compile(r"j.*\("), '',
                response_raw.decode('utf-8')
            ).replace(')', '')
            response_json = json.loads(response_str)
            await self.parse_data(response_json)

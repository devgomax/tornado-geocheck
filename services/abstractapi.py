import os

from models.service import Service


class AbstractApi(Service):
    name = 'abstractapi'

    async def parse_data(self, data: dict):
        if self.only_country_code:
            self.model.country.code = data.get('country_code', '') or ''
            return
        self.model.traits.ip = data.get('ip_address', '') or ''
        self.model.traits.isp = data.get('connection', {}).get('isp_name', '') or ''
        self.model.city.en = data.get('city', '') or ''
        self.model.region.en = data.get('region', '') or ''
        self.model.region.code = data.get('region_iso_code', '') or ''
        self.model.country.en = data.get('country', '') or ''
        self.model.country.code = data.get('country_code', '') or ''
        self.model.continent.en = data.get('continent', '') or ''
        self.model.continent.code = data.get('continent_code', '') or ''
        self.model.location.zip = data.get('postal_code', '') or ''
        self.model.location.latitude = str(data.get('latitude', '')) or ''
        self.model.location.longitude = str(data.get('longitude', '')) or ''
        self.model.location.timezone = data.get('timezone', {}).get('name', '') or ''

    async def inner_task(self, ip):
        await self.prepare_context(
            base_url='https://ipgeolocation.abstractapi.com'
        )
        response = await self.context.request.get(
            '/v1/',
            params={'api_key': os.getenv('ABSTRACTAPI_KEY'), 'ip_address': ip})
        self.dictionary['status'] = f'{response.status} {response.status_text}'
        if response.ok:
            data = await response.json()
            await self.parse_data(data)

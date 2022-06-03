from models.base_service import BaseService


class Maxmind(BaseService):
    name = 'maxmind'

    async def parse_data(self, data: dict):
        self.model.country.code = data.get('country', {}).get('iso_code', '')
        if self.only_country_code:
            return
        self.model.traits.ip = data.get('traits', {}).get('ip_address', '')
        self.model.traits.isp = data.get('traits', {}).get('isp', '')
        self.model.traits.network = data.get('traits', {}).get('network', '')
        self.model.city.en = data.get('city', {}).get('names', {}).get('en', '')
        self.model.city.ru = data.get('city', {}).get('names', {}).get('ru', '')
        self.model.region.en = data.get('subdivisions', [{}])[0].get('names', {}).get('en', '')
        self.model.region.ru = data.get('subdivisions', [{}])[0].get('names', {}).get('ru', '')
        self.model.region.code = data.get('subdivisions', [{}])[0].get('iso_code', '')
        self.model.country.ru = data.get('country', {}).get('names', {}).get('ru', '')
        self.model.country.en = data.get('country', {}).get('names', {}).get('en', '')
        self.model.continent.code = data.get('continent', {}).get('code', '')
        self.model.continent.en = data.get('continent', {}).get('names', {}).get('en', '')
        self.model.continent.ru = data.get('continent', {}).get('names', {}).get('ru', '')
        self.model.location.zip = data.get('postal', {}).get('code', '')
        self.model.location.longitude = str(
            data.get('location', {}).get('longitude', ''))
        self.model.location.latitude = str(
            data.get('location', {}).get('latitude', ''))
        self.model.location.timezone = data.get('location', {}).get('time_zone', '')

    async def inner_task(self, ip):
        self.tags_to_abort += ['mmapiws', 'stats', 'google']
        await self.prepare_context()
        await self.prepare_page()
        async with self.page.expect_response(
                f'https://www.maxmind.com/geoip/v2.1/city/{ip}?demo=1'
        ) as response_info:
            await self.page.goto(
                f'https://www.maxmind.com/en/geoip2-precision-demo?ip_address={ip}'
            )
        response = await response_info.value
        self.dictionary['status'] = f'{response.status} {response.status_text}'
        if response.ok:
            data = await response.json()
            await self.parse_data(data)

from models.service import Service


class IpApi_Co(Service):
    name = 'ipapi_co'

    async def parse_data(self, data: dict):
        self.model.country.code = data.get('country_code', '')
        if self.only_country_code:
            return
        self.model.traits.ip = data.get('ip', '')
        self.model.traits.isp = data.get('org', '')
        self.model.city.en = data.get('city', '')
        self.model.region.en = data.get('region', '')
        self.model.region.code = data.get('region_code', '')
        self.model.country.en = data.get('country_name', '')
        self.model.continent.code = data.get('continent_code', '')
        self.model.location.zip = data.get('postal', '')
        self.model.location.latitude = str(data.get('latitude', ''))
        self.model.location.longitude = str(data.get('longitude', ''))
        self.model.location.timezone = data.get('timezone', '')

    async def inner_task(self, ip):
        await self.prepare_context(base_url='https://ipapi.co')
        response = await self.context.request.get(f'/{ip}/json/')
        self.dictionary['status'] = f'{response.status} {response.status_text}'
        if response.ok:
            data = await response.json()
            await self.parse_data(data)

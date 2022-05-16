from models.service import Service


class IpGeoLocation_Io(Service):
    name = 'ipgeolocation_io'

    async def parse_data(self, data: dict):
        self.model.country.code = data.get('country_code2', '')
        if self.only_country_code:
            return
        self.model.traits.ip = data.get('ip', '')
        self.model.traits.isp = data.get('isp', '')
        self.model.city.en = data.get('city', '')
        self.model.country.en = data.get('country_name', '')
        self.model.continent.code = data.get('continent_code', '')
        self.model.continent.en = data.get('continent_name', '')
        self.model.location.zip = data.get('zipcode', '')
        self.model.location.latitude = str(data.get('latitude', ''))
        self.model.location.longitude = str(data.get('longitude', ''))
        self.model.location.timezone = data.get('time_zone', {}).get('name', '')

    async def inner_task(self, ip):
        await self.prepare_context(base_url='https://api.ipgeolocation.io')
        response = await self.context.request.get(
            '/ipgeo',
            params={'include': 'hostname', 'ip': ip},
            headers={'Referer': 'https://ipgeolocation.io/'})
        self.dictionary['status'] = f'{response.status} {response.status_text}'
        if response.ok:
            data = await response.json()
            await self.parse_data(data)

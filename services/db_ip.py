from models.service import Service


class DB_IP(Service):
    name = 'db_ip'

    async def parse_data(self, data: dict):
        self.model.country.code = data.get('demoInfo', {}).get('countryCode', '')
        if self.only_country_code:
            return
        self.model.traits.ip = data.get('demoInfo', {}).get('ipAddress', '')
        self.model.traits.isp = data.get('demoInfo', {}).get('isp', '')
        self.model.city.en = data.get('demoInfo', {}).get('city', '')
        self.model.region.en = data.get('demoInfo', {}).get('stateProv', '')
        self.model.region.code = data.get('demoInfo', {}).get('stateProvCode', '')
        self.model.country.en = data.get('demoInfo', {}).get('countryName', '')
        self.model.continent.code = data.get('demoInfo', {}).get('continentCode', '')
        self.model.continent.en = data.get('demoInfo', {}).get('continentName', '')
        self.model.location.latitude = str(data.get('demoInfo', {}).get('latitude', ''))
        self.model.location.longitude = str(data.get('demoInfo', {}).get('longitude', ''))
        self.model.location.timezone = data.get('demoInfo', {}).get('timeZone', '')

    async def inner_task(self, ip):
        await self.prepare_context(
            locale='en-US',
            base_url='https://db-ip.com'
        )
        response = await self.context.request.get(
            '/demo/home.php', params={'s': ip}
        )
        self.dictionary['status'] = f'{response.status} {response.status_text}'
        if response.ok:
            data = await response.json()
            await self.parse_data(data)

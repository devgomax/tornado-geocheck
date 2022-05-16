from models.service import Service


class Api4Ip(Service):
    name = 'api4ip'

    async def parse_data(self, data: dict):
        self.model.country.code = data.get('countryCode', '')
        if self.only_country_code:
            return
        self.model.traits.ip = data.get('ip', '')
        self.model.traits.isp = data.get('isp', '')
        self.model.city.en = data.get('city', '')
        self.model.country.en = data.get('country', '')
        self.model.location.latitude = str(data.get('latitude', ''))
        self.model.location.longitude = str(data.get('longitude', ''))

    async def inner_task(self, ip):
        await self.prepare_context(base_url='http://api4ip.info')
        response = await self.context.request.get(
            '/api/ip/check', params={'ip': ip}
        )
        self.dictionary['status'] = f'{response.status} {response.status_text}'
        if response.ok:
            data = await response.json()
            await self.parse_data(data)

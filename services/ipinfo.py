from models.service import Service


class IpInfo(Service):
    name = 'ipinfo'

    async def parse_data(self, data: dict):
        self.model.country.code = data.get('data', {}).get('country', '')
        if self.only_country_code:
            return
        self.model.traits.ip = data.get('data', {}).get('ip', '')
        self.model.traits.isp = data.get('data', {}).get('asn', {}).get(
            'name', '')
        self.model.traits.network = data.get('data', {}).get('asn', {}).get(
            'route', '')
        self.model.city.en = data.get('data', {}).get('city', '')
        self.model.region.en = data.get('data', {}).get('region', '')
        self.model.location.zip = data.get('data', {}).get('postal', '')
        self.model.location.latitude, self.model.location.longitude = data.get(
            'data', {}).get('loc', ',').split(',')
        self.model.location.timezone = data.get('data', {}).get('timezone',
                                                                  '')

    async def inner_task(self, ip):
        await self.prepare_context(base_url='https://ipinfo.io')
        response = await self.context.request.get(
            f'/widget/demo/{ip}',
            headers={
                'Referer': 'https://ipinfo.io/products/ip-geolocation-api?'
            }
        )
        self.dictionary['status'] = f'{response.status} {response.status_text}'
        if response.ok:
            data = await response.json()
            await self.parse_data(data)

from models.service import Service


class IpApi_Com(Service):
    name = 'ipapi_com'

    async def parse_data(self, r_json: dict):
        self.model.country.code = r_json.get('country_code', '')
        if self.only_country_code:
            return
        self.model.traits.ip = r_json.get('ip', '')
        self.model.traits.isp = r_json.get('connection', {}).get('isp', '')
        self.model.city.en = r_json.get('city', '')
        self.model.region.en = r_json.get('region_name', '')
        self.model.region.code = r_json.get('region_BY', '')
        self.model.country.en = r_json.get('country_name', '')
        self.model.continent.code = r_json.get('continent_code', '')
        self.model.continent.en = r_json.get('continent_name', '')
        self.model.location.zip = r_json.get('zip', '')
        self.model.location.latitude = str(r_json.get('latitude', ''))
        self.model.location.longitude = str(r_json.get('longitude', ''))
        self.model.location.timezone = r_json.get('time_zone', {}).get('id', '')

    async def inner_task(self, ip):
        await self.prepare_context(base_url='https://ipapi.com')
        response = await self.context.request.get(
            '/ip_api.php', params={'ip': ip}
        )
        self.dictionary['status'] = f'{response.status} {response.status_text}'
        if response.ok:
            data = await response.json()
            await self.parse_data(data)

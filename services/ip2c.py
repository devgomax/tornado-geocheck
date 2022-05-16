from ipaddress import IPv4Address

from models.service import Service


class Ip2C(Service):
    name = 'ip2c'

    async def parse_data(self, data: list):
        if len(data) == 4:
            self.model.country.code = data[1]
            self.model.country.en = data[3]

    async def inner_task(self, ip):
        await self.prepare_context(base_url='https://ip2c.org')
        response = await self.context.request.get(f'/{int(IPv4Address(ip))}')
        self.dictionary['status'] = f'{response.status} {response.status_text}'
        if response.ok:
            data = await response.text()
            await self.parse_data(data.split(';'))

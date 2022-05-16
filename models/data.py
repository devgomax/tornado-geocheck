from dataclasses import dataclass, field


@dataclass
class City:
    ru: str = ""  # Омск
    en: str = ""  # Omsk


@dataclass
class Region:
    ru: str = ""  # Омская область
    en: str = ""  # Omsk Oblast
    code: str = ""  # OMS


@dataclass
class Country:
    ru: str = ""  # Россия
    en: str = ""  # Russia
    code: str = ""  # RU


@dataclass
class Continent:
    ru: str = ""  # Европа
    en: str = ""  # Europe
    code: str = ""  # EU


@dataclass
class Location:
    latitude: str = ""  # 54.9978
    longitude: str = ""  # 73.4001
    timezone: str = ""  # Asia/Omsk
    zip: str = ""  # 644000


@dataclass
class Traits:
    ip: str = ""  # 94.137.20.203
    isp: str = ""  # Omskie kabelnye seti Ltd.
    network: str = ""  # 94.137.20.0/24


@dataclass
class IPModel:
    traits: Traits = field(default_factory=Traits)
    city: City = field(default_factory=City)
    region: Region = field(default_factory=Region)
    country: Country = field(default_factory=Country)
    continent: Continent = field(default_factory=Continent)
    location: Location = field(default_factory=Location)

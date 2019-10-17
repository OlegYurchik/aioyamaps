import aiohttp
import json
from typing import Sequence, Union
import xmltodict


class YaMapsException(Exception):
    pass


class IncorrectFormatException(YaMapsException):
    def __init__(self, format: str):
        super().__init__(f"Incorrect format '{format}")
        self.format = format


class YaMapsClient:
    GEOCODE_URL = "http://geocode-maps.yandex.ru/1.x/"

    HOUSE = "house"
    STREET = "street"
    METRO = "metro"
    DISTRICT = "district"
    LOCALITY = "locality"
    TOPONYMS = (HOUSE, STREET, METRO, DISTRICT, LOCALITY)

    JSON = "json"
    XML = "xml"
    FORMATS = (JSON, XML)

    RUSSIAN = "ru_RU"
    UKRAINIAN = "uk_UA"
    BELORUSSIAN = "be_BY"
    ENGLISH_RUSSIAN = "en_RU"
    ENGLISH_USA = "en_US"
    TURKISH = "tr_TR"
    language = (RUSSIAN, UKRAINIAN, BELORUSSIAN, ENGLISH_RUSSIAN, ENGLISH_USA, TURKISH) 

    def __init__(self, api_key: str):
        self.api_key = api_key

    async def addresses_by_coordinates(self, longitude: float, latitude: float,
                                       toponym: Union[str, None]=None,
                                       border: Union[Sequence, None]=None, format: str=XML,
                                       count: int=10, offset: int=0, language: str=RUSSIAN):
        request_data = {
            "url": self.GEOCODE_URL,
            "params": {
                "apikey": self.api_key,
                "geocode": f"{longitude},{latitude}",
                "format": format,
                "results": count,
                "skip": offset,
                "lang": language,
            },
        }
        if toponym is not None and toponym in self.TOPONYMS:
            request_data["params"]["kind"] = toponym
        if border is not None:
            request_data["params"]["rspn"] = 1
            request_data["params"]["bbox"] = "%s,%s-%s,%s" % border

        async with aiohttp.ClientSession() as session:
            async with session.get(**request_data) as response:
                response_data = await response.text()

        if format == self.JSON:
            response_data = json.loads(response_data)
            response_data = response_data["response"]["GeoObjectCollection"]["featureMember"]
        elif format == self.XML:
            response_data = xmltodict.parse(response_data)

        return response_data

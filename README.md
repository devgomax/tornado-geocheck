# Настройка проекта:
* Создать и запустить виртуальное окружение для проекта `python -m venv venv`
* Активировать окружение `source venv/bin/activate`
* Установить зависимости `pip install -r requirements.txt`
* Установить браузеры для PlayWright `playwright install`
* Создать пустой файл с названием log.json в корне проекта
* Создать файл `.env` для переменных окружения в корне проекта
* * Добавить в файл `.env` apikey сервиса abstractapi.com в переменную `ABSTRACTAPI_KEY`
# Для запуска скрипта:
* `python main.py --ips={список IP адресов через запятую без пробелов}`
#### примеры строки: 
* `python main.py --ips=123.123.123.123`
* `python main.py --ips=123.123.123.123,222.222.222.222`
# Вывод данных
### Подробный вывод пишется в файл log.json, пример:
```
{
  "ip2location": {
    "status": "",
    "data": {
      "traits": {
        "ip": "",
        "isp": "",
        "network": ""
      },
      "city": {
        "ru": "",
        "en": ""
      },
      "region": {
        "ru": "",
        "en": "",
        "code": ""
      },
      "country": {
        "ru": "",
        "en": "",
        "code": ""
      },
      "continent": {
        "ru": "",
        "en": "",
        "code": ""
      },
      "location": {
        "latitude": "",
        "longitude": "",
        "timezone": "",
        "zip": ""
      }
    }
  },
  "api4ip": {...},
  "maxmind": {...},
  ...
}
```
### Упрощенный вывод пишется в консоль, пример:
```
{
  "ip": "82.200.37.207",
  "data": {
    "maxmind": {
      "country": "RU",
      "city": "Omsk"
    },
    "ipinfo": {...},
    "2ip": {...},
    "ipapi_com": {...}
    ...
  }
}
...
```
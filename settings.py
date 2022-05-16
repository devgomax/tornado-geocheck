# Prints exception's info if True
DEBUG = False

# Checks only country_code from each service if True
ONLY_COUNTRY_CODE = False

# Writes geodata to log.json if True
WRITE_TO_FILE = False

# Truncates log.json before new writing if True
REWRITE_LOG_FILE = True

# Default timeout for browser actions
TIMEOUT = 10000

# Multiplies timeout value after each failed check try
TO_MULTIPLIER = 1.1

# Defines how many times in total it must check each service if it fails
RETRIES_COUNT = 3

# Name of file we should take proxies from
PROXIES_FILENAME = 'data_files/geoCheck_proxy.txt'

# Name of file where should write json logs
LOG_FILENAME = 'data_files/log.json'

# Name of file we should take user_agents from
UA_FILENAME = 'data_files/user_agents.txt'

# Name of file where we will store a start point of proxy we will get as next
CURSOR_FILENAME = 'data_files/cursor.txt'

# Defines the order of data to be returned from script
KEY_ORDER = {
    'maxmind': {},
    'db_ip': {},
    'ip2location': {},
    'ipinfo': {},
    '2ip': {},
    'whoer': {},
    'abstractapi': {},
    'ipapi_co': {},
    'ipapi_com': {},
    'ip_api_com': {},
    'ipgeolocation_io': {},
    'ipregistry': {},
    'ipdata': {},
    'ip2c': {}
}

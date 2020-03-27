from configparser import ConfigParser

cp = ConfigParser()
cp.read('config', encoding='utf-8')
interval = cp.get('scheduler', 'refresh_interval')
print(interval)
import json
from data.regions import Region
from data import db_session

#  Обновляем статистику в БД (берем из yandex_statisctics.json)


with open('yandex_statistics.json', 'r') as stats:
    data = stats.read()

data = json.loads(data)
regions = data['data']['items'][180:]
print(regions)

db_session.global_init("../db/database.sqlite")
session = db_session.create_session()
for region in regions:
    name = region['name']
    reg = session.query(Region).filter(Region.name == name).first()
    if reg:
        reg.cases = region['cases']
        reg.cured = region['cured']
        reg.deaths = region['deaths']
        reg.lon = region['coordinates'][0]
        reg.lat = region['coordinates'][1]
        session.commit()
    else:
        reg = Region()
        reg.name = region['name']
        reg.cases = region['cases']
        reg.cured = region['cured']
        reg.deaths = region['deaths']
        reg.lon = region['coordinates'][0]
        reg.lat = region['coordinates'][1]
        session.add(reg)
        session.commit()

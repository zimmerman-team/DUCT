from geodata.importer.country import CountryImport
from geodata.importer.region import RegionImport
from geodata.importer.subnational import SubnationalImport

print('Country data')
ci = CountryImport()
ci.update_polygon()
ci.update_alt_name()
ci.update_country_center()

print('Region data')
ri = RegionImport()
ri.update_region_center()

print('Subnational data')
si = SubnationalImport()
si.update_polygon()

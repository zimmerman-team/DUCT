from geodata.importer.country import CountryImport
from geodata.importer.region import RegionImport
from geodata.importer.subnational import SubnationalImport

print('Region data')
ri = RegionImport()
ri.update_region_center()

print('Country data')
ci = CountryImport()
ci.update_polygon()
ci.update_alt_name()
ci.update_country_center()
ci.update_regions()


print('Subnational data')
si = SubnationalImport()
si.update_polygon()

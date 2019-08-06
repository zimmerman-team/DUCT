from geodata.importer.country import CountryImport
# from geodata.importer.region import RegionImport
from geodata.importer.subnational import SubnationalImport

# print('Region data')
# ri = RegionImport()
# ri.update_region_center()

print('Country data')
ci = CountryImport()
ci.update_polygon()
ci.update_alt_name()
ci.update_country_center()
ci.update_regions()
ci.update_hd_polygons()
ci.update_region_polygons_centers()


print('Subnational data')
si = SubnationalImport()
si.update_polygon()
si.update_kenya()
si.update_kenya_county_centers()

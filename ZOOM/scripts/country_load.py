from geodata.importer.country import CountryImport
from geodata.importer.region import RegionImport

ci = CountryImport()
ci.update_polygon()
ci.update_alt_name()

ri = RegionImport()
ri.update_region_center()

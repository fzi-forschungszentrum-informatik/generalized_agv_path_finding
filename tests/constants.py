from generalized_path_finding.nodes import GeoCoords

# distance checks out with online results, online seems to have lower speed limits, as duration is shorter here.
# https://www.openstreetmap.org/directions?engine=fossgis_osrm_car&route=42.46333811337092%2C1.489878394942694%3B42.50946473317848%2C1.5397046939511791#map=14/42.48647/1.51457
ORIGIN = GeoCoords(42.46333811337092, 1.489878394942694)
DESTINATION = GeoCoords(42.50946473317848, 1.5397046939511791)
DURATION = 507.478  # this is internally an int in milliseconds (here in seconds)
DISTANCE = 7807.0  # this is internally an int in meters

# after snapping to grid:
EXACT_ORIGIN = GeoCoords(lat=42.463077545166016, lon=1.4901460409164429)
EXACT_DESTINATION = GeoCoords(lat=42.509552001953125, lon=1.5399820804595947)

KPH_PER_MPS = 3.6

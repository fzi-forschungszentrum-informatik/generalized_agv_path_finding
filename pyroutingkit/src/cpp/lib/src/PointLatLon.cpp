#include "pyroutingkit/PointLatLon.h"
#include <stdio.h>
#include <sstream>
#include <iomanip>

namespace fzi::routing {
PointLatLon::PointLatLon(double latitude, double longitude)
    : latitude(latitude)
    , longitude(longitude) {
}

bool PointLatLon::operator==(const PointLatLon& other) const {
    return this->latitude == other.latitude && this->longitude == other.longitude;
}

void PointLatLon::writeToFile(FILE* file) const {
    fwrite(&this->latitude, sizeof(double), 1, file);
    fwrite(&this->longitude, sizeof(double), 1, file);
}

std::string PointLatLon::toString() const {
    std::stringstream stream;
    stream << "(";
    stream << std::fixed << std::setprecision(6);
    stream << latitude << ", " << longitude << ")";
    return stream.str();
}

PointLatLon PointLatLon::readFromFile(FILE* file) {
    double lat;
    double lon;
    fread(&lat, sizeof(double), 1, file);
    fread(&lon, sizeof(double), 1, file);
    return PointLatLon(lat, lon);
}

} // namespace fzi::routing
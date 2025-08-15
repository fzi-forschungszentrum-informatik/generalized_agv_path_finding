#pragma once
#include <stdio.h>
#include <string>

namespace fzi::routing {
class PointLatLon {
public:
    PointLatLon(double latitude, double longitude);
    bool operator==(const PointLatLon& other) const;

    double latitude;
    double longitude;

    void writeToFile(FILE* file) const;
    std::string toString() const;

    static PointLatLon readFromFile(FILE* file);

};
} // namespace fzi::ridesharing
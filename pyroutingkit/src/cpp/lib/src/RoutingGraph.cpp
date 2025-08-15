#include <stdio.h>
#include <pyroutingkit/RoutingGraph.h>

namespace fzi::routing {
unsigned RoutingGraph::nodeCount() const {
    return this->latitude.size();
}

unsigned RoutingGraph::arcCount() const {
    return this->head.size();
}

void writePointLatLonVector(const std::vector<PointLatLon>& pointVec, FILE* file)
{
    unsigned entries = pointVec.size();

    fwrite(&entries, sizeof(unsigned), 1, file);
    for (int i = 0; i < entries; i++) {
        pointVec[i].writeToFile(file);
    };
}

void readPointLatLonVector(FILE* file, std::vector<PointLatLon>* destination) 
{
    unsigned entries;
    fread(&entries, sizeof(unsigned), 1, file);
    for (int i = 0; i < entries; i++) {
        PointLatLon pointVec = PointLatLon::readFromFile(file);
        destination->push_back(pointVec);
    };
}

void RoutingGraph::store(const char* filePath) const {
    FILE* file = fopen(filePath, "wb");
    const unsigned arcCount = this->arcCount();
    const unsigned nodeCount = this->nodeCount();
    fwrite(&nodeCount, sizeof(unsigned), 1, file);
    fwrite(&arcCount, sizeof(unsigned), 1, file);
    fwrite(&(this->firstOut[0]), sizeof(unsigned), nodeCount + 1, file);
    fwrite(&(this->head[0]), sizeof(unsigned int), arcCount, file);
    fwrite(&(this->tail[0]), sizeof(unsigned), arcCount, file);
    fwrite(&(this->travelTime[0]), sizeof(unsigned), arcCount, file);
    fwrite(&(this->geoDistance[0]), sizeof(unsigned), arcCount, file);
    fwrite(&(this->osmWayId[0]), sizeof(uint64_t), arcCount, file);
    fwrite(&(this->latitude[0]), sizeof(float), nodeCount, file);
    fwrite(&(this->longitude[0]), sizeof(float), nodeCount, file);
    fwrite(&(this->osmNodeId[0]), sizeof(uint64_t), nodeCount, file);

    for (int i = 0; i < arcCount; i++)
    {
        writePointLatLonVector(this->geometry[i], file);
    }

    fclose(file);
}

RoutingGraph RoutingGraph::load(const char* filePath) {
    FILE* file = fopen(filePath, "rb");
    unsigned nodeCount;
    unsigned arcCount;
    fread(&nodeCount, sizeof(unsigned), 1, file);
    fread(&arcCount, sizeof(unsigned), 1, file);

    RoutingGraph routingGraph;

    routingGraph.firstOut.resize(nodeCount + 1);
    routingGraph.head.resize(arcCount);
    routingGraph.tail.resize(arcCount);
    routingGraph.geoDistance.resize(arcCount);
    routingGraph.travelTime.resize(arcCount);
    routingGraph.osmWayId.resize(arcCount);
    routingGraph.latitude.resize(nodeCount);
    routingGraph.longitude.resize(nodeCount);
    routingGraph.osmNodeId.resize(nodeCount);
    routingGraph.geometry.resize(arcCount);

    fread(&(routingGraph.firstOut[0]), sizeof(unsigned), nodeCount + 1, file);
    fread(&(routingGraph.head[0]), sizeof(unsigned), arcCount, file);
    fread(&(routingGraph.tail[0]), sizeof(unsigned), arcCount, file);
    fread(&(routingGraph.travelTime[0]), sizeof(unsigned), arcCount, file);
    fread(&(routingGraph.geoDistance[0]), sizeof(unsigned), arcCount, file);
    fread(&(routingGraph.osmWayId[0]), sizeof(uint64_t), arcCount, file);
    fread(&(routingGraph.latitude[0]), sizeof(float), nodeCount, file);
    fread(&(routingGraph.longitude[0]), sizeof(float), nodeCount, file);
    fread(&(routingGraph.osmNodeId[0]), sizeof(uint64_t), nodeCount, file);

    for (int i = 0; i < arcCount; i++)
    {
        readPointLatLonVector(file, &(routingGraph.geometry[i]));
    }

    fclose(file);

    return routingGraph;
}
} // namespace fzi::routing
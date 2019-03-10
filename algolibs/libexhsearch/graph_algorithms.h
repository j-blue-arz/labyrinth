#pragma once

#include "static_graph.h"
#include "location.h"

namespace graph {

namespace algorithm {

bool isReachable(const StaticGraph & graph, const Location & source, const Location & target);

}

}
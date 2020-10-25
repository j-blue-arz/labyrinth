#pragma once

#include "solvers.h"

#include <future>

namespace labyrinth {
namespace solvers {
namespace exhsearch {

static std::atomic_bool is_aborted = false;

/** Aborts the current computation. This is only safe to use if findBestActions is called from a single thread.
 * Otherwise, this will abort all currently running computations in the best case, and might not have any effect at all
 * in the worst case.
 */
void abortComputation();

/** Searches for the lowest number of actions which lead to the objective. */
std::vector<PlayerAction> findBestActions(const SolverInstance& solver_instance);

} // namespace exhsearch
} // namespace solvers
} // namespace labyrinth

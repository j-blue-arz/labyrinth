### Experiments for minimax algorithm

The `instances` folder already contains generated instance files - json for the benchmark script, txt for algolibs c++.
The `results` folder contains benchmark results, evaluations and plots.

---

The minimax implementation uses iterative deepening without an upper bound on the depth. The benchmarks in this folder therefore
observe and plot the search depth increments of minimax runs for multiple instances.

To observe the search depths, run
    python depths.py --folder instances/ --outfile sample_depths.csv --library ../lib/libminimax.so
The instances to run can be selected with the `--pattern` option, e.g. `--pattern minimax_s7*.json`.

After that determine the depth increments with
    python evaluate.py increments sample_depths.csv depth_increments.csv

Then create a plot with
    python evaluate.py plot depth_increments.csv depths.png

---

See docstrings in the respective modules for further instructions.
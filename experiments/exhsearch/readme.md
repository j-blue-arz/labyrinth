### Experiments for exhaustive search algorithm

The `instances` folder already contains generated instance files - json for the benchmark script, txt for algolibs c++.
The `results` folder contains benchmark results, evaluations and plots.

---

To run the exhsearch library on all of these instances, invoke
    python benchmark.py --folder instances/ --outfile benchmark_raw.csv --library ../lib/libexhsearch.so
The instances to run can be selected with the `--pattern` option, e.g. `--pattern exhsearch_s7*.json`.

After that reduce the benchmark times with
    python compare.py combine --outfile benchmark.csv -n libexhsearch benchmark_raw.csv

Then create a plot with
    python evaluate.py benchmark.csv plot.png

---

See docstrings in the respective modules for further instructions.
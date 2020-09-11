The scripts have dependencies to the labyrinth module, and hence have to be run as modules themselves, from the `backend/` directory.
All scripts require the path to the shared library libexhsearch. See instructions in main readme for compilation.

Running the scripts also requires the dependencies of `exp-requirements` to be installed in the virtual env.
For example (given the virtual env in `backend/` is activated):

    python -m experiments.exhsearch.benchmark instances --outfile results.csv --library instance/lib/libexhsearch.so --folder experiments/exhsearch/instances

The `instances` folder already contains generated instance files - json for the benchmark script, txt for algolibs c++.
The `results` folder contains benchmark results, evaluations and plots.
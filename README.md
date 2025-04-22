This is a very simple toy analysis based on our LQ -> eejj analysis, for the purpose of experimenting with `pocket-coffea`.
The documentation for `pocket-coffea` can be found here: https://pocketcoffea.readthedocs.io/en/stable/index.html

Before running any of this code, from lxplus:

If you haven't done so recently, run:
```
voms-proxy-init -voms cms -valid 192:00
```
Then set up the `pocket-coffea` environment on lxplus like:
```
apptainer shell -B /afs -B /cvmfs/cms.cern.ch \
                -B /tmp  -B /eos/cms/  -B /etc/sysconfig/ngbauth-submit \
                -B ${XDG_RUNTIME_DIR}  --env KRB5CCNAME="FILE:${XDG_RUNTIME_DIR}/krb5cc" \
    /cvmfs/unpacked.cern.ch/gitlab-registry.cern.ch/cms-analysis/general/pocketcoffea:lxplus-el9-stable
```
All commands listed here are to be run from inside this singularity container.
(The environment setup is also in the `pocket-coffea` documentation, see: https://pocketcoffea.readthedocs.io/en/stable/installation.html )

A discussion of how the code works and some sample results are given in the slides here: https://indico.cern.ch/event/1539421/contributions/6477874/attachments/3052591/5400931/pocket-coffea_Emma_22Apr25.pdf

In general, running a `pocket-coffea` analysis happens in three steps. 

(1) Build the datasets

(2) Run the analysis code

(3) Make plots

The dataset json files have been included in this repo, so while instructions to recreate them are given here, one could skip directly to step (2) if desired.

**********************************************************************************************************************************
(1) Build the datasets
```
pocket-coffea build-datasets --cfg datasets/datasets_definitions.json -o -rs 'T[123]_(FR|IT|BE|CH)_\w+'
```
```
pocket-coffea build-datasets --cfg datasets/datasets_definitions_signal.json -o -rs 'T[123]_(US)_\w+'
```
The `-rs` option specifies allowed sites.
This was not quite as straightforward as advertised.

-> Anything stored at desy was giving me "resource temporarily unavailable" messages, and I do not know why.

-> The signal samples seem to be only available at US sites.

-> It seemed to have issues reading the EGamma datasets if they were stored at a US site, but no problems at all if I don't allow US sites.

This is the reason that the signal dataset is in a separate `.json` file, and for running separate commands.
**********************************************************************************************************************************
(2) Run the analysis
```
pocket-coffea run --cfg config.py -o [name_of_output_dir] --executor dask@lxplus --scaleout 500
```
The `--cfg` option points to the config file, `-o` specifies the directory to store the output.
Then `--executor` specifies where to run (in this case condor submission from lxplus) and `--scaleout` is the number of workers.
More info about executors can be found here: https://pocketcoffea.readthedocs.io/en/stable/running.html#executors

For the code in this repo, the total run time for all of the samples is between 10 and 15 minutes once the jobs start to run.
To run over just a little bit of data from each sample as a test, one can instead run 
```
pocket-coffea run --cfg config.py -o [name_of_output_dir] --test
```
**********************************************************************************************************************************
(3) Make plots

From inside the directory where you stored the output, run:
```
pocket-coffea make-plots -i output_all.coffea --cfg parameters_dump.yaml --overwrite --overwrite-parameters ../plot_config.yaml --log
```
`output_all.coffea` and `parameters_dump.yaml` are outputs from running the analysis.
`--overwrite` overwrites any existing plots.
`--overwrite-parameters ../plot_config.yaml` uses the file `plot_config.yaml` (included in this repo) for plot styling instead of the defaults.
`--log` makes the y axis on the plots in log scale.
Since this toy analysis has two categories, "preselection" and "trainingRegion", the output `plots` folder will have a separate directory for each.

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
All commands listed here are to be run from inside this singularity container unless otherwise noted.
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
pocket-coffea build-datasets --cfg config/dataset_definitions/datasets_definitions.json -o -rs 'T[123]_(FR|IT|BE|CH)_\w+'
```
```
pocket-coffea build-datasets --cfg config/dataset_definitions/datasets_definitions_signal.json -o -rs 'T[123]_(US)_\w+'
```
The `-rs` option specifies allowed sites.
This was not quite as straightforward as advertised.

-> Anything stored at desy was giving me "resource temporarily unavailable" messages, and I do not know why.

-> The signal samples seem to be only available at US sites.

-> It seemed to have issues reading the EGamma datasets if they were stored at a US site, but no problems at all if I don't allow US sites.

This is the reason that the signal dataset is in a separate `.json` file, and for running separate commands.
**********************************************************************************************************************************
(2) Run the analysis

(2-a) Skims
```
pocket-coffea run --cfg config_skimOnly,py -o [name_of_output_dir] --executor condor@lxplus -ro params/run_options.yaml
```
This saves the skims in NanoAOD format.
It has its own `run_options.yaml` file because these jobs require more memory than if we only save the final selection columns and histograms.
Note that the skims run with direct condor submission rather than using dask, as the pocket-coffea experts have told us that this is better for large jobs.

The output from this command includes a file `skimmed_dataset_definitions.json` which can be used as-is in any subsequent configs without the need to run `build-datasets`.
Skims for EGamma and DY have already been made, so you could skip directly to running the preselection and final selections if desired (but see the note at the end of this section).

This outputs many small files, and it is recommended to `hadd` them to get fewer, larger files. Pocket-coffea has a script for this which can be run as follows:

Inside the container, run the following which produces scripts you will use to submit condor jobs. It will save the files to your current working directory. `[output folder]` is the folder in your AFS space that you specified with the `-o` option when you ran the skim jobs. `[place to put skims]` is the location where you would like the output NanoAOD root files to be saved.
```
pocket-coffea hadd-skimmed-files -fl [output folder]/output_all.coffea -o [place to put skims] --dry
```
Then, open the file `hadd_job_splitbyfile.sub` and change the job flavor from `esspresso` to `microcentury` (`esspresso` kills jobs after 20 minutes of runtime which I found to be too short).

Finally, outside the container, run the following command to submit the condor jobs
```
condor_submit hadd_job_splitbyfile.sub
```
Note:
When you run `hadd-skimmed-files`, it also produces a file `skimmed_dataset_definitions_hadd.json`. This can be used as-is in any later config files which run on the skims without the need to run `build-datasets`.

(2-b) Preselection and training regions

To run the preselection and training region selections:
```
pocket-coffea run --cfg config.py -o [name_of_output_dir] --executor dask@lxplus --scaleout 500
```
The `--cfg` option points to the config file, `-o` specifies the directory to store the output.
Then `--executor` specifies where to run (in this case condor submission from lxplus) and `--scaleout` is the number of workers.
More info about executors can be found here: https://pocketcoffea.readthedocs.io/en/stable/running.html#executors

`pocket-coffea` uses dask to schedule jobs.
It provides some useful job monitoring tools.
I found some nice instructions on how to access it here: https://higgs-dna.readthedocs.io/en/latest/jobs.html#connect-to-the-dashboard .
So for me, to connect to the dask dashboard on lxplus950 it worked to do the following from my local machine:
```
ssh -Y -N -f -L localhost:8000:lxplus950.cern.ch:8787 [my username]@lxplus950.cern.ch
```
Then, in a browser use `http://localhost:8000/status`

For the code in this repo, the total run time to do the preseleciton and final selections for all of the samples is about 10 minutes once the jobs start to run.
To run over just a little bit of data from each sample as a test, one can instead run 
```
pocket-coffea run --cfg config.py -o [name_of_output_dir] --test
```
Important note: 

`config.py` reads skim files from Emma's CERNBox space. 
The link is not posted here because this project is public, but if you ask Emma she will give you permission to access the relevant folder.

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

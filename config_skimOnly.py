import os
localdir = os.path.dirname(os.path.abspath(__file__))

from pocket_coffea.lib.columns_manager import ColOut
from pocket_coffea.parameters import defaults
from pocket_coffea.utils.configurator import Configurator
from pocket_coffea.lib.cut_definition import Cut
from pocket_coffea.lib.cut_functions import get_nObj_min, get_HLTsel, get_nPVgood, goldenJson, eventFlags
from pocket_coffea.parameters.cuts import passthrough
from pocket_coffea.parameters.histograms import *
import workflow
from workflow import eejjBaseProcessor
from pocket_coffea.lib.weights.common import common_weights

import cloudpickle
import custom_cut_functions 
import utilsLQ
cloudpickle.register_pickle_by_value(utilsLQ)
cloudpickle.register_pickle_by_value(workflow)
cloudpickle.register_pickle_by_value(custom_cut_functions)
from custom_cut_functions import *

default_parameters = defaults.get_default_parameters()
defaults.register_configuration_dir("config_dir",localdir+"/params")

parameters = defaults.merge_parameters_from_files(default_parameters, "{}/params/object_preselection.yaml".format(localdir),"{}/params/triggers.yaml".format(localdir), update=True)

cfg = Configurator(
    parameters = parameters, 
    datasets = {
        "jsons":["{}/datasets/DYJetsToLL_M-50.json".format(localdir), "{}/datasets/DATA_EGamma.json".format(localdir), "{}/datasets/LQToDEle_M-1500.json".format(localdir)],
        "filter": {
            "samples": ["DYJetsToLL", "DATA_EGamma"], #, "LQToDEle_M-1500"],
            "samples_exclude": ["LQToDEle_M-1500"],
            "year":["2018"]
        }
    },
    
    workflow = eejjBaseProcessor,
    save_skimmed_files = "root://eosuser.cern.ch://eos/user/e/eipearso/LQ/lqData/testCoffeaSkims/skims/",
    skim = [
            eventFlags,
            goldenJson,
            get_nPVgood(1),
            get_nObj_min(1, 50., "Electron"),
            get_HLTsel(primaryDatasets=["EGamma"])
    ],
    
    preselections = [passthrough],

    categories = {
        "sk": [passthrough]
    },

    weights_classes = common_weights,

    weights = {
        "common":{
            "inclusive":{},
            "bycategory":{}
        },
        "bysample":{}
    },

    variations = {
        "weights": {
            "common": {
                "inclusive":{},
                "bycategory" : {}
            },
        "bysample": {
        }    
        },
    },

    variables = {}
)

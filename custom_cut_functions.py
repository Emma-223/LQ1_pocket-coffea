import awkward as ak
from pocket_coffea.lib.cut_definition import Cut

def eejj(events, params, year, sample, **kwargs):
    mask = (
        (events.nElectronGood >= 2) & 
        (events.nJetGood >= 2) &
        (events.nMuonGood == 0) &
        (events.ll.mass > params["mll"]) &
        (events.sT_eejj > params["sT"]) & 
        (events.pT_ee > params["Pt_ee"]) 
    )
    return ak.where(ak.is_none(mask), False, mask)

def trainingRegion_common(events, params, year, sample, **kwargs):
    mask = (
        (events.sT_eejj > params["sT"]) &
        (events.ll.mass > params["mll"])
    )
    return ak.where(ak.is_none(mask), False, mask)

eejj_presel = Cut(
    name = "eejj_presel",
    params = {
        "mll": 50,
        "sT": 300,
        "Pt_ee": 70
    },
    function = eejj,
)

eejj_trainingRegion_common = Cut(
    name = "eejj_trainingRegion_common",
    params = {
        "mll": 220,
        "sT": 400
    },
    function = trainingRegion_common,
)

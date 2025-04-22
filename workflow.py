import awkward as ak
from utilsLQ.calculateMejsAndST import *

from pocket_coffea.workflows.base import BaseProcessorABC
from pocket_coffea.utils.configurator import Configurator
from pocket_coffea.lib.hist_manager import Axis
from pocket_coffea.lib.objects import (
    jet_correction,
    lepton_selection,
    jet_selection,
    btagging,
    get_dilepton,
)

class eejjBaseProcessor(BaseProcessorABC):
    def __init__(self, cfg: Configurator):
        super().__init__(cfg)

    def apply_object_preselection(self, variation):
        self.events["ElectronGood"] = lepton_selection(
            self.events, "Electron", self.params
        )
        self.events["MuonGood"] = lepton_selection(
            self.events, "Muon", self.params
        )
        leptons = ak.with_name(
            ak.concatenate((self.events.MuonGood, self.events.ElectronGood), axis=1),
            name='PtEtaPhiMCandidate',
        )
        self.events["LeptonGood"] = leptons[ak.argsort(leptons.pt, ascending=False)]

        jetsGoodUnsorted, self.jetGoodMask = jet_selection(
            self.events, "Jet", self.params, 
            year=self._year, 
            leptons_collection="LeptonGood"
        )
        self.events["JetGood"] = jetsGoodUnsorted[ak.argsort(jetsGoodUnsorted.pt, ascending=False)]

        self.events["ll"] = get_dilepton(
            self.events.ElectronGood, self.events.MuonGood
        )

    def count_objects(self, variation):
        self.events["nMuonGood"] = ak.num(self.events.MuonGood)
        self.events["nElectronGood"] = ak.num(self.events.ElectronGood)
        self.events["nLeptonGood"] = (
            self.events["nMuonGood"] + self.events["nElectronGood"]
        )
        self.events["nJetGood"] = ak.num(self.events.JetGood)

    def define_common_variables_before_presel(self, variation):
        elePts = ak.fill_none(ak.pad_none(self.events.ElectronGood.pt, 2, axis=1),0)
        elePhis = ak.fill_none(ak.pad_none(self.events.ElectronGood.phi, 2, axis=1),0)
        jetPts = ak.fill_none(ak.pad_none(self.events.JetGood.pt, 2, axis=1),0)
        self.events["sT_eejj"] = Calculate_sT_eejj(elePts, jetPts)
        self.events["pT_ee"] = Calculate_Pt_ee(elePts, elePhis)
        print(self.events.pT_ee)
        self.events["pt1stEle"] = elePts[:,0]
        self.events["pt2ndEle"] = elePts[:,1]

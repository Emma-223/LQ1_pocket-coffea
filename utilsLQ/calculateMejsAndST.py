import math
import numpy as np

def Calculate_sT_eejj(elePts, jetPts):
    sT = elePts[:,0] + elePts[:,1] + jetPts[:,0] + jetPts[:,1]
    return sT

def Calculate_Pt_ee(elePts, elePhis):
    pT_ee_x = elePts[:,0] * np.cos(elePhis[:,0]) + elePts[:,1] * np.cos(elePhis[:,1])
    pT_ee_y = elePts[:,0] * np.sin(elePhis[:,0]) + elePts[:,1] * np.sin(elePhis[:,1])
    pT_ee = np.sqrt(pT_ee_x ** 2 + pT_ee_y ** 2)
    return pT_ee

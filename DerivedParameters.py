import os
import pandas as pd

from SimulationsData import *



def DerivedParameters_f(ulaz):
    allData = pd.read_pickle(ulaz)


    allData["Ddr"] = allData["D"] / allData["d0"]
    allData["Ddr1"] = allData["D"] / allData["d1"]
    allData["Ddr2"] = allData["D"] / allData["d2"]
    allData["Ddr3"] = allData["D"] / allData["d3"]

    allData["T"] = allData["L"] / allData["H"]

    allData["GRPI"] = allData["L"]**3*(4*allData["D"]**2-allData["d0"]**2)/allData["d0"]**2
    allData["GRPI1"] = allData["L"]**3*(4*allData["D"]**2-allData["d1"]**2)/allData["d1"]**2
    allData["GRPI2"] = allData["L"]**3*(4*allData["D"]**2-allData["d2"]**2)/allData["d2"]**2
    allData["GRPI3"] = allData["L"]**3*(4*allData["D"]**2-allData["d3"]**2)/allData["d3"]**2

    allData["NAL"] = allData["L"]*(4*allData["D"]**2-allData["d0"]**2)/allData["d0"]**2
    allData["NAL"] = allData["L"]*(4*allData["D"]**2-allData["d1"]**2)/allData["d1"]**2
    allData["NAL"] = allData["L"]*(4*allData["D"]**2-allData["d2"]**2)/allData["d2"]**2
    allData["NAL"] = allData["L"]*(4*allData["D"]**2-allData["d3"]**2)/allData["d3"]**2



    # for i in allData:
    #     print(i)


    def Flag(S22, GR):
        if S22 < flagCondition["S22"][0] and GR < flagCondition["GR"][0]:
            flag = "A"
        elif flagCondition["S22"][0] <= S22 < flagCondition["S22"][1] and GR < flagCondition["GR"][1]:
            flag = "B"
        elif S22 >= flagCondition["S22"][1] and GR >= flagCondition["GR"][0]:
            flag = "C"


    v = []
    for key, value in allData.iteritems():
        allData.loc[key]












DerivedParameters_f(PickleData)
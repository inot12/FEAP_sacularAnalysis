"""
Class made to analyze every simulation. After FolderSearch, sim path and name is passed to every simulation dir


"""








import os, math
import numpy as np
import pandas as pd
from scipy.spatial import ConvexHull
# from openpyxl.styles import Font, PatternFill

from FolderSearch import FolderSearch
from SimulationsData import *


# chosenTimeSteps = [190, 220,280, 316, 350]



###################################################################################################################
# analyzing just one simulation for testing
oneSimTestPath = "/home/josip/feapMoje/pocetak/" + parametarskaAnaliza + "/rezultati/sakularna/r=10/parametar_k1/k1=1.06"
###################################################################################################################

#TSLenght depends on number of mesh elements. Same for all simulations
TSLenght = 51
TSLegnht_eIW = TSLenght + 3
TSLegnht_rIl = TSLenght + 1
TSLegnht_ctl = TSLenght + 1
TSLegnht_rN1704 = 1

###################################################################################################################


class DataExtraction:

    def __init__(self, resultsFolder, nSim=0):
        self.nSim = nSim

        if allSimulationsAnalysis == True:
            self.objectDE = FolderSearch(resultsFolder)         # DataExtraction object
            self.simPath = self.objectDE.allPaths[self.nSim]    # get info from FolderSearch
            self.simName = self.objectDE.allNames[self.nSim]
            os.chdir(self.simPath)

        elif allSimulationsAnalysis == False:                   # for test case
            self.simPath = oneSimTestPath
            self.simName = "TestName"
            os.chdir(self.simPath)

        self.chosenTSList = list(chosenTimeSteps)             # copy of selected TimeSteps for analysis in case certain TS is invalid has to change
        self.nTSt = 0
        self.Creating_allTS_Vector()

        while self.nTSt < len(self.chosenTSList):            # as long as there are TimeSteps in list to analyze
            self.SettingAnalysisFiles()

            if self.SameAsPreviousStep()==True:
                break

            if self.CheckAAAFormation() == False:
                self.NoAAAFormed()
                self.DataStorage()
                self.chosenTSList.remove(self.chosenTSList[self.nTSt])
                continue

            elif self.CheckAAAFormation() == True:          #if AAA formed
                if self.chosenTSList[self.nTSt] <= self.maxTS:  #used for limiting simulation till last TS
                    self.Calculating_d0_H_L()
                    self.Calculating_D_S22_GR()
                    if self.GR < 0 or self.D < 0:
                        self.chosenTSList[self.nTSt] -= 1
                        continue
                    self.MainProgram()
                    self.DataStorage()
                else:
                    break
                self.nTSt += 1
        self.DataFrameConstruct()


    #Create lists/vectors to store data
    def Creating_allTS_Vector(self):
        self.TSName_allTS = []
        self.D_allTS = []
        self.d0_allTS = []
        self.d1_allTS = []
        self.d2_allTS = []
        self.d3_allTS = []
        self.S22_allTS = []
        self.H_allTS = []
        self.L_allTS = []
        self.S_allTS = []
        self.V_allTS = []
        self.GR_allTS = []


    # Set and load the .txt files.
    # Set the starting lines depending on the chosen TimeStep
    def SettingAnalysisFiles(self):
        # os.chdir(self.simPath)
        for suffix in suffixList:                                               # suffix name added to simulation name
            try:
                opening_eIW = open("export__INNER_WALL__" + suffix, "r")
                self.wholeDocument_eIW = opening_eIW.readlines()                                # whole txt read
                self.nl_eIW = sum(1 for line in open("export__INNER_WALL__" + suffix))          # number of lines in export Inner Wall
                self.maxTS = int(self.wholeDocument_eIW[-TSLegnht_eIW + 1].strip().split()[1])  # last TimeStep in simulation

                if self.chosenTSList[self.nTSt] <= self.maxTS:                                  # chosenTimeStep = chosen or  maxTS if chosen is bigger
                    chosenTimeStep = self.chosenTSList[self.nTSt]
                elif self.chosenTSList[self.nTSt] > self.maxTS:
                    chosenTimeStep = self.maxTS
                    self.chosenTSList[self.nTSt] = self.maxTS

                if chosenTimeStep > 0:
                    startLine_eIW = 68 + TSLegnht_eIW * (chosenTimeStep - 0)                   # staring line in each .txt file
                    startLine_rIL = 5 + TSLegnht_rIl * (chosenTimeStep - 0)
                    startLine_ctl = 4 + TSLegnht_ctl * (chosenTimeStep - 0)
                    startLine_rN1704 = 5 + TSLegnht_rN1704 * (chosenTimeStep - 0)

                elif chosenTimeStep < 0:                                                        # negative timesteps counts from the last
                    startLine_eIW = 1 + TSLegnht_eIW * chosenTimeStep
                    startLine_rIL = 0 + TSLegnht_rIl * chosenTimeStep
                    startLine_ctl = 0 + TSLegnht_ctl * chosenTimeStep
                    startLine_rN1704 = 0 + TSLegnht_rN1704 * chosenTimeStep

                if self.SameAsPreviousStep() == True:
                    break

                self.startLine_eIW = startLine_eIW % self.nl_eIW                                # to convert negative starting line to positive
                nNodes = self.wholeDocument_eIW[2].strip().split()                              # number of nodes, written in eIW file
                self.nTheta, self.nZ = int(nNodes[0]), int(nNodes[1])                           # number of elements in theta / Z direction

                opening_rIL = open("res__INNER_lines__" + suffix, "r")
                self.wholeDocument_rIl = opening_rIL.readlines()
                self.nl_rIL = sum(1 for line in open("res__INNER_lines__" + suffix))
                self.startLine_rIL = startLine_rIL  # % self.nl_rIL

                opening_ctl = open("res__CENTERLINE__" + suffix, "r")
                self.wholeDocument_ctl = opening_ctl.readlines()
                self.nl_ctl = sum(1 for line in open("res__CENTERLINE__" + suffix))
                self.startLine_ctl = startLine_ctl  # % self.nl_ctl

                opening_rN1704 = open("res__NODE_1704_" + suffix, "r")
                self.wholeDocument_rN1704 = opening_rN1704.readlines()
                self.nl_rN1704 = sum(1 for line in open("res__NODE_1704_" + suffix))
                self.startLine_rN1704 = startLine_rN1704 #% self.nl_rN1704

            except:                                                                            # skip if there is no files in dir
                FileNotFoundError
                continue

    # Check whether Timesteps start to repeat
    def SameAsPreviousStep(self):
        if self.chosenTSList[self.nTSt] == self.chosenTSList[self.nTSt-1]:
            return True

    # Check if AAA has been formed on the maximum diameter condition
    def CheckAAAFormation(self):
        if sameInitalRadius == True:                                                                 # healthy radius d0 calculated from initial mesh
            self.d0 = float(self.wholeDocument_rIl[5].strip().split()[0]) * 2
        elif sameInitalRadius == False:                                                              # healthy radius d0 calculated from current, deformed mesh
            self.d0 = (float(self.wholeDocument_rIl[self.startLine_rIL].strip().split()[0]) +
                       float(self.wholeDocument_rIl[self.startLine_rIL].strip().split()[1]) +
                       float(self.wholeDocument_rIl[self.startLine_rIL].strip().split()[2])) * 2 / 3

        # iterating over chosen TimeStep lines, checking in AAA condition is fulfilled
        nLine_rIL = self.startLine_rIL
        for line in self.wholeDocument_rIl[self.startLine_rIL: (self.startLine_rIL + TSLegnht_rIl - 1)]:
            nLine_rIL += 1
            line = line.strip().split()
            D = (float(line[0]) + float(line[1]) + float(line[2])) * 2 / 3
            if D >= self.d0 * 1.5:
                return True
        return False

    # In case AAA is not formed, anaysis is not performed and all parameters are set to None
    def NoAAAFormed(self):
        self.TSName = self.wholeDocument_eIW[self.startLine_eIW: self.startLine_eIW + TSLegnht_eIW][0].strip().split()[1]
        self.D = None
        self.d0 = None
        self.d1 = None
        self.d2 = None
        self.d3 = None
        self.S22 = None
        self.H = None
        self.L = None
        self.S = None
        self.V = None
        self.GR = None

    # Calculate d0, H, L from readINNERLines file
    def Calculating_d0_H_L(self):

        # auxiliary function for calculating average diameter from 3 positions
        def CalculatingDiameter(numberOfLine):
            D = (float(self.wholeDocument_rIl[self.startLine_rIL + numberOfLine].strip().split()[0]) +
                 float(self.wholeDocument_rIl[self.startLine_rIL + numberOfLine].strip().split()[1]) +
                 float(self.wholeDocument_rIl[self.startLine_rIL + numberOfLine].strip().split()[2])) * 2 / 3
            return D

        if sameInitalRadius == True:                                                      # healthy radius d0 calculated from initial mesh
            self.d0 = float(self.wholeDocument_rIl[5].strip().split()[0]) * 2
        elif sameInitalRadius == False:                                                   # healthy radius d0 calculated from current, deformed mesh
            self.d0 =  CalculatingDiameter(numberOfLine=0)

        self.d1 =  CalculatingDiameter(numberOfLine=20)                                   # proximal diameter at height 62mm from AAA apex
        self.d2 =  CalculatingDiameter(numberOfLine=21)                                   # proximal diameter at height 55mm from AAA apex
        self.d3 =  CalculatingDiameter(numberOfLine=22)                                   # proximal diameter at height 48mm from AAA apex
        self.HVainTotal = float(self.wholeDocument_rIl[self.startLine_rIL + TSLegnht_rIl - 2].strip().split()[5])  # total vain leght


        lineA, lineB = 0, 0                                                               # auxiliary indices to find before/after AAA formation start lines
        lineBefore = [0, 0, 0]
        self.vectorAAAIndices = []                                                        # elements indices where AAA is formed
        nLine_rIL = self.startLine_rIL                                                    # starting line in rIL

        # checking AAA formation condition at every hight/line
        for line in self.wholeDocument_rIl[self.startLine_rIL: (self.startLine_rIL + TSLegnht_rIl-1)]:
            nLine_rIL += 1                                                                # number of line in chosen TimeStep in rIL txt
            line = line.strip().split()
            D_ = (float(line[0]) + float(line[1]) + float(line[2])) * 2 / 3               # D in every line / height

            if D_ > self.d0 * 1.05:
                self.vectorAAAIndices.append((nLine_rIL-6) % TSLegnht_rIl)
                if lineB == 0:
                    lineA = lineBefore                                                    # collect elements before and after condition
                    lineB = line
            lineBefore = line

        # linear inteerpolation between before/after forming AAA elements
        try:
            #coordinates of pointA, pointB of line that connects elements before/after condition
            # pA = (rCoord, zCoord)
            pA = [(float(lineA[0]) + float(lineA[1]) + float(lineA[2])) / 3, (float(lineA[3]) + float(lineA[4]) + float(lineA[5])) / 3]
            pB = [(float(lineB[0]) + float(lineB[1]) + float(lineB[2])) / 3, (float(lineB[3]) + float(lineB[4]) + float(lineB[5])) / 3]
            slope = (pB[1] - pA[1]) / (pB[0] - pA[0])

            dR = pB[0] - 1.05 * self.d0 / 2                                       # AAA formation point radial offset from element before coordinates
            dH = (dR) * slope                                                     # AAA formation point axial offset from element before coordinates
            dL = np.sqrt(dR ** 2 + dH ** 2) * 2
            dH *= 2                                                               # becuase of upper and lower halves
        except TypeError:
            dH, dL = 0, 0

        # AAA points coordinate
        coordAAA = {"z":[], "y":[]}
        for indAn in self.vectorAAAIndices: #iterating over points that fulfill AAA condition, z,y obtained from ctl file !!
            z = float(self.wholeDocument_ctl[self.startLine_ctl + indAn].strip().split()[0])
            y = float(self.wholeDocument_ctl[self.startLine_ctl + indAn].strip().split()[1])
            coordAAA["z"].append(z), coordAAA["y"].append(y)
        try:
            self.H = (coordAAA["z"][len(coordAAA["y"]) - 1] - coordAAA["z"][0]) + 0
            self.L = 0
            for n in range(0, len(coordAAA["y"]) - 1):
                self.L += math.sqrt((coordAAA["z"][n + 1] - coordAAA["z"][n]) ** 2 + (coordAAA["y"][n + 1] - coordAAA["y"][n]) ** 2)
        except IndexError:
            self.H, self.L = 0, 0

        self.H = self.H + dH        # interpolation addition
        self.L = self.L + dL

    def Calculating_D_S22_GR(self):
        if self.chosenTSList[self.nTSt] > 0:
            nLine = self.wholeDocument_rN1704[self.startLine_rN1704 - 1].strip().split()
        elif self.chosenTSList[self.nTSt] < 0:
            nLine = self.wholeDocument_rN1704[self.startLine_rN1704].strip().split()

        self.D = float(nLine[2]) * 2
        self.GR = float(nLine[3]) * 2
        self.S22 = float(nLine[5]) * 1000  # kPa# Reading D, GR, S22 from r1704 file

    def MainProgram(self):
        self.TSData = {}  # for whole TS points data, made of coordinates in in theta direction  --> Z Lines
        n_eIW = -1  #

        #firstly, iteerating every cut that represents first radial layer
        for line in self.wholeDocument_eIW[self.startLine_eIW: self.startLine_eIW + TSLegnht_eIW]:
            line = line.strip().split()  # red teksta
            if line == []: continue  # preskakanje praznih redova, ne ulaze u brojac_eIW
            n_eIW += 1

            if n_eIW == 0:  # ==Timestep: red
                self.TSName = line[1]  # New TS
                self.ZLines = []
                continue                # to exclude empty lines
            # iteerating every arc line (Theta line)
            thetaLine, pointCoord = [],[]
            for number in line:             #iterating every line. Points are constructed as (x1,y1,z1, x2,y2,z2...)
                number = float(number)
                pointCoord.append(number)
                if len(pointCoord) == 3:        #constructing one points coordinate for every 3 coordinates
                    thetaLine.append(pointCoord)
                    pointCoord = []
            self.ZLines.append(thetaLine)  # when all theta lines are over appending last line

            if n_eIW == self.nZ:                # if counter n_eIW==nZ, Timestep is over
                self.Calculating_S_V()
                self.brojac_eIW = -1
                self.TSData[self.TSName] = self.ZLines      #filling TSData#Reading eIW (table of data)

    def Calculating_S_V(self):
        S0 = self.d0 * math.pi * self.HVainTotal * (178 / 180) * 0.9988         #inital surface. 178 deg, straight edgges
        self.S = -S0
        V0 = 1/4*(self.d0)**2*math.pi*self.HVainTotal*((178/180)**2)*(0.9941)
        self.V = -V0

        for nThL in range(len(self.ZLines)):    #iterating every cut
            STh = 0
            pointsOfElement = []

            for nPoint in range(len(self.ZLines[nThL])):  # iterating the theta line in cut
                try:
                    A = self.ZLines[nThL][nPoint]
                    B = self.ZLines[nThL + 1][nPoint]
                    C = self.ZLines[nThL][nPoint + 1]
                    D = self.ZLines[nThL + 1][nPoint + 1]

                    pointsOfElement.extend([A, B, C, D])

                except IndexError:
                    break
                try:
                    vTheta1 = np.subtract(C, A)  # vektori izmedu tocaka
                    vZ1 = np.subtract(B, A)
                    vTheta2 = np.subtract(B, C)
                    vZ2 = np.subtract(D, C)
                    vProdukt1 = np.cross(vZ1, vTheta1)  # == vektorska površina 1. trokuta
                    vProdukt2 = np.cross(vTheta2, vZ2)  # == vektorska površina 2.
                    vProduktSuma = (vProdukt1 + vProdukt2) / 2  # jer će četverokuti bit nepravilni
                    SEl = np.linalg.norm(vProduktSuma)  # povrsina elementa, kvadratica
                    STh += SEl  # povrsina theta snite
                except ValueError:
                    continue

            self.S += STh*2

            pointsOfElementArray = np.array(pointsOfElement, dtype="object")
            try:
                VTh = ConvexHull(pointsOfElementArray).volume  # ugradena funkcija za V kao array[tocke]
            except:
                VTh = False  # ako se dogodi da ne valja volumen
            self.V += VTh*2

    def DataStorage(self):
        self.TSName_allTS.append(self.TSName)
        self.D_allTS.append(self.D)
        self.d0_allTS.append(self.d0)
        self.d1_allTS.append(self.d1)
        self.d2_allTS.append(self.d2)
        self.d3_allTS.append(self.d3)
        self.S22_allTS.append(self.S22)
        self.H_allTS.append(self.H)
        self.L_allTS.append(self.L)
        self.S_allTS.append(self.S)
        self.V_allTS.append(self.V)
        self.GR_allTS.append(self.GR)

    def DataFrameConstruct(self):
        allTimeSteps = pd.Series(self.TSName_allTS)
        allDataTS = {
                        "r": [int(self.simName[2:4]) for i in range(len(self.D_allTS))],
                        "D": self.D_allTS,
                        "d0": self.d0_allTS,
                        "d1": self.d1_allTS,
                        "d2": self.d2_allTS,
                        "d3": self.d3_allTS,
                        "S22": self.S22_allTS,
                        "H": self.H_allTS,
                        "L": self.L_allTS,
                        "S": self.S_allTS,
                        "V": self.V_allTS,
                        "GR": self.GR_allTS,
                      }

        self.simDataFromAllTS = pd.DataFrame(allDataTS, index=allTimeSteps)


# comment if allSimulationsAnalysis=True
# proba = DataExtraction(oneSimTestPath)






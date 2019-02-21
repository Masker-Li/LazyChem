# -*- coding: utf-8 -*-
"""
Created on Aug. 3, 2018
@author: Masker_Li
"""

import os
import sys
import numpy as np
import pandas as pd
import time
from scipy import constants as Const
import re
from glob import glob
    
class GaussianOutputFileTypeError(SyntaxError):
    pass

class Gaussian_Output:
    def __init__(self, path=''):
        np.set_printoptions(suppress=True)
        self._isStable = None
        self._StableIndex = None

        self.is_NormalEnd = False

        self._mainOutIndexDict = {'Start': [], 'End': []}
        self.taskTypeList = []
        self._MainOutRecording = False
        self._mainOutput_str = None
        self.MainOutput = None
        self.Atoms = []
        self.AtomsCoordinates = []

        #self.MainOut = self.MainOut()
        self.__NBO = False 
        self.__link_103 = False
        self.__link_601 = False 

        self.path = path
        if os.path.isfile(path) == True:
            self.dir = os.path.split(path)[0]
            if self.dir != '':
                os.chdir(r'%s' % self.dir)
            self.fn = os.path.basename(path)
            self._readfile()
        else:
            raise GaussianOutputFileTypeError(
                'Please pass in the correct gaussian output file: \n%s' % path)

    def rename(self, extraname):
        l_e = len(extraname)
        if self.fn[-l_e-5:] != '_%s.log' % extraname:
            new_fn = self.fn[:-4] + '_%s.log' % extraname  # 新的文件名
            os.rename(self.fn, new_fn)  # 重命名
        return self

    def _isfloat(aString):
        try:
            float(aString)
            return True
        except:
            return False

    def _is_stable(self,line_index,line,words):
        '''
        line_index: the index of textlines
        '''
        if len(self.taskTypeList) == 1:
            if 'Stability' in self.taskTypeList[0]:
                self._isStable = False
                if len(words) >= 5:
                    if line == ' The wavefunction is already stable.\n':
                        #print('Stable = True')
                        self._isStable = True
                        self._StableIndex = line_index
        return self

    def _normal_end(self):
        '''
        Search the last line of the file to check if it contains "Normal termination"
        '''
        line = self.textlines[-1]
        words = line.split()
        if len(words) > 8:
            if words[0] == 'Normal' and words[1] == 'termination':
                self.is_NormalEnd = True
        return self

    def _main_out_index(self,line_index,line,words):
        '''
        line_index: the index of textlines
        '''
        if self._MainOutRecording == True:
            self._mainOutput_str = line[1:].strip(
                '\n') + str(self._mainOutput_str)
        if self._MainOutRecording == False and self._mainOutput_str != None:
            self.MainOutput = self._mainOutput_str.split('\\')

        if len(line) > 0 and '\\' in line:
            if line[:9] == r' 1\1\GINC':
                self._mainOutIndexDict['Start'].append(line_index)
                subWords = line.split('\\')
                self.taskTypeList.append(subWords[3])
                self._MainOutRecording = False
            elif line[-1] == '@':
                self._mainOutIndexDict['End'].append(line_index)
                if len(self._mainOutIndexDict['End']) == 1:
                    self._MainOutRecording = True
        if line==' @':
            self._mainOutIndexDict['End'].append(line_index)
            if len(self._mainOutIndexDict['End']) == 1:
                self._MainOutRecording = True
        return self

    # get main information of molecular
    # @classmethod
    def _MainOut(self):
        nBlank = 0
        blankIndex = []

        if self.MainOutput != None:
            self.FunctionalMethod = self.MainOutput[4]
            self.BasisSet = self.MainOutput[5]
            self.MolecularFormula = self.MainOutput[6]
            self.LastLink0 = self.MainOutput[11]
            self.Title = self.MainOutput[13]
            self.Charge, self.Spin = map(int,self.MainOutput[15].split(','))
            self.Version, self.EleState, self.S2, self.S2A = None, None, None, None
            self.E_HF_short, self.ZeroPoint, self.Thermal, self.Dipole, self.PG = None, None, None, None, None

            for i in range(len(self.MainOutput)):
                if self.MainOutput[i] == '':
                    nBlank += 1
                    blankIndex.append(i)
                if nBlank == 3 and i >= blankIndex[2]+2:
                    self.Atoms += [self.MainOutput[i].split(',')[0]]
                    self.AtomsCoordinates += [
                        self.MainOutput[i].split(',')[-3:]]
                if nBlank == 4:
                    subWords = self.MainOutput[i].split('=')
                    if subWords[0] == 'Version':
                        self.Version = subWords
                    if subWords[0] == 'State':
                        self.EleState = subWords
                    if subWords[0] == 'HF':
                        self.E_HF_short = subWords
                    if subWords[0] == 'S2':
                        self.S2 = subWords
                    if subWords[0] == 'S2A':
                        self.S2A = subWords
                    if subWords[0] == 'ZeroPoint':
                        self.ZeroPoint = subWords
                    if subWords[0] == 'Thermal':
                        self.Thermal = subWords
                    if subWords[0] == 'Dipole':
                        self.Dipole = subWords
                    if subWords[0] == 'PG':
                        self.PG = subWords
                    if 'CCSD' in self.FunctionalMethod and subWords[0] == 'CCSD':
                        self.CCSD = subWords
                    else:
                        self.CCSD = None
                    if 'CCSD(T)' in self.FunctionalMethod and subWords[0] == 'CCSD(T)':
                        self.CCSD_T = subWords
                    else:
                        self.CCSD_T = None
        return self        
        
    def _readfile(self):
        '''
        Reverse search from file
        '''
        with open(self.fn, 'r') as self._f:
            self.textlines = self._f.readlines()
        self._normal_end()
        if self.is_NormalEnd:
            n_textlines = len(self.textlines)
            t0 = time.clock()
            for n in range(n_textlines):
                line = self.textlines[-n].strip('\n')
                words = line.split()
                
                self._is_stable(line_index=-n,line=line,words=words)
                self._main_out_index(line_index=-n,line=line,words=words)
                if self.MainOutput != None and self.Atoms == []:
                    self._MainOut()
                    self._nAtoms = len(self.Atoms)
                if len(self._mainOutIndexDict['Start']) == 1:
                    if -n == self._mainOutIndexDict['Start'][-1]-1:
                        break
            print('____________________\n::: Reading %s cost %ss'%(self.fn,time.clock() - t0))
            return self
        else:
            self.rename('False')
            print('Gaussian output file does not end normally: \n%s' % self.fn)

    def __str__(self):
        if self.is_NormalEnd:
            return 'Gaussian Output object (filename: %s, Type: %s)' % (self.fn, self.taskTypeList[-1])
        else:
            return 'Abnormal Gaussian Output object (filename: %s)' % (self.fn)
   
def Rewrite(path_dir,fn0,n):    
    new_fn = 'SI_Coordinates.txt'
    GO = Gaussian_Output(fn0)
    fn = GO.fn
    if GO.is_NormalEnd == True:    
        with open( r"%s/%s"%(path_dir,new_fn), 'a' ) as nf:  # 打开文件
            nf.truncate()
            if '-TS' in fn:
                fn = fn.split('-')[1]
            nf.write(fn[:-4])
            nf.write("\n")
            for i in range(GO._nAtoms):
                xx,yy,zz = map(float,GO.AtomsCoordinates[i])
                line = ' %-5s%10s%14.8f%14.8f%14.8f\n'%(GO.Atoms[i],' ',xx,yy,zz)
                nf.write(line)    
            nf.write("\n")  
        print("%s  %-30s is OK and has converted successfully!" %(n,fn))
    else:
        logTXT = path_dir + '/%s'%('WrongPOST.txt')
        with open(logTXT,'a') as log:
            log.write('%-30s     %s  \n'%(fn,path))
        print('%s in %s is Failed'%(fn,path))

##---------------------------------------------------------------------------------------        
path = os.getcwd() 
os.chdir(path)   
n=0   
for eachfile in glob('*.log'):
    n+=1
    Rewrite(path_dir=path,fn0=eachfile,n=n)
print ('\n')
print ('There are %d files have transformed'%n)

print ('')
os.system("pause")

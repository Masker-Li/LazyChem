# -*- coding: utf-8 -*-
"""
Created on Oct. 1, 2017
@author: Masker_Li
"""

import os
import sys


def ReadIn( fname ) :
    
    ZPE = '1'
    DE = '1'
    DH = '1'
    DG = '1'
    E = '1'
    EZPE = '1'
    EDE = '1'
    H = '1'
    G = '1'
    F = '1'
    nTS = -1
    nNormals = 0
    isNormals = False
    
    ifile = open( fname, 'r' )
    lines = ifile.readlines()
    ifile.close()
    print (fname.ljust(20),end='')
    #check if this file is normal termination
    line = lines[-1]
    words = line.split()
    if len(words) > 8:
        if words[0] == 'Normal' and words[1] == 'termination':
            isNormals = True
    for line in lines :
        words = line.split()
        if len(words) > 6:         
            if words[0] == 'Sum' and words[4] == 'zero-point':
                EZPE = words[6]    
            if words[0] == '' and words[3] == '':
                EDE = words[4]       
            if words[0] == 'Sum' and words[5] == 'Enthalpies=':
                H = words[6]
            if words[0] == 'Sum' and words[5] == 'Free' and words[6] == 'Energies=':
                G = words[7]
                nTS += 1
        if len(words) > 3:
            if words[0] == 'SCF' and words[1] == 'Done:':
                E = words[4]
            if words[0] == 'Zero-point' and words[1] == 'correction=':
                ZPE = words[2]
            if words[0] == 'Thermal' and words[3] == 'Energy=':
                DE = words[4]
            if words[0] == 'Thermal' and words[3] == 'Enthalpy=':
                DH = words[4]
            if words[0] == 'Thermal' and words[3] == 'Gibbs':
                DG = words[6]                             
            if words[0] == 'Frequencies' and float(words[2]) < 0:
                F = words[2]
                nTS += 1
            if words[0] == 'Frequencies' and float(words[3]) < 0:
                nTS += 1
            if words[0] == 'Frequencies' and float(words[4]) < 0:
                nTS += 1
##    print ('%15.6f' %float(ZPE),'%15.6f' %float(DE), '%15.6f' %float(DH), '%15.6f' %float(DG),'%15.6f' %float(E),'%15.6f' %float(H), '%15.6f' %float(G), '%10.3f' %float(F),'%10.0f' %float(nTS), '%10s' %isNormals)
    print ('%15.6f' %float(DG),'%15.6f' %float(E), '%15.6f' %float(G), '%10.3f' %float(F),'%6.0f' %float(nTS), '%7s' %isNormals)

from glob import glob
##print 'filename'.ljust(28), 'ZPE'.ljust(15),'DE'.ljust(15),'DH'.ljust(15),'DG'.ljust(15),'E'.ljust(15), 'H'.ljust(15),'G'.ljust(15), 'F'.ljust(15),'nTS'.ljust(10)
print ('filename'.ljust(30), 'DG'.ljust(15),'E'.ljust(15),'G'.ljust(12), 'F'.ljust(7),'nTS'.ljust(6), 'C'.ljust(7))
for eachfile in glob('*.log') :
    ReadIn( eachfile )
print ('')
os.system("pause")


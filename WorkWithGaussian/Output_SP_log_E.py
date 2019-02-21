# -*- coding: utf-8 -*-
"""
Created on Oct. 1, 2017
@author: Masker_Li
"""

import os

def ReadIn( fname ) :
    
    E = '1.0000'
    F = '1.0000'
    NormalsOrNot = False
    
    ifile = open( fname, 'r' )
    lines = ifile.readlines()
    ifile.close()
    print (fname.ljust(40),end=''),
    for line in lines :
        words = line.split()
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
            if words[0] == 'Normal' and words[1] == 'termination':
                NormalsOrNot = True
    print ('%15.6f' %float(E), '%15.3f' %float(F), '%10s' %NormalsOrNot)
                  
               
from glob import glob
print ('filename'.ljust(48), 'E'.ljust(15), 'F'.ljust(15),'C?'.ljust(10))
for eachfile in glob('*sp.log') :
    ReadIn( eachfile )
print ('')
os.system("pause")

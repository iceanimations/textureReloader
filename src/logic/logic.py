'''
Created on Sep 11, 2013

@author: qurban.ali
'''
import pymel.core as pc

def objects(typ = None):
    return pc.ls(type = typ)
'''
Created on Apr 9, 2016

@author: qurban.ali
'''
import pymel.core as pc
import os.path as osp
import os
import re


def getNormalMaps():
    items = []
    try:
        for node in pc.ls(exactType=pc.nt.RedshiftNormalMap):
            if node.tex0.get():
                items.append(NormalMap(node))
    except AttributeError:
        pass
    return items


def getDomeLights():
    items = []
    try:
        for node in pc.ls(exactType=pc.nt.RedshiftDomeLight):
            if node.tex0.get():
                items.append(DomeLight(node))
    except AttributeError:
        pass
    return items


def getIESLights():
    items = []
    try:
        for node in pc.ls(exactType=pc.nt.RedshiftIESLight):
            if node.profile.get():
                items.append(IESLight(node))
    except AttributeError:
        pass
    return items


def getFileNodes():
    items = []
    for node in pc.ls(exactType=pc.nt.File):
        if node.ftn.get():
            items.append(FileNode(node))
    return items


def getRSSprites():
    items = []
    try:
        for node in pc.ls(exactType=pc.nt.RedshiftSprite):
            if node.tex0.get():
                items.append(RedshiftSprite(node))
    except AttributeError:
        pass
    return items


class Texture(object):
    def __init__(self, node=None):
        super(Texture, self).__init__()
        self.node = node

    def setPath(self, path):
        pass

    def getPath(self):
        pass

    def remap(self, path):
        path = osp.join(path, self.getFileName())
        if self.fileExists(path):
            self.setPath(path)
        else:
            return path

    def getFileName(self):
        return osp.basename(self.getPath())

    def getDirName(self):
        return osp.dirname(self.getPath())

    def fileExists(self, filepath=None):
        if not filepath:
            filepath = self.getPath()
        basename = osp.basename(filepath)
        path = osp.dirname(filepath)
        if not osp.exists(path):
            return False
        if self.isUDIM(filepath):
            pattern = '^' + basename.replace('<udim>', r'\d+').replace(
                '<UDIM>', r'\d+') + '$'
            for phile in os.listdir(path):
                if re.match(pattern, phile):
                    return True
        else:
            return osp.exists(filepath)
        return False

    def isUDIM(self, path):
        return True if '<udim>' in path.lower() else False


class RedshiftSprite(Texture):
    def __init__(self, node=None):
        super(RedshiftSprite, self).__init__(node)

    def setPath(self, path):
        self.node.tex0.set(path.replace('\\', '/'))

    def getPath(self):
        return osp.normpath(self.node.tex0.get())


class FileNode(Texture):
    def __init__(self, node=None):
        super(FileNode, self).__init__(node)

    def setPath(self, path):
        colorSpace = self.node.colorSpace.get()
        self.node.ftn.set(path.replace('\\', '/'))
        self.node.colorSpace.set(colorSpace)

    def getPath(self):
        return osp.normpath(self.node.ftn.get())


class NormalMap(Texture):
    def __init__(self, node=None):
        super(NormalMap, self).__init__(node)

    def setPath(self, path):
        self.node.tex0.set(path.replace('\\', '/'))

    def getPath(self):
        return osp.normpath(self.node.tex0.get())


class IESLight(Texture):
    def __init__(self, node=None):
        super(IESLight, self).__init__(node)

    def setPath(self, path):
        self.node.profile.set(path.replace('\\', '/'))

    def getPath(self):
        return osp.normpath(self.node.profile.get())


class DomeLight(Texture):
    def __init__(self, node=None):
        super(DomeLight, self).__init__(node)

    def setPath(self, path):
        self.node.tex0.set(path.replace('\\', '/'))

    def getPath(self):
        return osp.normpath(self.node.tex0.get())
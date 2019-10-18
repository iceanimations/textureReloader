'''
Created on Apr 9, 2016

@author: qurban.ali
'''
import os.path as osp

from uiContainer import uic
import cui
from PyQt4.QtGui import QLabel, QMessageBox, QColor
from PyQt4.QtCore import Qt
import qtify_maya_window as qtfy
import subprocess
import backend
import appUsageApp


reload(backend)


rootPath = osp.dirname(osp.dirname(__file__))
uiPath = osp.join(rootPath, 'ui')
Form, Base = uic.loadUiType(osp.join(uiPath, 'main.ui'))
Form1, Base1 = uic.loadUiType(osp.join(uiPath, 'texture.ui'))


class Main(Form, Base):
    def __init__(self, parent=qtfy.getMayaWindow()):
        super(Main, self).__init__(parent)
        self.setupUi(self)
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.items = []

        self.refreshButton.clicked.connect(self.populate)
        self.remapButton.clicked.connect(self.remap)

        appUsageApp.updateDatabase('textureReloader')

        self.populate()

    def showMessage(self, **kwargs):
        cui.showMessage(self, title='Remap Textures', **kwargs)

    def closeEvent(self, event):
        self.deleteLater()

    def getMappings(self, nodes):
        mappings = {}
        for node in nodes:
            path = node.getDirName()
            if mappings.has_key(path):
                mappings[path].append(node)
            else:
                mappings[path] = [node]
        return mappings

    def addTextures(self, title, mappings):
        if mappings:
            label = QLabel(title, self)
            self.items.append(label)
            self.textureLayout.addWidget(label)
            for path in mappings.keys():
                tex = Texture(self, path, mappings[path])
                self.textureLayout.addWidget(tex)
                self.items.append(tex)

    def populate(self):
        for item in self.items:
            item.deleteLater()
        del self.items[:]

        fileNodeMappings = self.getMappings(backend.getFileNodes())
        normalMapMappings = self.getMappings(backend.getNormalMaps())
        iesLightMappings = self.getMappings(backend.getIESLights())
        domeLightMappings = self.getMappings(backend.getDomeLights())
        spriteMappings = self.getMappings(backend.getRSSprites())

        self.addTextures('File Node', fileNodeMappings)
        self.addTextures('Redshift Normal Map', normalMapMappings)
        self.addTextures('Redshift IES Light', iesLightMappings)
        self.addTextures('Redshift Dome Light', domeLightMappings)
        self.addTextures('Reshift Sprite', spriteMappings)

    def remap(self):
        for item in self.items:
            try:
                item.remap()
            except AttributeError:
                pass
        self.populate()


class Texture(Form1, Base1):
    def __init__(self, parent=None, path=None, items=None):
        super(Texture, self).__init__(parent)
        self.setupUi(self)
        self.parentWin = parent
        self.items = items
        self.path = path

        self.fileBox.view().setAttribute(Qt.WA_Disabled, True)
        self.fileBox.view().setAttribute(Qt.WA_MouseTracking, False)
        self.fileBox.addItem('Textures (%s)' % len(items))

        self.populateFileBox()

        self.pathBox.setText(self.path)

        self.pathBox.returnPressed.connect(self.callRemap)
        self.browseButton.clicked.connect(self.openLocation)

    def openLocation(self):
        subprocess.Popen('explorer %s' % osp.normpath(self.path))

    def populateFileBox(self):
        for i, item in enumerate(self.items):
            self.fileBox.addItem(item.getFileName())
            if not item.fileExists():
                self.fileBox.setItemData(i + 1, QColor(Qt.green),
                                         Qt.BackgroundRole)
        self.fileBox.view().setFixedWidth(self.fileBox.sizeHint().width())

    def callRemap(self):
        self.remap()
        self.parentWin.populate()

    def remap(self):
        errors = []
        for item in self.items:
            err = item.remap(self.pathBox.text())
            if err: errors.append(err)
        if errors:
            self.parentWin.showMessage(msg='Following file not found\n\n' +
                                       '\n'.join(errors),
                                       icon=QMessageBox.Warning)
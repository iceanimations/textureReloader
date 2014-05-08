'''
Created on Sep 11, 2013

@author: qurban.ali
'''
import os.path as osp
import os
import sys
import site
import webbrowser
# add PyQt/PySide to sys.modules
site.addsitedir(r"R:\Pipe_Repo\Users\Qurban\utilities")
from uiContainer import uic
from PyQt4.QtGui import *
from PyQt4.QtCore import QRegExp, Qt
import qtify_maya_window as util
modulePath = __file__
root = osp.dirname(osp.dirname(modulePath))
import pymel.core as pc
 
Form, Base = uic.loadUiType('%s\ui\ui.ui'%root)
class Window(Form, Base):
    def __init__(self, parent = util.getMayaWindow()):
        super(Window, self).__init__(parent)
        self.setupUi(self)
        self.reloadButton.clicked.connect(self.reloadTextures)
        self.closeButton.clicked.connect(self.close)
        self.refreshButton.clicked.connect(self.refresh)
        self.clearButton.clicked.connect(self.clear)
        self.helpButton.clicked.connect(self.showHelp)
        self.reloadMappings = {}
        self.boxComboMappings = {}
        self.listBoxes()

        if pc.optionVar(exists='releaseNotes'):
            self.heyLabel.hide()
        
        # update the database, how many times this app is used
        site.addsitedir(r'r:/pipe_repo/users/qurban')
        import appUsageApp
        appUsageApp.updateDatabase('textureReloader')
        
    def showHelp(self):
        webbrowser.open_new_tab(r'R:\Pipe_Repo\Users\Qurban\docs\textureReloader\help.html')
        pc.optionVar(iv=('releaseNotes', 1))
        self.heyLabel.hide()
        
    def closeEvent(self, event):
        self.deleteLater()
        
    def hideEvent(self, event):
        self.close()
        
    def listBoxes(self):
        self.clear()
        fileNodes = pc.ls(type=['file', 'aiImage'])
        textureMappings = {}
        if not fileNodes:
            self.msgBox(msg = 'No texture found in the Scene',
                        icon = QMessageBox.Information)
            return
        self.availableLabel.setText('Available Textures: '+ str(len(fileNodes)))
        emptyTextures = [x for x in fileNodes if not self.getFile(x)]
        reloadableTextures = [x for x in fileNodes if x not in emptyTextures]
        self.emptyLabel.setText('Empty Textures: '+ str(len(emptyTextures)))
        for node in reloadableTextures:
            key = osp.dirname(self.getFile(node))
            key = osp.normpath(key)
            if textureMappings.has_key(key):
                textureMappings[key].append(node)
            else: textureMappings[key] = [node]
        for path in textureMappings:
            textureFrame = QFrame(self)
            lay = QHBoxLayout(textureFrame)
            textureFrame.setLayout(lay)
            pathBox = QLineEdit(textureFrame)
            self.reloadMappings[pathBox] = textureMappings[path]
            comboBox = QComboBox(textureFrame)
            comboBox.setFixedWidth(100)
            lay.addWidget(pathBox)
            lay.addWidget(comboBox)
            self.texturesBoxLayout.addWidget(textureFrame)
            pathBox.setText(path)
            num = len(textureMappings[path])
            comboBox.addItem(str(num) + (' Textures' if num > 1 else ' Texture'))
            comboBox.addItems([osp.basename(self.getFile(x)) for x in textureMappings[path]])
            comboBox.view().setFixedWidth(comboBox.sizeHint().width())
            comboBox.view().setAttribute(Qt.WA_Disabled, True)
            comboBox.view().setAttribute(Qt.WA_MouseTracking, False)
            self.boxComboMappings[pathBox] = comboBox
        self.messageLabel.hide()
        map(lambda box: self.bindReturnPressedEvent(box), self.reloadMappings.keys())
        
    def refresh(self):
        self.listBoxes()
        
    def getFile(self, node):
        if type(node) == pc.nt.AiImage:
            return node.filename.get()
        return node.fileTextureName.get()
    
    def setFile(self, node, name):
        if type(node) == pc.nt.AiImage:
            node.filename.set(name)
            return
        node.fileTextureName.set(name)
        
    def bindReturnPressedEvent(self, box):
        box.returnPressed.connect(lambda: self.reloadSingleBox(box))
    
    def clear(self):
        self.availableLabel.setText('Available Textures: 0')
        self.emptyLabel.setText('Empty Textures: 0')
        for box in self.reloadMappings:
            box.parent().deleteLater()
        self.reloadMappings.clear()
        self.boxComboMappings.clear()
        self.messageLabel.hide()
        
    def reloadTextures(self):
        if self.reloadMappings:
            badTextures = []
            self.messageLabel.show()
            self.messageLabel.setText('Reloading textures...')
            self.messageLabel.repaint()
            for box in self.reloadMappings:
                badTextures.extend(self.reloadSingleBox(box, msg=False))
            if badTextures:
                detail = 'Following paths do not exist:\n'
                for i in range(len(badTextures)):
                    detail += str(i+1) + "- " + badTextures[i] + "\n"
                self.msgBox(msg = "The system can find the path specified",
                            details = detail, icon = QMessageBox.Information)
            self.refresh()
            self.messageLabel.setText('Done reloading textures...')
            self.messageLabel.show()
            self.messageLabel.repaint()
            
    def reloadSingleBox(self, box, msg=True):
        badTextures = []
        path = str(box.text())
        if not path:
            for nod in self.reloadMappings[box]:
                self.setFile(nod, '')
            return
        if osp.exists(path):
            for node in self.reloadMappings[box]:
                baseName = osp.basename(self.getFile(node))
                fullPath = osp.join(path, baseName)
                flag = True
                if not osp.exists(fullPath):
                    flag = False
                    if '<udim>' in baseName:
                        flag = self.checkUDIM(path, baseName)
                if flag:
                    self.setFile(node, fullPath)
                else:
                    badTextures.append(fullPath)
        else: badTextures.append(path)
        if msg:
            if badTextures:
                paths = '\n'.join(badTextures)
                self.msgBox(msg='The system can not find the path specified\n'+ paths, icon=QMessageBox.Warning)
            self.refresh()
            self.messageLabel.show()
        else:
            return badTextures
        
    def checkUDIM(self, path, basename):
        pattern = '^'+ basename.replace('<udim>', '\d+') +'$'
        regex = QRegExp(pattern)
        flag = False
        for phile in os.listdir(path):
            if osp.isfile(osp.join(path, phile)):
                if regex.indexIn(phile) == 0:
                    flag = True
                    break
        return flag
        
    def msgBox(self, msg = None, btns = QMessageBox.Ok,
           icon = None, ques = None, details = None):
        '''
        dispalys the warnings
        @params:
                args: a dictionary containing the following sequence of variables
                {'msg': 'msg to be displayed'[, 'ques': 'question to be asked'],
                'btns': QMessageBox.btn1 | QMessageBox.btn2 | ....}
        '''
        if msg:
            mBox = QMessageBox(self)
            mBox.setWindowTitle('TextureReloader')
            mBox.setText(msg)
            if ques:
                mBox.setInformativeText(ques)
            if icon:
                mBox.setIcon(icon)
            if details:
                mBox.setDetailedText(details)
            mBox.setStandardButtons(btns)
            buttonPressed = mBox.exec_()
            return buttonPressed      
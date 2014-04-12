'''
Created on Sep 11, 2013

@author: qurban.ali
'''
import os.path as osp
import sys
import site

# add PyQt/PySide to sys.modules
site.addsitedir(r"R:\Pipe_Repo\Users\Qurban\utilities")
from uiContainer import uic

from PyQt4.QtGui import *
site.addsitedir(r"R:\Pipe_Repo\Users\Hussain\packages")
import qtify_maya_window as util
reload(util)
modulePath = sys.modules[__name__].__file__
root = osp.dirname(osp.dirname(osp.dirname(modulePath)))
from ..logic import logic
 
Form, Base = uic.loadUiType('%s\ui\ui.ui'%root)
class Window(Form, Base):
    def __init__(self, parent = util.getMayaWindow()):
        super(Window, self).__init__(parent)
        self.setupUi(self)
        self.reloadButton.clicked.connect(self.reloadTextures)
        self.closeButton.clicked.connect(self.close)
        self.recheckButton.clicked.connect(self.recheck)
        self.clearButton.clicked.connect(self.clear)
        self.reloadMappings = {}
        self.textureMappings = {}
        self.badTextures = []
        self.recheck()
        
        # update the database, how many times this app is used
        site.addsitedir(r'r:/pipe_repo/users/qurban')
        import appUsageApp
        appUsageApp.updateDatabase('textureReloader')
        
    def recheck(self):
        self.clear()
        fileNodes = logic.objects('file')
        if not fileNodes:
            self.msgBox(msg = 'No texture found in the Scene',
                        icon = QMessageBox.Information)
            return
        self.availableLabel.setText('Available Textures: '+ str(len(fileNodes)))
        emptyTextures = [x for x in fileNodes if not x.fileTextureName.get()]
        reloadableTextures = [x for x in fileNodes if x not in emptyTextures]
        self.emptyLabel.setText('Empty Textures: '+ str(len(emptyTextures)))
        for node in reloadableTextures:
            key = osp.dirname(node.fileTextureName.get())
            key = osp.normpath(key)
            if self.textureMappings.has_key(key):
                self.textureMappings[key].append(node)
            else: self.textureMappings[key] = [node]
        for path in self.textureMappings:
            textureFrame = QFrame(self)
            lay = QHBoxLayout(textureFrame)
            textureFrame.setLayout(lay)
            pathBox = QLineEdit(self)
            self.reloadMappings[pathBox] = self.textureMappings[path]
            label = QLabel(textureFrame)
            lay.addWidget(pathBox)
            lay.addWidget(label)
            self.texturesBoxLayout.addWidget(textureFrame)
            pathBox.setText(path)
            label.setText(str(len(self.textureMappings[path])) +' Textures')
        self.messageLabel.hide()
            
    def pathChanged(self, path):
        print path
#        if not osp.exists(osp.normpath(path)):
#            pathBox.setStyleSheet("border: 2px solid red;")
#        else: pathBox.setStyleSheet("border: 0px;")
        
    
    def clear(self):
        self.availableLabel.setText('Available Textures: 0')
        self.emptyLabel.setText('Empty Textures: 0')
        for box in self.reloadMappings:
            box.parent().deleteLater()
        self.reloadMappings.clear()
        self.textureMappings.clear()
        self.badTextures[:] = []
        self.messageLabel.hide()
        
    def reloadTextures(self):
        if self.reloadMappings:
            self.messageLabel.show()
            self.messageLabel.setText('Reloading textures...')
            self.messageLabel.repaint()
            for box in self.reloadMappings:
                path = str(box.text())
                if not path:
                    for nod in self.reloadMappings[box]:
                        nod.fileTextureName.set('')
                    continue
                #if osp.exists(path):
                for node in self.reloadMappings[box]:
                    baseName = osp.basename(node.fileTextureName.get())
                    tempName = osp.splitext(baseName)[0] +'.png'
                    if not osp.exists(osp.join(path, tempName)):
                        tempName = osp.splitext(tempName)[0] +'.tga'
                        if not osp.exists(osp.join(path, tempName)):
                            tempName = osp.splitext(tempName)[0] +'.tx'
                            if not osp.exists(osp.join(path, tempName)):
                                pass
                            else: baseName = tempName
                        else: baseName = tempName
                    else: baseName = tempName
                    fullPath = osp.join(path, baseName)
                    #if osp.exists(fullPath):
                    node.fileTextureName.set(fullPath)
                    #else: self.badTextures.append(fullPath)
                #else: self.badTextures.append(path)
            if self.badTextures:
                detail = 'Following files not found in the specified directories:\n'
                for i in range(len(self.badTextures)):
                    detail += str(i+1) + "- " + self.badTextures[i] + "\n"
                self.msgBox(msg = "Files not found in the specified directory",
                            details = detail, icon = QMessageBox.Information)
            self.recheck()
            self.messageLabel.setText('Done reloading textures...')
            self.messageLabel.show()
            self.messageLabel.repaint()
            
    def folderDialog(self):
        folder = QFileDialog.getExistingDirectory(self, 'Texture Directory',
                                                  '', QFileDialog.ShowDirsOnly)
        
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
        
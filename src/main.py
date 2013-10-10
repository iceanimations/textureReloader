'''
Created on Sep 11, 2013

@author: qurban.ali
'''
#use this module when running this application from outside of Maya
import interface.window as window
import sys
import site
site.addsitedir(r"R:\Python_Scripts")
from PyQt4.QtGui import QApplication, QStyleFactory

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create('plastique'))
    win = window.Window()
    win.show()
    sys.exit(app.exec_())
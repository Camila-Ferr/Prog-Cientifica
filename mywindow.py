from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from mycanvas import *
from mymodel import *

class MyWindow(QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        self.setGeometry(100,100,600,400)
        self.setWindowTitle("MyGLDrawer")
        self.canvas = MyCanvas()
        self.setCentralWidget(self.canvas)
        # create a model object and pass to canvas
        self.model = MyModel()
        self.canvas.setModel(self.model)
        # create a Toolbar
        tb = self.addToolBar("File")
        fit = QAction(QIcon("icons/fit.png"),"fit",self)
        export = QAction(QIcon("icons/export.png"), "export", self)
        create = QAction(QIcon("icons/create.png"), "create", self)

        tb.addAction(fit)
        tb.addAction(export)
        tb.addAction(create)
        tb.actionTriggered[QAction].connect(self.tbpressed)

    def tbpressed(self,a):
        if a.text() == "fit":
            self.canvas.fitWorldToViewport()
        if a.text() == "export":
            self.canvas.exportJson()
        if a.text() == "create":
            self.canvas.showDialog()




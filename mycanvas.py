import json
import sys

from PyQt5 import QtOpenGL, QtCore
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from OpenGL.GL import *
import mymodel
from he.hecontroller import HeController
from he.hemodel import HeModel
from geometry.segments.line import Line
from geometry.point import Point
from compgeom.tesselation import Tesselation


class BoxDialog(QDialog):
    def __init__(self, title="BoxDialog", labels=[""],dialogs = 1):
        super().__init__()
        self.setWindowTitle(title)
        self.setWindowModality(Qt.ApplicationModal)

        self.lineEdits = [None] * dialogs
        self.layout = QVBoxLayout()

        #vários inputs em um dialog
        for i in range(dialogs):
            self.lineEdits[i] = QLineEdit()
            self.layout.addWidget(QLabel("{}:".format(labels[i])))
            self.layout.addWidget(self.lineEdits[i])

        self.pushButton = QPushButton()
        self.pushButton.setIcon(QIcon('icons/confirm.png'))
        self.pushButton.setGeometry(200, 200, 100, 30)
        self.pushButton.clicked.connect(self.accept)
        self.layout.addWidget(self.pushButton)

        self.setLayout(self.layout)

class MyCanvas(QtOpenGL.QGLWidget):

    def __init__(self):
        super(MyCanvas, self).__init__()

        self.m_model = None
        self.m_w = 0  # width: GL canvas horizontal size
        self.m_h = 0  # height: GL canvas vertical size
        self.m_L = -1000.0
        self.m_R = 1000.0
        self.m_B = -1000.0
        self.m_T = 1000.0
        self.list = None
        self.mesh = []
        self.m_buttonPressed = False
        self.m_pt0 = QtCore.QPoint(0, 0)
        self.m_pt1 = QtCore.QPoint(0, 0)
        self.m_hmodel = HeModel()
        self.m_controller = HeController(self.m_hmodel)
        self.last_mesh_spacing = 1.0
        self.temperatura = 100.0
        self.var = 1.2
        self.punch = -1000.0
        self.punch_particles = 10
        self.mass = 7850.0
        self.density = 210000000000.0


    def initializeGL(self):
        # glClearColor(1.0, 1.0, 1.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)
        glEnable(GL_LINE_SMOOTH)
        self.list = glGenLists(1)

    def resizeGL(self, _width, _height):
        self.m_w = _width
        self.m_h = _height
        if (self.m_model == None) or (self.m_model.isEmpty()):
            self.scaleWorldWindow(1.0)
        else:
            self.m_L, self.m_R, self.m_B, self.m_T = self.m_model.getBoundBox()
            self.scaleWorldWindow(1.1)
        glViewport(0, 0, self.m_w, self.m_h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(self.m_L, self.m_R, self.m_B, self.m_T, -1.0, 1.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()


    def paintGL(self):

        # clear the buffer with the current clear color
        glClear(GL_COLOR_BUFFER_BIT)
        # draw a triangle with RGB color at the 3 vertices
        # interpolating smoothly the color in the interior
        glCallList(self.list)
        glDeleteLists(self.list, 1)
        self.list = glGenLists(1)
        glNewList(self.list, GL_COMPILE)
        # Display model polygon RGB color at its vertices
        # interpolating smoothly the color in the interior
        # glShadeModel(GL_SMOOTH)
        pt0_U = self.convertPtCoordsToUniverse(self.m_pt0)
        pt1_U = self.convertPtCoordsToUniverse(self.m_pt1)
        glColor3f(1.0, 0.0, 0.0)
        glBegin(GL_LINE_STRIP)
        glVertex2f(pt0_U.x(), pt0_U.y())
        glVertex2f(pt1_U.x(), pt1_U.y())
        glEnd()
        if not ((self.m_model == None) and (self.m_model.isEmpty())):
            verts = self.m_model.getVerts()
            glColor3f(0.0, 1.0, 0.0)  # green
            glBegin(GL_TRIANGLES)
            for vtx in verts:
                glVertex2f(vtx.getX(), vtx.getY())
            glEnd()
            curves = self.m_model.getCurves()
            glColor3f(0.0, 0.0, 1.0)  # blue
            glBegin(GL_LINES)
            for curv in curves:

                glVertex2f(curv.getP1().getX(), curv.getP1().getY())
                glVertex2f(curv.getP2().getX(), curv.getP2().getY())
            glEnd()
        glEndList()
        if not(self.m_hmodel.isEmpty()):
            patches = self.m_hmodel.getPatches()
            for pat in patches:
                pts = pat.getPoints()
                triangs = Tesselation.tessellate(pts)
                for j in range(0, len(triangs)):
                    glColor3f(1.0, 0.0, 1.0)
                    glBegin(GL_TRIANGLES)
                    glVertex2d(pts[triangs[j][0]].getX(), pts[triangs[j][0]].getY())
                    glVertex2d(pts[triangs[j][1]].getX(), pts[triangs[j][1]].getY())
                    glVertex2d(pts[triangs[j][2]].getX(), pts[triangs[j][2]].getY())
                    glEnd()
            segments = self.m_hmodel.getSegments()
            for curv in segments:
                ptc = curv.getPointsToDraw()
                glColor3f(0.0, 1.0, 1.0)
                glBegin(GL_LINES)
                for curv in curves:
                    glVertex2f(ptc[0].getX(), ptc[0].getY())
                    glVertex2f(ptc[1].getX(), ptc[1].getY())
                glEnd()

            for point in self.mesh:
                glColor3f(3.0, 3.0, 3.0)
                glBegin(GL_POINTS)
                glVertex2f(point.getX(), point.getY())
                glEnd()

    def showDialog(self):
        if self.m_hmodel.isEmpty():
            return

        default = 1.0
        dialog = BoxDialog(title="Grade", labels=["Defina o valor da grade "])
        dialog.exec()
        if dialog.result() == 1:
            try:
                default = float(dialog.lineEdits[0].text())
            except:
                default = 1.0
        self.last_mesh_spacing = default

        if not (self.m_hmodel.isEmpty()):
            patches = self.m_hmodel.getPatches()
            for pat in patches:
                pts = pat.getPoints()
                xMin = pts[0].getX()
                xMax = xMin
                yMin = pts[0].getY()
                yMax = yMin
                for i in range(1, len(pts)):
                    if pts[i].getX() < xMin:
                        xMin = pts[i].getX()
                    if pts[i].getX() > xMax:
                        xMax = pts[i].getX()
                    if pts[i].getY() < yMin:
                        yMin = pts[i].getY()
                    if pts[i].getY() > yMax:
                        yMax = pts[i].getY()
                x = []
                y = []
                xMin += default
                yMin += default

                while xMin < xMax:
                    x.append(xMin)
                    xMin += default
                while yMin < yMax:
                    y.append(yMin)
                    yMin += default
                for i in range(len(x)):
                    for j in range(len(y)):
                        if pat.isPointInside(Point(x[i], y[j])):
                            self.mesh.append(Point(x[i], y[j]))

        self.update()
        self.repaint()

    def exportJson(self):
        upY = -sys.maxsize
        lowerY = sys.maxsize

        upX = -sys.maxsize
        lowerX = sys.maxsize

        archiveJson = []
        for point in self.mesh:

            if (point.getY() < lowerY):
                lowerY = point.getY()

            if (point.getY() > upY):
                upY = point.getY()

            if (point.getX() < lowerX):
                lowerX = point.getX()

            if (point.getX() > upX):
                upX = point.getX()

            archiveJson.append({"x": int(point.getX()), "y": int(point.getY())})


        yAdjust = int(lowerY) * (-1)
        xAdjust = int(lowerX) * (-1)

        outputDem = {"coordenadas": []}

        for point in archiveJson:

            point["x"] = int(int(point["x"] + xAdjust) / self.last_mesh_spacing)
            point["y"] = int(int(point["y"] + yAdjust) / self.last_mesh_spacing)
            outputDem["coordenadas"].append([point["x"], point["y"]])

        lenX, lenY = 1,1

        for point in archiveJson:

            if point["x"] > lenX:
                lenX = point["x"]

            if point["y"] > lenY:
                lenY = point["y"]

        outputMdf = [[-2.0 for x in range(int(lenX + 1))] for y in range(int(lenY + 1))]

        for point in archiveJson:
            outputMdf[point["y"]][point["x"]] = -1.0

        self.temperatura -= self.var

        tam_i = len(outputMdf)
        for i in range(tam_i):

            self.temperatura += self.var
            self.temperatura = round(self.temperatura, 2)

            tam_j = len(outputMdf)
            for j in range(tam_j):

                if outputMdf[i][j] == -1.0:

                    if i == 0 or j == 0 or (i + 1) == tam_i or (j + 1) == tam_j:
                        outputMdf[i][j] = self.temperatura
                    else:
                         if i > 0 and outputMdf[i - 1][j] == -2.0:
                             outputMdf[i][j] = self.temperatura
                         if i + 1 < tam_i and outputMdf[i + 1][j] == -2.0:
                             outputMdf[i][j] = self.temperatura
                         if j > 0 and outputMdf[i][j - 1] == -2.0:
                             outputMdf[i][j] = self.temperatura
                         if j + 1 < tam_j and outputMdf[i][j + 1] == -2.0:
                             outputMdf[i][j] = self.temperatura

        connective = []

        for i in range (0,len(outputDem["coordenadas"])):
            connective.append([0,0,0,0,0])



        tam_i = len(outputMdf)
        for i in range(tam_i):
             tam_j = len(outputMdf[i])
             for j in range(tam_j):
                 if outputMdf[i][j] != -2.0:
                     actualPoint = self.getPointIndex(outputDem["coordenadas"], j, i)
                     amountConnections = 0

                     if i > 0 and outputMdf[i - 1][j] != -2.0:
                         conectedPoint = self.getPointIndex(outputDem["coordenadas"], j, i - 1)
                         amountConnections += 1
                         connective[actualPoint - 1][amountConnections] = conectedPoint

                     if i + 1 < tam_i and outputMdf[i + 1][j] != -2.0:
                         conectedPoint = self.getPointIndex(outputDem["coordenadas"], j, i + 1)
                         amountConnections += 1
                         connective[actualPoint - 1][amountConnections] = conectedPoint

                     if j > 0 and outputMdf[i][j - 1] != -2.0:
                         conectedPoint = self.getPointIndex(outputDem["coordenadas"], j - 1, i)
                         amountConnections += 1
                         connective[actualPoint - 1][amountConnections] = conectedPoint

                     if j + 1 < tam_j and outputMdf[i][j + 1] != -2.0:
                         conectedPoint = self.getPointIndex(outputDem["coordenadas"], j + 1, i)
                         amountConnections += 1
                         connective[actualPoint - 1][amountConnections] = conectedPoint
                         connective[actualPoint - 1][0] = amountConnections

        force = []
        resistence = []

        for i in range (0, len(outputDem["coordenadas"])):
            force.append([0.0, 0.0])
            resistence.append([0,0])

        amountForce = self.punch_particles

        tam_i = len(outputMdf)
        for i in range(tam_i - 1, 0, -1):
             tam_j = len(outputMdf[i])
             for j in range(tam_j - 1, 0, -1):

                 if outputMdf[i][j] != -2.0:
                     if amountForce > 0:
                         force[self.getPointIndex(outputDem["coordenadas"], j, i) - 1][0] = self.punch
                         amountForce -= 1
                     else:
                         break
             if amountForce <= 0:
                 break

        amountResistence = self.punch_particles
        tam_i = len(outputMdf)
        for i in range(tam_i):
             tam_j = len(outputMdf[i])

             for j in range(tam_j):

                 if outputMdf[i][j] != -2.0:
                     if amountResistence > 0:
                         resistence[self.getPointIndex(outputDem["coordenadas"], j, i) - 1][0] = 1
                         resistence[self.getPointIndex(outputDem["coordenadas"], j, i) - 1][1] = 1
                         amountResistence -= 1
                     else:
                         break

             if amountResistence <= 0:
                 break

        outputDem["connective"] = connective
        outputDem["force"] = force
        outputDem["resistence"] = resistence
        outputDem["mass"] = self.mass
        outputDem["density"] = self.density

        with open("dem_input.json", "w") as file:
            json.dump(outputDem, file)

        with open("mdf_input.json", "w") as file:
            json.dump(outputMdf, file)

    def setTemp(self):
        dialog = BoxDialog(title="Calor", labels=["Defina o calor ao redor do Objeto  ", "Defina a variação de calor  "], dialogs=2)
        dialog.exec()
        if dialog.result() == 1:
            try:
                self.temperatura = float(dialog.lineEdits[0].text())
                self.var = float(dialog.lineEdits[1].text())
            except:
                self.temperatura = 100.0
                self.var = 1.2

    def setForce(self):

        dialog = BoxDialog(
            title="Força",
            labels=[
                "Defina a força aplicada ",
                "Defina a quantidade de particulas afetadas de inicio ",
                "Defina a massa do objeto ",
                "Defina a densidade do objeto "
            ],
            dialogs=4
        )
        dialog.exec()
        if dialog.result() == 1:
            try:
                self.punch = float(dialog.lineEdits[0].text())
                self.punch_particles = int(dialog.lineEdits[2].text())
                self.mass = float(dialog.lineEdits[3].text())
                self.density = float(dialog.lineEdits[4].text())
            except:
                self.punch = -1000.0
                self.punch_particles = 10
                self.mass = 7850.0
                self.density = 210000000000.0

    def setModel(self,_model):
        self.m_model = _model

    def fitWorldToViewport(self):
        
        if (self.m_model==None)or(self.m_model.isEmpty()): return
        self.m_L,self.m_R,self.m_B,self.m_T=self.m_model.getBoundBox()
        self.scaleWorldWindow(1.10)
        self.update()

    def getPointIndex(self, coordenadas, x, y):
        for i, coordenadas in enumerate(coordenadas):
            if coordenadas[0] == x and coordenadas[1] == y:
                return i + 1
        return 0

    def scaleWorldWindow(self, _scaleFac):

        # Compute canvas viewport distortion ratio.
        vpr = self.m_h / self.m_w

        # Get current window center.
        cx = (self.m_L + self.m_R) / 2.0
        cy = (self.m_B + self.m_T) / 2.0

        # Set new window sizes based on scaling factor.
        sizex = (self.m_R - self.m_L) * _scaleFac
        sizey = (self.m_T - self.m_B) * _scaleFac

        # Adjust window to keep the same aspect ratio of the viewport.
        if sizey > (vpr * sizex):
            sizex = sizey / vpr
        else:
            sizey = sizex * vpr
        self.m_L = cx - (sizex * 0.5)
        self.m_R = cx + (sizex * 0.5)
        self.m_B = cy - (sizey * 0.5)
        self.m_T = cy + (sizey * 0.5)

        # Establish the clipping volume by setting up an
        # orthographic projection
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(self.m_L, self.m_R, self.m_B, self.m_T, -1.0, 1.0)

    def panWorldWindow(self, _panFacX, _panFacY):

        # Compute pan distances in horizontal and vertical directions.
        panX = (self.m_R - self.m_L) * _panFacX
        panY = (self.m_T - self.m_B) * _panFacY
        # Shift current window.
        self.m_L += panX
        self.m_R += panX
        self.m_B += panY
        self.m_T += panY
        # Establish the clipping volume by setting up an
        # orthographic projection
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(self.m_L, self.m_R, self.m_B, self.m_T, -1.0, 1.0)


    def convertPtCoordsToUniverse(self, _pt):
        dX = self.m_R - self.m_L
        dY = self.m_T - self.m_B
        mX = _pt.x() * dX / self.m_w
        mY = (self.m_h - _pt.y()) * dY / self.m_h
        x = self.m_L + mX
        y = self.m_B + mY
        return QtCore.QPointF(x, y)


    def mousePressEvent(self, event):
        self.m_buttonPressed = True
        self.m_pt0 = event.pos()


    def mouseMoveEvent(self, event):
        if self.m_buttonPressed:
            self.m_pt1 = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        pt0_U = self.convertPtCoordsToUniverse(self.m_pt0)

        pt1_U = self.convertPtCoordsToUniverse(self.m_pt1)
        self.m_model.setCurve(pt0_U.x(), pt0_U.y(), pt1_U.x(), pt1_U.y())

        self.m_buttonPressed = False
        self.m_pt0.setX(0)
        self.m_pt0.setY(0)
        self.m_pt1.setX(0)
        self.m_pt1.setY(0)
        p0 = Point(pt0_U.x(), pt0_U.y())
        p1 = Point(pt1_U.x(), pt1_U.y())
        segment = Line(p0, p1)
        self.m_controller.insertSegment(segment, 0.01)
        self.update()
        self.repaint()


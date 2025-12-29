from PySide6.QtWidgets import QMainWindow, QWidget
from PySide6.QtCore import Qt
from win_main_ui import Ui_MainWindow

import vtk
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

class FreeMoveController:
    def __init__(self, actor, interactor, renderer):
        self.actor = actor
        self.interactor = interactor
        self.renderer = renderer
        self.free_move = False
        self.old_position = actor.GetPosition()


    def key_press(self, obj, event):
        key = obj.GetKeySym()
        print(key)  

        if key == "m":
            self.free_move = True
            self.old_position = self.actor.GetPosition()
            

        elif key == "Escape":
            print("e")
            self.actor.SetPosition(self.old_position)
            self.free_move = False
            self.interactor.GetRenderWindow().Render()

        

        elif key == "Return":
            print ("d")
            self.free_move = False
            self.interactor.GetRenderWindow().Render()
            

    def mouse_move(self, obj, event):
        if not self.free_move:
            return
        x, y = obj.GetEventPosition()
        
        wx, wy, wz = self.actor.GetPosition()

        self.renderer.SetWorldPoint (wx,wy,wz,2.0)
        self.renderer.WorldToDisplay()
        _, _, display_z = self.renderer.GetDisplayPoint()

        self.renderer.SetDisplayPoint(x, y, display_z)
        self.renderer.DisplayToWorld()
        world_point =self.renderer.GetWorldPoint()
        
        


        if world_point[3] != 0:
            nx = world_point[0] / world_point[3]
            ny = world_point[1] / world_point[3]
            nz = world_point[2] / world_point[3]
            
            self.actor.SetPosition(nx ,ny ,nz)
        
    

        self.interactor.GetRenderWindow().Render()     

    def left_key(self,obj, event):
        self.free_move = False    


class WinMain(QMainWindow):
    def __init__(self, aParent: QWidget = None):
        super().__init__(aParent)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.setup_vtk()

    def setup_vtk(self):

        
        layout = self.ui.vtkWidget.layout()

        self.vtk_widget = QVTKRenderWindowInteractor(self.ui.vtkWidget)
        layout.addWidget(self.vtk_widget)

        
        self.renderer = vtk.vtkRenderer()
        self.vtk_widget.GetRenderWindow().AddRenderer(self.renderer)

        
        self.interactor = self.vtk_widget.GetRenderWindow().GetInteractor()
        self.interactor.SetInteractorStyle(
            vtk.vtkInteractorStyleTrackballCamera()
        )

        
        cube = vtk.vtkCubeSource()
        cube.SetXLength(1)
        cube.SetYLength(1)
        cube.SetZLength(1)

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(cube.GetOutputPort())

        self.actor = vtk.vtkActor()
        self.actor.SetMapper(mapper)
        self.actor.GetProperty().SetColor(1, 1, 0)

        self.renderer.AddActor(self.actor)
        self.renderer.SetBackground(0.2, 0.2, 0.2)

        
        self.renderer.ResetCamera()

        
        self.controller = FreeMoveController(
            self.actor, self.interactor, self.renderer
        )

        self.interactor.AddObserver(
            "KeyPressEvent", self.controller.key_press
        )
        self.interactor.AddObserver(
            "MouseMoveEvent", self.controller.mouse_move
        )

        self.interactor.AddObserver(
            "LeftButtonPressEvent",self.controller.left_key
        )

        self.vtk_widget.setFocusPolicy(Qt.StrongFocus)
        self.vtk_widget.setFocus()

        self.interactor.Initialize()
        self.vtk_widget.GetRenderWindow().Render()
from PySide6.QtWidgets import QMainWindow, QWidget
from PySide6.QtCore import Qt
from win_main_ui import Ui_MainWindow

import vtk
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

class FreeMoveController:
    def __init__(self, actors, interactor, renderer):
        self.actors = actors
        self.selected_actors = []
        self.interactor = interactor
        self.renderer = renderer
        self.free_move = False
        self.old_positions = {}


    def key_press(self, obj, event):
        key = obj.GetKeySym()
         

        if key == "m" and self.selected_actors:
            self.free_move = True
           
            


        elif key == "Escape" and self.selected_actors:

            print("ESC pressed", self.old_positions)
            for actor, pos in self.old_positions.items():
                actor.SetPosition(pos)
            
            self.free_move = False
            self.interactor.GetRenderWindow().Render()
        

        

        elif key == "Return" and self.selected_actors:
            self.old_positions ={
                actor: actor.GetPosition()



                for actor  in self.selected_actors 

            }
            self.free_move = False
            self.interactor.GetRenderWindow().Render()
            

    def mouse_move(self, obj, event):
        if not self.free_move or not self.selected_actors:
            return
        x, y = obj.GetEventPosition()

        ref_actor = self.selected_actors[0]

        
        wx, wy, wz = ref_actor.GetPosition()

        self.renderer.SetWorldPoint (wx,wy,wz,1.0)
        self.renderer.WorldToDisplay()
        _, _, display_z = self.renderer.GetDisplayPoint()

        self.renderer.SetDisplayPoint(x, y, display_z)
        self.renderer.DisplayToWorld()
        world_point =self.renderer.GetWorldPoint()
        
        


        if world_point[3] != 0:
            nx = world_point[0] / world_point[3]
            ny = world_point[1] / world_point[3]
            nz = world_point[2] / world_point[3]
            
            dx = nx - wx
            dy = ny - wy
            dz = nz - wz

            for actor in self.selected_actors:
                ax, ay, az = actor.GetPosition()
                actor.SetPosition(ax +dx, ay+ dy , az + dz)  
        self.renderer.ResetCameraClippingRange()            

        self.interactor.GetRenderWindow().Render() 
        

    def left_key(self,obj, event):
        self.free_move =  False
        x, y = obj.GetEventPosition()

        picker = vtk.vtkPropPicker()
        picker.Pick(x, y, 0, self.renderer)
        actor = picker.GetActor()

        if actor not in self.actors:
            return
        ctrl_pressed = obj.GetControlKey()


        if not ctrl_pressed:
            for a in self.selected_actors:
                a.GetProperty().SetEdgeVisibility(0)
            self.selected_actors.clear()
            self.old_positions.clear()

        if actor not in self.selected_actors:
            self.selected_actors.append(actor)
            self.old_positions[actor] = actor.GetPosition()                    

            actor.GetProperty().SetEdgeVisibility(1)
            actor.GetProperty().SetEdgeColor(1, 1, 0)    



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
        
        self.actors = []

        def create_cube(x, y, z, color):
            cube = vtk.vtkCubeSource()
            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputConnection(cube.GetOutputPort())

            actor = vtk.vtkActor()
            actor.SetMapper(mapper)
            actor.SetPosition(x, y, z)
            actor.GetProperty().SetColor(color)

            self.renderer.AddActor(actor)
            self.actors.append(actor)

        create_cube(-2, 0, 0, (0, 1, 1))   
        create_cube(2, 0, 0, (1, 0, 0))    


        
        self.renderer.SetBackground(0.2, 0.2, 0.2)

        
        self.renderer.ResetCamera()

        
        self.controller = FreeMoveController(
            self.actors, self.interactor, self.renderer
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
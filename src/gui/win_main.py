from PySide6.QtWidgets import QMainWindow, QWidget
from PySide6.QtCore import Qt
from win_main_ui import Ui_MainWindow

import vtk
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor


# ================= FREE MOVE CONTROLLER =================
class FreeMoveController:
    def __init__(self, actor, interactor, renderer):
        self.actor = actor
        self.interactor = interactor
        self.renderer = renderer
        self.free_move = False
        self.old_position = actor.GetPosition()

    def key_press(self, obj, event):
        key = obj.GetKeySym()

        if key == "m":
            self.free_move = True
            self.old_position = self.actor.GetPosition()
            print("FREE MOVE ENABLED")

        elif key == "Escape":
            self.actor.SetPosition(self.old_position)
            self.free_move = False
            self.interactor.GetRenderWindow().Render()
            print("POSITION REVERTED")

        elif key == "Return":
            self.free_move = False
            print("POSITION CONFIRMED")

    def mouse_move(self, obj, event):
        if not self.free_move:
            return

        x, y = obj.GetEventPosition()

        # Screen → World conversion (SAFE METHOD)
        self.renderer.SetDisplayPoint(x, y, 0)
        self.renderer.DisplayToWorld()
        world_point = self.renderer.GetWorldPoint()

        if world_point[3] != 0:
            wx = world_point[0] / world_point[3]
            wy = world_point[1] / world_point[3]
            wz = world_point[2] / world_point[3]
            self.actor.SetPosition(wx, wy, wz)

        self.interactor.GetRenderWindow().Render()


# ================= MAIN WINDOW =================
class WinMain(QMainWindow):
    def __init__(self, aParent: QWidget = None):
        super().__init__(aParent)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.setup_vtk()

    def setup_vtk(self):

        # ----- Qt Layout -----
        layout = self.ui.vtkWidget.layout()

        # ----- VTK Widget -----
        self.vtk_widget = QVTKRenderWindowInteractor(self.ui.vtkWidget)
        layout.addWidget(self.vtk_widget)

        # ----- Renderer -----
        self.renderer = vtk.vtkRenderer()
        self.vtk_widget.GetRenderWindow().AddRenderer(self.renderer)

        # ----- Interactor -----
        self.interactor = self.vtk_widget.GetRenderWindow().GetInteractor()
        self.interactor.SetInteractorStyle(
            vtk.vtkInteractorStyleTrackballCamera()
        )

        # ----- Cube -----
        cube = vtk.vtkCubeSource()
        cube.SetXLength(1)
        cube.SetYLength(1)
        cube.SetZLength(1)

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(cube.GetOutputPort())

        self.actor = vtk.vtkActor()
        self.actor.SetMapper(mapper)
        self.actor.GetProperty().SetColor(1, 0, 1)

        self.renderer.AddActor(self.actor)
        self.renderer.SetBackground(0.2, 0.2, 0.2)

        # IMPORTANT: camera reset so cube is visible
        self.renderer.ResetCamera()

        # ----- Controller + Observers -----
        self.controller = FreeMoveController(
            self.actor, self.interactor, self.renderer
        )

        self.interactor.AddObserver(
            "KeyPressEvent", self.controller.key_press
        )
        self.interactor.AddObserver(
            "MouseMoveEvent", self.controller.mouse_move
        )

        # ----- Focus (keyboard fix) -----
        self.vtk_widget.setFocusPolicy(Qt.StrongFocus)
        self.vtk_widget.setFocus()

        # ----- Init -----
        self.interactor.Initialize()
        self.vtk_widget.GetRenderWindow().Render()

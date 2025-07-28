from PyQt5 import Qt3DExtras, Qt3DCore
from PyQt5.Qt3DExtras import QSphereMesh
from PyQt5.Qt3DRender import QGeometry, QMesh
from PyQt5.QtCore import QObject, pyqtSignal, pyqtProperty, QPropertyAnimation, QUrl
from PyQt5.QtGui import QMatrix4x4, QVector3D, QQuaternion


class OrbitTransformController(QObject):
    def __init__(self, parent):
        super().__init__(parent)
        self._target = None
        self._matrix = QMatrix4x4()
        self._radius = 1
        self._angle = 0
        self._scale = 1

    def setTarget(self, t):
        self._target = t

    def getTarget(self):
        return self._target

    def setRadius(self, radius):
        if self._radius != radius:
            self._radius = radius
            self.updateMatrix()
            self.radiusChanged.emit()

    def getScale(self):
        return self._scale

    def setScale(self, scale: QVector3D):
        if self._scale != scale:
            self._scale = scale
            self.updateMatrix()
            self.scaleChanged.emit()

    def getRadius(self):
        return self._radius

    def setAngle(self, angle):
        if self._angle != angle:
            self._angle = angle
            self.updateMatrix()
            self.angleChanged.emit()

    def getAngle(self):
        return self._angle

    def updateMatrix(self):
        self._matrix.setToIdentity()
        self._matrix.rotate(self._angle, QVector3D(0, 1, 0))
        self._matrix.translate(self._radius, 0, 0)
        self._matrix.scale(self._scale)
        if self._target is not None:
            self._target.setMatrix(self._matrix)

    angleChanged = pyqtSignal()
    radiusChanged = pyqtSignal()
    scaleChanged = pyqtSignal()
    angle = pyqtProperty(float, getAngle, setAngle, notify=angleChanged)
    radius = pyqtProperty(float, getRadius, setRadius, notify=radiusChanged)
    scale = pyqtProperty(QVector3D, getScale, setScale, notify=scaleChanged)


class DroneVisualisation3DWindow(Qt3DExtras.Qt3DWindow):
    def __init__(self):
        super().__init__()

        # Camera
        self.camera().lens().setPerspectiveProjection(45, 16 / 9, 0.1, 1000)
        self.camera().setPosition(QVector3D(0, 0, 40))
        self.camera().setViewCenter(QVector3D(0, 0, 0))

        # For camera controls
        self.createScene()
        self.camController = Qt3DExtras.QOrbitCameraController(self.rootEntity)
        self.camController.setLinearSpeed(50)
        self.camController.setLookSpeed(180)
        self.camController.setCamera(self.camera())

        self.setRootEntity(self.rootEntity)

    def createScene(self):
        # Root entity
        self.rootEntity = Qt3DCore.QEntity()

        # Material
        self.material = Qt3DExtras.QPhongMaterial(self.rootEntity)

        # # Torus
        # self.torusEntity = Qt3DCore.QEntity(self.rootEntity)
        # self.torusMesh = Qt3DExtras.QTorusMesh()
        # self.torusMesh.setRadius(5)
        # self.torusMesh.setMinorRadius(1)
        # self.torusMesh.setRings(100)
        # self.torusMesh.setSlices(20)
        #
        # self.torusTransform = Qt3DCore.QTransform()
        # self.torusTransform.setScale3D(QVector3D(1.5, 1, 0.5))
        # self.torusTransform.setRotation(QQuaternion.fromAxisAndAngle(QVector3D(1, 0, 0), 45))
        #
        # self.torusEntity.addComponent(self.torusMesh)
        # self.torusEntity.addComponent(self.torusTransform)
        # self.torusEntity.addComponent(self.material)

        # Vehicle
        self.vehicleEntity = Qt3DCore.QEntity(self.rootEntity)
        self.vehicleMesh = QMesh()
        self.vehicleMesh.setSource(QUrl("qrc:/x500.obj"))

        self.vehicleTransform = Qt3DCore.QTransform()
        self.controller = OrbitTransformController(self.vehicleTransform)
        self.controller.setTarget(self.vehicleTransform)
        self.controller.setRadius(0)
        self.controller.setScale(QVector3D(0.05, 0.05, 0.05))

        self.VehicleRotateTransformAnimation = QPropertyAnimation(self.vehicleTransform)
        self.VehicleRotateTransformAnimation.setTargetObject(self.controller)
        self.VehicleRotateTransformAnimation.setPropertyName(b"angle")
        self.VehicleRotateTransformAnimation.setStartValue(0)
        self.VehicleRotateTransformAnimation.setEndValue(360)
        self.VehicleRotateTransformAnimation.setDuration(10000)
        self.VehicleRotateTransformAnimation.setLoopCount(-1)
        self.VehicleRotateTransformAnimation.start()

        self.vehicleEntity.addComponent(self.vehicleMesh)
        self.vehicleEntity.addComponent(self.vehicleTransform)
        self.vehicleEntity.addComponent(self.material)

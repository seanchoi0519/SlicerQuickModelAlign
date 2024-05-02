##BASE PYTHON
import os
import unittest
import logging
import copy
import json
import subprocess
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import glob
import vtk.util.numpy_support as vtk_np
import numpy as np
from datetime import datetime
import time

#
# QuickModelAlign
#

class QuickModelAlign(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "QuickModelAlign"
    self.parent.categories = ["QuickModelAlign"]
    self.parent.dependencies = []
    self.parent.contributors = ["Arthur Porto (LSU), Sara Rolfe (UW), Murat Maga (UW), Dr. Sean Choi"]
    self.parent.helpText = """
      This module automatically aligns and compares two given models, allowing easy, clear visualization of the differences between the models.
      """
    self.parent.acknowledgementText = """
     This module is built using Slicermorph - ALPACA as a foundation for the registration capability (developed by Arthur Porto, Sara Rolfe, and Murat Maga) [https://doi.org/10.1111/2041-210X.13689]
Dr. Sean Choi has led development of this extension project to enable quick, simple alignment of 3D models, and the various visual display modes. Thank you also to Dr. Ryan Choi, Prof. Ove Peters (UQ), and Dr. Christine Peters (UQ) for significant contributions to this research project.
      """


#
# QuickModelAlignWidget
#

class QuickModelAlignWidget(ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

  def __init__(self, parent=None):
    ScriptedLoadableModuleWidget.__init__(self, parent)

  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)
    # Ensure that correct version of open3d Python package is installed
    needRestart = False
    needInstall = False
    Open3dVersion = "0.14.1+816263b"
    try:
      import open3d as o3d
      import cpdalp
      from packaging import version
      if version.parse(o3d.__version__) != version.parse(Open3dVersion):
        if not slicer.util.confirmOkCancelDisplay(f"QuickModelAlign requires installation of open3d (version {Open3dVersion}).\nClick OK to upgrade open3d and restart the application."):
          #self.ui.showBrowserOnEnter = False
          return
        needRestart = True
        needInstall = True
    except ModuleNotFoundError:
      needInstall = True

    if needInstall:
      progressDialog = slicer.util.createProgressDialog(labelText='Upgrading open3d. This may take a minute...', maximum=0)
      slicer.app.processEvents()
      import SampleData
      sampleDataLogic = SampleData.SampleDataLogic()
      try:
        if slicer.app.os == 'win':
          url = "https://app.box.com/shared/static/friq8fhfi8n4syklt1v47rmuf58zro75.whl"
          wheelName = "open3d-0.14.1+816263b-cp39-cp39-win_amd64.whl"
          wheelPath = sampleDataLogic.downloadFile(url, slicer.app.cachePath, wheelName)
        elif slicer.app.os == 'macosx':
          url = "https://app.box.com/shared/static/ixhac95jrx7xdxtlagwgns7vt9b3mbqu.whl"
          wheelName = "open3d-0.14.1+816263b-cp39-cp39-macosx_10_15_x86_64.whl"
          wheelPath = sampleDataLogic.downloadFile(url, slicer.app.cachePath, wheelName)
        elif slicer.app.os == 'linux':
          url = "https://app.box.com/shared/static/wyzk0f9jhefrbm4uukzym0sow5bf26yi.whl"
          wheelName = "open3d-0.14.1+816263b-cp39-cp39-manylinux_2_27_x86_64.whl"
          wheelPath = sampleDataLogic.downloadFile(url, slicer.app.cachePath, wheelName)
      except:
          slicer.util.infoDisplay('Error: please check the url of the open3d wheel in the script')
          progressDialog.close()
      slicer.util.pip_install(f'cpdalp')
      # wheelPath may contain spaces, therefore pass it as a list (that avoids splitting
      # the argument into multiple command-line arguments when there are spaces in the path)
      slicer.util.pip_install([wheelPath])
      import open3d as o3d
      import cpdalp
      progressDialog.close()
    if needRestart:
      slicer.util.restart()

    self.showMinimalScreenUI()
    self.updateLayout()
    self.setUpShortcuts()



# Set up tabs to split workflow
    tabsWidget = qt.QTabWidget()
    alignSingleTab = qt.QWidget()
    alignSingleTabLayout = qt.QFormLayout(alignSingleTab)
    tabsWidget.addTab(alignSingleTab, "3D Dental Align")
    self.layout.addWidget(tabsWidget)
    
    # Layout within the tab
    alignSingleWidget=ctk.ctkCollapsibleButton()
    alignSingleWidgetLayout = qt.QFormLayout(alignSingleWidget)
    alignSingleWidget.text = "Load your models"
    alignSingleTabLayout.addRow(alignSingleWidget)
  
    #
    # Select source mesh
    #
    self.sourceModelSelector = ctk.ctkPathLineEdit()
    self.sourceModelSelector.filters  = ctk.ctkPathLineEdit().Files
    self.sourceModelSelector.nameFilters=["*.ply"]
    alignSingleWidgetLayout.addRow("Prepared: ", self.sourceModelSelector)
    
    # Select target mesh
    #
    self.targetModelSelector = ctk.ctkPathLineEdit()
    self.targetModelSelector.filters  = ctk.ctkPathLineEdit().Files
    self.targetModelSelector.nameFilters=["*.ply"]
    alignSingleWidgetLayout.addRow("Ideal: ", self.targetModelSelector)

    # Make scaling of models optional
    self.skipScalingCheckBox = qt.QCheckBox()
    self.skipScalingCheckBox.checked = 1
    self.skipScalingCheckBox.setToolTip("If checked, QuickModelAlign will skip scaling during the alignment (Not recommended).")
    #alignSingleWidgetLayout.addRow("Skip scaling", self.skipScalingCheckBox)

    [self.projectionFactor,self.pointDensity, self.errorToleranceValue, self.normalSearchRadius, self.FPFHSearchRadius, self.distanceThreshold, self.maxRANSAC, self.RANSACConfidence,
    self.ICPDistanceThreshold, self.alpha, self.beta, self.CPDIterations, self.CPDTolerence] = self.addAdvancedMenu(alignSingleWidgetLayout)

    #
    # Subsample Button
    #
    self.loadModelsButton = qt.QPushButton("Load my models")
    self.loadModelsButton.enabled = False
    alignSingleWidgetLayout.addRow(self.loadModelsButton)

    #
    # Align Button
    #
    self.startAlignButton = qt.QPushButton("Align my models")
    self.startAlignButton.enabled = False
    alignSingleWidgetLayout.addRow(self.startAlignButton)
    
    #
    # Clear Button
    #
    self.clearButton = qt.QPushButton("Start Over!")
    self.clearButton.enabled = False
    alignSingleWidgetLayout.addRow(self.clearButton)
    self.clearButton.hide()
    
    #
    # Ruler Widget
    #
    self.rulerWidget = slicer.qSlicerMarkupsPlaceWidget()
    self.rulerWidget.buttonsVisible=False
    self.rulerWidget.placeButton().show()
    self.rulerWidget.deleteButton().show()
    self.rulerWidget.setDeleteAllMarkupsOptionVisible(True)
    self.layout.addWidget(self.rulerWidget)
    self.rulerWidget.hide()

    # Connections
    self.sourceModelSelector.connect('validInputChanged(bool)', self.onSelect)
    self.targetModelSelector.connect('validInputChanged(bool)', self.onSelect)
    self.projectionFactor.connect('valueChanged(double)', self.onSelect)
    self.errorToleranceValue.connect('valueChanged(double)', self.onChangeTolerance)
    self.loadModelsButton.connect('clicked(bool)', self.onLoadModelsButton)
    self.startAlignButton.connect('clicked(bool)', self.onStartAlignButton)
    self.clearButton.connect('clicked(bool)', self.clearScene)
    
    # initialize the parameter dictionary from single run parameters
    self.parameterDictionary = {
      "projectionFactor": self.projectionFactor.value,
      "pointDensity": self.pointDensity.value,
      "errorToleranceValue": self.errorToleranceValue.value,
      "normalSearchRadius" : self.normalSearchRadius.value,
      "FPFHSearchRadius" : self.FPFHSearchRadius.value,
      "distanceThreshold" : self.distanceThreshold.value,
      "maxRANSAC" : int(self.maxRANSAC.value),
      "RANSACConfidence" : int(self.RANSACConfidence.value),
      "ICPDistanceThreshold"  : self.ICPDistanceThreshold.value,
      "alpha" : self.alpha.value,
      "beta" : self.beta.value,
      "CPDIterations" : int(self.CPDIterations.value),
      "CPDTolerence" : self.CPDTolerence.value
      }

  
  def clearScene(self):
    slicer.mrmlScene.Clear(0)
    self.showMinimalScreenUI()
    self.updateLayout()
    self.view.cornerAnnotation().SetText(vtk.vtkCornerAnnotation.LowerEdge,'')
    self.sourceModelSelector.currentPath = ""
    self.targetModelSelector.currentPath = ""
    self.clearButton.hide()
    self.rulerWidget.hide()
    self.rocking = False

    
  def onSelect(self):
    self.loadModelsButton.enabled = bool ( self.sourceModelSelector.currentPath and self.targetModelSelector.currentPath)

  def onLoadModelsButton(self):
    logic = QuickModelAlignLogic()
    sourceModelNode = slicer.util.loadModel(self.sourceModelSelector.currentPath)
    targetModelNode = slicer.util.loadModel(self.targetModelSelector.currentPath)

    self.sourcePoints, self.targetPoints, self.sourceFeatures, \
      self.targetFeatures, self.voxelSize, self.scaling = logic.runSubsample(sourceModelNode,targetModelNode, self.skipScalingCheckBox.checked, self.parameterDictionary)

    sourceModelNode.GetDisplayNode().SetVisibility(False)
    targetModelNode.GetDisplayNode().SetVisibility(False)

    # Convert to VTK points
    self.sourceSLM_vtk = logic.convertPointsToVTK(self.sourcePoints.points)
    self.targetSLM_vtk = logic.convertPointsToVTK(self.targetPoints.points)
    
    # Display target points
    blue=[0,0,1]
    self.targetCloudNode = logic.displayPointCloud(self.targetSLM_vtk, self.voxelSize/10, 'Target Pointcloud', blue)
    logic.RAS2LPSTransform(self.targetCloudNode)
    
    # Display source points
    red=[1,0,0]
    self.sourceCloudNode = logic.displayPointCloud(self.sourceSLM_vtk, self.voxelSize/10, 'Source Pointcloud', red)
    logic.RAS2LPSTransform(self.sourceCloudNode)
    
    self.updateLayout()
    
    self.loadModelsButton.enabled = False
    self.startAlignButton.enabled = True
    
    lineNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsLineNode', "L")
    self.rulerWidget.setCurrentNode(lineNode)
    self.rulerWidget.setMRMLScene(slicer.mrmlScene)



  def onStartAlignButton(self):
    self.alignModels()
    self.displayAlignedMesh()
    self.clearButton.show()
    self.clearButton.enabled = True
    self.rulerWidget.show()

  def alignModels(self):
    logic = QuickModelAlignLogic()
    self.transformMatrix = logic.estimateTransform(self.sourcePoints, self.targetPoints, self.sourceFeatures, self.targetFeatures, self.voxelSize, self.skipScalingCheckBox.checked, self.parameterDictionary)
    self.ICPTransformNode = logic.convertMatrixToTransformNode(self.transformMatrix, 'Rigid Transformation Matrix')

    # Alignment of Tooth Models
    transform_vtk = self.ICPTransformNode.GetMatrixTransformToParent()
    self.sourceVTK = logic.convertPointsToVTK(self.sourcePoints.points)
    self.alignedSourceSLM_vtk = logic.applyTransform(transform_vtk, self.sourceVTK)
    
    self.startAlignButton.enabled = False
    self.updateLayout()

 

  def displayAlignedMesh(self):
    from open3d import geometry
    from open3d import utility
    logic = QuickModelAlignLogic()
    # Display target points
    self.targetModelNode = slicer.util.loadModel(self.targetModelSelector.currentPath)
    self.sourceModelNode = slicer.util.loadModel(self.sourceModelSelector.currentPath)

    self.sourceModelNode.GetPolyData().GetPoints().GetData().Modified()
    self.sourceModelNode.SetAndObserveTransformNodeID(self.ICPTransformNode.GetID())
    slicer.vtkSlicerTransformLogic().hardenTransform(self.sourceModelNode)
    logic.RAS2LPSTransform(self.sourceModelNode)
    logic.RAS2LPSTransform(self.targetModelNode)
    toothColor=[1, 1, 1]
    
    # instance of Source Model & Target Model. Calculate the difference and feed
    # the distance filter onto the colour model
    m1 = self.sourceModelNode
    m2 = self.targetModelNode
    m1.GetDisplayNode().SetVisibility(True)
    m2.GetDisplayNode().SetVisibility(True)
    m1.GetDisplayNode().SetColor(toothColor)
    m2.GetDisplayNode().SetColor(toothColor)
    m1.GetDisplayNode().SetInterpolation(0)
    m2.GetDisplayNode().SetInterpolation(0)

    self.sourceCloudNode.GetDisplayNode().SetVisibility(False)
    self.targetCloudNode.GetDisplayNode().SetVisibility(False)

    self.setUpAnimation()
    self.ShowInAnimationMode()

    tolerableErrorMargin = self.errorToleranceValue.value

    moduleDir = os.path.dirname(slicer.util.modulePath(self.__module__))
    #iconPath = os.path.join(moduleDir, 'Resources/Icons', imageFileName)
    self.redColorMapPath = moduleDir +'/Resources/CustomColorMaps/red.txt'
    self.blueColorMapPath = moduleDir +'/Resources/CustomColorMaps/blue.txt'


    #   Color the Source Model
    distanceFilter = vtk.vtkDistancePolyDataFilter()
    distanceFilter.SetInputData(0, m1.GetPolyData())
    distanceFilter.SetInputData(1, m2.GetPolyData())
    distanceFilter.Update()
    m1.SetAndObservePolyData( distanceFilter.GetOutput() )
    m1.GetDisplayNode().SetActiveScalarName('Distance')
    customBlueTxtFilePath = self.blueColorMapPath
    customBlueColorMapTable = slicer.util.loadColorTable(customBlueTxtFilePath, False)
    m1.GetDisplayNode().SetAndObserveColorNodeID(customBlueColorMapTable.GetID())
    m1.GetDisplayNode().SetScalarRangeFlag(0)
    m1.GetDisplayNode().SetScalarRange(-tolerableErrorMargin, tolerableErrorMargin)
    
    #   Color the target model
    distanceFilter2 = vtk.vtkDistancePolyDataFilter()
    distanceFilter2.SetInputData(0, m2.GetPolyData())
    distanceFilter2.SetInputData(1, m1.GetPolyData())
    distanceFilter2.Update()
    m2.SetAndObservePolyData( distanceFilter2.GetOutput() )
    m2.GetDisplayNode().SetActiveScalarName('Distance')
    customRedTxtFilePath = self.redColorMapPath
    customRedColorMapTable = slicer.util.loadColorTable(customRedTxtFilePath, False)
    m2.GetDisplayNode().SetAndObserveColorNodeID(customRedColorMapTable.GetID())
    m2.GetDisplayNode().SetScalarRangeFlag(0)
    m2.GetDisplayNode().SetScalarRange(-tolerableErrorMargin, tolerableErrorMargin)


  def onChangeTolerance(self):
    #
    tolerableErrorMargin = self.errorToleranceValue.value
    m1 = self.sourceModelNode
    m2 = self.targetModelNode
    m1.GetDisplayNode().SetScalarRange(-tolerableErrorMargin, tolerableErrorMargin)
    m2.GetDisplayNode().SetScalarRange(-tolerableErrorMargin, tolerableErrorMargin)
   

  def showMinimalScreenUI(self):
  
    self.isSingleModuleShown = False
    slicer.util.mainWindow().setWindowTitle("3DAlign")
    self.showSingleModule(True)
    boxNode = slicer.app.layoutManager().threeDWidget(0).mrmlViewNode()
    boxNode.SetBoxVisible(0)
    boxNode.SetAxisLabelsVisible(0)

 
  def showSingleModule(self, singleModule=True, toggle=False):
    
    if toggle:
      singleModule = not self.isSingleModuleShown

    self.isSingleModuleShown = singleModule

    if singleModule:
      import qt
      settings = qt.QSettings()
      settings.setValue('MainWindow/RestoreGeometry', 'false')

    keepToolbars = [
      #slicer.util.findChild(slicer.util.mainWindow(), 'MainToolBar'),
      #slicer.util.findChild(slicer.util.mainWindow(), 'ViewToolBar')
      ]
    slicer.util.setToolbarsVisible(not singleModule, keepToolbars)
    slicer.util.setMenuBarsVisible(not singleModule)
    slicer.util.setApplicationLogoVisible(not singleModule)
    slicer.util.setModuleHelpSectionVisible(not singleModule)
    slicer.util.setModulePanelTitleVisible(not singleModule)
    slicer.util.setDataProbeVisible(not singleModule)
    slicer.util.setViewControllersVisible(not singleModule)
    slicer.util.setPythonConsoleVisible(False)
  


  def setUpShortcuts(self):

    shortcut = qt.QShortcut(slicer.util.mainWindow())
    shortcut.setKey(qt.QKeySequence("Ctrl+Shift+b"))
    shortcut.connect('activated()', lambda: self.showSingleModule(toggle=True))

    shortcut1 = qt.QShortcut(slicer.util.mainWindow())
    shortcut1.setKey(qt.QKeySequence("1"))
    shortcut1.connect('activated()', lambda: self.ShowInAnimationMode())
    
    shortcut2 = qt.QShortcut(slicer.util.mainWindow())
    shortcut2.setKey(qt.QKeySequence("2"))
    shortcut2.connect('activated()', lambda: self.ShowInWireframeMode())
    
    shortcut3 = qt.QShortcut(slicer.util.mainWindow())
    shortcut3.setKey(qt.QKeySequence("3"))
    shortcut3.connect('activated()', lambda: self.ShowInColourMapMode())
    
    shortcut4 = qt.QShortcut(slicer.util.mainWindow())
    shortcut4.setKey(qt.QKeySequence("Space"))
    shortcut4.connect('activated()', lambda: self.startStopAnimation())

  # ACTIVATED when user presses 1 to show models in animation mode (default)
  def ShowInAnimationMode(self):

    self.rock()
    self.sourceModelNode.GetDisplayNode().SetScalarVisibility(False)
    self.targetModelNode.GetDisplayNode().SetScalarVisibility(False)
    self.sourceModelNode.GetDisplayNode().SetColor([1,1,1])
    self.targetModelNode.GetDisplayNode().SetColor([1,1,1])
    self.sourceModelNode.GetDisplayNode().SetRepresentation(slicer.vtkMRMLDisplayNode.SurfaceRepresentation)
    self.targetModelNode.GetDisplayNode().SetRepresentation(slicer.vtkMRMLDisplayNode.SurfaceRepresentation)
    self.rockTimer.start()

  # ACTIVATED when user presses 2 to show models in wireframe semi-transparent mode
  def ShowInWireframeMode(self):

    self.sourceModelNode.GetDisplayNode().SetScalarVisibility(False)
    self.targetModelNode.GetDisplayNode().SetScalarVisibility(False)
    self.sourceModelNode.GetDisplayNode().SetColor([1,0,0])
    self.targetModelNode.GetDisplayNode().SetColor([0,0,1])
    self.sourceModelNode.GetDisplayNode().SetRepresentation(slicer.vtkMRMLDisplayNode.WireframeRepresentation)
    self.targetModelNode.GetDisplayNode().SetRepresentation(slicer.vtkMRMLDisplayNode.WireframeRepresentation)
    self.rockTimer.start()

  # ACTIVATED when user presses 3 to show models in colour map feedback mode
  def ShowInColourMapMode(self):

    self.sourceModelNode.GetDisplayNode().SetScalarVisibility(True)
    self.targetModelNode.GetDisplayNode().SetScalarVisibility(True)
    self.sourceModelNode.GetDisplayNode().SetOpacity(1)
    self.targetModelNode.GetDisplayNode().SetOpacity(1)
    self.sourceModelNode.GetDisplayNode().SetRepresentation(slicer.vtkMRMLDisplayNode.SurfaceRepresentation)
    self.targetModelNode.GetDisplayNode().SetRepresentation(slicer.vtkMRMLDisplayNode.SurfaceRepresentation)
    #self.sourceModelNode.GetDisplayNode().SetScalarOpacity(0.1)
    self.view.cornerAnnotation().SetText(vtk.vtkCornerAnnotation.LowerEdge,'Colour Map')
    self.rockTimer.stop()

  def setUpAnimation(self):
    self.fadeSlider = ctk.ctkSliderWidget()
    self.fadeSlider.minimum = 0
    self.fadeSlider.maximum = 1.0
    self.fadeSlider.value = 0.5
    self.fadeSlider.singleStep = 0.05
    self.rockCount = 0
    self.rocking = True
    self.rockTimer = None
    
    self.view = slicer.app.layoutManager().threeDWidget(0).threeDView()
    self.view.cornerAnnotation().SetText(vtk.vtkCornerAnnotation.LowerEdge,'Prepared')
    #self.view.cornerAnnotation().SetText(vtk.vtkCornerAnnotation.LowerEdge,'Prepared')
    self.view.cornerAnnotation().GetTextProperty().SetColor(255,255,255)
    self.view.forceRender()
    

  def startStopAnimation(self):

    if self.rocking == True:
      #self.rockTimer.stop()
      self.rocking = False
    else:
      #self.rockTimer.start()
      self.rocking = True
    
  def rock(self):

    if self.rocking:
      if not self.rockTimer:
        self.rockTimer = qt.QTimer()
        self.rockTimer.start(80)
        self.rockTimer.connect('timeout()', self.rock)
      import math
      self.fadeSlider.value = 0.5 + math.sin(self.rockCount / 10. ) / 2.
      self.sourceModelNode.GetDisplayNode().SetOpacity(self.fadeSlider.value)
      self.targetModelNode.GetDisplayNode().SetOpacity(1-self.fadeSlider.value)
      
      if self.fadeSlider.value > 0.5:
        self.view.cornerAnnotation().SetText(vtk.vtkCornerAnnotation.LowerEdge,'Prepared')
      else:
        self.view.cornerAnnotation().SetText(vtk.vtkCornerAnnotation.LowerEdge,'Ideal')
        
      self.rockCount += 1
    

  def cleanup(self):
    pass

  def addLayoutButton(self, layoutID, buttonAction, toolTip, imageFileName, layoutDiscription):
    layoutManager = slicer.app.layoutManager()
    layoutManager.layoutLogic().GetLayoutNode().AddLayoutDescription(layoutID, layoutDiscription)

    viewToolBar = slicer.util.mainWindow().findChild('QToolBar', 'ViewToolBar')
    layoutMenu = viewToolBar.widgetForAction(viewToolBar.actions()[0]).menu()
    layoutSwitchActionParent = layoutMenu
    # use `layoutMenu` to add inside layout list, use `viewToolBar` to add next the standard layout list
    layoutSwitchAction = layoutSwitchActionParent.addAction(buttonAction) # add inside layout list

    moduleDir = os.path.dirname(slicer.util.modulePath(self.__module__))
    iconPath = os.path.join(moduleDir, 'Resources/Icons', imageFileName)
    self.redColorMapPath = moduleDir +'/Resources/CustomColorMaps/red.txt'
    self.blueColorMapPath = moduleDir +'/Resources/CustomColorMaps/blue.txt'
    
    layoutSwitchAction.setIcon(qt.QIcon(iconPath))
    layoutSwitchAction.setToolTip(toolTip)
    layoutSwitchAction.connect('triggered()', lambda layoutId = layoutID: slicer.app.layoutManager().setLayout(layoutId))
    layoutSwitchAction.setData(layoutID)


  def updateLayout(self):
    layoutManager = slicer.app.layoutManager()
    layoutManager.setLayout(9)  #set layout to 3D only
    layoutManager.threeDWidget(0).threeDView().resetFocalPoint()
    layoutManager.threeDWidget(0).threeDView().resetCamera()
    viewNode = slicer.app.layoutManager().threeDWidget(0).mrmlViewNode()
    viewNode.SetBackgroundColor(0.9,0.9,0.9)
    viewNode.SetBackgroundColor2(0.9,0.9,0.9)

  def addAdvancedMenu(self, currentWidgetLayout):
    #
    # Advanced menu for single run
    #
    advancedCollapsibleButton = ctk.ctkCollapsibleButton()
    advancedCollapsibleButton.text = "Advanced settings"
    advancedCollapsibleButton.collapsed = True
    currentWidgetLayout.addRow(advancedCollapsibleButton)
    advancedFormLayout = qt.QFormLayout(advancedCollapsibleButton)

    # Point density label
    pointDensityCollapsibleButton=ctk.ctkCollapsibleButton()
    pointDensityCollapsibleButton.text = "Allowed Error Tolerance"
    advancedFormLayout.addRow(pointDensityCollapsibleButton)
    pointDensityFormLayout = qt.QFormLayout(pointDensityCollapsibleButton)

    # Rigid registration label
    rigidRegistrationCollapsibleButton=ctk.ctkCollapsibleButton()
    rigidRegistrationCollapsibleButton.text = "Rigid registration"
    #advancedFormLayout.addRow(rigidRegistrationCollapsibleButton)
    rigidRegistrationFormLayout = qt.QFormLayout(rigidRegistrationCollapsibleButton)
    
    # Deformable registration label
    deformableRegistrationCollapsibleButton=ctk.ctkCollapsibleButton()
    deformableRegistrationCollapsibleButton.text = "Deformable registration"
    #advancedFormLayout.addRow(deformableRegistrationCollapsibleButton)
    deformableRegistrationFormLayout = qt.QFormLayout(deformableRegistrationCollapsibleButton)
    
    # Set max projection factor
    errorToleranceValue = ctk.ctkSliderWidget()
    errorToleranceValue.enabled = True
    errorToleranceValue.singleStep = 0.05
    errorToleranceValue.minimum = 0
    errorToleranceValue.maximum = 2
    errorToleranceValue.value = 0.15
    pointDensityFormLayout.addRow("Error Tolerance (mm): ", errorToleranceValue)
    
    # Point Density slider
    pointDensity = ctk.ctkSliderWidget()
    pointDensity.singleStep = 0.1
    pointDensity.minimum = 0.1
    pointDensity.maximum = 3
    pointDensity.value = 0.8
    pointDensity.setToolTip("Adjust the density of the pointclouds. Larger values increase the number of points, and vice versa.")
    #pointDensityFormLayout.addRow("Point Density Adjustment: ", pointDensity)

    # Set max projection factor
    projectionFactor = ctk.ctkSliderWidget()
    projectionFactor.enabled = True
    projectionFactor.singleStep = 1
    projectionFactor.minimum = 0
    projectionFactor.maximum = 10
    projectionFactor.value = 1
    projectionFactor.setToolTip("Set maximum point projection as a percentage of the image diagonal. Point projection is used to make sure predicted landmarks are placed on the target mesh.")
    #rigidRegistrationFormLayout.addRow("Maximum projection factor: ", projectionFactor)

    # Normal search radius slider
    
    normalSearchRadius = ctk.ctkSliderWidget()
    normalSearchRadius.singleStep = 1
    normalSearchRadius.minimum = 2
    normalSearchRadius.maximum = 12
    normalSearchRadius.value = 2
    normalSearchRadius.setToolTip("Set size of the neighborhood used when computing normals")
    #rigidRegistrationFormLayout.addRow("Normal search radius: ", normalSearchRadius)
    
    #FPFH Search Radius slider
    FPFHSearchRadius = ctk.ctkSliderWidget()
    FPFHSearchRadius.singleStep = 1
    FPFHSearchRadius.minimum = 3
    FPFHSearchRadius.maximum = 20
    FPFHSearchRadius.value = 5
    FPFHSearchRadius.setToolTip("Set size of the neighborhood used when computing FPFH features")
    #rigidRegistrationFormLayout.addRow("FPFH Search radius: ", FPFHSearchRadius)
    
    
    # Maximum distance threshold slider
    distanceThreshold = ctk.ctkSliderWidget()
    distanceThreshold.singleStep = .25
    distanceThreshold.minimum = 0.5
    distanceThreshold.maximum = 4
    distanceThreshold.value = 1.5
    distanceThreshold.setToolTip("Maximum correspondence points-pair distance threshold")
    #rigidRegistrationFormLayout.addRow("Maximum corresponding point distance: ", distanceThreshold)

    # Maximum RANSAC iterations slider
    maxRANSAC = ctk.ctkDoubleSpinBox()
    maxRANSAC.singleStep = 1
    maxRANSAC.setDecimals(0)
    maxRANSAC.minimum = 1
    maxRANSAC.maximum = 500000000
    maxRANSAC.value = 4000000
    maxRANSAC.setToolTip("Maximum number of iterations of the RANSAC algorithm")
    #rigidRegistrationFormLayout.addRow("Maximum RANSAC iterations: ", maxRANSAC)

    # Maximum RANSAC validation steps
    RANSACConfidence = ctk.ctkDoubleSpinBox()
    RANSACConfidence.singleStep = 0.001
    RANSACConfidence.setDecimals(0)
    RANSACConfidence.minimum = 0
    RANSACConfidence.maximum = 1
    RANSACConfidence.value = 0.999
    RANSACConfidence.setToolTip("RANSAC Confidence")
    #rigidRegistrationFormLayout.addRow("RANSAC Confidence: ", RANSACConfidence)

    # ICP distance threshold slider
    ICPDistanceThreshold = ctk.ctkSliderWidget()
    ICPDistanceThreshold.singleStep = .1
    ICPDistanceThreshold.minimum = 0.1
    ICPDistanceThreshold.maximum = 2
    ICPDistanceThreshold.value = 0.4
    ICPDistanceThreshold.setToolTip("Maximum ICP points-pair distance threshold")
    #rigidRegistrationFormLayout.addRow("Maximum ICP distance: ", ICPDistanceThreshold)

    # Alpha slider
    alpha = ctk.ctkDoubleSpinBox()
    alpha.singleStep = .1
    alpha.setDecimals(1)
    alpha.minimum = 0.1
    alpha.maximum = 10
    alpha.value = 2
    alpha.setToolTip("Parameter specifying trade-off between fit and smoothness. Low values induce fluidity, while higher values impose rigidity")
    #deformableRegistrationFormLayout.addRow("Rigidity (alpha): ", alpha)

    # Beta slider
    beta = ctk.ctkDoubleSpinBox()
    beta.singleStep = 0.1
    beta.setDecimals(1)
    beta.minimum = 0.1
    beta.maximum = 10
    beta.value = 2
    beta.setToolTip("Width of gaussian filter used when applying smoothness constraint")
    #deformableRegistrationFormLayout.addRow("Motion coherence (beta): ", beta)

    # # CPD iterations slider
    CPDIterations = ctk.ctkSliderWidget()
    CPDIterations.singleStep = 1
    CPDIterations.minimum = 100
    CPDIterations.maximum = 1000
    CPDIterations.value = 100
    CPDIterations.setToolTip("Maximum number of iterations of the CPD procedure")
    #deformableRegistrationFormLayout.addRow("CPD iterations: ", CPDIterations)

    # # CPD tolerance slider
    CPDTolerence = ctk.ctkSliderWidget()
    CPDTolerence.setDecimals(4)
    CPDTolerence.singleStep = .0001
    CPDTolerence.minimum = 0.0001
    CPDTolerence.maximum = 0.01
    CPDTolerence.value = 0.001
    CPDTolerence.setToolTip("Tolerance used to assess CPD convergence")
    #deformableRegistrationFormLayout.addRow("CPD tolerance: ", CPDTolerence)

    return projectionFactor, pointDensity, errorToleranceValue, normalSearchRadius, FPFHSearchRadius, distanceThreshold, maxRANSAC, RANSACConfidence, ICPDistanceThreshold, alpha, beta, CPDIterations, CPDTolerence

 
#
# QuickModelAlignLogic
#

class QuickModelAlignLogic(ScriptedLoadableModuleLogic):


  def RAS2LPSTransform(self, modelNode):
    matrix=vtk.vtkMatrix4x4()
    matrix.Identity()
    matrix.SetElement(0,0,-1)
    matrix.SetElement(1,1,-1)
    transform=vtk.vtkTransform()
    transform.SetMatrix(matrix)
    transformNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLTransformNode', 'RAS2LPS')
    transformNode.SetAndObserveTransformToParent( transform )
    modelNode.SetAndObserveTransformNodeID(transformNode.GetID())
    slicer.vtkSlicerTransformLogic().hardenTransform(modelNode)
    slicer.mrmlScene.RemoveNode(transformNode)

  def convertMatrixToVTK(self, matrix):
    matrix_vtk = vtk.vtkMatrix4x4()
    for i in range(4):
      for j in range(4):
        matrix_vtk.SetElement(i,j,matrix[i][j])
    return matrix_vtk

  def convertMatrixToTransformNode(self, matrix, transformName):
    matrix_vtk = vtk.vtkMatrix4x4()
    for i in range(4):
      for j in range(4):
        matrix_vtk.SetElement(i,j,matrix[i][j])

    transform = vtk.vtkTransform()
    transform.SetMatrix(matrix_vtk)
    transformNode =  slicer.mrmlScene.AddNewNodeByClass('vtkMRMLTransformNode', transformName)
    transformNode.SetAndObserveTransformToParent( transform )

    return transformNode

  def applyTransform(self, matrix, polydata):
    transform = vtk.vtkTransform()
    transform.SetMatrix(matrix)

    transformFilter = vtk.vtkTransformPolyDataFilter()
    transformFilter.SetTransform(transform)
    transformFilter.SetInputData(polydata)
    transformFilter.Update()
    return transformFilter.GetOutput()

  def convertPointsToVTK(self, points):
    array_vtk = vtk_np.numpy_to_vtk(points, deep=True, array_type=vtk.VTK_FLOAT)
    points_vtk = vtk.vtkPoints()
    points_vtk.SetData(array_vtk)
    polydata_vtk = vtk.vtkPolyData()
    polydata_vtk.SetPoints(points_vtk)
    return polydata_vtk


  def displayPointCloud(self, polydata, pointRadius, nodeName, nodeColor):
    #set up glyph for visualizing point cloud
    sphereSource = vtk.vtkSphereSource()
    sphereSource.SetRadius(pointRadius)
    glyph = vtk.vtkGlyph3D()
    glyph.SetSourceConnection(sphereSource.GetOutputPort())
    glyph.SetInputData(polydata)
    glyph.ScalingOff()
    glyph.Update()

    #display
    # modelNode=slicer.mrmlScene.GetFirstNodeByName(nodeName)
    #if modelNode is None:  # if there is no node with this name, create with display node
    modelNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode', nodeName)
    modelNode.CreateDefaultDisplayNodes()

    modelNode.SetAndObservePolyData(glyph.GetOutput())
    modelNode.GetDisplayNode().SetColor(nodeColor)
    return modelNode


  def displayMesh(self, polydata, nodeName, nodeColor):
    modelNode=slicer.mrmlScene.GetFirstNodeByName(nodeName)
    if modelNode is None:  # if there is no node with this name, create with display node
      modelNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode', nodeName)
      modelNode.CreateDefaultDisplayNodes()

    modelNode.SetAndObservePolyData(polydata)
    modelNode.GetDisplayNode().SetColor(nodeColor)
    return modelNode

  def estimateTransform(self, sourcePoints, targetPoints, sourceFeatures, targetFeatures, voxelSize, skipScaling, parameters):
    ransac = self.execute_global_registration(sourcePoints, targetPoints, sourceFeatures, targetFeatures, voxelSize,
      parameters["distanceThreshold"], parameters["maxRANSAC"], parameters["RANSACConfidence"], skipScaling)
    # Refine the initial registration using an Iterative Closest Point (ICP) registration
    #import time
    icp = self.refine_registration(sourcePoints, targetPoints, sourceFeatures, targetFeatures, voxelSize, ransac, parameters["ICPDistanceThreshold"])
    return icp.transformation

  def runSubsample(self, sourceModel, targetModel, skipScaling, parameters):
    from open3d import io
    from open3d import geometry
    from open3d import utility
    print(":: Loading point clouds and downsampling")
    sourcePoints = slicer.util.arrayFromModelPoints(sourceModel)
    source = geometry.PointCloud()
    source.points = utility.Vector3dVector(sourcePoints)
    targetPoints = slicer.util.arrayFromModelPoints(targetModel)
    target = geometry.PointCloud()
    target.points = utility.Vector3dVector(targetPoints)
    sourceSize = np.linalg.norm(np.asarray(source.get_max_bound()) - np.asarray(source.get_min_bound()))
    targetSize = np.linalg.norm(np.asarray(target.get_max_bound()) - np.asarray(target.get_min_bound()))
    voxel_size = targetSize/(55*parameters["pointDensity"])
    scaling = (targetSize)/sourceSize
    if skipScaling != 0:
        scaling = 1
    source.scale(scaling, center = (0,0,0))
    points = slicer.util.arrayFromModelPoints(sourceModel)
    points[:] = np.asarray(source.points)
    sourceModel.GetPolyData().GetPoints().GetData().Modified()
    source_down, source_fpfh = self.preprocess_point_cloud(source, voxel_size, parameters["normalSearchRadius"], parameters["FPFHSearchRadius"])
    target_down, target_fpfh = self.preprocess_point_cloud(target, voxel_size, parameters["normalSearchRadius"], parameters["FPFHSearchRadius"])
    return source_down, target_down, source_fpfh, target_fpfh, voxel_size, scaling


  def preprocess_point_cloud(self, pcd, voxel_size, radius_normal_factor, radius_feature_factor):
    from open3d import geometry
    from open3d import pipelines
    registration = pipelines.registration
    print(":: Downsample with a voxel size %.3f." % voxel_size)
    pcd_down = pcd.voxel_down_sample(voxel_size)
    radius_normal = voxel_size * radius_normal_factor
    print(":: Estimate normal with search radius %.3f." % radius_normal)
    pcd_down.estimate_normals(
        geometry.KDTreeSearchParamHybrid(radius=radius_normal, max_nn=30))
    radius_feature = voxel_size * radius_feature_factor
    print(":: Compute FPFH feature with search radius %.3f." % radius_feature)
    pcd_fpfh = registration.compute_fpfh_feature(
        pcd_down,
        geometry.KDTreeSearchParamHybrid(radius=radius_feature, max_nn=100))
    return pcd_down, pcd_fpfh


  def execute_global_registration(self, source_down, target_down, source_fpfh,
                                target_fpfh, voxel_size, distance_threshold_factor, maxIter, confidence, skipScaling):
    from open3d import pipelines
    registration = pipelines.registration
    distance_threshold = voxel_size * distance_threshold_factor
    print(":: RANSAC registration on downsampled point clouds.")
    print("   Since the downsampling voxel size is %.3f," % voxel_size)
    print("   we use a liberal distance threshold %.3f." % distance_threshold)

    result = registration.registration_ransac_based_on_feature_matching(
        source_down, target_down, source_fpfh, target_fpfh, True,
        distance_threshold,
        registration.TransformationEstimationPointToPoint(False),
        3, [
            registration.CorrespondenceCheckerBasedOnEdgeLength(
                0.9),
            registration.CorrespondenceCheckerBasedOnDistance(
                distance_threshold)
        ], registration.RANSACConvergenceCriteria(100000, 0.999))


    return result



  def refine_registration(self, source, target, source_fpfh, target_fpfh, voxel_size, result_ransac, ICPThreshold_factor):
    from open3d import pipelines
    registration = pipelines.registration
    distance_threshold = voxel_size * ICPThreshold_factor
    print(":: Point-to-plane ICP registration is applied on original point")
    print("   clouds to refine the alignment. This time we use a strict")
    print("   distance threshold %.3f." % distance_threshold)
    result = registration.registration_icp(
        source, target, distance_threshold, result_ransac.transformation,
        registration.TransformationEstimationPointToPlane())
    return result



  def process(self, inputVolume, outputVolume, imageThreshold, invert=False, showResult=True):
    """
    Run the processing algorithm.
    Can be used without GUI widget.
    :param inputVolume: volume to be thresholded
    :param outputVolume: thresholding result
    :param imageThreshold: values above/below this threshold will be set to 0
    :param invert: if True then values above the threshold will be set to 0, otherwise values below are set to 0
    :param showResult: show output volume in slice viewers
    """

    if not inputVolume or not outputVolume:
      raise ValueError("Input or output volume is invalid")

    import time
    startTime = time.time()
    logging.info('Processing started')

    # Compute the thresholded output volume using the "Threshold Scalar Volume" CLI module
    cliParams = {
      'InputVolume': inputVolume.GetID(),
      'OutputVolume': outputVolume.GetID(),
      'ThresholdValue' : imageThreshold,
      'ThresholdType' : 'Above' if invert else 'Below'
      }
    cliNode = slicer.cli.run(slicer.modules.thresholdscalarvolume, None, cliParams, wait_for_completion=True, update_display=showResult)
    # We don't need the CLI module node anymore, remove it to not clutter the scene with it
    slicer.mrmlScene.RemoveNode(cliNode)

    stopTime = time.time()
    logging.info(f'Processing completed in {stopTime-startTime:.2f} seconds')


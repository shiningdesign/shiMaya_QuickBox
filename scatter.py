'''
scatter based on Univeral Tool Template
by ying - http://shining-lucy.com/wiki

v3.0 2016.08.10
  - support both vtx and particle based position spread
  - add random shortlist vtx feature
  - independent  x,y,z scale random option
  - align to normal on surface option
  - open option for distance filter option
  - open option for duplicate as instance for geo input
  - add scale min, so range from min to scale

log
v2.0: 
  * select geo, select surface, then GUI to scatter it with random rotate and scale


usage in maya: 
import scatter
scatter.main()

'''
deskMode = 0
qtMode = 0 # 0: PySide; 1 : PyQt
try:
    import maya.OpenMayaUI as mui
    import maya.cmds as cmds
except ImportError:
    deskMode = 1

# ==== for PyQt4 ====
#from PyQt4 import QtGui,QtCore
#import sip

# ==== for pyside ====
#from PySide import QtGui,QtCore
#import shiboken

# ==== auto Qt load ====
try:
    from PySide import QtGui,QtCore
    import shiboken
    qtMode = 0
except ImportError:
    from PyQt4 import QtGui,QtCore
    import sip
    qtMode = 1
    
from functools import partial
import sys

import json
import random
import math
# note: if you want to create a window with menu, then use QMainWindow Class
class ScatterUI(QtGui.QMainWindow):
#class ScatterUI(QtGui.QDialog):
    def __init__(self, parent=None, mode=0):
        QtGui.QMainWindow.__init__(self, parent)
        #QtGui.QDialog.__init__(self, parent)
        
        self.version="3.5"
        self.uiList={} # for ui obj storage
        self.fileType='.ScatterUI_EXT'
        self.memoData = {}
        # mode: example for receive extra user input as parameter
        self.mode = 0
        if mode in [0,1]:
            self.mode = mode # mode validator
        
        # global app style setting for desktop
        if deskMode == 1:
            QtGui.QApplication.setStyle(QtGui.QStyleFactory.create('Cleanlooks'))
        self.setStyleSheet("QLineEdit:disabled{background-color: gray;}")
        self.setupMenu() # only if you use QMainWindows Class
        self.setupWin()
        self.setupUI()
        self.Establish_Connections()
        self.loadData()

    def setupMenu(self):
        self.quickMenu(['file_menu;&File','setting_menu;&Setting','help_menu;&Help'])
        cur_menu = self.uiList['setting_menu']
        self.quickMenuAction('setParaA_atn','Set Parameter &A','A example of tip notice.','setParaA.png', cur_menu)
        cur_menu.addSeparator()
        # for info review
        cur_menu = self.uiList['help_menu']
        self.quickMenuAction('helpDeskMode_atn','Desk Mode - {}'.format(deskMode),'Desktop Running Mode - 0: Maya Mode; 1: Desktop Mode.','', cur_menu)
        self.quickMenuAction('helpQtMode_atn','PyQt4 Mode - {}'.format(qtMode),'Qt Library - 0: PySide; 1: PyQt4.','', cur_menu)
        
    def setupWin(self):
        self.setWindowTitle("ScatterUI" + " - v" + self.version) 
        #self.setGeometry(300, 300, 800, 600)
        self.resize(250,250)
        # - for frameless or always on top option
        #self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint) # it will keep ui always on top of desktop, but to set this in Maya, dont set Maya as its parent
        #self.setWindowFlags(QtCore.Qt.FramelessWindowHint) # it will hide ui border frame, but in Maya, use QDialog instead as QMainWindow will disappear
        #self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint) # best for Maya case with QDialog without parent, for always top frameless ui
        # - for transparent and non-regular shape ui
        #self.setAttribute(QtCore.Qt.WA_TranslucentBackground) # use it if you set main ui to transparent and want to use alpha png as irregular shape window
        #self.setStyleSheet("background-color: rgba(0, 0, 0,0);") # black color better white color for get better look of semi trans edge, like pre-mutiply
        
    def setupUI(self):
        #==============================
        
        # main_layout for QMainWindow
        main_widget = QtGui.QWidget()
        self.setCentralWidget(main_widget)        
        main_layout = self.quickLayout('vbox') # grid
        main_widget.setLayout(main_layout)
        '''
        # main_layout for QDialog
        main_layout = self.quickLayout('vbox')
        self.setLayout(main_layout)
        '''
        
        #------------------------------
        # ui element creation part
        particle_layout = self.quickUI(['particleSelect_btn;QPushButton;Select Surface Particle', 'particleCreate_btn;QPushButton;Create Surface Particle'],"particle_QHBoxLayout")
        vtx_layout= self.quickUI(['vtxSelect_btn;QPushButton;Select Vtx based', 'vtxRandom_btn;QPushButton;Random Selected Vtx','vtxRandomNum_input;QLineEdit;5'],"vtx_QHBoxLayout")
        scatter_layout = self.quickUI(['rot_check;QCheckBox;Rot:','xRot_input;QLineEdit','yRot_input;QLineEdit','zRot_input;QLineEdit'],"scatterRot_QGridLayout", "h")
        self.quickUI(['scale_check;QCheckBox;Scale:','xScale_input;QLineEdit','yScale_input;QLineEdit','zScale_input;QLineEdit'],scatter_layout, "h")
        self.quickUI(['scaleMin_check;QCheckBox;S min:','xScaleMin_input;QLineEdit','yScaleMin_input;QLineEdit','zScaleMin_input;QLineEdit'],scatter_layout, "h")
        self.quickUI(['geoSelect_btn;QPushButton;Select Scatter Geo / GeoList', particle_layout, vtx_layout, scatter_layout,'scaleLink_check;QCheckBox;Use same scale for x,y,z','scatter_btn;QPushButton;Scatter', self.quickUI(['alignNormal_check;QCheckBox;Align Y to normal','normalSurfaceSelect_btn;QPushButton;Select Normal Surface'],"alignNormal_QHBoxLayout"), 'pointDistanceFilter_chek;QCheckBox;Point Distance Filter', 'minDist_label;QLabel;min dist(0 means bbox) -','minDist_input;QLineEdit','instanceCheck_check;QCheckBox;Duplicate as Instance for geo','help_label;QLabel'],main_layout)
        tmpTxt="""
ScatterUI is a tool to scatter a geo on each particle
with a optional random rotate and/or scale;
1. Select the geo/s to scatter;
2. select particle/vtx for the position info,
- for particle, optionally select the surface to create 
  a object emit particle, then play timeline to a frame 
  that fit your partcile amount.
- for vtx, optionally random pickup a num of points 
  from your vtx selection
3. use scatter random option (TRS,align,mixDistBetPoint,Inst);
4. scatter button to scatter.
        """
        self.uiList['help_label'].setText(tmpTxt)
        '''
        self.uiList['secret_btn'] = QtGui.QPushButton(self) # invisible but functional button
        self.uiList['secret_btn'].setText("")
        self.uiList['secret_btn'].setGeometry(0, 0, 50, 20)
        self.uiList['secret_btn'].setStyleSheet("QPushButton{background-color: rgba(0, 0, 0,0);} QPushButton:pressed{background-color: rgba(0, 0, 0,0); border: 0px;} QPushButton:hover{background-color: rgba(0, 0, 0,0); border: 0px;}")
        #:hover:pressed:focus:hover:disabled
        '''

    def Establish_Connections(self):
        # loop button and menu action to link to functions
        for ui_name in self.uiList.keys():
            if ui_name.endswith('_btn'):
                QtCore.QObject.connect(self.uiList[ui_name], QtCore.SIGNAL("clicked()"), getattr(self, ui_name[:-4]+"_action", partial(self.default_action,ui_name)))
            if ui_name.endswith('_atn'):
                QtCore.QObject.connect(self.uiList[ui_name], QtCore.SIGNAL("triggered()"), getattr(self, ui_name[:-4]+"_action", partial(self.default_action,ui_name)))
        QtCore.QObject.connect(self.uiList['scaleLink_check'], QtCore.SIGNAL("toggled(bool)"), self.scaleLink_toggle_action)
    
    #############################################
    # UI Response functions
    ##############################################
    def loadData(self):
        print("Load data")
    def geoSelect_action(self):
        selected = cmds.ls(sl=1)
        if len(selected) > 0:
            self.memoData["geoList"] = selected
            print "Geo Defined \n"
            bboxMax = 0
            for geo in selected:
                bbox = cmds.xform(geo,q=1,ws=1,bb=1)
                maxDist = self.distance(bbox[3:],bbox[:3])
                if bboxMax < maxDist:
                    bboxMax = maxDist
            oldTxt = str(self.uiList['minDist_label'].text()).split('-')[0]
            newTxt= oldTxt + "- "+str(bboxMax)
            self.uiList['minDist_label'].setText(newTxt)
            self.memoData['minDist'] = bboxMax
        else:
            QtGui.QMessageBox.information(self, "Note", "Please select the geometry for scatter.")
    def vtxSelect_action(self):
        vtxList = cmds.ls(sl=1,fl=1)
        self.memoData['vtxList'] = vtxList
        self.storePositionBy_vtx()
    def vtxRandom_action(self):
        #input
        growPoint = cmds.ls(sl=1,fl=1)
        rootName = growPoint[0].split(".")[0]
        branchCnt = str(self.uiList['vtxRandomNum_input'].text())
        branchCnt = 5 if branchCnt == "" else int(branchCnt)

        # random pick branch point
        cnt = len(growPoint)
        ids = []
        for i in range(branchCnt):
            random.seed(i)
            ids.append(int(random.random()*cnt)) #range(1, cnt)
        ids.sort()
        vtxList = [growPoint[i] for i in ids]
        cmds.select(vtxList,r=1)
    def particleSelect_action(self):
        selected = cmds.ls(sl=1)
        if len(selected) > 0:
            self.memoData["particle"] = selected[0]
            print "Particle Defined \n"
            self.storePositionBy_particle()
        else:
            QtGui.QMessageBox.information(self, "Note", "Please select the particle for scatter at.")
    def particleCreate_action(self):
        selected = cmds.ls(sl=1)
        if not len(selected) > 0:
            QtGui.QMessageBox.information(self, "Note", "Please select the surface for the particle to scatter at.")
        else:
            self.memoData["surface"] = selected[0]
            print "Surface Defined \n"
            emitterSys = cmds.emitter(n="ScatterUI_emitter", type="surface", r=100, sro=0, spd=0, srn=0)[1]
            particleSys =cmds.particle(n="ScatterUI_particle")[0]
            cmds.connectDynamic(particleSys, em=emitterSys)
            self.memoData["particle"] = particleSys
            # move a few frame to generate particle
            for i in range(10):
                cmds.NextFrame()
            print "Particle Defined \n"
            self.storePositionBy_particle()
    def storePositionBy_vtx(self):
        vtxList = self.memoData['vtxList']
        cnt = len(vtxList)
        pos = []
        for i in range(cnt):
            pos.append( tuple(cmds.xform(vtxList[i],q=1,ws=1,t=1)) )
        self.memoData["posList"]=pos
    def storePositionBy_particle(self):
        particleSys = self.memoData["particle"]
        cnt = cmds.particle(particleSys, q=1,ct=1)
        pos = []
        for i in range(cnt):
            pos.append( tuple(cmds.particle( particleSys, q=1,at="position", id=i)) )
        self.memoData["posList"]=pos
    def filterPositionBy_bbox(self):
        minDist = self.memoData['minDist']
        return self.filterPositionBy_distance(minDist)
    def filterPositionBy_distance(self, minDist):
        pos = self.memoData["posList"]
        cnt = len(pos)
        
        invalidPointIdList = []
        for i in range(cnt-1):
            if i in invalidPointIdList:
                continue
            curPoint = pos[i]
            for j in range((i+1),cnt):
                endPoint = pos[j]
                t_dist = self.distance(curPoint, endPoint)
                if t_dist < minDist:
                    invalidPointIdList.append(j)
        
        validPointIdList = [i for i in range(cnt) if i not in invalidPointIdList]
        return validPointIdList
        
    def distance(self,a,b):
        return math.sqrt(math.pow((a[0]-b[0]),2) + math.pow((a[1]-b[1]),2) + math.pow((a[2]-b[2]),2))
    def scaleLink_toggle_action(self, bool):
        self.uiList['yScale_input'].setDisabled(bool)
        self.uiList['zScale_input'].setDisabled(bool)
        self.uiList['yScaleMin_input'].setDisabled(bool)
        self.uiList['zScaleMin_input'].setDisabled(bool)
    def normalSurfaceSelect_action(self):
        selected = cmds.ls(sl=1)
        if not len(selected) > 0:
            QtGui.QMessageBox.information(self, "Note", "Please select the surface to align.")
        else:
            self.memoData['surface'] = selected[0]
    def scatter_action(self):
        rot = {}
        scale = {}
        sMin = {}
        scaleMinCheck = self.uiList['scaleMin_check'].isChecked()
        for dir in ['x','y','z']:
            tValue = str(self.uiList[ (dir+'Rot_input') ].text())
            rot[dir] = 0 if tValue == "" else float(tValue)
            tValue = str(self.uiList[ (dir+'Scale_input') ].text())
            scale[dir] = 1 if tValue == "" else float(tValue)
            tValue = str(self.uiList[ (dir+'ScaleMin_input') ].text())
            sMin[dir] = 0 if tValue == "" or not scaleMinCheck else float(tValue)

        pos = self.memoData["posList"]
        geoCnt = len(self.memoData['geoList'])
        # step 2: keep clear of distance of object size, clear too close point
        distanceFilterCheck = self.uiList['pointDistanceFilter_chek'].isChecked()
        validPointIdList = range(len(self.memoData["posList"]))
        if distanceFilterCheck:
            distVal = str(self.uiList['minDist_input'].text())
            distVal = 0 if distVal == "" else float(distVal)
            if distVal == 0:
                validPointIdList = self.filterPositionBy_bbox()
            else:
                validPointIdList = self.filterPositionBy_distance(distVal)
        #print validPointIdList
        # step 3: loop through each valid point, and create object
        scatterGrp = 'ScatterUI_dupGrp'
        if not cmds.objExists(scatterGrp):
            scatterGrp = cmds.group(n=scatterGrp,em=1)
        
        instanceCheck = self.uiList['instanceCheck_check'].isChecked()
        cnt = len(validPointIdList)
        for i in validPointIdList:
            each_pos = pos[i]
            newGeo =""
            # random geo from geoList
            random.seed(i+geoCnt)
            geoId = random.randint(0, geoCnt-1)
            geo = self.memoData['geoList'][geoId]
            
            if instanceCheck:
                newGeo = cmds.instance(geo)[0]
            else:
                newGeo = cmds.duplicate(geo)[0]
            cmds.parent(newGeo, scatterGrp)
            random.seed(i)
            rot_x = (random.random()-0.5)*2*rot['x']
            random.seed(i+cnt*1)
            rot_y = (random.random()-0.5)*2*rot['y']
            random.seed(i+cnt*2)
            rot_z = (random.random()-0.5)*2*rot['z']
            
            random.seed(i+cnt*3)
            s_x = random.uniform(sMin['x'],scale['x']) if scale['x']!=0 else 1
            s_y=s_x
            s_z=s_x
            if not self.uiList['scaleLink_check'].isChecked():
                random.seed(i+cnt*4)
                s_y = random.uniform(sMin['y'],scale['y']) if scale['y']!=0 else 1
                random.seed(i+cnt*5)
                s_z = random.uniform(sMin['z'],scale['z']) if scale['z']!=0 else 1
            
            cmds.xform(newGeo,t=each_pos)
            if self.uiList['alignNormal_check'].isChecked():
                link = cmds.normalConstraint(self.memoData['surface'],newGeo,aimVector=(0, 1, 0), upVector=(0,0,1), worldUpType="object", worldUpObject=self.memoData['surface'])[0]
                cmds.delete(link)
            if self.uiList['rot_check'].isChecked():
                cmds.xform(newGeo,r=1,ro=(rot_x,rot_y,rot_z))
            if self.uiList['scale_check'].isChecked():
                cmds.xform(newGeo,r=1,s=(s_x,s_y,s_z))
                
    def default_action(self, btnName):
        print("No action defined for this button: "+btnName)
    
    #=======================================
    #- UI and Mouse Interaction functions
    #=======================================
    
    def contextMenuEvent(self, event):
        menu = QtGui.QMenu(self)
        quitAction = menu.addAction("Quit")
        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == quitAction:
            self.close()
    def mouseMoveEvent(self, event):
        if (event.buttons() == QtCore.Qt.LeftButton):
            self.move(event.globalPos().x() - self.drag_position.x(),
                event.globalPos().y() - self.drag_position.y())
        event.accept()
    def mousePressEvent(self, event):
        if (event.button() == QtCore.Qt.LeftButton):
            self.drag_position = event.globalPos() - self.pos()
        event.accept()
    
    #=======================================
    #- UI and RAM content update functions
    #=======================================
    '''
    def memory_to_source_ui(self):
        # update ui once memory gets update
        txt='\n'.join([row for row in self.memoData])
        self.uiList['source_txtEdit'].setText(txt)
    
    def memory_to_result_ui(self):
        # update result ui based on memory data
        txt='\n'.join([('Converted: '+row) for row in self.memoData])
        self.uiList['result_txtEdit'].setText(txt)
    
    def source_ui_to_memory(self):
        # 1: get source content
        source_txt = str(self.uiList['source_txtEdit'].text())
        # 2: update memory
        self.memoData = [row.strip() for row in source_txt.split('\n')]
        print("Memory: update finished.")
        # 3. process memory data and update result ui
        self.memory_to_result_ui()
        print("Process: process memory finished.")
    '''
    #=======================================
    #- File Operation functions
    #=======================================
    '''
    def fileExport_action(self):
        file=str(self.uiList['filePath_input'].text())
        # open file dialog if no text input for file path
        if file == "":
            file = QtGui.QFileDialog.getSaveFileName(self, "Save File","","RAW data (*.json);;Format Txt(*{});;AllFiles(*.*)".format(self.fileType))
            if isinstance(file, (list, tuple)): # for deal with pyside case
                file = file[0]
            else:
                file = str(file) # for deal with pyqt case
        # read file if open file dialog not cancelled
        if not file == "":
            self.uiList['filePath_input'].setText(file)
            if file.endswith(self.fileType): # formated txt file
                self.writeFormatFile(self.process_rawData_to_formatData(self.memoData), file) 
            else: 
                self.writeRawFile(self.memoData, file) # raw json file
            self.uiList['result_txtEdit'].setText("File: '"+file+"' creation finished.")
    
    def fileLoad_action(self):
        file=str(self.uiList['filePath_input'].text())
        # open file dialog if no text input for file path
        if file == "":
            file = QtGui.QFileDialog.getOpenFileName(self, "Open File","","RAW data (*.json);;Format Txt(*{});;AllFiles(*.*)".format(self.fileType))
            if isinstance(file, (list, tuple)): # for deal with pyside case
                file = file[0]
            else:
                file = str(file) # for deal with pyqt case
        # read file if open file dialog not cancelled
        if not file == "":
            self.uiList['filePath_input'].setText(file)
            if file.endswith(self.fileType): # formated txt file loading
                self.memoData = self.process_formatData_to_rawData( self.readFormatFile(file) )
            else: 
                self.memoData = self.readRawFile(file) # raw json file loading
            self.memory_to_source_ui()
            self.uiList['result_txtEdit'].setText("File: '"+file+"' loading finished.")
                

    # json data functions
    def readRawFile(self,file):
        with open(file) as f:
            data = json.load(f)
        return data
    def writeRawFile(self, data, file):
        with open(file, 'w') as f:
            json.dump(data, f)
            
    # format data functions
    def readFormatFile(self, file):
        txt = ''
        with open(file) as f:
            txt = f.read()
        return txt
    def writeFormatFile(self, txt, file):    
        with open(file, 'w') as f:
            f.write(txt)
    def process_formatData_to_rawData(self, file_txt):
        # 1: prepare clean data from file Data
        file_data=[] # to implement here
        return file_data
    def process_rawData_to_formatData(self, memo_data):
        # 1: prepare memory data from file Data
        file_txt = '' # to implement here
        return file_txt
    '''
    #############################################
    # quick ui function for speed up programming
    ##############################################
    def quickMenu(self, ui_names):
        if isinstance(self, QtGui.QMainWindow):
            menubar = self.menuBar()
            for each_ui in ui_names:
                createOpt = each_ui.split(';')
                if len(createOpt) > 1:
                    uiName = createOpt[0]
                    uiLabel = createOpt[1]
                    self.uiList[uiName] = menubar.addMenu(uiLabel)
        else:
            print("Warning (QuickMenu): Only QMainWindow can have menu bar.")
        
    def quickMenuAction(self, objName, title, tip, icon, menuObj):
        self.uiList[objName] = QtGui.QAction(QtGui.QIcon(icon), title, self)        
        self.uiList[objName].setStatusTip(tip)
        menuObj.addAction(self.uiList[objName])

    def quickUI(self, ui_names, parentLayout="", opt=""):
        # quick ui for hbox, vbox, grid, form layout
        # example: vbox, hbox, grid
        # quickUI(['mod_check;QCheckBox;Good One?','mod_space;QSpaceItem;(20,20,0,0)','modAct_btn;QPushButton;Build Module','mod_input;QLineEdit'],"baseProc_QHBoxLayout")
        # example: form
        # quickUI(['mod_check@Label A;QCheckBox','mod_input@Name B;QLineEdit','mod_choice@Type C;QComboBox;(AAA,BBB)'],"baseProc_QFormLayout")
        tmp_ui_list = []
        tmp_ui_label = [] # for form layout
        form_type = 0 # for form layout
        
        if not isinstance(ui_names, list):
            print("Error (QuickUI):  require string list as ui creation input")
            return
        for each_ui in ui_names:
            # create if it is string
            if not isinstance(each_ui, str):
                if isinstance(each_ui, QtGui.QWidget) or isinstance(each_ui, QtGui.QLayout) or isinstance(each_ui, QtGui.QSpacerItem):
                    tmp_ui_list.append(each_ui)
                    tmp_ui_label.append("")
                else:
                    print("Warning (QuickUI): Currently only support string ui creation or qwidget and qlayout object insertion.")
            else:
                # get Qt elements option
                createOpt = each_ui.split(';')
                uiNameLabel = createOpt[0].split('@')
                uiName = uiNameLabel[0]
                uiLabel = uiNameLabel[1] if len(uiNameLabel) > 1 else ""
                if len(uiNameLabel) > 1:
                    form_type = 1 
                uiType = createOpt[1] if len(createOpt) > 1 else ""
                uiArgs = createOpt[2] if len(createOpt) > 2 else ""
                
                # create qt elemeent
                if uiType == "":
                    print uiType
                    print("Warning (QuickUI): uiType is empty, current ui is not created.")
                else:
                    ui_create_state = 0
                    if not uiType[0] == 'Q':
                        # if 3rd ui, it create like UI_Class.UI_Class()
                        self.uiList[uiName] = getattr(eval(uiType), uiType)()
                        tmp_ui_list.append(self.uiList[uiName])
                        ui_create_state = 1
                    else:
                        if uiArgs == "":
                            self.uiList[uiName] = getattr(QtGui, uiType)()
                            tmp_ui_list.append(self.uiList[uiName])
                            ui_create_state = 1
                        else:
                            arg_list = uiArgs.replace('(','').replace(')','').split(',')
                            if not ( uiArgs.startswith("(") and uiArgs.endswith(")") ):
                                self.uiList[uiName] = getattr(QtGui, uiType)(uiArgs)
                                tmp_ui_list.append(self.uiList[uiName])
                                ui_create_state = 1
                            else:
                                if uiType == 'QComboBox':
                                    self.uiList[uiName] = QtGui.QComboBox()
                                    self.uiList[uiName].addItems(arg_list)
                                    tmp_ui_list.append(self.uiList[uiName])
                                    ui_create_state = 1
                                elif uiType == 'QSpacerItem':
                                    policyList = ( QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Ignored)
                                    # 0 = fixed; 1 > min; 2 < max; 3 = prefered; 4 = <expanding>; 5 = expanding> Aggresive; 6=4 ignored size input
                                    # factors in fighting for space: horizontalStretch
                                    # extra space: setContentsMargins and setSpacing
                                    # ref: http://www.cnblogs.com/alleyonline/p/4903337.html
                                    arg_list = [ int(x) for x in arg_list ]
                                    self.uiList[uiName] = QtGui.QSpacerItem(arg_list[0],arg_list[1], policyList[arg_list[2]], policyList[arg_list[3]] )
                                    tmp_ui_list.append(self.uiList[uiName])
                                    ui_create_state = 1
                                else:
                                    print("Warning (QuickUI): This Object type : "+uiType+" is not implemented in quickUI function.")
                    # if ui create ok, create its label
                    if ui_create_state == 1:
                        if not uiLabel == "":
                            uiLabel = QtGui.QLabel(uiLabel) # create label widget if label not empty
                            self.uiList[uiName+'_label'] = uiLabel
                        tmp_ui_label.append(uiLabel)
                    ui_create_state = 0
        
        if parentLayout == "":
            # - has no layout input, then
            if form_type == 1:
                return (tmp_ui_list, tmp_ui_label)
            else:
                return tmp_ui_list
        else:
            # - has layout input, then
            # create parentLayout if not a layout object there
            if isinstance(parentLayout, str):
                layout_type = parentLayout.split('_')[-1]
                type_txt = "vbox"
                if layout_type == "QHBoxLayout":
                    type_txt = "hbox"
                elif layout_type == "QFormLayout":
                    type_txt = "form"
                elif layout_type == "QGridLayout":
                    type_txt = "grid"
                parentLayout = self.quickLayout(type_txt, parentLayout)
            # layout ready, add widgets
            if isinstance(parentLayout, QtGui.QBoxLayout):
                for each_ui in tmp_ui_list:
                    if isinstance(each_ui, QtGui.QWidget):
                        parentLayout.addWidget(each_ui)
                    elif isinstance(each_ui, QtGui.QSpacerItem):
                        parentLayout.addItem(each_ui)
                    elif isinstance(each_ui, QtGui.QLayout):
                        parentLayout.addLayout(each_ui)
            elif isinstance(parentLayout, QtGui.QGridLayout):
                # one row/colume operation only
                insertRow = parentLayout.rowCount()
                insertCol = parentLayout.columnCount()
                for i in range(len(tmp_ui_list)):
                    each_ui = tmp_ui_list[i]
                    x = insertRow if opt=="h" else i
                    y = i if opt=="h" else insertCol
                    if isinstance(each_ui, QtGui.QWidget):
                        parentLayout.addWidget(each_ui,x,y)
                    elif isinstance(each_ui, QtGui.QSpacerItem):
                        parentLayout.addItem(each_ui,x,y)
                    elif isinstance(each_ui, QtGui.QLayout):
                        parentLayout.addLayout(each_ui,x,y)
            elif isinstance(parentLayout, QtGui.QFormLayout):
                for i in range(len(tmp_ui_list)):
                    each_ui = tmp_ui_list[i]
                    if isinstance(each_ui, QtGui.QWidget) or isinstance(each_ui, QtGui.QLayout):
                        parentLayout.addRow(tmp_ui_label[i], each_ui)
            else:
                print("Warning (QuickUI): Currently quickUI only support vbox, hbox, form and grid layout.")
            
            return parentLayout
            
    def quickLayout(self, type, ui_name=""):
        the_layout = QtGui.QVBoxLayout()
        if type == "form":
            the_layout = QtGui.QFormLayout()
            the_layout.setLabelAlignment(QtCore.Qt.AlignLeft)
            the_layout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)    
        elif type == "grid":
            the_layout = QtGui.QGridLayout()
        elif type == "hbox":
            the_layout = QtGui.QHBoxLayout()
            the_layout.setAlignment(QtCore.Qt.AlignTop)
        else:        
            the_layout = QtGui.QVBoxLayout()
            the_layout.setAlignment(QtCore.Qt.AlignTop)
        if ui_name != "":
            self.uiList[ui_name] = the_layout
        return the_layout
        
    def quickSplitUI(self, name, part_list, type):
        split_type = QtCore.Qt.Horizontal
        if type == 'v':
            split_type = QtCore.Qt.Vertical
        self.uiList[name]=QtGui.QSplitter(split_type)
        
        for each_part in part_list:
            if isinstance(each_part, QtGui.QWidget):
                self.uiList[name].addWidget(each_part)
            else:
                tmp_holder = QtGui.QWidget()
                tmp_holder.setLayout(each_part)
                self.uiList[name].addWidget(tmp_holder)
        return self.uiList[name]

#############################################
# window instance creation
##############################################
# If you want to be able to Keep only one copy of windows ui, use code below
single_ScatterUI = None   
def main():
    parentWin = None
    app = None
    if deskMode == 0:
        if qtMode == 0:
            # ==== for pyside ====
            parentWin = shiboken.wrapInstance(long(mui.MQtUtil.mainWindow()), QtGui.QWidget)
        elif qtMode == 1:
            # ==== for PyQt====
            parentWin = sip.wrapinstance(long(mui.MQtUtil.mainWindow()), QtCore.QObject)
    if deskMode == 1:
        app = QtGui.QApplication(sys.argv)
    
    # single UI window code, so no more duplicate window instance when run this function
    global single_ScatterUI
    if single_ScatterUI is None:
        single_ScatterUI = ScatterUI(parentWin) # extra note: in Maya () for no parent; (parentWin,0) for extra mode input
    single_ScatterUI.show()
    
    if deskMode == 1:
        sys.exit(app.exec_())
    
    # example: show ui stored
    print(single_ScatterUI.uiList.keys())
    return single_ScatterUI
    
# If you want to be able to load multiple windows of the same ui, use code below
'''
def main():
    parentWin = None
    if deskMode == 0:
        if qtMode == 0:
            # ==== for pyside ====
            parentWin = shiboken.wrapInstance(long(mui.MQtUtil.mainWindow()), QtGui.QWidget)
        elif qtMode == 1:
            # ==== for PyQt====
            parentWin = sip.wrapinstance(long(mui.MQtUtil.mainWindow()), QtCore.QObject)
            
    ui = ScatterUI(parentWin) # extra note: in Maya () for no parent; (parentWin,0) for extra mode input
    ui.show()
    # example: show ui stored
    print(ui.uiList.keys())
    return ui
'''
if __name__ == "__main__":
    main()

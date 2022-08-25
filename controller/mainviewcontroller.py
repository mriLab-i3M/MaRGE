"""
Main View Controller

@author:    Yolanda Vives

@status:    Sets up the main view, its views and controllers
@todo:

"""
from PyQt5.QtWidgets import  QMessageBox,  QFileDialog,  QTextEdit, QLabel, QWidget
from PyQt5 import QtCore
from PyQt5.QtCore import *
from PyQt5.uic import loadUiType, loadUi
from PyQt5 import QtGui
from PyQt5.QtGui import QIcon
import pyqtgraph.exporters
from functools import partial
import os
import sys
import experiment as ex
from scipy.io import savemat
import csv
from sessionmodes import defaultsessions
from manager.datamanager import DataManager
from datetime import date,  datetime 
from globalvars import StyleSheets as style
from stream import EmittingStream
from local_config import ip_address
import cgitb
cgitb.enable(format = 'text')
import pdb
import numpy as np
import imageio
from plotview.spectrumplot import Spectrum3DPlot

st = pdb.set_trace

# Import sequences
from seq.sequences import defaultsequences
from seq.localizer import Localizer

# Import controllers
# from controller.acquisitioncontroller import AcquisitionController                                  # Acquisition
from controller.batchcontroller import BatchController                                              # Batches
from controller.sequencecontroller import SequenceList                                              # Sequence list

MainWindow_Form, MainWindow_Base = loadUiType('ui/mainview.ui')

class MainViewController(MainWindow_Form, MainWindow_Base):
    """
    MainViewController Class
    """
    onSequenceChanged = pyqtSignal(str)
    iterativeRun = False

    def __init__(self, session, parent=None):
        super(MainViewController, self).__init__(parent)
        self.ui = loadUi('ui/mainview.ui')
        self.setupUi(self)
        self.styleSheet = style.breezeLight
        self.setupStylesheet(self.styleSheet)
        
        # Initialisation of sequence list
        self.session = session
        dict = vars(defaultsessions[self.session])
        self.sequencelist = SequenceList(self)
        self.sequencelist.setCurrentIndex(0)
        self.sequencelist.currentIndexChanged.connect(self.selectionChanged)
        self.layout_operations.addWidget(self.sequencelist)
        self.sequence = self.sequencelist.currentText()
        self.session_label.setText(dict["name_code"])
                
        # Console
        self.cons = self.generateConsole('')
        self.layout_output.addWidget(self.cons)
        sys.stdout = EmittingStream(textWritten=self.onUpdateText)
        sys.stderr = EmittingStream(textWritten=self.onUpdateText)

        # Initialize multithreading
        self.threadpool = QThreadPool()
        print("Multithreading with maximum %d threads \n" % self.threadpool.maxThreadCount())

        # First plot
        self.firstPlot()

        # Initialisation of acquisition controller
        # self.acqCtrl = AcquisitionController(self, self.session, self.sequencelist)

        # Connection to the server
        self.ip = ip_address
        
        # XNAT upload
        self.xnat_active = 'FALSE'
        
        # Toolbar Actions
        self.action_gpaInit.triggered.connect(self.initgpa)
        self.action_autocalibration.triggered.connect(self.autocalibration)
        self.action_changeappearance.triggered.connect(self.changeAppearanceSlot)
        self.action_acquire.triggered.connect(self.startAcquisition)
        self.action_close.triggered.connect(self.close)
        self.action_exportfigure.triggered.connect(self.export_figure)
        self.action_viewsequence.triggered.connect(self.startSequencePlot)
        self.action_batch.triggered.connect(self.batch_system)
        self.action_XNATupload.triggered.connect(self.xnat)
        self.action_run_localizer.triggered.connect(self.startLocalizer)
        self.action_iterate.triggered.connect(self.iterate)

        # Menu Actions
        self.actionLarmor.triggered.connect(self.runLarmor)
        self.actionNoise.triggered.connect(self.runNoise)
        self.actionRabi_Flop.triggered.connect(self.runRabiFlop)
        self.actionCPMG.triggered.connect(self.runCPMG)
        self.actionInversion_Recovery.triggered.connect(self.runInversionRecovery)
        self.actionAutocalibration.triggered.connect(self.autocalibration)
        self.actionLoad_parameters.triggered.connect(self.load_parameters)
        self.actionSave_parameters.triggered.connect(self.save_parameters)
        self.actionRun_sequence.triggered.connect(self.startAcquisition)
        self.actionPlot_sequence.triggered.connect(self.startSequencePlot)
        self.actionInit_GPA.triggered.connect(self.initgpa)
        self.actionLocalizer.triggered.connect(self.startLocalizer)
        self.actionNew_sesion.triggered.connect(self.change_session)

        self.seqName = self.sequencelist.getCurrentSequence()
        defaultsequences[self.seqName].sequenceInfo()

        self.showMaximized()

    def iterate(self):
        if self.iterativeRun == False:
            self.iterativeRun = True
            self.action_iterate.setIcon(QIcon('/home/physioMRI/git_repos/PhysioMRI_GUI/resources/icons/refresh-outline.svg') )
            self.action_iterate.setToolTip('Switch to single run')
            self.action_iterate.setText('Iterative run')
        else:
            self.iterativeRun = False
            self.action_iterate.setIcon(QIcon('/home/physioMRI/git_repos/PhysioMRI_GUI/resources/icons/refresh.svg') )
            self.action_iterate.setToolTip('Switch to iterative run')
            self.action_iterate.setText('Single run')

    def startAcquisition(self, seqName=None):
        """
        @author: J.M. Algarín, MRILab, i3M, CSIC, Valencia
        @email: josalggui@i3m.upv.es
        @Summary: run selected sequence
        """
        print('Start sequence')

        # Delete previous plots
        self.clearPlotviewLayout()

        # Load sequence name
        if seqName==None or seqName==False:
            self.seqName = self.sequencelist.getCurrentSequence()
        else:
            self.seqName = seqName

        # Save sequence list into the current sequence, just in case you need to do sweep
        defaultsequences[self.seqName].sequenceList = defaultsequences

        # Save input parameters
        defaultsequences[self.seqName].saveParams()

        # Create and execute selected sequence
        defaultsequences[self.seqName].sequenceRun(0)

        # Do sequence analysis and acquire de plots
        out = defaultsequences[self.seqName].sequenceAnalysis()

        # Create label with rawdata name
        fileName = defaultsequences[self.seqName].mapVals['fileName']
        self.label = QLabel(fileName)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setStyleSheet("background-color: black;color: white")
        self.plotview_layout.addWidget(self.label)

        # Add plots to the plotview_layout
        for item in out:
            self.plotview_layout.addWidget(item)

        # self.parent.onSequenceChanged.emit(self.parent.sequence)
        print('End sequence')

    def startSequencePlot(self):
        """
        @author: J.M. Algarín, MRILab, i3M, CSIC, Valencia
        @email: josalggui@i3m.upv.es
        @Summary: plot sequence instructions
        """
        # Delete previous plots
        self.clearPlotviewLayout()

        # Load sequence name
        self.seqName = self.sequencelist.getCurrentSequence()

        # Create sequence to plot
        print('Plot sequence')
        defaultsequences[self.seqName].sequenceRun(1)  # Run sequence only for plot

        # Get sequence to plot
        out = defaultsequences[self.seqName].sequencePlot()  # Plot results

        # Create plots
        n = 0
        plot = []
        for item in out:
            plot.append(SpectrumPlotSeq(item[0], item[1], item[2], 'Time (ms)', 'Amplitude (a.u.)', item[3]))
            if n > 0: plot[n].plotitem.setXLink(plot[0].plotitem)
            n += 1
        for n in range(4):
            self.plotview_layout.addWidget(plot[n])

    def startLocalizer(self):
        """
        @author: J.M. Algarín, MRILab, i3M, CSIC, Valencia
        @email: josalggui@i3m.upv.es
        @Summary: run localizer
        """

        print('Start localizer')

        # Delete previous localizer
        self.clearLocalizerLayout()

        # Set localizer sequence to RARE
        localizer = Localizer()

        # Load default parameters
        localizer.loadParams()
        localizer.mapVals['seqName'] = 'Localizer'
        localizer.mapNmspc['seqName'] = 'LocalizerInfo'
        localizer.saveParams()

        # Add parent to localizer so it can update sequences parameters
        localizer.parent = self

        # Add sequences to localizer
        localizer.sequencelist = defaultsequences

        # Create and execute selected sequence
        localizer.sequenceRunProjections(0)

        # Do sequence analysis and acquire de plots
        out = localizer.sequenceAnalysis()

        # Create label with rawdata name
        fileName = localizer.mapVals['fileName']
        self.label = QLabel(fileName)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setStyleSheet("background-color: black;color: white")
        self.localizer_layout.addWidget(self.label)

        # Add plots to the localizer_layout
        self.localizer_layout.addWidget(out[0])

    def autocalibration(self):
        self.clearPlotviewLayout()

        # Get Larmor frequency
        print("Larmor frequency...")
        larmorSeq = defaultsequences['Larmor']
        larmorSeq.sequenceRun()
        outLarmor = larmorSeq.sequenceAnalysis()
        for seq in defaultsequences:
            defaultsequences[seq].mapVals['larmorFreq'] = larmorSeq.mapVals['larmorFreqCal']

        # Get noise
        noiseSeq = defaultsequences['Noise']
        noiseSeq.sequenceRun()
        outNoise = noiseSeq.sequenceAnalysis()

        # Get Rabi flops
        rabiSeq = defaultsequences['RabiFlops']
        rabiSeq.sequenceRun()
        outRabi = rabiSeq.sequenceAnalysis()

        # Spectrum
        # Create label with rawdata name
        fileName = larmorSeq.mapVals['fileName']
        self.label = QLabel(fileName)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setStyleSheet("background-color: black;color: white")
        self.plotview_layout.addWidget(self.label)

        # Add plots to the plotview_layout
        item = outLarmor[1]
        selfplotview_layout.addWidget(item)

        # Noise
        # Create label with rawdata name
        fileName = noiseSeq.mapVals['fileName']
        self.label = QLabel(fileName)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setStyleSheet("background-color: black;color: white")
        self.plotview_layout.addWidget(self.label)

        # Add plots to the plotview_layout
        for item in outNoise:
            self.plotview_layout.addWidget(item)

        # Rabi
        # Create label with rawdata name
        fileName = rabiSeq.mapVals['fileName']
        self.label = QLabel(fileName)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setStyleSheet("background-color: black;color: white")
        self.plotview_layout.addWidget(self.label)

        # Add plots to the plotview_layout
        item = outRabi[0]
        self.plotview_layout.addWidget(item)

        self.onSequenceChanged.emit(self.sequence)

    def runLarmor(self):
        self.startAcquisition(seqName="Larmor")

    def runNoise(self):
        self.startAcquisition(seqName="Noise")

    def runRabiFlop(self):
        self.startAcquisition(seqName="RabiFlops")

    def runCPMG(self):
        self.startAcquisition(seqName="CPMG")

    def runInversionRecovery(self):
        self.startAcquisition(seqName="InversionRecovery")

    def lines_that_start_with(self, str, f):
        return [line for line in f if line.startswith(str)]
    
    # @staticmethod
    def generateConsole(self, text):
        con = QTextEdit()
        con.setText(text)
        return con

    def onUpdateText(self, text):
        cursor = self.cons.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.cons.setTextCursor(cursor)
        self.cons.ensureCursorVisible()
    
    def __del__(self):
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

    def closeEvent(self, event):
        """Shuts down application on close."""
        # Return stdout to defaults.
        sys.stdout = sys.__stdout__
        os.system('ssh root@192.168.1.101 "killall marcos_server"') # Kill marcos server
        print('GUI closed successfully!')
        super().closeEvent(event)
    
    @pyqtSlot(bool)
    def changeAppearanceSlot(self) -> None:
        """
        Slot function to switch application appearance
        @return:
        """
        if self.styleSheet is style.breezeDark:
            self.setupStylesheet(style.breezeLight)
        else:
            self.setupStylesheet(style.breezeDark)

    def close(self):
        os.system('ssh root@192.168.1.101 "killall marcos_server"')
        print('GUI closed successfully!')
        sys.exit()


    def setupStylesheet(self, style) -> None:
        """
        Setup application stylesheet
        @param style:   Stylesheet to be set
        @return:        None
        """
        self.styleSheet = style
        file = QFile(style)
        file.open(QFile.ReadOnly | QFile.Text)
        stream = QTextStream(file)
        stylesheet = stream.readAll()
        self.setStyleSheet(stylesheet)  

    def selectionChanged(self,item):
        self.sequence = self.sequencelist.currentText()
        self.onSequenceChanged.emit(self.sequence)
        self.action_acquire.setEnabled(True)
        # self.clearPlotviewLayout()
    
    def clearPlotviewLayout(self) -> None:
        """
        Clear the plot layout
        @return:    None
        """
        for i in reversed(range(self.plotview_layout.count())):
            self.plotview_layout.itemAt(i).widget().setParent(None)

    def clearLocalizerLayout(self) -> None:
        """
        Clear the localizer layout
        @return:    None
        """
        for i in reversed(range(self.localizer_layout.count())):
            self.localizer_layout.itemAt(i).widget().setParent(None)
    
    def save_data(self):
        
        dataobject: DataManager = DataManager(self.data_avg, self.sequence.lo_freq, len(self.data_avg), [self.sequence.n_rd, self.sequence.n_ph, self.sequence.n_sl], self.sequence.BW)
        dict1=vars(defaultsessions[self.session])
        dict2 = vars(self.sequence)
        dict = self.merge_two_dicts(dict1, dict2)
        dt = datetime.now()
        dt_string = dt.strftime("%d-%m-%Y_%H:%M")
        dt2 = date.today()
        dt2_string = dt2.strftime("%d-%m-%Y")
        dict["rawdata"] = self.rxd
        dict["fft"] = dataobject.f_fftData
        if not os.path.exists('experiments/acquisitions/%s' % (dt2_string)):
            os.makedirs('experiments/acquisitions/%s' % (dt2_string))
            
        if not os.path.exists('experiments/acquisitions/%s/%s' % (dt2_string, dt_string)):
            os.makedirs('experiments/acquisitions/%s/%s' % (dt2_string, dt_string)) 
            
        if not os.path.exists('/media/physiomri/TOSHIBA\ EXT/experiments/acquisitions/%s' % (dt2_string)):
            os.makedirs('/media/physiomri/TOSHIBA\ EXT/%s'% (dt2_string) )
            
        if not os.path.exists('/media/physiomri/TOSHIBA\ EXT/experiments/acquisitions/%s/%s' % (dt2_string, dt_string)):
            os.makedirs('/media/physiomri/TOSHIBA\ EXT/%s/%s'% (dt2_string, dt_string) )   
            
        savemat("experiments/acquisitions/%s/%s/%s.mat" % (dt2_string, dt_string, self.sequence), dict)
        savemat("/media/physiomri/TOSHIBA\ EXT/%s/%s/%s.mat" % (dt2_string, dt_string, self.sequence), dict)
        
        self.messages("Data saved")

        if hasattr(self.parent, 'f_plotview'):
            exporter1 = pyqtgraph.exporters.ImageExporter(self.f_plotview.scene())
            exporter1.export("experiments/acquisitions/%s/%s/Freq%s.png" % (dt2_string, dt_string, self.sequence))
        if hasattr(self.parent, 't_plotview'):
            exporter2 = pyqtgraph.exporters.ImageExporter(self.t_plotview.scene())
            exporter2.export("experiments/acquisitions/%s/%s/Temp%s.png" % (dt2_string, dt_string, self.sequence))

        from controller.WorkerXNAT import Worker
        
        if self.xnat_active == 'TRUE':
            # Step 2: Create a QThread object
            self.thread = QThread()
            # Step 3: Create a worker object
            self.worker = Worker()
            # Step 4: Move worker to the thread
            self.worker.moveToThread(self.thread)
            # Step 5: Connect signals and slots
            self.thread.started.connect(partial(self.worker.run, 'experiments/acquisitions/%s/%s' % (dt2_string, dt_string)))
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)
            
            # Step 6: Start the thread
            self.thread.start()

    def export_figure(self):
        
        dt = datetime.now()
        dt_string = dt.strftime("%d-%m-%Y_%H:%M")
        dt2 = date.today()
        dt2_string = dt2.strftime("%d-%m-%Y")

        if not os.path.exists('experiments/acquisitions/%s' % (dt2_string)):
            os.makedirs('experiments/acquisitions/%s' % (dt2_string))    
        if not os.path.exists('experiments/acquisitions/%s/%s' % (dt2_string, dt_string)):
            os.makedirs('experiments/acquisitions/%s/%s' % (dt2_string, dt_string)) 
                    
        exporter1 = pyqtgraph.exporters.ImageExporter(self.f_plotview.scene())
        exporter1.export("experiments/acquisitions/%s/%s/Freq%s.png" % (dt2_string, dt_string, self.sequence))
        exporter2 = pyqtgraph.exporters.ImageExporter(self.t_plotview.scene())
        exporter2.export("experiments/acquisitions/%s/%s/Temp%s.png" % (dt2_string, dt_string, self.sequence))
        
        self.messages("Figures saved")
   
    def merge_two_dicts(self, x, y):
        z = x.copy()   # start with keys and values of x
        z.update(y)    # modifies z with keys and values of y
        return z
   
    def load_parameters(self):
    
        file_name, _ = QFileDialog.getOpenFileName(self, 'Open Parameters File', "experiments/parameterisations/")

        seq = defaultsequences[self.sequence]
        mapValsOld = seq.mapVals
        with open(file_name, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for l in reader:
                mapValsNew = l

        seq.mapVals = {}

        # Get key for corresponding modified parameter
        for key in seq.mapKeys:
            dataLen = seq.mapLen[key]
            valOld = mapValsOld[key]
            valNew = mapValsNew[key]
            valNew = valNew.replace('[', '')
            valNew = valNew.replace(']', '')
            valNew = valNew.split(',')
            if type(valOld) == str:
                valOld = [valOld]
            elif dataLen == 1:
                valOld = [valOld]
            dataType = type(valOld[0])

            inputNum = []
            for ii in range(dataLen):
                if dataType == float or dataType == np.float64:
                    try:
                        inputNum.append(float(valNew[ii]))
                    except:
                        inputNum.append(float(valOld[ii]))
                elif dataType == int:
                    try:
                        inputNum.append(int(valNew[ii]))
                    except:
                        inputNum.append(int(valOld[ii]))
                else:
                    try:
                        inputNum.append(str(valNew[0]))
                        break
                    except:
                        inputNum.append(str(valOld[0]))
                        break
            if dataType == str:
                seq.mapVals[key] = inputNum[0]
            else:
                if dataLen == 1:  # Save value into mapVals
                    seq.mapVals[key] = inputNum[0]
                else:
                    seq.mapVals[key] = inputNum

        self.onSequenceChanged.emit(self.sequence)
        self.messages("Parameters of %s sequence loaded" %(self.sequence))

    def save_parameters(self):
        
        dt = datetime.now()
        dt_string = dt.strftime("%Y.%m.%d.%H.%M.%S.%f")[:-3]
        seq = defaultsequences[self.sequence]

        # Save csv with input parameters
        if not os.path.exists('experiments/parameterisations'):
            os.makedirs('experiments/parameterisations')
        with open('experiments/parameterisations/%s.%s.csv' % (seq.mapNmspc['seqName'], dt_string), 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=seq.mapKeys)
            writer.writeheader()
            mapVals = {}
            for key in seq.mapKeys:  # take only the inputs from mapVals
                mapVals[key] = seq.mapVals[key]
            writer.writerows([seq.mapNmspc, mapVals])

        self.messages("Parameters of %s sequence saved" %(self.sequence))
        
    def plot_sequence(self):
        
        plotSeq=1
        self.sequence = defaultsequences[self.sequencelist.getCurrentSequence()]
        self.seqName = self.sequence.mapVals['seqName']
        defaultsequences[self.seqName].sequenceRun(plotSeq=plotSeq)
        
    def messages(self, text):
        
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(text)
        msg.exec();
        
    def calibrate(self):
        calibrationApp = CalibrationController(parent=self)
        calibrationApp.show()
        
    def initgpa(self):
        expt = ex.Experiment(init_gpa=True)
        expt.add_flodict({
            'grad_vx': (np.array([100]), np.array([0])),
        })
        expt.run()
        expt.__del__()
        print("GPA init done!")

    def batch_system(self):
        batchW = BatchController(self, self.sequencelist)
        batchW.show()

    def xnat(self):
        
        if self.xnat_active == 'TRUE':
            self.xnat_active = 'FALSE'
            self.action_XNATupload.setIcon(QIcon('/home/physioMRI/git_repos/PhysioMRI_GUI/resources/icons/upload-outline.svg') )
            self.action_XNATupload.setToolTip('Activate XNAT upload')
        else:
            self.xnat_active = 'TRUE'
            self.action_XNATupload.setIcon(QIcon('/home/physioMRI/git_repos/PhysioMRI_GUI/resources/icons/upload.svg') )
            self.action_XNATupload.setToolTip('Deactivate XNAT upload')
            
    def change_session(self):
        from controller.sessionviewer_controller import SessionViewerController
        sessionW = SessionViewerController(self.session)
        sessionW.show()
        self.hide()

    def firstPlot(self):
        """
        @author: J.M. Algarín, MRILab, i3M, CSIC, Valencia
        @email: josalggui@i3m.upv.es
        @Summary: show the initial figure
        """
        logo = imageio.imread("resources/images/logo.png")
        logo = np.flipud(logo)
        self.clearPlotviewLayout()
        welcome = Spectrum3DPlot(logo.transpose([1, 0, 2]),
                                 title='Institute for Instrimentation in Molecular Imaging (i3M)')
        welcome.hideAxis('bottom')
        welcome.hideAxis('left')
        welcome.showHistogram(False)
        welcomeWidget = welcome.getImageWidget()
        self.plotview_layout.addWidget(welcomeWidget)

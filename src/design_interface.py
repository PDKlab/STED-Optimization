
from PyQt5 import QtCore, QtWidgets

SX, SY = 480, 350
MARGINS = 10


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        self.MainWindow = MainWindow
        self.MainWindow.setObjectName("MainWindow")
        self.MainWindow.setWindowModality(QtCore.Qt.NonModal)
        self.MainWindow.resize(SX, SY)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.MainWindow.sizePolicy().hasHeightForWidth())
        self.MainWindow.setSizePolicy(sizePolicy)
        self.MainWindow.setMinimumSize(QtCore.QSize(SX, SY))
        self.MainWindow.setMaximumSize(QtCore.QSize(SX, SY))
        self.MainWindow.setWindowOpacity(1.0)
        self.MainWindow.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.MainWindow.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
        self.MainWindow.setDocumentMode(False)
        self.MainWindow.setTabShape(QtWidgets.QTabWidget.Rounded)
        self.MainWindow.setDockOptions(QtWidgets.QMainWindow.AllowTabbedDocks | QtWidgets.QMainWindow.AnimatedDocks)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # OUTPUT DIRECTORY BOX
        self.outputBox = QtWidgets.QGroupBox(self.centralwidget)
        self.outputBox.setGeometry(QtCore.QRect(MARGINS, 0, SX - 2 * MARGINS, 150))
        self.outputBox.setObjectName("outputbox")
        self.outputBoxGrid = QtWidgets.QGridLayout()
        self.outputBoxGrid.maximumSize()
        self.dir_button = QtWidgets.QToolButton(self.outputBox)
        self.dir_button.setFixedWidth(90)
        self.dir_button.setCheckable(False)
        self.dir_button.setChecked(False)
        self.dir_label = QtWidgets.QLineEdit(self.config["output"]["saving_dir"], self.outputBox)
        self.dir_label.setStyleSheet("background-color: white;")
        self.dir_label.setFixedWidth(325)
        self.folder_label = QtWidgets.QLineEdit(self.config["output"]["folder"], self.outputBox)
        self.folder_label.setStyleSheet("background-color: white")
        self.folder_label.setFixedWidth(325)
        self.prev_dir_button = QtWidgets.QToolButton(self.outputBox)
        self.prev_dir_button.setCheckable(False)
        self.prev_dir_button.setChecked(False)
        self.prev_dir_label = QtWidgets.QLabel("")
        self.outputBoxGrid.addWidget(self.dir_button, 0, 0, 1, 2)
        self.outputBoxGrid.addWidget(self.dir_label, 0, 1, 1, 2)
        self.outputBoxGrid.addWidget(QtWidgets.QLabel("Output Name :"), 1, 0, 1, 2)
        self.outputBoxGrid.addWidget(self.folder_label, 1, 1, 1, 2)
        self.outputBoxGrid.addWidget(QtWidgets.QLabel("Previous :"), 2, 0)
        self.outputBoxGrid.addWidget(self.prev_dir_label, 2, 1)
        self.outputBoxGrid.addWidget(self.prev_dir_button, 2, 2)
        self.outputBox.setLayout(self.outputBoxGrid)

        # PARAMETERS AND OBJECTIVES BOX
        self.paramObjBox = QtWidgets.QGroupBox(self.centralwidget)
        self.paramObjBox.setGeometry(QtCore.QRect(MARGINS, 150, SX - 2 * MARGINS, 150))
        self.paramObjBox.setObjectName("paramobjbox")
        self.poGrid = QtWidgets.QGridLayout(self.paramObjBox)
        self.list_params = QtWidgets.QListWidget()
        self.list_params.addItems([key for key in self.config["params_space"]])
        self.list_params.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)  # Multiple selections
        self.poGrid.addWidget(self.list_params, 0, 0)
        self.list_objs = QtWidgets.QListWidget()
        self.list_objs.addItems([key for key in self.config["objectives"]])
        self.list_objs.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.poGrid.addWidget(self.list_objs, 0, 1)

        # START, MICROSCOPE CONFIGURATION AND ADVANCED BUTTON
        self.buttonBox = QtWidgets.QGroupBox(self.centralwidget)
        self.buttonBox.setGeometry(QtCore.QRect(MARGINS, 300, SX - 2 * MARGINS, 30))
        self.adv_button = QtWidgets.QToolButton(self.buttonBox)
        self.adv_button.setGeometry(QtCore.QRect(10, (30 - 20) / 2 - 1, 240, 20))
        self.adv_button.setCheckable(False)
        self.adv_button.setChecked(False)
        self.microscope_button = QtWidgets.QToolButton(self.buttonBox)
        self.microscope_button.setGeometry(QtCore.QRect(250, (30 - 20) / 2 - 1, 100, 20))
        self.microscope_button.setCheckable(False)
        self.microscope_button.setChecked(False)
        self.start_button = QtWidgets.QToolButton(self.buttonBox)
        self.start_button.setGeometry(QtCore.QRect(460 - 100 - 10, (30 - 20) / 2 - 1, 100, 20))
        self.start_button.setCheckable(False)
        self.start_button.setChecked(False)

        # MENU BAR
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar=QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, SY, SX, 52))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar=QtWidgets.QStatusBar(MainWindow)
        sizePolicy=QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.statusbar.sizePolicy().hasHeightForWidth())
        self.statusbar.setSizePolicy(sizePolicy)
        self.statusbar.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.statusbar.setAutoFillBackground(False)
        self.statusbar.setSizeGripEnabled(False)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate=QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "STED Optimization"))
        self.outputBox.setTitle(_translate("MainWindow", "Output directory"))
        self.paramObjBox.setTitle(_translate("MainWindow", "Parameters and Objectives"))
        self.dir_button.setText(_translate("MainWindow", "Browse"))
        self.prev_dir_button.setText(_translate("MainWindow", "Browse"))
        self.adv_button.setText(_translate("MainWindow", "Show advanced parameters"))
        self.microscope_button.setText(_translate("MainWindow", "Microscope config"))
        self.start_button.setText(_translate("MainWindow", "Start Optimization"))

    def set_adv_params_space(self):
        """ This function sets the layout for the advanced parameters contained
        in the params space
        """
        g = QtWidgets.QGridLayout()
        c = self.config["params_space"]
        for i, key in enumerate(c):
            g.addWidget(QtWidgets.QLabel(key), i, 0)
            qle=QtWidgets.QLineEdit(str(c[key][0]), self.outputBox)
            qle.setFixedWidth(40)
            g.addWidget(qle, i, 1)
            qle=QtWidgets.QLineEdit(str(c[key][1]), self.outputBox)
            qle.setFixedWidth(40)
            g.addWidget(qle, i, 2)
            qle=QtWidgets.QLineEdit(str(c[key][2]), self.outputBox)
            qle.setFixedWidth(40)
            g.addWidget(qle, i, 3)
        return g

    def set_adv_nobj_space(self):
        """ This function sets the layout for the noise uperbound contained in the
        advanced parameters
        """
        g = QtWidgets.QGridLayout()
        c = self.config["noise_ub_objectives"]
        for i, key in enumerate(c):
            g.addWidget(QtWidgets.QLabel(key), i, 0)
            qle=QtWidgets.QLineEdit(str(c[key]), self.outputBox)
            g.addWidget(qle, i, 1)
        return g


class Ui_advancedWindow(object):
    def setup_adv(self, MainWindow):
        self.MainWindow = MainWindow
        self.MainWindow.setObjectName("MainWindow")
        self.MainWindow.setWindowModality(QtCore.Qt.NonModal)
        self.MainWindow.resize(700, 625)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.MainWindow.sizePolicy().hasHeightForWidth())
        self.MainWindow.setSizePolicy(sizePolicy)
        self.MainWindow.setMinimumSize(QtCore.QSize(700, 625))
        self.MainWindow.setMaximumSize(QtCore.QSize(700, 625))
        self.MainWindow.setWindowOpacity(1.0)
        self.MainWindow.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.MainWindow.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
        self.MainWindow.setDocumentMode(False)
        self.MainWindow.setTabShape(QtWidgets.QTabWidget.Rounded)
        self.MainWindow.setDockOptions(QtWidgets.QMainWindow.AllowTabbedDocks | QtWidgets.QMainWindow.AnimatedDocks)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # PARAMETER SPACE
        self.pSpaceBox = QtWidgets.QGroupBox(self.centralwidget)
        self.pSpaceBox.setGeometry(QtCore.QRect(0, 0, 350, 200))
        self.pSpaceGrid = QtWidgets.QGridLayout(self.pSpaceBox)
        self.pSpaceGrid.maximumSize()
        self.pSpaceLayout = self.set_params_space()
        self.pSpaceGrid.addLayout(self.pSpaceLayout, 0, 0)

        # PARAMETER SET
        self.pSetBox = QtWidgets.QGroupBox(self.centralwidget)
        self.pSetBox.setGeometry(QtCore.QRect(0, 200, 350, 150))
        self.pSetGrid = QtWidgets.QGridLayout(self.pSetBox)
        self.pSetGrid.maximumSize()
        self.pSetLayout = self.set_single_qle(self.parent.config["params_set"], self.pSetBox)
        self.pSetGrid.addLayout(self.pSetLayout, 0, 0)

        # OBJECTIVES VALUES
        self.oValuesBox = QtWidgets.QGroupBox(self.centralwidget)
        self.oValuesBox.setGeometry(QtCore.QRect(350, 0, 350, 125))
        self.oValuesGrid = QtWidgets.QGridLayout(self.oValuesBox)
        self.oValuesGrid.maximumSize()
        self.oValuesLayout = self.set_single_qle(self.parent.config["objectives_values"], self.oValuesBox)
        self.oValuesGrid.addLayout(self.oValuesLayout, 0, 0)

        # NOISE UPPER BOUND OBJECTIVES
        self.nUbBox = QtWidgets.QGroupBox(self.centralwidget)
        self.nUbBox.setGeometry(QtCore.QRect(350, 125, 350, 225))
        self.nUbGrid = QtWidgets.QGridLayout(self.nUbBox)
        self.nUbGrid.maximumSize()
        self.nUbLayout = self.set_single_qle(self.parent.config["noise_ub_objectives"], self.nUbBox)
        self.nUbGrid.addLayout(self.nUbLayout, 0, 0)

        # QUALITYNETWORK
        self.qNetworkBox = QtWidgets.QGroupBox(self.centralwidget)
        self.qNetworkBox.setGeometry(QtCore.QRect(0, 350, 700, 75))
        self.qNetworkGrid = QtWidgets.QGridLayout(self.qNetworkBox)
        self.qNetworkGrid.maximumSize()
        self.qNetworkLayout = self.set_network_qle(self.parent.config["autoquality"], self.qNetworkBox)
        self.qNetworkGrid.addLayout(self.qNetworkLayout, 0, 0)

        # PREFNETWORK
        self.pNetworkBox = QtWidgets.QGroupBox(self.centralwidget)
        self.pNetworkBox.setGeometry(QtCore.QRect(0, 425, 700, 75))
        self.pNetworkGrid = QtWidgets.QGridLayout(self.pNetworkBox)
        self.pNetworkGrid.maximumSize()
        self.pNetworkLayout = self.set_network_qle(self.parent.config["autopref"], self.pNetworkBox)
        self.pNetworkGrid.addLayout(self.pNetworkLayout, 0, 0)

        # WITHTIME AND PSEUDOPOINTS
        self.wpBox = QtWidgets.QGroupBox(self.centralwidget)
        self.wpBox.setGeometry(QtCore.QRect(0, 500, 700, 75))
        self.wpGrid = QtWidgets.QGridLayout(self.wpBox)
        self.wpGrid.maximumSize()
        self.wpLayout = self.set_wp()
        self.wpGrid.addLayout(self.wpLayout, 0, 0)

        # UPDATE CONFIGURATION AND CLOSE WINDOW
        self.update_button = QtWidgets.QToolButton(self.centralwidget)
        self.update_button.setGeometry(QtCore.QRect(700 - 150, 575, 147, 25))

        # MENU BAR
        self.MainWindow.setCentralWidget(self.centralwidget)
        self.menubar=QtWidgets.QMenuBar(self.MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, SX, 52))
        self.menubar.setObjectName("menubar")
        self.MainWindow.setMenuBar(self.menubar)
        self.statusbar=QtWidgets.QStatusBar(self.MainWindow)
        sizePolicy=QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.statusbar.sizePolicy().hasHeightForWidth())
        self.statusbar.setSizePolicy(sizePolicy)
        self.statusbar.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.statusbar.setAutoFillBackground(False)
        self.statusbar.setSizeGripEnabled(False)
        self.statusbar.setObjectName("statusbar")
        self.MainWindow.setStatusBar(self.statusbar)
        self.retranslateUi(self.MainWindow)
        QtCore.QMetaObject.connectSlotsByName(self.MainWindow)

    def set_params_space(self):
        """ This function sets the layout for the advanced parameters contained
        in the params space
        """
        g = QtWidgets.QGridLayout()
        c = self.parent.config["params_space"]
        i = 0
        for j, l in enumerate(["", "min", "max", "inc."]):
            g.addWidget(QtWidgets.QLabel(l), i, j)
        i += 1
        for key in c:
            g.addWidget(QtWidgets.QLabel(key), i, 0)
            qle=QtWidgets.QLineEdit(str(c[key][0]), self.pSpaceBox)
            qle.setFixedHeight(20)
            g.addWidget(qle, i, 1)
            qle=QtWidgets.QLineEdit(str(c[key][1]), self.pSpaceBox)
            qle.setFixedHeight(20)
            g.addWidget(qle, i, 2)
            qle=QtWidgets.QLineEdit(str(c[key][2]), self.pSpaceBox)
            qle.setFixedHeight(20)
            g.addWidget(qle, i, 3)
            i += 1
        return g

    def set_single_qle(self, config, parent):
        """ This function sets the layout for the given configuration

        :param config: A configuration dict
        :param parent: A parent to assign the QLineEdit

        :returns : A grid layout
        """
        g = QtWidgets.QGridLayout()
        for i, key in enumerate(config):
            g.addWidget(QtWidgets.QLabel(key), i, 0)
            qle = QtWidgets.QLineEdit(str(config[key]), parent)
            qle.setFixedHeight(20)
            qle.setFixedWidth(100)
            g.addWidget(qle, i, 1)
        return g

    def set_network_qle(self, config, parent):
        """ This function sets the layout for the given configuration

        :param config: A configuration dict
        :param parent: A parent to assign the QEditLine

        :returns : A grid layout
        """
        g = QtWidgets.QGridLayout()
        g.addWidget(QtWidgets.QRadioButton("Check to use"), 0, 0)
        i = 1
        for key in config:
            g.addWidget(QtWidgets.QLabel(key), 0, i)
            qle = QtWidgets.QLineEdit(str(config[key]), parent)
            g.addWidget(qle, 0, i + 1)
            i += 2
        return g

    def set_wp(self):
        """ This finctions sets the layout for the QRadioButton of the with_time
        and pseudo_points parameters

        :returns : A grid layout
        """
        g = QtWidgets.QGridLayout()
        g.addWidget(QtWidgets.QCheckBox("with_time"), 0, 0)
        g.addWidget(QtWidgets.QCheckBox("pseudo_points"), 0, 1)
        g.addWidget(QtWidgets.QCheckBox("thrash_data"), 0, 2)
        return g

    def retranslateUi(self, MainWindow):
        _translate=QtCore.QCoreApplication.translate
        self.MainWindow.setWindowTitle(_translate("MainWindow", "Advanced parameters"))
        self.pSpaceBox.setTitle(_translate("MainWindow", "Parameter space"))
        self.pSetBox.setTitle(_translate("MainWindow", "Parameter set"))
        self.oValuesBox.setTitle(_translate("MainWindow", "Objectives values"))
        self.nUbBox.setTitle(_translate("MainWindow", "Objectives noise upper bound"))
        self.qNetworkBox.setTitle(_translate("MainWindow", "Auto quality network"))
        self.pNetworkBox.setTitle(_translate("MainWindow", "Fully auto network"))
        self.wpBox.setTitle(_translate("MainWindow", "Optionnal parameters"))
        self.update_button.setText(_translate("MainWindow", "Update configuration"))

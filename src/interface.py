
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
pyqtRemoveInputHook()
from PyQt5.QtGui import QPixmap
from skimage import io
import os

import design_interface
import create_config
import microscope


class MainApp(QMainWindow, design_interface.Ui_MainWindow):
    """Menu to choose the desired type of analysis and the images directory"""

    def __init__(self):
        super(self.__class__, self).__init__()
        self.config = create_config.create_config()
        self.autoquality = False
        self.autopref = False
        self.thrash_data = False
        self.config_conf = None
        self.config_sted = None
        self.readjust = False
        self.more_regions = False
        self.t = 0
        self.setupUi(self)

        self.advancedMenu = AdvancedMenu(self)

        self.dir_button.clicked.connect(self.choose_directory)
        self.prev_dir_button.clicked.connect(self.choose_prev_directory)
        self.adv_button.clicked.connect(self.unlock_advanced)
        self.microscope_button.clicked.connect(self.get_microscope_config)
        self.start_button.clicked.connect(self.start_optimizer)

        self.show()

    def choose_directory(self):
        """ This function opens a dialog to select the directory where to save
        the data
        """
        directory = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        self.dir_label.setText(directory)

    def choose_prev_directory(self):
        """ This function opens a dialog to select the directories that contains
        previous knowledge
        """
        self.multiple_directories = QFileDialog()
        self.multiple_directories.setFileMode(QFileDialog.DirectoryOnly)
        self.multiple_directories.setOption(QFileDialog.DontUseNativeDialog, True)
        for view in self.multiple_directories.findChildren((QListView, QTreeView)):
            if isinstance(view.model(), QFileSystemModel):
                view.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.multiple_directories.exec_()
        label = ""
        for f in self.multiple_directories.selectedFiles():
            label = label + "/" + f.split("/")[-1] + " "
        self.prev_dir_label.setText(label)

    def unlock_advanced(self):
        """ This function allows to unlock the advanced parameters in a different
        window
        """
        self.advancedMenu.show()

    def start_optimizer(self):
        """ This function allows to start the optmization with the given parameters
        in a different thread so it doesn't block the GUI. It also finishes the
        updates of the configuration parameter
        """
        self.update_output(self.config["output"])
        self.update_selected(self.config["params"], self.list_params)
        self.update_selected(self.config["objectives"], self.list_objs)

        if self.config_conf:
            QCoreApplication.exit(0)
        else:
            print("No microscope configurations were choosen")

    def get_microscope_config(self):
        """ This function gets the configuration of the confocal and the STED
        from the microscope
        """
        # setting the confocal and the sted configuration of the microscope
        self.config_conf = microscope.get_config("Setting confocal configuration.")
        self.config_sted = microscope.get_config("Setting STED configuration.")
        # verify that confocal and STED configurations can be used together
        assert microscope.get_imagesize(self.config_conf) == microscope.get_imagesize(self.config_sted),\
            "Confocal and STED images must have the same size!"

    def update_output(self, config):
        """ This function updates the configuration with the items from the output
        directory box
        """
        config["saving_dir"] = self.dir_label.text()
        config["folder"] = self.folder_label.text()
        try:
            config["previous"] = self.multiple_directories.selectedFiles()
        except AttributeError:
            pass

    def update_selected(self, config, list_widget):
        """ This function updates the configuration with the items selected in the
        parameters and objectives list
        """
        selected = [item.text() for item in list_widget.selectedItems()]
        for key in config:
            if key in selected:
                config[key] = True
            else:
                config[key] = False


class AdvancedMenu(QMainWindow, design_interface.Ui_advancedWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setup_adv(self)

        self.update_button.clicked.connect(self.update_config)

    def update_config(self):
        """ This function updates the configuration dict using the parameters
        from the GUI
        """
        # update params space
        self.update_params_space(self.parent.config["params_space"], self.pSpaceLayout)

        # update params set
        self.update_singles(self.parent.config["params_set"], self.pSetLayout)

        # update objectives values
        self.update_singles(self.parent.config["objectives_values"], self.oValuesLayout)

        # update noise upper bound objectives
        self.update_singles(self.parent.config["noise_ub_objectives"], self.nUbLayout)

        # update QualityNet
        self.parent.autoquality = self.update_network(self.parent.config["autoquality"], self.qNetworkLayout)

        # update PrefNet
        self.parent.autopref = self.update_network(self.parent.config["autopref"], self.pNetworkLayout)

        # update with_time, pseudo_points and thrash_data
        self.parent.config["with_time"] = self.wpLayout.itemAt(0).widget().isChecked()
        self.parent.config["pseudo_points"] = self.wpLayout.itemAt(1).widget().isChecked()
        self.parent.thrash_data = self.wpLayout.itemAt(2).widget().isChecked()

    def update_params_space(self, config, layout):
        """ This function allows to update the configuration of the parameters
        space from the advanced parameters

        ::param config: A configuration dict
        :param layout: The layout to get the parameters from
        """
        # starts at 4 to avoid min, max, inc
        params, values = [], []
        for i in range(4, layout.count()):
            text = layout.itemAt(i).widget().text()
            try:
                values.append(float(text))
            except ValueError:
                params.append(text)
        for i, p in enumerate(params):
            for j in range(3):
                config[p][j] = values[i * 3 + j]

    def update_singles(self, config, layout):
        """ This function allows to update the configuration of the single QLineEdit
        from the advanced parameters

        :param config: A configuration dict
        :param layout: The layout to get the parameters from
        """
        for i in range(0, layout.count(), 2):
            param = layout.itemAt(i).widget().text()
            val = layout.itemAt(i + 1).widget().text()
            config[param] = val

    def update_network(self, config, layout):
        """ This function allows to update the configuration of the neural network

        :param config: A configuration dict
        :param layout: The Layout to get the parameters from

        returns : The state of the QRadioButton
        """
        for i in range(1, layout.count(), 2):
            param = layout.itemAt(i).widget().text()
            val = layout.itemAt(i + 1).widget().text()
            config[param] = val
        return layout.itemAt(0).widget().isChecked()

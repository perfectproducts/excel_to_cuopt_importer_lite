import omni.ext
import omni.ui as ui
from omni.kit.pipapi import install 
from omni.kit.window.filepicker import FilePickerDialog
from omni.kit.widget.filebrowser import FileBrowserItem
import random 
import requests as req
import os 
import glob
import networkx as nx 
from pxr import Gf, Usd 
from itertools import product
import gc
import scipy as sp
import numpy as np
from scipy.sparse import csr_matrix

from .transport_fleet_model import *
from .network_model import *
from .network_customdata import * 
from .network_simpleviz import *
from .transport_fleet_model import *
from .transport_fleet_customdata import *
from .transport_fleet_simpleviz import * 
from .transport_tasks_model import *
from .cuopt_connector import CuOptConnector
from .geo_utils import GeoUtils 
from .network_builder import NetworkBuilder
from .network_excel import NetworkExcelReaderWriter
from .network_customdata import NetworkModelCustomData
from .cuopt_connector import CuOptConnector
from .sampledata import SampleData

# Any class derived from `omni.ext.IExt` in top level module (defined in `python.modules` of `extension.toml`) will be
# instantiated when extension gets enabled and `on_startup(ext_id)` will be called. Later when extension gets disabled
# on_shutdown() is called.
class ExcelToCuOptImporterFull(omni.ext.IExt):
    # ext_id is current extension id. It can be used with extension manager to query additional information, like where
    # this extension is located on filesystem.

    def on_check_connection_click(self):
        url = f"{self._base_path_field.model.get_value_as_string()}/{self._cuopt_api_health_path}" 
        print(f"check {url}")
        response = req.get(url)
        print(response)
        self.set_status(str(response))
                    
    
    def show_excel_selection_dialog(self):
        heading = "Select Excel..."
        dialog = FilePickerDialog(
            heading,
            allow_multi_selection=False,
            apply_button_label="select file",
            click_apply_handler=lambda filename, dirname: self.on_excel_selected( dialog, f"{dirname}/{filename}"),
            #click_cancel_handler = 
            file_extension_options = [("*.xlsx", "Excel")]
            
        )            
        dialog.show()

    def build_network_from_excel(self, excel_file=""):                
        print(f"LOAD EXCEL {excel_file}")
        self._network = NetworkExcelReaderWriter().read(excel_file)
        
        gb = GeoUtils()
        new_usd_path = self._SCRIPT_ROOT+"/data/network.usd"
        stage = gb.open_or_create_stage(new_usd_path)
        
        NetworkModelCustomData().write(stage, self._network)
        NetworkSimpleViz().write(stage, self._network)
        stage.Save()
        print(f"load {new_usd_path}")
        omni.usd.get_context().open_stage(new_usd_path)
        self.on_network_changed()
        
    def on_excel_selected(self, dialog, filename):
        print(f"SELECTED EXCEL {filename}")
        dialog.hide()
        self.build_network_from_excel(filename)

    def on_load_network_click(self):
        self.show_excel_selection_dialog()

    def load_fleet_xls(self, xls_path):
        self._cuopt.load_fleet_from_excel(xls_path=xls_path)

    def on_load_fleet_click(self):
        fleet_xls_path = f"{self._SCRIPT_ROOT}/fleet.xlsx"
        self.load_fleet_xls(fleet_xls_path)

    def load_tasks_xls(self, xls_path):
        self._cuopt.load_tasks_from_excel(xls_path)

    def on_load_tasks_click(self):        
        tasks_xls_path = f"{self._SCRIPT_ROOT}/tasks.xlsx"
        self.load_tasks_xls(tasks_xls_path)
    
    def on_network_changed(self):
        self._network_info_label.text = f"{len(self._network.nodes)} nodes, {len(self._network.edges)} edges"
        
    def on_fleet_changed(self):
        self._fleet_info_label.text = f"0 vehicles"

    def on_tasks_changed(self):
        self._tasks_info_label.text = f"0 tasks"

    def on_startup(self, ext_id):        
        self._SCRIPT_ROOT = os.path.dirname(os.path.realpath(__file__))
        self._cuopt_default_srv_url = "http://localhost:5000/cuopt"
            
        self._cuopt = CuOptConnector(self._cuopt_default_srv_url)

        self._window = ui.Window("CuOpt Excel Importer Lite", width=300, height=450)
        self._network = NetworkModel()

        with self._window.frame:
            with ui.VStack():
                ui.Label("CuOpt Server:")
                
                self._base_path_field = ui.StringField(height=30)
                self._base_path_field.model.set_value(self._cuopt_default_srv_url)

                ui.Label("Network")
                self._network_info_label = ui.Label("[network info]")
                self.on_network_changed()
                ui.Button("load network...", clicked_fn=lambda: self.on_load_network_click())
                ui.Label("Fleet")
                self._fleet_info_label = ui.Label("[fleet info]")
                ui.Button("load fleet...", clicked_fn=lambda: self.on_load_fleet_click())
                self.on_fleet_changed()
                ui.Label("Tasks")
                self._tasks_info_label = ui.Label("[task info]")
                ui.Button("load tasks...", clicked_fn=lambda: self.on_load_tasks_click())
                self.on_tasks_changed()
                ui.Label("Status:")
                self._statusTextModel = ui.StringField(multiline=True).model

    def set_status(self, txt):
        self._statusTextModel.set_value(txt)

    def on_shutdown(self):
        print("[synctwin.cuopt.testbed] MyExtension shutdown")
        self._window = None
        gc.collect()

    
# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ciaDialog
                                 A QGIS plugin
 build isochrones or isodistances maps from the "geoservice" API (french geographic institute)
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2022-09-06
        git sha              : $Format:%H$
        copyright            : (C) 2022 by Lucas Fages
        email                : lucas.fages@laposte.net
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.core import *
import pandas as pd
import json
import requests as req
from qgis.core import (
    QgsVectorLayer
)
from openrouteservice import client
# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'cia_geo_dialog_base.ui'))


class ciaDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(ciaDialog, self).__init__(parent)
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        
        #uajout des widgets
        self.val_calcul.clicked.connect(self.calcul_iso)
        self.val_calcul_ors.clicked.connect(self.calcul_iso_ors)
        # self.pushButton.clicked.connect(self.file_save)
        
    def calcul_iso_ors(self):
        x = self.val_long_ors.text()
        if x=="":
            print("valeur manquante")
            return 0
        y = self.val_lat_ors.text()
        if y=="":
            print('valeur manquante')
            return 0
        
        # metres ou secondes
        cout=self.val_cout_ors.text()
        if cout=="":
            print('valeur manquante')
            return 0
        
        # isodistance/isochrone : time/distance
        if self.rb_chrone_ors.isChecked():
            type_ = 'time'
        if self.rb_dist_ors.isChecked():
            type_ = 'distance'
        
        # Myen de déplacement pedestrian / car / velo
        if self.rb_auto_ors.isChecked():
            moyen='driving-car'
        if self.rb_marche_ors.isChecked():
            moyen= 'foot-walking'
        if self.rb_velo_ors.isChecked():
            moyen= 'cycling-road'
            
            
        api_key = '5b3ce3597851110001cf624881278ce4081942c59865ed226e87a928'
        ors = client.Client(key=api_key)

        params_iso = {'profile': moyen,
                      'range': [float(cout)],  # 900/60 = 15 minutes
                      'range_type':type_,
                      'attributes': ['total_pop']  # Get population count for isochrones
                      }

        params_iso['locations'] =  [[float(y), float(x)]]# [apt['location']] 

        res = ors.isochrones(**params_iso)  # Perform isochrone request


        # test = res#['geometry']
        # with open('5km.json', 'w') as outfile:
            # json.dump(test, outfile)    
        
        isochrone=json.dumps(res)#json.dumps(file) # conversion du dict en string
        
        var_nom = self.var_nom_ors.text() # variable du nom de la couche json
        vlayer = QgsVectorLayer(isochrone, var_nom)
        
        # ecriture de la couche dans le projet courant
        if not vlayer.isValid():
            print("Layer failed to load!")
        else:
            QgsProject.instance().addMapLayer(vlayer)
        return 1            
                    
    
    def calcul_iso(self):
        
       
        x = self.val_long.text()
        if x=="":
            print("valeur manquante")
            return 0
        y = self.val_lat.text()
        if y=="":
            print('valeur manquante')
            return 0
        
        # metres ou secondes
        cout=self.val_cout.text()
        if cout=="":
            print('valeur manquante')
            return 0
        
        # isodistance/isochrone : time/distance
        if self.rb_chrone.isChecked():
            type_ = 'time'
        if self.rb_dist.isChecked():
            type_ = 'distance'
        
        # Myen de déplacement pedestrian / car
        if self.rb_auto.isChecked():
            moyen='car'
        if self.rb_marche.isChecked():
            moyen= 'pedestrian'
            
            
         #### URL API GEOSERVICES
        url=        'https://wxs.ign.fr/essentiels/geoportail/isochrone/rest/1.0.0/isochrone?resource=bdtopo-iso&profile='+str(moyen)+ '&costType='+str(type_)+'&costValue='+str(cout)+'&point=' + str(x) + ',' + str(y) + '&geometryFormat=geojson'

        resp = req.get(url) #chargement de la requete
        file = resp.json() # conversion en fichier json
        isochrone=json.dumps(file) # conversion du dict en string
        
        var_nom = self.var_nom_.text() # variable du nom de la couche json
        vlayer = QgsVectorLayer(isochrone, var_nom)
        
        # ecriture de la couche dans le projet courant
        if not vlayer.isValid():
            print("Layer failed to load!")
        else:
            QgsProject.instance().addMapLayer(vlayer)
        return 1

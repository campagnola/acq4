# -*- coding: utf-8 -*-
from __future__ import print_function

import collections
import numpy as np
from pyqtgraph.WidgetGroup import WidgetGroup
from pyqtgraph.parametertree import Parameter, ParameterTree
from acq4.util import Qt


class CameraDeviceGui(Qt.QWidget):
    def __init__(self, dev, win):
        Qt.QWidget.__init__(self)
        self.dev = dev
        self.win = win
        self.layout = Qt.QGridLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout)
        
        self.params = self.dev.listParams()
        self.stateGroup = WidgetGroup([])
        
        params = []
        
        for k, p in self.params.items():
            params.append(makeParameterTreeSpec(dev, k, p))
        
        self.paramSet = Parameter(name='cameraParams', type='group', children=params)
        self.paramWidget = ParameterTree()
        self.paramWidget.setParameters(self.paramSet, showTop=False)
        self.layout.addWidget(self.paramWidget)
        
        self.paramSet.sigTreeStateChanged.connect(self.stateChanged)
        self.dev.sigParamsChanged.connect(self.paramsChanged)
            
    def stateChanged(self, param, changes):
        #print "tree state changed:"
        ## called when state is changed by user
        vals = collections.OrderedDict()
        for param, change, data in changes:
            if change == 'value':
                #print param.name(), param.value()
                vals[param.name()] = param.value()
        
        self.dev.setParams(vals)    
        
    def paramsChanged(self, params):
        #print "Camera param changed:", params
        ## Called when state of camera has changed
        for p in list(params.keys()):  ## flatten out nested dicts
            if isinstance(params[p], dict):
                for k in params[p]:
                    params[k] = params[p][k]
        
        try:   ## need to ignore tree-change signals while updating it.
            self.paramSet.sigTreeStateChanged.disconnect(self.stateChanged)
            for k, v in params.items():
                self.paramSet[k] = v
                for p2 in self.params[k][3]:    ## Update bounds if needed
                    newBounds = self.dev.listParams([p2])[p2][0]
                    self.paramSet.param(p2).setLimits(newBounds)
        finally:
            self.paramSet.sigTreeStateChanged.connect(self.stateChanged)

    def reconnect(self):
        self.dev.reconnect()


def makeParameterTreeSpec(dev, name, info):
    """Return specification for building a parametertree item to represent a camera
    parameter.

    name,info must be a key:value pair from camera.listParams()
    """
    try:
        val = dev.getParam(name)
    except:
        return None
    
    values, isWritable, isReadable, dependencies = info

    if not isWritable:
        return {'name': name, 'readonly': True, 'value': val, 'type': 'str'}

    else:  ## parameter is writable
        if isinstance(values, tuple):
            if len(values) == 3:
                (mn, mx, step) = values
            elif len(values) == 2:
                (mn, mx) = values
                step = 1
            else:
                raise TypeError("Invalid parameter specification for '%s': %s" % (name, repr(p)))
            if isinstance(mx, (int, np.integer)) and isinstance(mn, (int, np.integer)):
                return {'name': name, 'type': 'int', 'value': val, 'limits': (mn, mx), 'step': step}
            else:
                spec = {'name': name, 'type': 'float', 'value': val, 'limits': (mn, mx), 'dec': True, 'step': 1}
                if name == 'exposure':
                    spec['suffix'] = 's'
                    spec['siPrefix'] = True
                    spec['minStep'] = 1e-6
                return spec
        elif isinstance(values, list):
            {'name': name, 'type': 'list', 'value': val, 'values': values}
        else:
            # print("    Ignoring parameter '%s': %s" % (name, str(p)))
            return None

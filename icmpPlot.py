#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class MatplotlibNotFound(Exception):
    """Exception in case Matplotlib is not found"""
    def __init__(self, msg=None):
        if msg is None:
            msg = '*** IcmpPlotter::ERROR: something wrong happened while importing MatPlotLib.'
        super(MatplotlibNotFound, self).__init__(msg)

class NumpyNotFound(Exception):
    """Exception in case Numpy is not found"""
    def __init__(self, msg=None):
        if msg is None:
            msg = '*** IcmpPlotter::ERROR: something wrong happened while importing Numpy.'
        super(MatplotlibNotFound, self).__init__(msg)


class TkInterNotFound(Exception):
    """Exception in case TkInter is not found"""
    def __init__(self, msg=None):
        if msg is None:
            msg = '*** IcmpPlotter::ERROR: something wrong happened while importing TkInter.'
        super(TkInterNotFound, self).__init__(msg)



import json, os, pickle, sys, tabulate, time


##### THIS CHECKS IF AGG-MODULE DEPENDENCIES ARE SATIFIED
#EXPT = None
try:
    import _tkinter
except ImportError as e:
    EXPT = e
    raise TkInterNotFound(
        msg='*** IcmpPlotter::ERROR: could not import TkInter. Consider installing the python3-tk package.'
    )

##### THIS CHECKS IF MATPLOTLIB IS AVAILABLE
IMPORT_MPL = False
try:
    import matplotlib
except ImportError:
    raise MatplotlibNotFound(
        msg='*** IcmpPlotter::ERROR: could not import Matplotlib. Please install it and try again ("pip3 install matplotlib").'
    )
else:
    IMPORT_MPL = True
    
if IMPORT_MPL:
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.ticker import MultipleLocator, FormatStrFormatter

##### THIS CHECKS IF NUMPY IS AVAILABLE
try:
    from numpy import arange
except ImportError:
    raise NumpyNotFound(
        msg='*** IcmpPlotter::ERROR: could not import Numpy. Please install it and try again ("pip3 install numpy").'
    )


class IcmpPlotter():
    def __init__(self, pkts, sessionImgDir, logSuffix, jsonSource=None):
        self.sessionImgDir = sessionImgDir
        self.logSuffix     = logSuffix
        if jsonSource is None:
            # Set the plot-data from the cycles given
            self.plotData      = self.preparePlotResults(pkts)
        else:
            self.plotData      = self.preparePlotResults(self.loadJson(jsonSource))
    
    def preparePlotResults(self, pkts):
        # Set the time of sending as X axis
        #Xlabels = [time.strftime('%d-%H:%M:%S', time.localtime(pkts[0].startTime))]
        Xlabels = []
        answers = []
        targets = {}
        targetsIndex = []
        cycleTracker = 0
        timeout = pkts[0]["timeout"]
        
        # Build {pings/target} and [targetIndex]
        for p in pkts:
            if not p["hostIp"] in targets:
                targets[p["hostIp"]] = []
                targetsIndex.append(p["hostIp"])
            targets[p["hostIp"]].append(p)
            
        # Add only xTicksLabels for the first target
        xTicksCounter = 0
        for p in targets[targetsIndex[0]]:
            # Add the send-time of each packet of the first target to X axis
            Xlabels.append(time.strftime('%d-%H:%M:%S', time.localtime(p["startTime"])))

        # Answers per cycle
        for i,xTick in enumerate(Xlabels):
            #Initialise the answers count for this tick
            answers.append(0)
            # Count the answers
            for k in targets:
                t = targets[k]
                if t[i]["answered"]:
                    answers[i] += 1
        return (Xlabels, answers, timeout, targetsIndex, targets)
        

    def plot(self):
        self.generateImage(self.plotData)
 
    def generateImage(self, pings):
        Xlabels,answers,pingTimeout,targetsIndex,targets = pings
        ### Define sizes
        figWidth       = len(answers)/2 - 5
        figHeight      = len(targets)*6 + 5
        xyRatio        = (figWidth / figHeight)
        
        # Determine orientation
        if figWidth >= figHeight:
            lanscape   = True
        else:
            lanscape   = False
        
        # Font sizes
        titleFontSize  = xyRatio*30
        xLabelFontSize = xyRatio*20
        ticksFontSize  = 10
        
        # Create the figure and the axes
        fig, axes = plt.subplots(nrows=len(targets) + 1, ncols=1, figsize=(figWidth,figHeight))
        index = [i for i in range(len(Xlabels))]
        graphs = axes.flatten()
        #majorLocator = MultipleLocator(20)
        #majorFormatter = FormatStrFormatter('%d')
        #minorLocator = MultipleLocator(5)
        #ticksFreq = 5
        # First graph is total answers
        graphs[0].set_title('Ping statistics for timeout=%s' % pingTimeout, fontsize=titleFontSize)
        # X-axis parameters
        graphs[0].set_xlabel('Pings answered for this timeout', fontsize=xLabelFontSize)
        graphs[0].set_xticklabels(Xlabels, rotation = 45, ha="right")
        # Y-axis parameters
        graphs[0].set_ylabel('Total number of answers', fontsize=ticksFontSize)
        # Set a fixed limit for the Y-axis
        graphs[0].set_ylim(0,len(targetsIndex))
        #print(len(Xlabels), len(answers))
        graphs[0].bar(Xlabels,answers)

        for i,graph in enumerate(graphs[1:]):
            t = targets[targetsIndex[i]]
            respTime = [float(p["time"]) if p["answered"] is not False else float(0) for p in t]
            answered = len([p["time"] for p in t if (p["answered"] is not False)])
            graph.set_ylabel('Response time (seconds)', fontsize=10)
            xlabel = '%s (%s) - [%s/%s]' % (t[0]["hostAlias"], t[0]["hostIp"], answered, len(respTime))
            graph.set_xlabel(xlabel, fontsize=xLabelFontSize)
            graph.set_xticklabels(Xlabels, rotation = 45, ha="right")
            graph.tick_params(which='both', width=3)
            graph.set_ylim(0, pingTimeout + .5)
            #print(len(Xlabels), len(respTime))
            graph.bar(Xlabels,respTime)
            #graph.xaxis.set_major_locator(majorLocator)
            #graph.xaxis.set_major_formatter(majorFormatter)
        imgTimestamp = time.strftime('%Y%m%d-%H%M%S', time.localtime(targets[targetsIndex[0]][0]["startTime"]))
        imgFile      = '%s_%s.png' % (imgTimestamp, self.logSuffix)
        plt.tight_layout()
        try:
            fig.savefig(os.path.join(self.sessionImgDir, imgFile))
        except KeyboardInterrupt:
            pass
    
    def loadJson(self, jsonSource):
        if os.path.exists(jsonSource):
            with open(jsonSource) as fp:
                return json.load(fp)

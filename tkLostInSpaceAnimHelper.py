# tkLostAnimHelper.py

from functools import partial 
import maya.cmds as cmds
import maya.mel as mel

global tk_edgeMemory
global tk_counter
tk_edgeMemory = []

"""

"""

def cShrinkWin(windowToClose, *args):
    """
    Shrink window to optimal size
    """

    cmds.window(windowToClose, e=1, h=20, w=440)


ver = 'v0.1';
windowStartHeight = 150;
windowStartWidth = 440;
bh1 = 18;
bh2 = 22;
colRed              = [0.44, 0.2, 0.2]
colBlue             = [0.18, 0.28, 0.44]
colGreen            = [0.28, 0.44, 0.28]
colGreenL           = [0.38, 0.5, 0.38]
colGreenD           = [0.1, 0.22, 0.12]

colUI             = [0.08, 0.09, 0.10]
colUI1            = [0.02, 0.14, 0.14]
colUI2            = [0.02, 0.21, 0.22]
colUI3            = [0.02, 0.24, 0.22]
colUI4            = [0.02, 0.27, 0.26]
colUI5            = [0.02, 0.30, 0.28]
colUI6            = [0.02, 0.33, 0.32]

colYellow           = [0.50, 0.45, 0.00]
colYellow2          = [0.42, 0.37, 0.00]
colYellow3          = [0.39, 0.34, 0.00]
colYellow4          = [0.49, 0.44, 0.00]
colYellow5          = [0.33, 0.27, 0.00]

colBlk              = [0.00, 0.00, 0.00]



if cmds.window('win_tkLostAnimHelper', exists=1):
    cmds.deleteUI('win_tkLostAnimHelper')
myWindow = cmds.window('win_tkLostAnimHelper', t=('Lost In Space Helper ' + ver), s=1, wh=(windowStartHeight, windowStartWidth ))

cmds.columnLayout(adj=1, bgc=(colUI2[0], colUI2[1], colUI2[2]))

cmds.frameLayout('flAttributesAndConnections', l='SET VALUES	', fn='smallPlainLabelFont', bgc=(colUI2[0], colUI2[1], colUI2[2]), cll=1, cl=1, cc=partial(cShrinkWin, 'win_tkLostAnimHelper'))

cmds.columnLayout('layAdjAttr', adj=1)
cmds.rowColumnLayout(nc=6, cw=[(1, 90), (2, 90), (3, 60), (4, 60), (5, 60), (6, 80)])
cmds.button(l='Attr >>', c=partial(cSetAttr, 'tfAttr'), bgc=(colYellow5[0], colYellow5[1], colYellow5[2]))





cmds.showWindow(myWindow)
cmds.window(myWindow, w=440, h=20, e=1)

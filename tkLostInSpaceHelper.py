# tkLostInspace.py

from functools import partial 
import maya.cmds as cmds
import maya.mel as mel

global tk_edgeMemory
tk_edgeMemory = []


def cShrinkWin(windowToClose, *args):
    cmds.window(windowToClose, e=1, h=20, w=440)


def cBuildOnLoops(edge, *args):
    global tk_edgeMemory
    id = int(edge.split('[')[1].split(':')[0].split(']')[0])
    obj = edge.split('.')[0]
    newLoop = cmds.polySelect(obj, el=id)
    newLoop = cmds.ls(sl=1, fl=1)
    check = cCollectIds(newLoop)
    print 'tk_edgeMemory:'
    print tk_edgeMemory
    if check == 1:
        cmds.select(newLoop, r=1)
        crvs = cmds.polyToCurve(form=2, degree=1, ch=0, conformToSmoothMeshPreview=1)



def cCollectIds(loop, *args):
    global tk_edgeMemory
    check = 1
    for edge in loop:
        id = int(edge.split('[')[1].split(':')[0].split(']')[0])
        if id not in tk_edgeMemory:
            tk_edgeMemory.append(id)
        else:
            check -=1
    print 'check:'
    print check
    return check




def cJntsOnLoop(*args):
    global tk_edgeMemory
    tk_edgeMemory = []
    mySel = cmds.ls(sl=1, fl=1)
    print 'mySel:'
    print mySel
    for edge in mySel:
        print edge
        if '.e' in edge:
            cBuildOnLoops(edge)
        if '.vtx' in edge:
            print 'vertex'
        if '.f' in edge:
            print 'face'





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
colDark             = [0.08, 0.09, 0.10]
colDark2            = [0.02, 0.21, 0.22]
colYellow           = [0.50, 0.45, 0.00]
colYellow2          = [0.42, 0.37, 0.00]
colYellow3          = [0.39, 0.34, 0.00]
colYellow4          = [0.49, 0.44, 0.00]
colYellow5          = [0.33, 0.27, 0.00]
colBlk              = [0.00, 0.00, 0.00]



if cmds.window('win_tkLostInSpaceHelper', exists=1):
    cmds.deleteUI('win_tkLostInSpaceHelper')

myWindow = cmds.window('win_tkLostInSpaceHelper', t=('Lost In Space Helper ' + ver), s=1, wh=(windowStartHeight, windowStartWidth ))
cmds.columnLayout(adj=1, bgc=(colGreenD[0], colGreenD[1], colGreenD[2]))
cmds.frameLayout('cJntsOnRing', l='RIG SETUP', fn='smallPlainLabelFont', bgc=(colGreen[0], colGreen[1], colGreen[2]), cll=1, cl=0, cc=partial(cShrinkWin, 'win_tkLostInSpaceHelper'))

cmds.columnLayout(adj=1)
cmds.rowColumnLayout(nc=4, cw=[(1, 140), (2, 60), (3, 60), (4, 140)])
cmds.button(l='Joints On Loop', c=partial(cJntsOnLoop), bgc=(colGreen[0], colGreen[1], colGreen[2]))
cmds.setParent('..')


cmds.textField('tfFeedback', tx='', ed=0, bgc=(colGreenD[0], colGreenD[1], colGreenD[2]))


cmds.showWindow(myWindow)
cmds.window(myWindow, w=400, h=50, e=1)

cmds.select('lam_01:mouth_04_lv1_geo.e[498]', r=1)
cmds.select('lam_01:mouth_04_lv1_geo.e[502]', add=1)
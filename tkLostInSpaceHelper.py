# tkLostInspaceHelper.py

from functools import partial 
import maya.cmds as cmds
import maya.mel as mel
import random as random

global tk_edgeMemory
global tk_counter
tk_edgeMemory = []

"""
"track selection order" has to be ON in the prefs!
grp above details cons has naming "_OFF"!
----------------
ctrl naming:
loop_1_crv_center_grp_con
- loop_1_crv_center_grp
-- loop_1_crv_center_jnt
--- loop_1_crv_0_jnt_half_nul
---- loop_1_crv_0_jnt_half_con_OFF
----- loop_1_crv_0_jnt_half_con
---------------

better ctrl naming:
loop_1_center_grp_con
- loop_1_center_grp
-- loop_1_center_jnt
--- loop_1_0_jnt_half_nul
---- loop_1_0_jnt_half_con_OFF
----- loop_1_0_jnt_half_con
---------------
to do
- build mesh from joints?
- ctrl size like BB curves
- controls on sik curve

---------------
pipeline:
1.  Loop to curves
2.  Start ID
3.  Crv with new start
4.  Just place (8 - 16) and adjust centere joint
5.  Halfway joint up for stars
6.  Select groups and add nail control: "Sel Under New Control (guide cons)"
7.  Select halfway joints (down) and "Parent Ctrl To Sel (half cons)"
8.  move vertices out (offset CVs, x)
9.  Setup attributes: 
    Setup Ring Scale (select guide cons)
    Setup Details (select guide cons)
10. Wave Expressions:
    Select guide cons and "Batch Write"
11. mGear: 
    chain FK spline 01
    override joint number with number of star elements

teeth
12. Select target mesh / teeth mesh / nth vertex and index start
13. Batch for multiple objects
14. Select base joints and use "Parent Ctrl To Sel (half cons)"
15. Main teeth with extra con (spread and expand)



"""

def cShrinkWin(windowToClose, *args):
    """
    shrink window to optimal size
    """
    cmds.window(windowToClose, e=1, h=20, w=440)


def winProgress(title, pBarName, numElements):
    if cmds.window(title, exists=1):
        cmds.deleteUI(title)

    windowProgress = cmds.window(title, wh=[300, 28])

    cmds.columnLayout()
    progressControl = cmds.progressBar(
        "pProgress", maxValue=numElements, w=300
    )

    cmds.showWindow(title)
    cmds.window(title, e=1, wh=[300, 28])


def cClearSE(*args):
    """
    clear script editor
    """
    cmds.scriptEditorInfo(ch=1)


def cSelectLevel(curSel, level, shapes, *args):
    """
    Select up to 4 level down
    Args:
            args(str, bool, int): 
            selection list, shapes on/off, hierarchy level
    Return:
            list: 
            selection
    """

    if curSel == 'selectForMe':
        curSel = cmds.ls(sl=1)

    if level == 1:
        if shapes == 0:
            newSel = cmds.listRelatives(curSel, f=1, c=1, type="transform")
        else:
            newSel = cmds.listRelatives(curSel, f=1, c=1)

    if level == 2:
        if shapes == 0:
            lv1 = cmds.listRelatives(curSel, f=1, c=1, type="transform")
            newSel = cmds.listRelatives(lv1, f=1, c=1, type="transform")
        else:
            lv1 = cmds.listRelatives(curSel, f=1, c=1)
            newSel = cmds.listRelatives(lv1, f=1, c=1)

    if level == 3:
        if shapes == 0:
            lv1 = cmds.listRelatives(curSel, f=1, c=1, type="transform")
            lv2 = cmds.listRelatives(lv1, f=1, c=1, type="transform")
            newSel = cmds.listRelatives(lv2, f=1, c=1, type="transform")
        else:
            lv1 = cmds.listRelatives(curSel, f=1, c=1)
            lv2 = cmds.listRelatives(lv1, f=1, c=1)
            newSel = cmds.listRelatives(lv2, f=1, c=1)

    if level == 4:
        if shapes == 0:
            lv1 = cmds.listRelatives(curSel, f=1, c=1, type="transform")
            lv2 = cmds.listRelatives(lv1, f=1, c=1, type="transform")
            lv3 = cmds.listRelatives(lv2, f=1, c=1, type="transform")
            newSel = cmds.listRelatives(lv3, f=1, c=1, type="transform")
        else:
            lv1 = cmds.listRelatives(curSel, f=1, c=1)
            lv2 = cmds.listRelatives(lv1, f=1, c=1)
            lv3 = cmds.listRelatives(lv2, f=1, c=1)
            newSel = cmds.listRelatives(lv3, f=1, c=1)

    cmds.select(newSel, r=1)


def cWalkUp(*args):
    """
    simply walk up
    """

    cmds.pickWalk(d='up')


def cReOrder(*args):
    """
    Order in outliner according to the selection
    """

    mySel = cmds.ls(os=1)
    dad = cmds.listRelatives(mySel[0], p=1)
    cmds.group(mySel, n='reorder_GRP')
    childs = cmds.listRelatives(c=1)
    if dad:
        cmds.parent(childs, dad)
    else:
        cmds.parent(childs, w=1)
    cmds.delete('reorder_GRP')


def cAddNullGrp(*args):
    """
    Add null grp and parent selection under it
    """

    mySel = cmds.ls(sl=1)
    suffix = '_OFF'
    for obj in mySel:
        emptyGrp = cmds.group(empty=1)
        dad = cmds.listRelatives(obj, p=1)
        constr = cmds.parentConstraint(obj, emptyGrp)
        cmds.delete(constr)

        if dad:
            cmds.parent(emptyGrp, dad)

        cmds.makeIdentity(emptyGrp, apply=1, t=1, r=1, s=1, n=0, pn=0)
        cmds.parent(obj, emptyGrp)
        emptyGrp = cmds.rename(emptyGrp, obj + suffix)
        cmds.select(emptyGrp, r=1)

        return(emptyGrp)





def cSelectionSet(type, *args):
    gShelfTopLevel = mel.eval("$tmpVar=$gShelfTopLevel")
    currentTab = cmds.tabLayout(gShelfTopLevel, q=1, st=1)
    setName = cmds.textField('tSelectionSet', tx=1, q=1)
    iconColor = cmds.radioCollection('rcIconColors', q=1, sl=1)
    if iconColor == 'rbRed':
        iconColor = 'red'
    if iconColor == 'rbGreen':
        iconColor = 'green'
    if iconColor == 'rbBlue':
        iconColor = 'blue'

    mySel = cmds.ls(os=1, fl=1)

    imageName = 'ss_' + iconColor + '_' + str(type) + '.png'
    cmd = 'cmds.select("'
    for i in range(0, len(mySel), 1):
        cmd += mySel[i]
        if i < len(mySel)-1:
            cmd += '", "'
    cmd += '", ' + type + '=1)'

    cmds.shelfButton(p=currentTab, rpt=1, i1=imageName, iol=setName, c=cmd, ann=cmd)



def cGetCurveData(nurbsCurve, *args):
    """
    Collect nurbs curve data
    
    Input: 
        nurbsCurve: One nurbs curve
   
    Return:
        curve shape, 
        degree, 
        spans, 
        numCVs, 
        cvPosList, 
        vtxPosList

    """

    cvPosList = []
    vtxPosList = [] 
    shp = cmds.listRelatives(nurbsCurve, s=1, type='nurbsCurve')[0]
    degree  = cmds.getAttr(shp + ".degree")
    spans   = cmds.getAttr(shp + ".spans")
    form    = cmds.getAttr(shp + ".form")
    numCVs  = spans + degree;           

    if form == 2:
        numCVs -= degree            

    for i in range(0, numCVs, 1):  
        cvPosList.append(cmds.xform(nurbsCurve + '.cv[' + str(i) + ']', q=1, translation=1, ws=1))

        vtxX = cmds.getAttr(shp + '.controlPoints[' + str(i) + '].xValue')
        vtxY = cmds.getAttr(shp + '.controlPoints[' + str(i) + '].yValue')
        vtxZ = cmds.getAttr(shp + '.controlPoints[' + str(i) + '].zValue')
        
        vtxPosList.append([vtxX, vtxY, vtxZ])

    return(shp, degree, spans, numCVs, cvPosList, vtxPosList)


def cOffsetCVs(*args):
    """
    Offset the local vertex position 
    The offset value is read from the "Lost In Space" UI 
    """

    mySel = cmds.ls(os=1)
    offsetX = cmds.floatField('fOffsetX', v=1, q=1)
    offsetY = cmds.floatField('fOffsetY', v=1, q=1)
    offsetZ = cmds.floatField('fOffsetZ', v=1, q=1)
    for crv in mySel:
        crvData     = cGetCurveData(crv)
        shp         = crvData[0]
        numCVs      = crvData[3]
        vtxPosList  = crvData[5]

        for i in range(0, numCVs, 1):
            cmds.setAttr(shp + '.controlPoints[' + str(i) + '].xValue', vtxPosList[i][0] + offsetX)
            cmds.setAttr(shp + '.controlPoints[' + str(i) + '].yValue', vtxPosList[i][1] + offsetY)
            cmds.setAttr(shp + '.controlPoints[' + str(i) + '].zValue', vtxPosList[i][2] + offsetZ)


def cResetField(field, value, *args):
    """
    reset field to value
    """

    cmds.floatField(field, v=value, e=1)


def cIncrease(field, value, *args):
    """
    Increse or decrease float field by a value
    """   

    curValue = cmds.floatField(field, v=0, q=1)
    cmds.floatField(field, v=(curValue + value), e=1)


def cJointsVis(*args):
    """
    Set jnt visibility to 0 or 1

    """

    myJnts = []
    mySel = cmds.ls(sl=1)
    if not mySel:
        myJnts = cmds.ls(type='joint')
    else:
        myJnts = cmds.listRelatives(mySel, ad=1, type='joint')

    state = cmds.getAttr(myJnts[0] + '.drawStyle')
    if not state == 0 or state == 2:
        state = 2 

    for jnt in myJnts:
        print jnt
        cmds.setAttr(jnt + '.drawStyle', 2-state)


def cLockAndHide(state, attrName, *args):
    """
    Lock, hide or free and show default attributes
    Also allows to hide and lock selected channels from the channelbox 
    """

    mySel = cmds.ls(sl=1, l=1)

    if attrName is not 'sel':
        if attrName is not 'translate' and attrName is not 'rotate' and attrName is not 'scale':
            for carry in mySel:
                cmds.setAttr(carry + '.' + attrName, lock=1-state)
                cmds.setAttr(carry + '.' + attrName, keyable=state, channelBox=0)

        if attrName is 'translate':
            cLockAndHide(state, 'tx')
            cLockAndHide(state, 'ty')
            cLockAndHide(state, 'tz')

        if attrName is 'rotate':
            cLockAndHide(state, 'rx')
            cLockAndHide(state, 'ry')
            cLockAndHide(state, 'rz')

        if attrName is 'scale':
            cLockAndHide(state, 'sx')
            cLockAndHide(state, 'sy')
            cLockAndHide(state, 'sz')

    else:
        attrList = []
        attrQuery = []

        attrQuery = cmds.channelBox('mainChannelBox', q=1, sma=1)
        if not attrQuery:
            attrQuery = cmds.channelBox('mainChannelBox', q=1, ssa=1)
            if not attrQuery:
                attrQuery = cmds.channelBox('mainChannelBox', q=1, sha=1)

        if attrQuery:
            for attr in attrQuery:
               cLockAndHide(state, attr) 


def cAddAttrib(selection, attrType, attrName, min, max, dv, state, *args):
    """
    Add or remove attributes to an object
    
    Input:
        Selection:  one object
        attrType:   data type like float, int, bool
        attrName:   attribute Name
        min:        min value, 'x' for none
        max:        max value, 'x' for none
        dv:         default value, 'x' for none
        state:      add or remove
    """

    defaultValueList = ['ringScale']

    # print 'selection:' + str(selection)
    attrExist = maya.cmds.attributeQuery(attrName, node=selection, exists=True)
    
    if state == 'remove':  # delete attribute
        if attrExist == 1:
            cmds.deleteAttr(selection, attribute=attrName)

    if state == 'add':   # add attribute
        if attrExist == 0:
            if attrName in defaultValueList:
                cmds.addAttr(selection, ln=attrName, at=attrType, dv=1) 
            else:
                cmds.addAttr(selection, ln=attrName, at=attrType, dv=0) 
            
            cmds.setAttr(selection + '.' + attrName, e=1, keyable=1)   
            
            if min is not 'x':
                cmds.addAttr(selection + '.' + attrName, min=min, e=1) 
            if max is not 'x':
                cmds.addAttr(selection + '.' + attrName, max=max, e=1) 
            if dv is not 'x':
                cmds.addAttr(selection + '.' + attrName, dv=dv, e=1) 
                cmds.setAttr(selection + '.' + attrName, dv)




def cSetAttr(field, *args):
    """
    Add attributes ftom the channelbox
    """

    attrTxt = ''
    attrQuery = []

    attrQuery = cmds.channelBox('mainChannelBox', q=1, sma=1)
    if not attrQuery:
        attrQuery = cmds.channelBox('mainChannelBox', q=1, ssa=1)
    if not attrQuery:
        attrQuery = cmds.channelBox('mainChannelBox', q=1, sha=1)

    if attrQuery:
        for i in range(0, len(attrQuery), 1):
            attrTxt += attrQuery[i]
            if i < len(attrQuery)-1:
                attrTxt += ' '

    cmds.textField(field, tx=attrTxt, e=1)


def cConnectAttr(*args):
    pass


def cAddGeoAttribute(*args):
    '''
    Adds "Normal", Template" and "Reference" functionality
    Adds Enum attribute to the first selection
    Connects it with the second selection 
    '''

    carry = cmds.ls(sl=1, l=1)[0]
    geoGrp = cmds.ls(sl=1, l=1)[1]
    cmds.addAttr(carry, ln='geo', at='enum', en='normal:template:reference')
    cmds.setAttr(carry + '.geo', e=1, keyable=1)
    cmds.setAttr(geoGrp + '.overrideEnabled', 1)
    cmds.setAttr (geoGrp + '.overrideEnabled', 1)
    cmds.connectAttr(str(carry) + '.geo', geoGrp + '.overrideDisplayType')
    cmds.setAttr(carry + '.geo', 1)
    cmds.select(carry)


def cCreateNodeAndConnect(*args):
    ''' 
    Create a node multiple times 
    and connect with sel
    '''
    counter = cmds.intField('ifCountFrom', v=1, q=1)
    nodeType = cmds.textField('tfNodeType', tx=1, q=1)
    fromAttr = cmds.textField('tfFromAttr', tx=1, q=1)
    toAttr = cmds.textField('tfToAttr', tx=1, q=1)
    newName = cmds.textField('tfNodeNewName', tx=1, q=1)

    mySel = cmds.ls(os=1, fl=1)

    for i in range(0, len(mySel), 1):
        node = cmds.createNode(nodeType, n=(newName + '_' + str(counter)))
        cmds.connectAttr(mySel[i] + '.' + fromAttr, node + '.' + toAttr)
        counter +=1





def cCreateNode(objType, field, *args):
    """
    Create a node, eg a locator

    Input
        objType:    spaceLocator
        field:      filed to fill in 

    """

    mySel = cmds.ls(sl=1)
    pos = cmds.xform(mySel[0], ws=1, t=1, q=1)
    print pos


    if objType == 'spaceLocator':
        LC = cmds.spaceLocator(p=(0,0,0))
        cmds.setAttr(LC[0] + '.translate', pos[0], pos[1], pos[2])

    cFillField(field)


def cJointSize(*args):
    """
    Opens UI for joint scale 
    """

    mel.eval('jdsWin')


def cFillField(field, *args):
    """
    Fill in the UI field with the selection

    Input:
        field:      field name

    """

    mySel = cmds.ls(sl=1)
    if mySel:
        cmds.textField(field, tx=mySel[0], e=1)
    else:
        cmds.textField(field, tx='', e=1)

    if field == 'tfDriver':
        cDeriveFromDriver('tfDriver', 1)

    if field == 'tfDriven':
        cDeriveFromDriven('tfDriven')

    if field == 'tfNmSpc':
        nmSpc = mySel.split(':')[0]
        cmds.textField(field, tx=nmSpc, e=1)

    if field == 'tfNodeType':
        objType = cmds.objectType(mySel[0])
        cmds.textField(field, tx=objType, e=1)



def cGetID(*args):
    """
    Get the pure vertex or CV ID
    Fill the ID field od the "Lost in space" UI
    """

    mySel = cmds.ls(sl=1)[0].split('[')[1].split(':')[-1].split(']')[0]
    value = int(mySel)
    cmds.intField('ifID', v=value, e=1)

    return(value)


def cRemoveEmptyTransforms(*args):
    """
    Starts "Remove Empty Groups" from the optimize scen menu
    """

    mel.eval('scOpt_performOneCleanup( { "transformOption" } );')


def tkGetCenter(object, type, output, *args):
    """
    Find the center of the selected meshes or nurbs

    Input
        object:     selection
        type:       mesh or nurbs
        output:     locator or joint

    Return 
        centerPos, 
        grp, 
        jnt
    """

    # print 'tkGetCenter...'
    # print object

    points = []
    cvPosList = []
    pos = []
    posX = 0.0
    posY = 0.0
    posZ = 0.0

    if type == 'mesh':
        mel.eval('ConvertSelectionToVertices')
        points = cmds.ls(sl=1, l=1)
        points = cmds.filterExpand(ex=1, sm=31)

    if type == 'nurbs':
        crv = cmds.listRelatives(object, s=1)[0] 
        degree = cmds.getAttr(crv + ".degree")
        spans = cmds.getAttr(crv + ".spans")
        form = cmds.getAttr(crv + ".form")
        numCVs = degree + spans

        if form == 2:
            numCVs -= degree            

        for i in range(0, numCVs, 1):
            singleCV = object + '.cv[' + str(i) + ']'
            points.append(singleCV)

    amount = len(points)

    for i in range(0, amount, 1):
        pos = cmds.xform(points[i], q=1, translation=1, ws=1)
        if pos not in cvPosList:
            posX += pos[0]
            posY += pos[1]
            posZ += pos[2]
            # print pos
            cvPosList.append(pos)
    
    amount = len(cvPosList)

    centerPos = (posX/amount, posY/amount, posZ/amount) 

    if output == 'locator':
        LC = cmds.spaceLocator(p=(0, 0, 0), n=str(object) + '_LC')
        cmds.setAttr(LC[0] + '.tx', centerPos[0])
        cmds.setAttr(LC[0] + '.ty', centerPos[1])
        cmds.setAttr(LC[0] + '.tz', centerPos[2])

        lc = cmds.listRelatives(LC, s=1)[0]
        cmds.setAttr(lc + '.localScaleX', 5)
        cmds.setAttr(lc + '.localScaleY', 5)
        cmds.setAttr(lc + '.localScaleZ', 5)

        return centerPos, LC

    if output == 'joint':
        cmds.select(clear=1)
        jnt = cmds.joint(p=(0, 0, 0), n=str(object) + '_center_jnt')
        grp = cmds.group(empty=1, n=object + '_center_grp')
        cmds.parent(jnt, grp)
        # print 'centerPos:'
        # print centerPos
        cmds.setAttr(grp + '.tx', centerPos[0])
        cmds.setAttr(grp + '.ty', centerPos[1])
        cmds.setAttr(grp + '.tz', centerPos[2])

        return centerPos, grp, jnt


def cMultiParent(*args):
    """
    Given an equal number of objects
    parent the first half under the second one 
    """

    mySel = cmds.ls(os=1, type = 'transform')
    num = len(mySel)

    if num%2 == 0:
        for i in range(0, num/2, 1):
            # print str(mySel[i]) + ' --> ' + str(mySel[i+(num/2)])
            cmds.parent(mySel[i], mySel[i+(num/2)])


def cEdegloopToCurves(*args):
    """
    relies on 
        cBuildOnLoops

    Input:  
        edge selection, NO border edges!

    Output: 
        nurbs curves, numbered in order of selection
    """

    global tk_edgeMemory
    global tk_counter
    tk_edgeMemory = []
    tk_counter = 1

    mySel = cmds.ls(os=1, fl=1)

    for edge in mySel:
        if '.e' in edge:
            cBuildOnLoops(edge)
        if '.vtx' in edge:
            pass
        if '.f' in edge:
            pass


def cBuildOnLoops(edge, *args):
    """
    relies on 
        cEdegloopToCurves

    Input:  
        edge

    Output: 
        nurbs curves, numbered in order of selection
    """

    global tk_edgeMemory
    global tk_counter

    id = int(edge.split('[')[1].split(':')[0].split(']')[0])
    obj = edge.split('.')[0]
    newLoop = cmds.polySelect(obj, el=id)
    newLoop = cmds.ls(sl=1, fl=1)
    check = cCollectIds(newLoop)
    if check == 1:
        cmds.select(newLoop, r=1)
        crvs = cmds.polyToCurve(form=2, degree=1, ch=0, conformToSmoothMeshPreview=1)
        newCrv = cmds.rename(crvs[0], 'loop_' + str(tk_counter))
        cmds.xform(newCrv, cpc=1)
        tk_counter +=1


def cCutAsStart(*args):
    """
    Reorder a nurbs curve 
    The selected CV is the first CV of the rebuilded curve
    ID is taken from the "Lost in space" UI 
    """

    mySel = cmds.ls(sl=1)
    idStart = cmds.intField('ifID', v=1, q=1)

    for CRV in mySel:
        cvList = []
        crv = cmds.listRelatives(CRV, s=1, type='nurbsCurve')[0]
        if crv: 
            degree = cmds.getAttr(crv + ".degree")
            spans = cmds.getAttr(crv + ".spans")
            form = cmds.getAttr(crv + ".form")
            numCVs = degree + spans
            form = cmds.getAttr(crv + '.form')

            if form == 2:
                numCVs -= degree            

            cmds.select(clear=1)
            for i in range(0, numCVs, 1):
                cvList.append(cmds.xform(crv + '.cv[' + str(i) + ']', q=1, translation=1, ws=1))

            cmd = 'cmds.curve(n="tempCrv", d=' + str(degree) + ', p=['
            

            for i in range(0, numCVs, 1):
                newId = (i + idStart)%numCVs
                cmd += '(' + str(cvList[newId][0]) + ',' + str(cvList[newId][1]) + ',' + str(cvList[newId][2]) + ')'

                if not i == numCVs-1:
                    cmd += ','
                else:
                    cmd += '], k=['

            for i in range(0, degree, 1):
                cmd += '0,'

            for i in range(1, numCVs-degree, 1):
               cmd += str(i)
               cmd += ','

            for i in range(numCVs-degree-degree, numCVs-degree+1, 1):
                cmd += str(numCVs-degree)
                cmd += ','

            cmd = cmd[0:-3]
            cmd += '])'

            eval(cmd)

            cmds.delete(CRV)
            cmds.rename('tempCrv', CRV)

            cmds.closeCurve(CRV, ch=1, ps=1, rpo=1, bb=0.5, bki=0, p=0.1)


def cCollectIds(loop, *args):
    """
    Check if an edge of an edge loop has already been selected
    Important for building curves from edgeloop
    That way only one crv per edgeloop is generated

    relies on 
        cEdegloopToCurves

    Input:  
        Loop

    Output: 
        Nurbs curves, numbered in order of selection

    Return: 
        check   int
    """

    global tk_edgeMemory
    check = 1
    for edge in loop:
        id = int(edge.split('[')[1].split(':')[0].split(']')[0])
        if id not in tk_edgeMemory:
            tk_edgeMemory.append(id)
        else:
            check -=1
    return check





def cBonesOnCurve(type, *args):
    """
    Build jnt chains on curves
    
    Input
        type:   "bonesOnly"
                    place bones evenly on a curve
                "bonesCV"
                    place a bone on each cv
                "bonesMP"
                    place bones evenly on a crv 
                    connect the joint via motionpath with the curve
    """

    print 'cBonesOnCurve...'
    v=0
    jntList = []
    centerGrpList = []
    centerJntList = []
    cvPosList = []
    mySel = []
    number = cmds.intField('fBonesNumber', q=1, v=1)

    mySel = cmds.ls(os=1, fl=1)

    # mySel = cmds.ls(sl=1)

    for CRV in mySel:
        crv = cmds.listRelatives(CRV, s=1)[0] 
        degree = cmds.getAttr(crv + ".degree")
        spans = cmds.getAttr(crv + ".spans")
        numCVs = degree + spans
        step = 1.0 / float(number)

        if type == "bonesOnly":
            print 'bonesOnly...'
            result = tkGetCenter(CRV, 'nurbs', 'joint')
            centerGrpList.append(result[1])
            centerJntList.append(result[2])
            centerPos = result[0]
            centerGrp = result[1]
            centerJnt = result[2]
            LC = cmds.spaceLocator(n="deleteMe_LC")[0]
            mp = cmds.pathAnimation(LC, CRV, fractionMode=1, follow=0, startTimeU=1)
            cmds.cutKey(mp, cl=1, t=(":", ":"), at="u")
            cmds.select(clear=1)

            for v in range(0, number, 1):
                cmds.setAttr(mp + '.uValue', v*step)
                pos = cmds.getAttr(LC + '.translate')
                cmds.select(centerJnt, r=1)
                jnt = cmds.joint(p=(pos[0][0], pos[0][1], pos[0][2]), n=CRV + '_' + str(v) + '_jnt')
                cmds.select(clear=1)

            cmds.delete('deleteMe_LC')

        if type == "bonesCV":
            print 'bonesCV...'
            cmds.select(clear=1)
            counter = 0
            for i in range(0, numCVs, 1):
                pos = cmds.pointPosition(str(CRV) + '.cv[' + str(i) + ']')
                if pos not in cvPosList:
                    jnt = cmds.joint(p=(pos[0], pos[1], pos[2]), n=CRV + '_' + str(counter) + '_jnt')
                    jntList.append(jnt)
                    cvPosList.append(pos)
                    counter +=1

            cmds.joint(jntList[0], e=1, oj='xyz', secondaryAxisOrient='yup', ch=0, zso=1) 

        if type == "bonesMP":
            print 'bonesMP...'
            MAIN = cmds.group(empty=1, n=CRV + '_main_grp')
            for v in range(0, number, 1):
                cmds.select(clear=1)
                grp = cmds.group(empty=1, n=CRV + '_' + str(v) + '_grp')
                jnt = cmds.joint(p=(0,0,0), n=CRV + '_' + str(v) + '_jnt')
                mp = cmds.pathAnimation(grp, CRV, fractionMode=1, followAxis='x', upAxis='y', worldUpType="vector", worldUpVector=(0, 1, 0), startTimeU=1)
                cmds.cutKey(mp, cl=1, at='uValue')
                cmds.setAttr(mp + ".uValue", v * step)
                cmds.parent(grp, MAIN)

            result = tkGetCenter(CRV, 'nurbs', 'joint')
            centerPos = result[0]
            centerGrp = result[1]

    cmds.select(centerGrpList, r=1)
            

def cSplineIK(*args):
    """
    Build a SIK 
    """

    fromJnt = cmds.textField('tfFromJnt', tx=1, q=1)
    toJnt = cmds.textField('tfToJnt', tx=1, q=1)
    print fromJnt
    print toJnt
    
    SIK = cmds.ikHandle(toJnt, fromJnt, sol='ikSplineSolver', scv=0, pcv=0, ns=4)
    print SIK
    cmds.setAttr(SIK[0] + '.v', 0)


def cSelToJoints(*args):
    """
    Find all Joints underneath the selection
    Select all found joints
    """

    childrenFound = []
    jntList = []
    mySel = cmds.ls(sl=1)

    for sel in mySel:
        if cmds.objectType(sel, isType='joint'):
            jntList.append(sel)
        childrenFound = cmds.listRelatives(sel, ad=1, type='joint')
        if childrenFound:
            for jnt in childrenFound:
                jntList.append(jnt)

    cmds.select(jntList, r=1)


def cSelToType(objType, *args):
    """
    Find all objects of the given selction type

    Input:
        objType:        eg nurbsCurve

    Return:
        objType_dic:    dictionary with all found types
    """

    childrenFound = []
    objType_dic = {}
    mySel = cmds.ls(sl=1)

    for sel in mySel:
        conns = cmds.listConnections(sel, t=objType)
        if conns:
            for con in conns:
                objType_dic[sel] = con

        childrenFound = cmds.listRelatives(sel, ad=1)
        if childrenFound:
            for child in childrenFound:
                conns = cmds.listConnections(child, t=objType)
                if conns:
                    for con in conns:
                        objType_dic[child] = con

    return objType_dic


def cJntsToChain(type, *args):
    """
    Connect all joints to a chain

    Input
        type:       "parent"
                    parents the joints in Order
    """

    jntsFound = []
    newChainList = []
    jntList = []
    mySel = cmds.ls(os=1, fl=1)

    for sel in mySel:
        if cmds.objectType(sel, isType='joint'):
            jntList.append(sel)
        jntsFound = cmds.listRelatives(sel, ad=1, type='joint')
        if jntsFound:
            for jnt in jntsFound:
                jntList.append(jnt)

    numJnts = len(jntList)

    if type == 'parent':
        for i in range(1, numJnts, 1):
            cmds.parent(jntList[i], jntList[i-1])
        
        cmds.select(jntList[numJnts-1])
        cmds.select(jntList)
        cmds.joint(jntList[0], e=1, oj='xyz', secondaryAxisOrient='zup', ch=0, zso=1) 


def cObjToChain(type, *args):
    """
    Sample the world postion of the selection (in order)
    Construct a new joint chain at the sampled locations

    Input:
        type:       "new"
                    parents the joints in Order
    """

    newChainList = []
    mySel = cmds.ls(os=1, fl=1)

    numSel = len(mySel)

    if type == 'new':
        cmds.select(clear=1)
        for i in range(0, numSel, 1):
            pos = cmds.xform(mySel[i], translation=1, ws=1, q=1)
            newChainList.append(cmds.joint(p=(pos[0], pos[1], pos[2]), n='chain_' + str(i) + '_jnt'))

        cmds.select(newChainList[0], r=1)
        cmds.joint(e=1, oj='xyz', secondaryAxisOrient='zup', ch=1, zso=1) 


def cJntInCenter(*args):
    """
    Place a joint in the center of the selection
    
    Relies on tkGetCenter(CRV, 'nurbs', 'locator')

    """

    centerPos = tkGetCenter(CRV, 'nurbs', 'locator')


def cHalfwayJnt(directin, *args):
    """
    Place an additional halfway joint 

    """

    mySel = cmds.ls(sl=1, type='joint')
    for jnt in mySel:
        dad = cmds.listRelatives(jnt, p=1, type='joint')
        if dad:
            cmds.select(clear=1)
            posDad = cmds.xform(dad, translation=1, ws=1, q=1)
            posJnt = cmds.xform(jnt, translation=1, ws=1, q=1)

            halfPosX = (posJnt[0] - posDad[0])/2 + posDad[0]
            halfPosY = (posJnt[1] - posDad[1])/2 + posDad[1]
            halfPosZ = (posJnt[2] - posDad[2])/2 + posDad[2]

            cmds.select(dad, r=1)
            halfJnt = cmds.joint(p=(halfPosX, halfPosY, halfPosZ), n=jnt + '_half')
            cmds.parent(jnt, halfJnt)
            cmds.select(halfJnt)
            cmds.joint(halfJnt, e=1, oj='xyz', secondaryAxisOrient='yup', ch=1, zso=1) 
            
            ori = cmds.getAttr(halfJnt + '.jointOrient')
            jnt = cmds.listRelatives(halfJnt, c=1)[0]
            cmds.setAttr(jnt + '.jointOrientX', ori[0][0])
            cmds.setAttr(jnt + '.jointOrientY', ori[0][1])
            cmds.setAttr(jnt + '.jointOrientZ', ori[0][2])






def cJntsFromSelection(parent, *args):
    """
    To be documented
    """

    pos = []
    mySel = cmds.ls(os=1, fl=1)
    jntList = []

    cmds.select(clear=1)

    for i in range(0, len(mySel), 1):
        pos.append(cmds.xform(mySel[i], translation=1, ws=1, q=1))

    cmds.select(clear=1)
    for i in range(0, len(mySel), 1):
        # jnt = cmds.joint(p=(0,0,0), n=CRV + '_' + str(v) + '_jnt')
        jnt = cmds.joint(p=(pos[i][0], pos[i][1], pos[i][2]), n='chain_' + str(i) + '_jnt')
        cmds.setAttr(jnt + '.radius',3)
        jntList.append(jnt)
     
    # orient joints chain! 

    cmds.select(clear=1)
    for i in range(0, len(mySel)-1, 1):
        if parent == 1:
            cmds.parent(mySel[i+1], jntList[i])


def cAdjustPivot(*args):
    """
    Places the joints pivot to the LCs location
    Choose the axis from the "Lost in space" UI    
    """

    pos = [0, 0, 0]
    mySel = cmds.ls(os=1, fl=1)
    pvLoc = cmds.textField('tfPivot', tx=1, q=1)
    x = cmds.checkBox('cbX', v=1, q=1)
    y = cmds.checkBox('cbY', v=1, q=1)
    z = cmds.checkBox('cbZ', v=1, q=1)
    
    if pvLoc:
        pos = cmds.xform(pvLoc, translation=1, ws=1, q=1)

    for jnt in mySel:
        curPos = cmds.xform(jnt, translation=1, ws=1, q=1)

        if x == 0:
            pos[0] = curPos[0]
        if y == 0:
            pos[1] = curPos[1]
        if z == 0:
            pos[2] = curPos[2]


        cmds.move(pos[0], pos[1], pos[2], jnt + '.scalePivot', jnt + '.rotatePivot', rpr=1)


    # move -rpr 0 0 0 polyToCurve1_center_jnt.scalePivot polyToCurve1_center_jnt.rotatePivot ;






def cCtrlSetup(ctrlShape, *args):
    """
    Prestep to generate new controls
    If nothing is selected, build a locator as temporary selection  
    
    Input
        ctrlShape:  "cube", "nail" or "circle"
                    Chosen via "Lost in space" UI
    """

    mySel = cmds.ls(os=1, fl=1)
    if not mySel:
        mySel = cmds.spaceLocator(n='deleteMe')
       
    for sel in mySel:
        cMakeCtrl(sel, ctrlShape)


def cMakeCtrl(sel, ctrlShape, *args):
    """
    Build the control curve

    Imput
        sel:        selection
        ctrlShape:  "cube", "nail" or "circle"

    Return:
        CON,       ctrl curve
        GRP        Grp name (parent of the ctrl)
    """

    CON = ''
    pos = []
    orient = [1, 0, 0]
    orientOption = cmds.radioCollection('rcXYZ', sl=1, q=1)
    if orientOption == 'rbOrientY':
        orient = [0, 1, 0]
    if orientOption == 'rbOrientZ':
        orient = [0, 0, 1]

    pos = cmds.xform(sel, translation=1, ws=1, q=1)

    if ctrlShape == 'cube':
        CON = cmds.curve(n=sel + '_con', d=1, p=[(5, 5, 5), (5, 5, -5), (-5, 5, -5), (-5, -5, -5), (5, -5, -5), (5, 5, -5), (-5, 5, -5), (-5, 5, 5), (5, 5, 5), (5, -5, 5), (5, -5,-5), (-5, -5, -5), (-5, -5, 5), (5, -5, 5), (-5, -5, 5), (-5, 5, 5)], k=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])

    if ctrlShape == 'nail' and orient == [1, 0, 0]:
        CON = cmds.curve(n=sel + '_con', d=1, p=[(0, 0, 0), (-5.639601, 0, 0), (-5.784686, 0, 0.350267), (-6.134953, 0, 0.495353), (-6.48522, 0, 0.350267), (-6.630306, 0, 0), (-6.48522, 0, -0.350267), (-6.134953, 0, -0.495353), (-5.784686, 0, -0.350267), (-5.639601, 0, 0)], k=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9])

    if ctrlShape == 'nail' and orient == [0, 1, 0]:
        CON = cmds.curve(n=sel + '_con', d=1, p=[(0, 0, 0), (0, 5.639601, 0), (0, 5.784686, 0.350267), (0, 6.134953, 0.495353), (0, 6.48522, 0.350267), (0, 6.630306, 0), (0, 6.48522, -0.350267), (0, 6.134953, -0.495353), (0, 5.784686, -0.350267), (0, 5.639601, 0)], k=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9])

    if ctrlShape == 'nail' and orient == [0, 0, 1]:
        CON = cmds.curve(n=sel + '_con', d=1, p=[(0, 0, 0), (0, 0, -5.639601), (0, 0.350267, -5.784686), (0, 0.495353, -6.134953), (0, 0.350267, -6.48522), (0, 0, -6.630306), (0, -0.350267, -6.48522), (0, -0.495353, -6.134953), (0, -0.350267, -5.784686), (0, 0, -5.639601)], k=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9])

    if ctrlShape == 'circle':
        CON = cmds.circle(n=sel + '_con', c=(0, 0, 0), nr=(orient[0], orient[1], orient[2]), sw=360, r=10, d=3, ut=0, tol=0.01, s=8, ch=0)

    GRP = cmds.group(n=sel + '_nul', empty=1)
    cmds.parent(CON, GRP)
    cmds.setAttr(GRP + '.translate', pos[0], pos[1], pos[2])
    cmds.select(CON, r=1)
    cScaleIcon()

    print 'delete me...'
    if cmds.objExists('deleteMe'):
        cmds.delete('deleteMe')

    return(CON, GRP)

    # cFillField('tfControl')


def cAddCtrlToSel(type, ctrlShape, *args):
    """
    Add ctrls
    Parent the selection to the ctrl curves

    Input
        type:       "parent"
                    "sel_under_ctrl"
    """

    mySel = cmds.ls(os=1)

    for sel in mySel:
        cmds.select(sel, r=1)
        ctrlList = cMakeCtrl(sel, ctrlShape)
        ctrl = ctrlList[0]
        ctrlGrp = ctrlList[1]
        dad = cmds.listRelatives(sel, p=1)

        if type == 'parent' and cmds.objectType(sel, isType='joint'):
            selPos = cmds.xform(sel, q=1, ws=1, t=1)
            selOri = cmds.getAttr(sel + '.jointOrient')
            cmds.setAttr(ctrlGrp + '.rotate', selOri[0][0], selOri[0][1], selOri[0][2])
            cmds.setAttr(ctrlGrp + '.translate', selPos[0], selPos[1], selPos[2])

            if dad:
                cmds.parent(ctrlGrp, dad)
                cmds.parent(sel, ctrl)

            cmds.select(ctrl, r=1)
            cAddNullGrp()


        if type == 'sel_under_ctrl': 
            cmds.parent(sel, ctrl)







def cScaleIcon(*args):
    """
    Scale a nurvbs curve via cvs
    """
    
    mySel = cmds.ls(sl=1)
    scale = cmds.floatField('fScaleIcon', v=1, q=1)
    for sel in mySel:
        origin = cmds.xform(sel, q=1, ws=1, t=1)

        crvs = cmds.listRelatives(sel, s=1, type='nurbsCurve')
        if crvs:
            print 'scale...'
            degree = cmds.getAttr(crvs[0] + ".degree")
            spans = cmds.getAttr(crvs[0] + ".spans")
            form = cmds.getAttr(crvs[0] + ".form")
            numCVs   = spans + degree;           

            if form == 2:
                numCVs -= degree            

            for i in range(0, numCVs, 1):  
                cvPos = cmds.xform(sel + '.cv[' + str(i) + ']', q=1, translation=1, ws=1)

                newPosX = (cvPos[0] - origin[0]) *scale +origin[0]            
                newPosY= (cvPos[1] - origin[1]) *scale +origin[1]            
                newPosZ = (cvPos[2] - origin[2]) *scale +origin[2]            
                cmds.xform(sel + '.cv[' + str(i) + ']', translation=(newPosX, newPosY, newPosZ), ws=1)                 


def cAssembleAttributes(type, *args):
    """
    Collect Infos to add a slide on a curve
    
    Input
        type:   "motionPath"

    """

    mySel = cmds.ls(os=1, fl=1)
    ctrl = cmds.textField('tfControl', tx=1, q=1) 

    if type == 'motionPath':
        print '-----------'
        print str(type) + ':'
       
        objType_dic = {}
        objType_dic = cSelToType(type)

        # cmds.select(ctrl, r=1)
        cAddAttrib(ctrl, 'double', 'offset', 'x', 'x', 'x', 'add')

        for key, value in objType_dic.items():
            print key
            print value
            plus = cmds.shadingNode('plusMinusAverage', asUtility=1)
            # cmds.select(value, r=1) 
            cAddAttrib(value, 'double', 'bindU', 'x', 'x', 'x', 'add')
            u = cmds.getAttr(value + '.uValue')
            cmds.setAttr(value + '.bindU', u)
            cmds.connectAttr(value + '.bindU', plus + '.input1D[0]', f=1) 
            cmds.connectAttr(ctrl + '.offset', plus + '.input1D[1]', f=1) 
            cmds.connectAttr(plus + '.output1D', value + '.uValue', f=1) 





def cAddLostAttr(attrType, state, *args):
    """
    Add attributes to a selection

    Input:
        attrType:       "double", "int", "bool"
        state:          "add", "remove"
    """
    
    attrList = []
    attrList = cmds.textField('tfAttr', tx=1, q=1).split()
    mySel = cmds.ls(os=1, type='transform')

    for attrName in attrList:
        for sel in mySel:
            cAddAttrib(sel, attrType, attrName, 'x', 'x', 'x', state)


def cConnectLost(attrName, *args):
    """
    connect attributes to selection
    Eg to connect ringScale to all child`s scale
    so far: ringScale, details 

    Input
        attrName:      attribute
    """

    mySel = cmds.ls(os=1)
    for sel in mySel:
        splits = sel.split('_')
        baseName = splits[0] + '_' + splits[1] + '_'

        print 'baseName: ' + str(baseName)

        if attrName == 'ringScale':
            # check attrName
            cAddAttrib(sel, 'double', 'ringScale', 'x', 'x', 1, 'add')

            drivenList = cmds.ls(str(baseName) + 'center_grp', type='transform')
            for driven in drivenList: 
                cmds.connectAttr(sel + '.' + attrName, driven + '.scaleX')
                cmds.connectAttr(sel + '.' + attrName, driven + '.scaleY')
                cmds.connectAttr(sel + '.' + attrName, driven + '.scaleZ')

        if attrName == 'details':
            # check attrName
            cAddAttrib(sel, 'bool', 'details', 'x', 'x', 1, 'add')

            drivenList = cmds.ls(str(baseName) + '*_half_con', type='transform')
            for driven in drivenList: 
                cmds.connectAttr(sel + '.' + attrName, driven + '.v')

            # driver:
            # loop_1_crv_center_grp_con
            
            # driven:
            # loop_1_crv_4_jnt_half_con 
            # loop_1_crv_3_jnt_half_con 
            # loop_1_crv_2_jnt_half_con 
            # loop_1_crv_1_jnt_half_con 
            # loop_1_crv_0_jnt_half_con 
            # loop_1_crv_7_jnt_half_con 
            # loop_1_crv_5_jnt_half_con 
            # loop_1_crv_6_jnt_half_con 



def cConnectLost_OLD(attrName, *args):
    """
    connect attributes to selection
    Eg to connect ringScale to all child`s scale
    so far: ringScale, details 

    Input
        attrName:      attribute
    """

    mySel = cmds.ls(os=1)
    for sel in mySel:
        splits = sel.split('_')
        baseName = splits[0] + '_' + splits[1]

        if attrName == 'ringScale':
            # check attrName
            cAddAttrib(sel, 'double', 'ringScale', 'x', 'x', 1, 'add')

            drivenList = cmds.ls(baseName + '*_center_grp', type='transform')
            for driven in drivenList: 
                cmds.connectAttr(sel + '.' + attrName, driven + '.scaleX')
                cmds.connectAttr(sel + '.' + attrName, driven + '.scaleY')
                cmds.connectAttr(sel + '.' + attrName, driven + '.scaleZ')

        if attrName == 'details':
            # check attrName
            cAddAttrib(sel, 'bool', 'details', 'x', 'x', 1, 'add')

            drivenList = cmds.ls(baseName + '*_half_con', type='transform')
            for driven in drivenList: 
                cmds.connectAttr(sel + '.' + attrName, driven + '.v')

            # driver:
            # loop_1_crv_center_grp_con
            
            # driven:
            # loop_1_crv_4_jnt_half_con 
            # loop_1_crv_3_jnt_half_con 
            # loop_1_crv_2_jnt_half_con 
            # loop_1_crv_1_jnt_half_con 
            # loop_1_crv_0_jnt_half_con 
            # loop_1_crv_7_jnt_half_con 
            # loop_1_crv_5_jnt_half_con 
            # loop_1_crv_6_jnt_half_con 


def cIncrementPos(fieldDriven, fieldPos, fieldCheck, *args):
    """
    check increments position 
    """

    text = ''
    driven = cmds.textField(fieldDriven, tx=1, q=1)
    countPos = cmds.intField(fieldPos, v=1, q=1)
    sp = driven.split('_')
    for i in range(0, countPos-1, 1):
        text += sp[i] + '_'
    text += ' <count> _'

    for i in range(countPos+1, len(sp)-1, 1):
        text += sp[i] + '_'
    text += sp[-1]

    cmds.textField(fieldCheck, tx=text, e=1)





def cDeriveFromDriver(fieldDriver, fieldPos, *args):
    """
    find driven objects by base name
    string fieldDriver
    int fieldPos

    Input
        fieldDriver:    driver field (UI)
        fieldPos:       int with increment divider
    """

    baseName = ''
    drivenList = []
    driver = cmds.textField(fieldDriver, tx=1, q=1)
    sp = driver.split('_')

    for i in range(0, fieldPos+1, 1):
        baseName += sp[i] + '_'

    drivenList = cmds.ls(str(baseName) + '*_con', type='transform')
    drivenList.remove(driver)

    cmds.textField('tfDriven', tx=drivenList[0], e=1)
    cIncrementPos('tfDriven', 'ifDriverCountPos', 'tfCheck')
    cCheckAmount('tfCheck')


def cDeriveFromDriven(fieldDriven, *args):
    """
    find all cons with the same base name

    Input
        fieldDriven:    driver field (UI)
    """

    cIncrementPos(fieldDriven, 'ifDriverCountPos', 'tfCheck')
    cCheckAmount('tfCheck')


def cCheckAmount(fieldCheck, *args):
    """
    How many objects of the given basename exist?
    Fill in the UI start and end

    Input
        fieldCheck:     field name of the check field (UI)

    Return
        drivenList,     list with all found driven dags 
        numDriven,      amount of founds
        start,          start value (int)
        end             end value (int)

    """

    splits = cmds.textField(fieldCheck, tx=1, q=1).split(' ')
    drivenList = cmds.ls(str(splits[0] + '*' + splits[2]), type='transform')
    numDriven = len(drivenList)
    start = 0
    end = numDriven
    cmds.intField('ifDrivenStart', v=0, e=1)
    cmds.intField('ifDrivenEnd', v=numDriven, e=1)

    return(drivenList, numDriven, start, end)


def cSelectMatching(field, *args):
    """
    Select matching objects

    Input
        field:      field to query
    """

    if field == 'tfDriver':
        name = cmds.textField(field, tx=1, q=1) 
        cmds.select(name, r=1)

    if field == 'tfCheck':
        sp = cmds.textField(field, tx=1, q=1).split(' ') 
        match = cmds.ls(sp[0] + '*' + sp[2])
        print match

        cmds.select(str(sp[0]) + '*' + str(sp[2]), r=1)




def cWriteExpr(action, *args):
    """
    write wave expression
    """

    driver = cmds.textField('tfDriver', tx=1, q=1)
    drivenList = cCheckAmount('tfCheck')
    driven = drivenList[0]
    start = drivenList[2]
    end = drivenList[3]

    if action is not 'delete' and not cmds.objExists('exWave_' + str(driver)):
        cAddAttrib(driver, 'float', 'wEnv', 0, 1, 1, 'add')
        cAddAttrib(driver, 'float', 'wAmplitude', 0, 'x', 0, 'add')
        cAddAttrib(driver, 'float', 'wSpeed', 0, 'x', .1, 'add')
        cAddAttrib(driver, 'float', 'frameOffset', 'x', 'x', 0, 'add')

        exp1 = 'expression -s "'
        exp2 = ''
        exp3 = '" -o loop_1_crv_center_grp_con -ae 1 -uc all -n "exWave_' + str(driver) + '";'

        for i in range(start, end, 1):
            cAddAttrib(driven[i], 'float', 'wEnv', 0, 1, 1, 'add')
            cAddAttrib(driven[i], 'float', 'frameOffset', 'x','x', 0, 'add')

            exp2 += str(driven[i]) + '_OFF.translateX = ' + str(driver) + '.wAmplitude * ' + str(driver) + '.wEnv * ' + str(driven[i]) + '.wEnv * sin((frame + ' + str(driver) + '.frameOffset + ' + str(driven[i]) + '.frameOffset) * ' + str(driver) + '.wSpeed);\\n'

        exp = exp1 + exp2 + exp3

        if action == 'print':
            print exp

        if action == 'write':
            mel.eval(exp)

    if action is 'delete':
        cmds.delete('exWave_' + str(driver))

    else:
        cmds.textField('tfFeedback', tx = 'expression already existing', e=1) 


def cWriteExprBatch(action, *args):
    """
    batch write wave expression for all selected objects
    """

    selection = cmds.ls(os=1)

    for sel in selection:
        cmds.select(sel, r=1)
        cFillField('tfDriver')
        cSelectMatching('tfCheck')
        cWriteExpr(action)

    cmds.select(selection, r=1)



def cRandom(action, incrPerGuide, *args):
    """
    Randomize attributes

    Input
        action:         increment
                        random
        incrPerGuide:  increment per mainGroup

    """

    print 'incrPerGuide: ' + str(incrPerGuide)

    mySel = cmds.ls(os=1)
    attributes = cmds.textField('tfAttrChange', tx=1, q=1).split(' ')
    fromValue = cmds.floatField('fFromValue', v=1, q=1)
    incrValue = cmds.floatField('fIncrement', v=1, q=1)

    newValue = fromValue + incrPerGuide
    if action == 'increment':
        print 'increment...'
        for sel in mySel:
            newValue = newValue + incrValue
            for i in range(0, len(attributes),1):
                print 'newValue: ' + str(newValue)
                cmds.setAttr(sel + '.' + attributes[i], newValue)

    if action == 'random':
        print 'random...'
        for sel in mySel:
            for i in range(0, len(attributes),1):
                newValue = random.uniform(fromValue, incrValue)
                print 'sel: ' + str(sel)
                print 'newValue: ' + str(newValue)
                cmds.setAttr(sel + '.' + attributes[i], newValue)


def cRandomBatch(action, *args):
    """
    batch randomize values for selected objects

    """

    selection = cmds.ls(os=1)
    incrPerGuide = cmds.floatField('fIncrementPerObj', v=1, q=1)
    newIncr = incrPerGuide

    for sel in selection:
        cmds.select(sel, r=1)
        cFillField('tfDriver')
        cSelectMatching('tfCheck')
        cRandom(action, newIncr)
        newIncr += incrPerGuide
    
    cmds.select(selection, r=1)




def cFindClosestOnMesh(*args):
    """
    Given a or more vertices
    Find the cloest point on a mesh

    """
    counter = cmds.intField('iIndex', v=1, q=1)
    mesh = cmds.textField('tfTargetMesh', tx=1, q=1)
    mySel = cmds.ls(sl=1, fl=1)

    # title = 'win_Progress'
    # progressBarName = 'pProgress'
    # winProgress(title, progressBarName, len(mySel))


    for vtx in mySel:
        # cmds.progressBar(progressBarName, e=1, step=1)
        baseName = vtx.split('.')[0]
        posTip = cmds.xform(vtx, ws=1, t=1, q=1)
        LC_in = cmds.spaceLocator(n='deleteMe_LC', p=(0,0,0))[0]
        LC_out =  cmds.spaceLocator(n='deleteMe_LC_out', p=(0,0,0))[0]

        cmds.setAttr(LC_in + '.translate', posTip[0], posTip[1], posTip[2])
        cp = cmds.createNode('closestPointOnMesh', n='cp_tk')

        cmds.connectAttr(mesh + '.outMesh', cp + '.inMesh')
        cmds.connectAttr(LC_in + '.translate', cp + '.inPosition')
        cmds.connectAttr(cp + '.result.position', LC_out + '.translate')
        u = cmds.getAttr(cp + '.u')
        v = cmds.getAttr(cp + '.v')

        pos = cmds.xform(LC_out, ws=1, t=1, q=1)

        cCreateFollicle(mesh, baseName, counter, u, v, pos, posTip)

        cmds.delete(cp, LC_in, LC_out)
        counter +=1 

    # cmds.deleteUI(title)


def cCreateFollicle(mesh, baseName, counter, u, v, pos, posTip, *args):
    """
    create a follicle on the given mesh at the give uv ccord

    Input
    mesh:
    basename
    counter
    u
    v
    pos
    posTip


    """


    meshShp = ''
    up = cmds.textField('tfLocatorUp', tx=1, q=1)
    
    meshShapes = cmds.listRelatives(mesh, s=1)
    for shp in meshShapes:
        intermed = cmds.getAttr(shp + '.intermediateObject')
        if intermed == 0:
            meshShp = shp

    FOL = cmds.createNode('transform', n=baseName + '_' + str(counter) + '_FOL', ss=1)
    fol = cmds.createNode('follicle', n=baseName + '_' + str(counter) + '_FOLShape', p=FOL, ss=1)

    cmds.connectAttr(meshShp + '.worldMesh', fol + '.inputMesh')
    cmds.connectAttr(meshShp + '.worldMatrix[0]', fol + '.inputWorldMatrix')
    cmds.connectAttr(fol + '.outRotate', FOL + '.rotate')
    cmds.connectAttr(fol + '.outTranslate', FOL + '.translate')
    cmds.setAttr(FOL + '.inheritsTransform', 0)
    cmds.setAttr(fol + '.parameterU', u)
    cmds.setAttr(fol + '.parameterV', v)

    cmds.select(clear=1)
    jntBase = cmds.joint(p=(pos[0], pos[1], pos[2]), n=(baseName + '_' + str(counter) + '_base_jnt'))
    jntTip = cmds.joint(p=(posTip[0], posTip[1], posTip[2]), n=(baseName + '_' + str(counter) + '_tip_jnt'))

    cmds.select(jntBase, r=1)
    grp = cAddNullGrp()
    
    cmds.select(clear=1)

    cmds.parent(grp, FOL)
    cmds.joint(jntBase, jntTip, e=1, oj='xyz', secondaryAxisOrient='zup', ch=1, zso=1) 

    cOrientJnts(jntBase, jntTip, up)


def cGetVertexID(field, *args):
    curSel = cmds.ls(sl=1, fl=1)[0]
    id = int(curSel.split('[')[1].split(']')[0])
    cmds.intField(field, v=id, e=1)



def cSelNthVertex(*args):
    """
    Select the first nth of every poly shell
    To eg select one cv of every tooth of a teeth
    """
    counter = 0
    vtx_dict = {}
    vtxList = []
    vtxListCollect = []
     
    nth = cmds.intField('iNthVertexId', v=1, q=1)
    teethMesh = cmds.textField('tfTeethMesh', tx=1, q=1)
    numVtx = cmds.polyEvaluate(teethMesh, vertex=1)

    # title = 'win_Progress'
    # progressBarName = 'pProgress'
    # winProgress(title, progressBarName, numVtx)

    for i in range(0, numVtx, 1):
        # cmds.progressBar(progressBarName, e=1, step=1)
        if not i in vtxListCollect: 
            cmds.select(teethMesh + '.vtx[' + str(i) + ']', r=1)
            cmds.polySelectConstraint(m=2, t=1, shell=1) 
            curSel = cmds.ls(sl=1, fl=1)

            for vtx in curSel:
                id = vtx.split('[')[1].split(':')[-1].split(']')[0]
                if id not in vtxListCollect:
                    vtxList.append(id)
                    vtxListCollect.append(id)

            if vtxList:
                vtx_dict[str(counter)] = vtxList
                counter +=1
                vtxList = []

    # cmds.deleteUI(title)
    cmds.polySelectConstraint(shell=0)
    cmds.select(clear=1)

    for key, value in vtx_dict.items():
        vtxList = value
        cmds.select(teethMesh + '.vtx[' + str(vtxList[nth]) + ']', add=1)

 



def cOrientJnts(jntBase, jntTip, up, *args):
    """
    Orient joints to an up vector
    """

    jntTip =  cmds.parent(jntTip, w=1)[0]
    cmds.setAttr(jntBase + '.jo', 0,0,0)
    cmds.setAttr(jntBase + '.rotate', 0,0,0)

    aimConstr = cmds.aimConstraint(jntTip, jntBase, worldUpType="object", worldUpObject=up, aimVector=(1,0,0), upVector=(0,1,0))
    # aimConstraint -offset 0 0 0 -weight 1 -aimVector 1 0 0 -upVector 0 1 0 -worldUpType "object" -worldUpObject locator1;
    cmds.delete(aimConstr)

    rot = cmds.getAttr(jntBase + '.r')
    cmds.setAttr(jntBase + '.jo', rot[0][0], rot[0][1], rot[0][2])
    cmds.setAttr(jntBase + '.r', 0,0,0)
    cmds.parent(jntTip, jntBase)


def cFindClosestBatch(*args):
    batchIndex = cmds.intField('iIndex', v=1, q=1)
    curSel = cmds.ls(os=1)
    amount = int(len(curSel))

    title = 'win_Progress'
    progressBarName = 'pProgress'
    winProgress(title, progressBarName, amount)

    for sel in curSel:
        cmds.progressBar(progressBarName, e=1, step=1)
        cmds.select(sel, r=1)
        cFillField('tfTeethMesh')
        cSelNthVertex()
        cFindClosestOnMesh()
        batchIndex +=1
        cmds.intField('iIndex', v=batchIndex, e=1)

    cmds.deleteUI(title)
    cmds.select(curSel, r=1)


def cBatchSkin(*args):
    curSel = cmds.ls(os=1)
    
    for sel in curSel:
        bindJnts = cmds.ls(sel + '*' + 'tip_jnt')
        if len(bindJnts) == 1:
            print sel
            print bindJnts[0]
            cmds.skinCluster(sel, bindJnts[0], tsb=1)


def cRemoveFromNmSpc(*args):
    mySel = cmds.ls(sl=1, fl=1)
    # nmSpc = cmds.textField('tfNmSpc', tx=1, q=1)

    for sel in mySel:
        newName = sel.split(':')[1]

        cmds.rename(sel, newName)





ver = 'v0.2';
windowStartHeight = 150;
windowStartWidth = 440;
bh1 = 18;
bh2 = 22;
colRed              = [0.44, 0.2, 0.2]
colBlue             = [0.18, 0.28, 0.34]
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



if cmds.window('win_tkLostInSpaceHelper', exists=1):
    cmds.deleteUI('win_tkLostInSpaceHelper')
myWindow = cmds.window('win_tkLostInSpaceHelper', t=('Lost In Space Helper ' + ver), s=1, wh=(windowStartHeight, windowStartWidth ))

cmds.columnLayout(adj=1, bgc=(colUI2[0], colUI2[1], colUI2[2]))
cmds.rowColumnLayout(nc=9, cw=[(1, 40), (2, 40), (3, 55), (4, 55), (5, 55), (6, 55), (7, 45), (8, 75), (9, 20)])
# cmds.rowColumnLayout(nc=8, cw=[(1, 55), (2, 55), (3, 55), (4, 55), (5, 55), (6, 55), (7, 55), (8, 55)])
cmds.button(l='Down', c=partial(cSelectLevel, 'selectForMe', 1, 0), bgc=(colYellow[0], colYellow[1], colYellow[2]))
cmds.button(l='Up', c=partial(cWalkUp), bgc=(colYellow[0], colYellow[1], colYellow[2]))
cmds.button(l='Tgl Jnts', c=partial(cJointsVis), bgc=(colYellow2[0], colYellow2[1], colYellow2[2]))
cmds.button(l='Jnt Size', c=partial(cJointSize), bgc=(colBlue[0], colBlue[1], colBlue[2]))
cmds.button(l='To Jnts', c=partial(cSelToJoints), bgc=(colYellow2[0], colYellow2[1], colYellow2[2]))
cmds.button(l='OFF', c=partial(cAddNullGrp), bgc=(colBlue[0], colBlue[1], colBlue[2]))
cmds.button(l='Order', c=partial(cReOrder), bgc=(colYellow2[0], colYellow2[1], colYellow2[2]))
cmds.button(l='Empty Grps', c=partial(cRemoveEmptyTransforms), bgc=(colRed[0], colRed[1], colRed[2]))
cmds.button(l='SE', c=partial(cClearSE), bgc=(colRed[0], colRed[1], colRed[2]))
cmds.setParent(top=1)



cmds.columnLayout(adj=1, bgc=(colUI[0], colUI[1], colUI[2]))
cmds.frameLayout('flRigSetup', l='RIG SETUP', fn='smallPlainLabelFont', bgc=(colUI2[0], colUI2[1], colUI2[2]), cll=1, cl=1, cc=partial(cShrinkWin, 'win_tkLostInSpaceHelper'))
cmds.columnLayout('layAdj', adj=1)


cmds.frameLayout('flCurves', l='--------------- CURVES -----------------------------', fn='smallPlainLabelFont', bgc=(colYellow5[0], colYellow5[1], colYellow5[2]))
cmds.columnLayout(adj=1, bgc=(colUI2[0], colUI2[1], colUI2[2]))

cmds.rowColumnLayout(nc=4, cw=[(1, 110), (2, 110), (3, 50), (4, 170)])
cmds.button(l='Loop To Curves', c=partial(cEdegloopToCurves), bgc=(colYellow4[0], colYellow4[1], colYellow4[2]))
cmds.button(l='Start ID >>', c=partial(cGetID), bgc=(colYellow2[0], colYellow2[1], colYellow2[2]))
cmds.intField('ifID', min=0, ed=1, v=0, bgc=(0,0,0))
cmds.button(l='Crv With New Start', c=partial(cCutAsStart), bgc=(colYellow4[0], colYellow4[1], colYellow4[2]))


cmds.setParent('layAdj')
cmds.frameLayout('flJntsOnCurves', l='--------------- JOINTS ON CURVES ---------------', fn='smallPlainLabelFont', bgc=(colYellow5[0], colYellow5[1], colYellow5[2]))
# cmds.columnLayout(adj=1)
cmds.rowColumnLayout(nc=4, cw=[(1, 55), (2, 95), (3, 110), (4, 180)])
cmds.intField('fBonesNumber', v=8) 
cmds.button(l='... Just Place', c=partial(cBonesOnCurve, 'bonesOnly'), bgc=(colYellow4[0], colYellow4[1], colYellow4[2]))
cmds.button(l='... On Curve CVs', c=partial(cBonesOnCurve, 'bonesCV'), bgc=(colYellow2[0], colYellow2[1], colYellow2[2]))
cmds.button(l='... JNTs On Curve As Motionpath', c=partial(cBonesOnCurve, 'bonesMP'), bgc=(colYellow4[0], colYellow4[1], colYellow4[2]))

cmds.setParent('layAdj')
cmds.rowColumnLayout(nc=5, cw=[(1, 55), (2, 110), (3, 55), (4, 120), (5, 100)])
cmds.button(l='From >>', c=partial(cFillField, 'tfFromJnt'), bgc=(colYellow2[0], colYellow2[1], colYellow2[2]))
cmds.textField('tfFromJnt', ed=0, bgc=(0,0,0))
cmds.button(l='To >>', c=partial(cFillField, 'tfToJnt'), bgc=(colYellow2[0], colYellow2[1], colYellow2[2]))
cmds.textField('tfToJnt', ed=0, bgc=(0,0,0))
cmds.button(l='Create SplineIK', c=partial(cSplineIK), bgc=(colYellow4[0], colYellow4[1], colYellow4[2]))


cmds.setParent('layAdj')
cmds.frameLayout('flJntPivots', l='--------------- SET JNT PIVOT ---------------------', fn='smallPlainLabelFont', bgc=(colYellow5[0], colYellow5[1], colYellow5[2]))
cmds.rowColumnLayout(nc=8, cw=[(1, 30), (2, 50), (3, 90), (4, 10), (5, 50), (6, 50), (7, 50), (8, 110)], bgc=(colYellow5[0], colYellow5[1], colYellow5[2]))
# cmds.rowColumnLayout(nc=7, cw=[(1, 80), (2, 90), (3, 10), (4, 50), (5, 50), (6, 50), (7, 110)], bgc=(colYellow5[0], colYellow5[1], colYellow5[2]))

cmds.button(l='LC', c=partial(cCreateNode, 'spaceLocator', 'tfPivot'), bgc=(colYellow4[0], colYellow4[1], colYellow4[2]))
cmds.button(l='LC >>', c=partial(cFillField, 'tfPivot'), bgc=(colYellow2[0], colYellow2[1], colYellow2[2]))
cmds.textField('tfPivot', ed=0, tx='', bgc=(0,0,0))
cmds.text(' ')
cmds.checkBox('cbX', l='X', v=0)
cmds.checkBox('cbY', l='Y', v=1)
cmds.checkBox('cbZ', l='Z', v=1)
cmds.button(l='Adjust Pivot', c=partial(cAdjustPivot), bgc=(colYellow2[0], colYellow2[1], colYellow2[2]))


cmds.setParent('layAdj')
cmds.frameLayout('flJntOperations', l='--------------- MAKE JOINT CHAINS --------------', fn='smallPlainLabelFont', bgc=(colYellow5[0], colYellow5[1], colYellow5[2]))
cmds.rowColumnLayout(nc=4, cw=[(1, 80), (2, 110), (3, 140), (4, 110)])
cmds.button(l='Jnts To Chain', c=partial(cJntsToChain, 'parent'), bgc=(colYellow4[0], colYellow4[1], colYellow4[2]))
cmds.button(l='Objs To New Chain', c=partial(cObjToChain, 'new'), bgc=(colYellow2[0], colYellow2[1], colYellow2[2]))
cmds.button(l='Jnts From Sel And Parent', c=partial(cJntsFromSelection, 1), bgc=(colYellow4[0], colYellow4[1], colYellow4[2]))
cmds.button(l='Halfway Joint Up', c=partial(cHalfwayJnt, 'up'), bgc=(colYellow2[0], colYellow2[1], colYellow2[2]))
cmds.setParent('..')


cmds.setParent('layAdj')
cmds.frameLayout('flCTRLs', l='--------------- CTRLs -------------------------------', fn='smallPlainLabelFont', bgc=(colYellow5[0], colYellow5[1], colYellow5[2]))


# cmds.rowColumnLayout(nc=4, cw=[(1, 90), (2, 90), (3, 150), (4, 110)])
# cmds.text('U To CTRL', bgc=(colYellow5[0], colYellow5[1], colYellow5[2]))
# cmds.button(l='Control >>', c=partial(cFillField, 'tfControl'), bgc=(colYellow2[0], colYellow2[1], colYellow2[2]))
# cmds.textField('tfControl', ed=0, tx='curve1', bgc=(0,0,0))
# cmds.button(l='Mo Path Offset', c=partial(cAssembleAttributes, 'motionPath'), bgc=(colYellow4[0], colYellow4[1], colYellow4[2]))


cmds.rowColumnLayout(nc=9, cw=[(1, 55), (2, 55), (3, 55), (4, 15), (5, 50), (6, 50), (7,50), (8, 50), (9, 60)], bgc=(colYellow5[0], colYellow5[1], colYellow5[2]))
cmds.button(l='Cube', c=partial(cCtrlSetup, 'cube'), bgc=(colYellow4[0], colYellow4[1], colYellow4[2]))
cmds.button(l='Nail', c=partial(cCtrlSetup, 'nail'), bgc=(colYellow2[0], colYellow2[1], colYellow2[2]))
cmds.button(l='Circle', c=partial(cCtrlSetup, 'circle'), bgc=(colYellow4[0], colYellow4[1], colYellow4[2]))
cmds.radioCollection('rcXYZ')
cmds.text(' ')
cmds.radioButton('rbOrientX', label='X')
cmds.radioButton('rbOrientY', label='Y', sl=1)
cmds.radioButton('rbOrientZ', label='Z')
cmds.button(l='Scale', c=partial(cScaleIcon), bgc=(colYellow4[0], colYellow4[1], colYellow4[2]))
cmds.floatField('fScaleIcon', v=.1, ed=1, pre=2, bgc=(0,0,0))

cmds.setParent('layAdj')
cmds.rowColumnLayout(nc=2, cw=[(1, 220), (2, 220)])
cmds.button(l='Sel Under New Ctrl (guide cons)', c=partial(cAddCtrlToSel,'sel_under_ctrl', 'nail'), bgc=(colYellow[0], colYellow[1], colYellow[2]))
cmds.button(l='Parent Ctrl To Sel (half cons)', c=partial(cAddCtrlToSel,'parent', 'cube'), bgc=(colYellow2[0], colYellow2[1], colYellow2[2]))

cmds.button(l='Multi Parent', c=partial(cMultiParent), bgc=(colYellow5[0], colYellow5[1], colYellow5[2]))
cmds.button(l='Add Ctrl At Sel', c=partial(cAddCtrlToSel, 'add', 'cube'), bgc=(colYellow5[0], colYellow5[1], colYellow5[2]))


cmds.setParent('layAdj')
cmds.rowColumnLayout(nc=13, cw=[(1,25), (2,25), (3,25), (4,50), (5,25), (6,25), (7,25), (8,50), (9,25), (10,25), (11,25), (12,50), (13,65)], bgc=(colYellow5[0], colYellow5[1], colYellow5[2]))
cmds.button(l='-', c=partial(cIncrease, 'fOffsetX', -1))
cmds.button(l='+', c=partial(cIncrease, 'fOffsetX', 1))
cmds.button(l='X', c=partial(cResetField, 'fOffsetX', 0))
cmds.floatField('fOffsetX', pre=3, v=1)

cmds.button(l='-', c=partial(cIncrease, 'fOffsetY', -1), bgc=(colYellow2[0], colYellow2[1], colYellow2[2]))
cmds.button(l='+', c=partial(cIncrease, 'fOffsetY', +1), bgc=(colYellow2[0], colYellow2[1], colYellow2[2]))
cmds.button(l='Y', c=partial(cResetField, 'fOffsetY', 0), bgc=(colYellow2[0], colYellow2[1], colYellow2[2]))
cmds.floatField('fOffsetY', pre=3, v=0)

cmds.button(l='-', c=partial(cIncrease, 'fOffsetZ', -1))
cmds.button(l='+', c=partial(cIncrease, 'fOffsetZ', +1))
cmds.button(l='Z', c=partial(cResetField, 'fOffsetZ', 0))
cmds.floatField('fOffsetZ', pre=3, v=0)

cmds.button(l='Offset CVs', c=partial(cOffsetCVs), bgc=(colYellow4[0], colYellow4[1], colYellow4[2]))




cmds.setParent(top=1)
cmds.frameLayout('flTeeth', l='TEETH SETUP', fn='smallPlainLabelFont', bgc=(colUI2[0], colUI2[1], colUI2[2]), cll=1, cl=1, cc=partial(cShrinkWin, 'win_tkLostInSpaceHelper'))

cmds.columnLayout('layAdjTeeth', adj=1)
cmds.rowColumnLayout(nc=5, cw=[(1, 90), (2, 90), (3, 30), (4,140), (5,90)])

cmds.button(l='Target Mesh >>', c=partial(cFillField, 'tfTargetMesh'), bgc=(colYellow5[0], colYellow5[1], colYellow5[2]))
cmds.textField('tfTargetMesh', tx='lam_01:LampreyLarge_mouth_lo_geo', ed=0, bgc=(0,0,0))
cmds.button(l='LC', c=partial(cCreateNode, 'spaceLocator', 'tfLocatorUp'), bgc=(colYellow4[0], colYellow4[1], colYellow4[2]))
cmds.button(l='Up Locator For JNTs >>', c=partial(cFillField, 'tfLocatorUp'), bgc=(colYellow2[0], colYellow2[1], colYellow2[2]))
cmds.textField('tfLocatorUp', tx='mainTeeth_LC', ed=0, bgc=(0,0,0))

cmds.setParent('layAdjTeeth')
cmds.rowColumnLayout(nc=5, cw=[(1, 90), (2, 90), (3, 90), (4,50), (5,120)])
cmds.button(l='Teeth Mesh >>', c=partial(cFillField, 'tfTeethMesh'), bgc=(colYellow5[0], colYellow5[1], colYellow5[2]))
cmds.textField('tfTeethMesh', tx='lam_01:fangLarge_001_geo', ed=0, bgc=(0,0,0))
cmds.button(l='Nth Vertex Id >>', c=partial(cGetVertexID, 'iNthVertexId'), bgc=(colYellow5[0], colYellow5[1], colYellow5[2]))
# cmds.text('Nth Vertex Id', bgc=(colYellow5[0], colYellow5[1], colYellow5[2]))
cmds.intField('iNthVertexId', v=19)
cmds.button(l='Select Nth Vertex', c=partial(cSelNthVertex), bgc=(colYellow4[0], colYellow4[1], colYellow4[2]))

cmds.setParent('layAdjTeeth')
cmds.rowColumnLayout(nc=3, cw=[(1, 90), (2, 90), (3, 260)])
cmds.text('Index Start', bgc=(colYellow5[0], colYellow5[1], colYellow5[2]))
cmds.intField('iIndex', v=1)
cmds.button(l='Each Vertex To JNTS On Mesh', c=partial(cFindClosestOnMesh), bgc=(colYellow4[0], colYellow4[1], colYellow4[2]))

cmds.setParent('layAdjTeeth')
# cmds.rowColumnLayout(nc=3, cw=[(1, 90), (2, 90), (3, 260)])
cmds.rowColumnLayout(nc=2, cw=[(1, 180), (2, 260)])
cmds.button(l='Batch Skin', c=partial(cBatchSkin), bgc=(colGreen[0], colGreen[1], colGreen[2]))
cmds.button(l='Batch - Same Vtx Count / Order Required!', c=partial(cFindClosestBatch), bgc=(colRed[0], colRed[1], colRed[2]))





cmds.setParent(top=1)
cmds.frameLayout('flAttributesAndConnections', l='ATTRIBUTES AND CONNECTIONS', fn='smallPlainLabelFont', bgc=(colUI2[0], colUI2[1], colUI2[2]), cll=1, cl=0, cc=partial(cShrinkWin, 'win_tkLostInSpaceHelper'))

cmds.columnLayout('layAdjAttr', adj=1)
cmds.rowColumnLayout(nc=6, cw=[(1, 90), (2, 90), (3, 60), (4, 60), (5, 60), (6, 80)])
cmds.button(l='Attr >>', c=partial(cSetAttr, 'tfAttr'), bgc=(colYellow5[0], colYellow5[1], colYellow5[2]))
cmds.textField('tfAttr', tx='ringScale', bgc=(0,0,0))
cmds.button(l='Float', c=partial(cAddLostAttr, 'double', 'add'), bgc=(colYellow4[0], colYellow4[1], colYellow4[2]))
cmds.button(l='Integer', c=partial(cAddLostAttr, 'long', 'add'), bgc=(colYellow2[0], colYellow2[1], colYellow2[2]))
cmds.button(l='Boolean', c=partial(cAddLostAttr, 'bool', 'add'), bgc=(colYellow4[0], colYellow4[1], colYellow4[2]))
cmds.button(l='Delete Attr', c=partial(cAddLostAttr, 'any', 'remove'), bgc=(colRed[0], colRed[1], colRed[2]))



# cmds.button(l='Connect To >>', c=partial(cSetAttr, 'tfToAttr'), bgc=(colYellow5[0], colYellow5[1], colYellow5[2]))
# cmds.textField('tfToAttr', tx='', bgc=(0,0,0))
# cmds.button(l='Connect', c=partial(cConnectAttr), bgc=(colGreen[0], colGreen[1], colGreen[2]))

cmds.setParent('layAdjAttr')
cmds.frameLayout('fPresets', l='--------------- LOST CONNECTIONS --------------------', fn='smallPlainLabelFont', bgc=(colYellow5[0], colYellow5[1], colYellow5[2]))
cmds.rowColumnLayout(nc=3, cw=[(1, 110), (2, 110), (3, 220)])
cmds.button(l='Setup Ring Scale', c=partial(cConnectLost, 'ringScale'), bgc=(colYellow4[0], colYellow4[1], colYellow4[2]))
cmds.button(l='Setup Details', c=partial(cConnectLost, 'details'), bgc=(colYellow2[0], colYellow4[1], colYellow4[2]))
cmds.button(l='Add Geo Chooser', c=partial(cAddGeoAttribute), bgc=(colYellow4[0], colYellow4[1], colYellow4[2]))


# cmds.setParent('layAdjAttr')
# cmds.button(l='nmSpc >>', c=partial(cFillField, 'tfNmSpc'), bgc=(colYellow4[0], colYellow4[1], colYellow4[2]))
# cmds.textField('tfNmSpc', tx='', bgc=(0,0,0))
cmds.text(' ', bgc=(colYellow5[0], colYellow5[1], colYellow5[2]))
cmds.text(' ', bgc=(colYellow5[0], colYellow5[1], colYellow5[2]))
cmds.button(l='Remove NmSpc From Selection', c=partial(cRemoveFromNmSpc), bgc=(colYellow2[0], colYellow2[1], colYellow2[2]))


cmds.setParent('layAdjAttr')
cmds.frameLayout('fCreateNodes', l='--------------- CREATE MULTIPLE NODES AND CONNECT --------------------', fn='smallPlainLabelFont', bgc=(colYellow5[0], colYellow5[1], colYellow5[2]))
cmds.rowColumnLayout(nc=4, cw=[(1, 110), (2, 110), (3, 110), (4, 110)])
cmds.button(l='Node Type >>', c=partial(cFillField, 'tfNodeType'), bgc=(colYellow5[0], colYellow5[1], colYellow5[2]))
cmds.textField('tfNodeType', tx='multiplyDivide', ed=0, bgc=(0,0,0))
cmds.button(l='New Name >>', c=partial(cFillField, 'tfNodeNewName'), bgc=(colYellow5[0], colYellow5[1], colYellow5[2]))
cmds.textField('tfNodeNewName', tx='contractMult', bgc=(0,0,0))

cmds.button(l='From Attr >>', c=partial(cSetAttr, 'tfFromAttr'), bgc=(colYellow5[0], colYellow5[1], colYellow5[2]))
cmds.textField('tfFromAttr', tx='contract', ed=0, bgc=(0,0,0))
cmds.button(l='To Attr >>', c=partial(cSetAttr, 'tfToAttr'), bgc=(colYellow5[0], colYellow5[1], colYellow5[2]))
cmds.textField('tfToAttr', tx='i1x', ed=0, bgc=(0,0,0))

cmds.setParent('layAdjAttr')
cmds.rowColumnLayout(nc=3, cw=[(1, 110), (2, 110), (3, 220)])
cmds.text('Count From', bgc=(colYellow5[0], colYellow5[1], colYellow5[2]))
cmds.intField('ifCountFrom', v=1)
cmds.button(l='Create And Connect', c=partial(cCreateNodeAndConnect, 'tfToAttr'), bgc=(colYellow4[0], colYellow4[1], colYellow4[2]))




cmds.setParent(top=1)
cmds.frameLayout('flExpressions', l='WAVE EXPRESSIONS', fn='smallPlainLabelFont', bgc=(colUI2[0], colUI2[1], colUI2[2]), cll=1, cl=1, cc=partial(cShrinkWin, 'win_tkLostInSpaceHelper'))

cmds.columnLayout('layAdjExpr', adj=1)
cmds.rowColumnLayout(nc=3, cw=[(1,40), (2,70), (3,330)])
cmds.button(l='Sel', c=partial(cSelectMatching, 'tfDriver'), bgc=(colYellow5[0], colYellow5[1], colYellow5[2]))
cmds.button(l='Driver >>', c=partial(cFillField, 'tfDriver'), bgc=(colYellow4[0], colYellow4[1], colYellow4[2]))
cmds.textField('tfDriver', tx='', bgc=(0,0,0))

cmds.setParent('layAdjExpr')
cmds.rowColumnLayout(nc=7, cw=[(1, 40), (2, 70), (3, 150), (4, 50), (5, 40), (6, 50), (7, 40)])
cmds.button(l='Sel', c=partial(cSelectMatching, 'tfCheck'), bgc=(colYellow5[0], colYellow5[1], colYellow5[2]))
cmds.button(l='Driven >>', c=partial(cFillField, 'tfDriven'), bgc=(colYellow3[0], colYellow3[1], colYellow3[2]))
cmds.textField('tfDriven', tx='', bgc=(0,0,0))
cmds.text('Start', bgc=(colYellow3[0], colYellow3[1], colYellow3[2]))
cmds.intField('ifDrivenStart', v=0)
cmds.text('End', bgc=(colYellow3[0], colYellow3[1], colYellow3[2]))
cmds.intField('ifDrivenEnd', v=8)

cmds.setParent('layAdjExpr')
cmds.rowColumnLayout(nc=3, cw=[(1, 90), (2, 20), (3, 330)])
cmds.button(l='Increment Pos', c=partial(cIncrementPos, 'tfDriven', 'ifDriverCountPos', 'tfCheck'), bgc=(colYellow3[0], colYellow3[1], colYellow3[2]))
cmds.intField('ifDriverCountPos', v=3, cc=partial(cIncrementPos, 'tfDriven', 'ifDriverCountPos', 'tfCheck'))
cmds.textField('tfCheck', tx='', ed=0, bgc=(colUI1[0], colUI1[1], colUI1[2]))

cmds.setParent('layAdjExpr')
cmds.rowColumnLayout(nc=3, cw=[(1, 110), (2, 220), (3, 110)])
cmds.button(l='Print Expression', c=partial(cWriteExpr, 'print'), bgc=(colYellow3[0], colYellow3[1], colYellow3[2]))
cmds.button(l='Write Expression', c=partial(cWriteExpr, 'write'), bgc=(colYellow4[0], colYellow4[1], colYellow4[2]))
cmds.button(l='Delete Expression', c=partial(cWriteExpr, 'delete'), bgc=(colRed[0], colRed[1], colRed[2]))

cmds.setParent('layAdjExpr')
cmds.rowColumnLayout(nc=2, cw=[(1, 330), (2, 110)])
cmds.button(l='Batch Write', c=partial(cWriteExprBatch, 'write'), bgc=(colYellow4[0], colYellow4[1], colYellow4[2]))
cmds.button(l='Batch Delete', c=partial(cWriteExprBatch, 'delete'), bgc=(colRed[0], colRed[1], colRed[2]))



cmds.setParent('layAdjExpr')
cmds.frameLayout('fChangeValues', l='--------------- CHANGE VALUES -----------------------', fn='smallPlainLabelFont', bgc=(colYellow5[0], colYellow5[1], colYellow5[2]))
cmds.rowColumnLayout(nc=8, cw=[(1, 60), (2, 90), (3, 50), (4, 40), (5, 50), (6, 40), (7,55), (8,55)])

cmds.button(l='Attr >>', c=partial(cSetAttr, 'tfAttrChange'), bgc=(colYellow5[0], colYellow5[1], colYellow5[2]))
cmds.textField('tfAttrChange', tx='frameOffset', bgc=(0,0,0))
cmds.button(l='From',  c=partial(cResetField, 'fFromValue', 0), bgc=(colYellow5[0], colYellow5[1], colYellow5[2]))
cmds.floatField('fFromValue', v=0, pre=2)
cmds.button(l='Incr',  c=partial(cResetField, 'fIncrement', 2), bgc=(colYellow5[0], colYellow5[1], colYellow5[2]))
cmds.floatField('fIncrement', v=2, pre=2)
cmds.button(l='Random', c=partial(cRandom, 'random', 0), bgc=(colYellow4[0], colYellow4[1], colYellow4[2]))
cmds.button(l='Incr', c=partial(cRandom, 'increment', 0), bgc=(colYellow2[0], colYellow2[1], colYellow2[2]))

cmds.setParent('layAdjExpr')
cmds.rowColumnLayout(nc=5, cw=[(1, 150), (2, 140), (3, 40), (4, 55), (5, 55)])
cmds.text('Batch', bgc=(colYellow5[0], colYellow5[1], colYellow5[2]))
cmds.button(l='Increment Per Object',  c=partial(cResetField, 'fIncrementPerObj', 0), bgc=(colYellow5[0], colYellow5[1], colYellow5[2]))
cmds.floatField('fIncrementPerObj', v=0, pre=2)

cmds.button(l='Random', c=partial(cRandomBatch, 'random'), bgc=(colYellow4[0], colYellow4[1], colYellow4[2]))
cmds.button(l='Incr', c=partial(cRandomBatch, 'increment'), bgc=(colYellow2[0], colYellow2[1], colYellow2[2]))



cmds.setParent('layAdj')
cmds.setParent(top=1)
cmds.frameLayout('flAttributes', l='LOCK AND FREE ATTRIBUTES', fn='smallPlainLabelFont', bgc=(colUI2[0], colUI2[1], colUI2[2]), cll=1, cl=1, cc=partial(cShrinkWin, 'win_tkLostInSpaceHelper'))

cmds.columnLayout('layAdjLock', adj=1)
cmds.text('lock and hide', bgc=(colUI6[0], colUI6[1], colUI6[2]))
cmds.rowColumnLayout(nc=4, cw=[(1, 132), (2, 132), (3, 132), (4, 44)])
cmds.button(l='translate', c=partial(cLockAndHide, 0, 'translate'), bgc=(colUI3[0], colUI3[1], colUI3[2]))
cmds.button(l='rotate', c=partial(cLockAndHide, 0, 'rotate'), bgc=(colUI4[0], colUI4[1], colUI4[2]))
cmds.button(l='scale', c=partial(cLockAndHide, 0, 'scale'), bgc=(colUI5[0], colUI5[1], colUI5[2]))
cmds.button(l='vis', c=partial(cLockAndHide, 0, 'v'), bgc=(colUI6[0], colUI6[1], colUI6[2]))
cmds.setParent('..')


cmds.rowColumnLayout(nc=10, cw=[(1, 44), (2, 44), (3, 44), (4, 44), (5, 44), (6, 44), (7, 44), (8, 44), (9, 44), (10, 44)])
cmds.button(l='tx', c=partial(cLockAndHide, 0, 'tx'), bgc=(colUI3[0], colUI3[1], colUI3[2]))
cmds.button(l='ty', c=partial(cLockAndHide, 0, 'ty'), bgc=(colUI3[0], colUI3[1], colUI3[2]))
cmds.button(l='tz', c=partial(cLockAndHide, 0, 'tz'), bgc=(colUI3[0], colUI3[1], colUI3[2]))
cmds.button(l='rx', c=partial(cLockAndHide, 0, 'rx'), bgc=(colUI4[0], colUI4[1], colUI4[2]))
cmds.button(l='ry', c=partial(cLockAndHide, 0, 'ry'), bgc=(colUI4[0], colUI4[1], colUI4[2]))
cmds.button(l='rz', c=partial(cLockAndHide, 0, 'rz'), bgc=(colUI4[0], colUI4[1], colUI4[2]))
cmds.button(l='sx', c=partial(cLockAndHide, 0, 'sx'), bgc=(colUI5[0], colUI5[1], colUI5[2]))
cmds.button(l='sy', c=partial(cLockAndHide, 0, 'sy'), bgc=(colUI5[0], colUI5[1], colUI5[2]))
cmds.button(l='sz', c=partial(cLockAndHide, 0, 'sz'), bgc=(colUI5[0], colUI5[1], colUI5[2]))
cmds.button(l='sel', c=partial(cLockAndHide, 0, 'sel'), bgc=(colRed[0], colRed[1], colRed[2]))

cmds.setParent('..')
cmds.text('unlock and show', bgc=(colUI6[0], colUI6[1], colUI6[2]))

cmds.rowColumnLayout(nc=10, cw=[(1, 44), (2, 44), (3, 44), (4, 44), (5, 44), (6, 44), (7, 44), (8, 44), (9, 44), (10, 44)])
cmds.button(l='tx', c=partial(cLockAndHide, 1, 'tx'), bgc=(colUI3[0], colUI3[1], colUI3[2]))
cmds.button(l='ty', c=partial(cLockAndHide, 1, 'ty'), bgc=(colUI3[0], colUI3[1], colUI3[2]))
cmds.button(l='tz', c=partial(cLockAndHide, 1, 'tz'), bgc=(colUI3[0], colUI3[1], colUI3[2]))
cmds.button(l='rx', c=partial(cLockAndHide, 1, 'rx'), bgc=(colUI4[0], colUI4[1], colUI4[2]))
cmds.button(l='ry', c=partial(cLockAndHide, 1, 'ry'), bgc=(colUI4[0], colUI4[1], colUI4[2]))
cmds.button(l='rz', c=partial(cLockAndHide, 1, 'rz'), bgc=(colUI4[0], colUI4[1], colUI4[2]))
cmds.button(l='sx', c=partial(cLockAndHide, 1, 'sx'), bgc=(colUI5[0], colUI5[1], colUI5[2]))
cmds.button(l='sy', c=partial(cLockAndHide, 1, 'sy'), bgc=(colUI5[0], colUI5[1], colUI5[2]))
cmds.button(l='sz', c=partial(cLockAndHide, 1, 'sz'), bgc=(colUI5[0], colUI5[1], colUI5[2]))
cmds.text(' ')

cmds.setParent('..')
cmds.rowColumnLayout(nc=4, cw=[(1, 132), (2, 132), (3, 132), (4, 44)])
cmds.button(l='translate', c=partial(cLockAndHide, 1, 'translate'), bgc=(colUI3[0], colUI3[1], colUI3[2]))
cmds.button(l='rotate', c=partial(cLockAndHide, 1, 'rotate'), bgc=(colUI4[0], colUI4[1], colUI4[2]))
cmds.button(l='scale', c=partial(cLockAndHide, 1, 'scale'), bgc=(colUI5[0], colUI5[1], colUI5[2]))
cmds.button(l='vis', c=partial(cLockAndHide, 1, 'v'), bgc=(colUI6[0], colUI6[1], colUI6[2]))



cmds.setParent(top=1)
cmds.frameLayout('flSelectionSets', l='SELECTION SETS', fn='smallPlainLabelFont', bgc=(colUI2[0], colUI2[1], colUI2[2]), cll=1, cl=1, cc=partial(cShrinkWin, 'win_tkLostInSpaceHelper'))

cmds.rowColumnLayout(nc=8, cw=[(1,44),(2,132),(3,44),(4,44),(5,44),(6,44),(7,44),(8,44)])
cmds.button(l='X', c=partial(cFillField, 'tSelectionSet'), bgc=(colRed[0], colRed[1], colRed[2]))
cmds.textField('tSelectionSet', tx='set')
cmds.button(l='rep', c=partial(cSelectionSet, 'r'), bgc=(colYellow5[0], colYellow5[1], colYellow5[2]))
cmds.button(l='add', c=partial(cSelectionSet, 'add'), bgc=(colYellow5[0], colYellow5[1], colYellow5[2]))
cmds.button(l='tgl', c=partial(cSelectionSet, 'tgl'), bgc=(colYellow5[0], colYellow5[1], colYellow5[2]))
cmds.radioCollection('rcIconColors')
cmds.radioButton('rbRed', label='R', bgc=(colRed[0], colRed[1], colRed[2]))
cmds.radioButton('rbGreen', label='G', sl=1, bgc=(colGreen[0], colGreen[1], colGreen[2]))
cmds.radioButton('rbBlue', label='B', bgc=(colBlue[0], colBlue[1], colBlue[2]))



cmds.setParent(top=1)
cmds.textField('tfFeedback', tx='', ed=0, bgc=(colUI1[0], colUI1[1], colUI1[2]))


cmds.showWindow(myWindow)
cmds.window(myWindow, w=440, h=20, e=1)

# tkLostInspaceHelper.py

from functools import partial 
import maya.cmds as cmds
import maya.mel as mel

global tk_edgeMemory
tk_edgeMemory = []

'''
to do
+ loop to curves out of order
track selection order has to be ON in the prefs!
- cut keys from path anim 
- orient joints chain! 
- build mesh from joints?
- delete empty transfoms
- ctrl size like BB curves

'''

def cShrinkWin(windowToClose, *args):
    cmds.window(windowToClose, e=1, h=20, w=440)


def cClearSE(*args):
    cmds.scriptEditorInfo(ch=1)


def cAddAttrib(type, attrName, *args):
   carry = cmds.ls(sl=1, l=1)[0]

   attrExist = maya.cmds.attributeQuery(attrName, node=carry, exists=True)
   if attrExist == 0:
        cmds.addAttr(carry, ln=attrName, at=type, dv=0) 
        cmds.setAttr(carry + '.' + attrName, e=1, keyable=1)   


def cCreateNode(objType, *args):
    LC = cmds.spaceLocator(p=(0,0,0))
    cFillField('tfPivot')


def cJointSize(*args):
    mel.eval('jdsWin')


def cFillField(field, *args):
    mySel = cmds.ls(sl=1)
    if mySel:
        cmds.textField(field, tx=mySel[0], e=1)
    else:
        cmds.textField(field, tx='', e=1)


def cRemoveEmptyTransforms(*args):
    mel.eval('scOpt_performOneCleanup( { "transformOption" } );')



def cJntInCenter(*args):
    centerPos = tkGetCenter(CRV, 'nurbs', 'locator')


def tkGetCenter(object, type, output, *args):
    print 'tkGetCenter...'
    print object

    points = []
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
        numCVs = degree + spans
        for i in range(0, numCVs, 1):
            singleCV = object + '.cv[' + str(i) + ']'
            points.append(singleCV)

    amount = len(points)

    for i in range(0, amount, 1):
        pos = cmds.xform(points[i], q=1, translation=1, ws=1)
        posX += pos[0]
        posY += pos[1]
        posZ += pos[2]

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
        cmds.setAttr(grp + '.tx', centerPos[0])
        cmds.setAttr(grp + '.ty', centerPos[1])
        cmds.setAttr(grp + '.tz', centerPos[2])

        return centerPos, grp, jnt


def cEdegloopToCurves(*args):
    global tk_edgeMemory
    tk_edgeMemory = []
    mySel = cmds.ls(os=1, fl=1)
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


def cJntsToChain(*args):
    jntsFound = []
    jntList = []
    mySel = cmds.ls(sl=1)

    for sel in mySel:
        if cmds.objectType(sel, isType='joint'):
            jntList.append(sel)
            print 'found'
        jntsFound = cmds.listRelatives(sel, ad=1, type='joint')
        if jntsFound:
            for jnt in jntsFound:
                jntList.append(jnt)

    print jntList
    numJnts = len(jntList)

    for i in range(1, numJnts, 1):
        cmds.parent(jntList[i], jntList[i-1])
    cmds.select(jntList[numJnts-1])
    cmds.joint(jntList[numJnts-1], e=1, oj='xyz', secondaryAxisOrient='zup', ch=0, zso=1) 


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
        cmds.xform(crvs[0], cpc=1)


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




def cBonesOnCurve(type, *args):
    print 'cBonesOnCurve...'
    v=0
    jntList = []
    mySel = []
    number = cmds.intField('fBonesNumber', q=1, v=1)
    print 'number:'
    print number

    mySel = cmds.ls(os=1, fl=1)

    print 'mySel:'
    print mySel
    # mySel = cmds.ls(sl=1)

    for CRV in mySel:
        print CRV
        crv = cmds.listRelatives(CRV, s=1)[0] 
        degree = cmds.getAttr(crv + ".degree")
        spans = cmds.getAttr(crv + ".spans")
        numCVs = degree + spans
        step = 1.0 / float(number)

        if type == "bonesCV":
            print 'bonesCV...'
            cmds.select(clear=1)
            for i in range(0, numCVs, 1):
                pos = cmds.pointPosition(str(CRV) + '.cv[' + str(i) + ']')
                jnt = cmds.joint(p=(pos[0], pos[1], pos[2]), n=CRV + '_' + str(i) + '_jnt')
                jntList.append(jnt)

            cmds.joint(jntList[0], e=1, oj='xyz', secondaryAxisOrient='yup', ch=0, zso=1) 


        if type == "bonesOnly":
            print 'bonesOnly...'
            result = tkGetCenter(CRV, 'nurbs', 'joint')
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


        if type == "bonesMP":
            print 'bonesMP...'
            MAIN = cmds.group(empty=1, n=CRV + '_main_grp')
            for v in range(0, number, 1):
                cmds.select(clear=1)
                grp = cmds.group(empty=1, n=CRV + '_' + str(v) + '_grp')
                jnt = cmds.joint(p=(0,0,0), n=CRV + '_' + str(v) + '_jnt')
                mp = cmds.pathAnimation(grp, CRV, fractionMode=1, followAxis='x', upAxis='y', worldUpType="vector", worldUpVector=(0, 1, 0), startTimeU=1)
                cmds.cutKey(mp, cl=1, t=(":", ":"), at="u")
                cmds.setAttr(mp + ".uValue", v * step)
                cmds.parent(grp, MAIN)

            result = tkGetCenter(CRV, 'nurbs', 'joint')
            centerPos = result[0]
            centerGrp = result[1]
            # cmds.parent(centerGrp, MAIN)




def cCutAsStart(*args):
    crvList = []
    mySel = cmds.ls(sl=1)
    text = cmds.textField('tfCutter', tx=1, q=1)
    shps = cmds.listRelatives(text, s=1)
    axis = '1, 0, 0'
    axisOpt = cmds.radioCollection('rcXYZ', sl=1, q=1)
    if axisOpt == 'rbOrientY':
        axis = '0, 1, 0'
    if axisOpt == 'rbOrientZ':
        axis = '0, 0, 1'
   
    if cmds.objectType(shps[0], isType='nurbsCurve'):
        cutter = text
        for sel in mySel:
            shps = cmds.listRelatives(sel, s=1, type='nurbsCurve')
            if shps:
                crvList.append(sel)
    
    for crv in crvList:
        print 'crv:'
        print crv
        cmds.closeCurve(crv, ch=0, ps=1, rpo=1, bb=0.5, bki=0, p=0.1) 
        cmds.select(crv, cutter, r=1)

            # cutCurvePreset:
            # int $history,
            # int $replaceOriginal,
            # float $tolerance,
            # int $useDirection,
            #     0 - off, 1 - on, 2 - use current view direction
            #     3 - x axis, 4 - y axis, 5 - z axis
            #     6 - smart mode: use view vector in ortho view
            # float $dirX,
            # float $dirY,
            # float $dirZ
            # int $segmentOrKeepLongestPiece,
            # int $cutAllCurveOrCutWithLast 
                            
        cmd = 'cutCurvePreset(1,1,0.0001,1,' + str(axis) + ',1,0,0,2,2)'
        mel.eval(cmd)  # result 2 curves
        cutCrvs = cmds.ls(sl=1)
        print cutCrvs
        attCrv = cmds.attachCurve(cutCrvs[0], cutCrvs[1], ch=1, rpo=1, kmk=1, m=0, bb=0.5, bki=0, p=0.1)
        print attCrv
        for i in attCrv:
            if cmds.objectType(i, isType = 'attachCurve'):
                print 'reverse'
                cmds.setAttr(i + '.reverse1', 0)
                cmds.setAttr(i + '.reverse2', 0)
        newCrv = cmds.ls(sl=1)
        cmds.delete(ch=1)
        cmds.delete(crv)
        cmds.rename(newCrv[0], str(crv))


def cSelToJoints(*args):
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


def cJntsFromSelection(parent, *args):
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
    print 'jntList:'
    print jntList

    cmds.select(clear=1)
    for i in range(0, len(mySel)-1, 1):
        if parent == 1:
            cmds.parent(mySel[i+1], jntList[i])


def cAdjustPivot(*args):
    pos = [0, 0, 0]
    mySel = cmds.ls(os=1, fl=1)
    pvLoc = cmds.textField('tfPivot', tx=1, q=1)
    x = cmds.checkBox('cbX', v=1, q=1)
    y = cmds.checkBox('cbY', v=1, q=1)
    z = cmds.checkBox('cbZ', v=1, q=1)
    
    if pvLoc:
        pos = cmds.xform(pvLoc, translation=1, ws=1, q=1)
        print pos

    for jnt in mySel:
        curPos = cmds.xform(jnt, translation=1, ws=1, q=1)
        print curPos

        if x == 0:
            pos[0] = curPos[0]
        if y == 0:
            pos[1] = curPos[1]
        if z == 0:
            pos[2] = curPos[2]


        cmds.move(pos[0], pos[1], pos[2], jnt + '.scalePivot', jnt + '.rotatePivot', rpr=1)


    # move -rpr 0 0 0 polyToCurve1_center_jnt.scalePivot polyToCurve1_center_jnt.rotatePivot ;


def cMakeCtrl(ctrlShape, *args):
    pos = [1, 0, 0]
    orient = [1, 0, 0]
    orientOption = cmds.radioCollection('rcXYZ', sl=1, q=1)
    if orientOption == 'rbOrientY':
        orient = [0, 1, 0]
    if orientOption == 'rbOrientZ':
        orient = [0, 0, 1]

    mySel = cmds.ls(os=1, fl=1)
    if not mySel:
        mySel = cmds.spaceLocator(n='deleteMe')

        print 'orient:'
        print orient
       
    for sel in mySel:
        CON = ''
        pos = cmds.xform(mySel[0], translation=1, ws=1, q=1)

        if ctrlShape == 'cube':
            CON = cmds.curve(n=sel + '_con', d=1, p=[(5, 5, 5), (5, 5, -5), (-5, 5, -5), (-5, -5, -5), (5, -5, -5), (5, 5, -5), (-5, 5, -5), (-5, 5, 5), (5, 5, 5), (5, -5, 5), (5, -5,-5), (-5, -5, -5), (-5, -5, 5), (5, -5, 5), (-5, -5, 5), (-5, 5, 5)], k=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])

        if ctrlShape == 'nail':
            CON = cmds.curve(n=sel + '_con', d=1, p=[(0, 0, 0), (5.639601, 0, 0), (5.784686, 0, 0.350267), (-6.134953, 0, 0.495353), (-6.48522, 0, 0.350267), (-6.630306, 0, 0), (-6.48522, 0, -0.350267), (-6.134953, 0, -0.495353), (-5.784686, 0, -0.350267), (-5.639601, 0, 0)], k=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9])

        if ctrlShape == 'circle':
            print 'circle'
            CON = cmds.circle(n=sel + '_con', c=(0, 0, 0), nr=(orient[0], orient[1], orient[2]), sw=360, r=10, d=3, ut=0, tol=0.01, s=8, ch=0)

        print 'CON:'
        print CON

        GRP = cmds.group(CON, n=CON[0] + '_nul')
        cmds.setAttr(GRP + '.translate', pos[0], pos[1], pos[2])
        cmds.select(CON, r=1)

        cFillField('tfControl')

    print 'delete me...'
    if cmds.objExists('deleteMe'):
        cmds.delete('deleteMe')


def cScaleIcon(*args):
    mySel = cmds.ls(sl=1)
    scale = cmds.floatField('fScaleIcon', v=1, q=1)
    for sel in mySel:
        origin = cmds.xform(sel, q=1, ws=1, t=1)

        crvs = cmds.listRelatives(sel, s=1, type='nurbsCurve')
        if crvs:
            degree = cmds.getAttr(crvs[0] + ".degree")
            spans = cmds.getAttr(crvs[0] + ".spans")
            for i in range(0, spans, 1):  
                cvPos = cmds.xform(sel + '.cv[' + str(i) + ']', q=1, translation=1, ws=1)
                newPos = (origin[0] + (origin[0] - cvPos[0]) * scale, origin[1] + (origin[1] - cvPos[1]) * scale, origin[2] + (origin[2] - cvPos[2]) * scale)
                cmds.xform(sel + '.cv[' + str(i) + ']', translation=(newPos[0], newPos[1], newPos[2]), ws=1)                 

def cAssembleAttributes(type, *args):
    mySel = cmds.ls(os=1, fl=1)
    ctrl = cmds.textField('tfControl', tx=1, q=1) 

    if type == 'motionPath':
        print '-----------'
        print str(type) + ':'
       
        objType_dic = {}
        objType_dic = cSelToType(type)

        cmds.select(ctrl, r=1)
        cAddAttrib('double', 'offset')

        for key, value in objType_dic.items():
            print key
            print value
            plus = cmds.shadingNode('plusMinusAverage', asUtility=1)
            cmds.select(value, r=1) 
            cAddAttrib('double', 'bindU')
            u = cmds.getAttr(value + '.uValue')
            cmds.setAttr(value + '.bindU', u)
            cmds.connectAttr(value + '.bindU', plus + '.input1D[0]', f=1) 
            cmds.connectAttr(ctrl + '.offset', plus + '.input1D[1]', f=1) 
            cmds.connectAttr(plus + '.output1D', value + '.uValue', f=1) 










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

cmds.columnLayout(adj=1, bgc=(colDark2[0], colDark2[1], colDark2[2]))
cmds.rowColumnLayout(nc=8, cw=[(1, 55), (2, 55), (3, 55), (4, 55), (5, 55), (6, 55), (7, 55), (8, 55)])
cmds.button(l='Jnt Size', c=partial(cJointSize), bgc=(colYellow[0], colYellow[1], colYellow[2]))
cmds.button(l='To Jnts', c=partial(cSelToJoints), bgc=(colYellow2[0], colYellow2[1], colYellow2[2]))
cmds.text(' ')
cmds.text(' ')
cmds.text(' ')
cmds.text(' ')
cmds.button(l='Empty', c=partial(cRemoveEmptyTransforms), bgc=(colRed[0], colRed[1], colRed[2]))
cmds.button(l='Clear SE', c=partial(cClearSE), bgc=(colRed[0], colRed[1], colRed[2]))
cmds.setParent(top=1)


cmds.columnLayout(adj=1, bgc=(colDark[0], colDark[1], colDark[2]))
cmds.frameLayout('flRigSetup', l='RIG SETUP', fn='smallPlainLabelFont', bgc=(colDark2[0], colDark2[1], colDark2[2]), cll=1, cl=0, cc=partial(cShrinkWin, 'win_tkLostInSpaceHelper'))
cmds.columnLayout('layAdj', adj=1)

cmds.frameLayout('flCurves', l='CURVES', fn='smallPlainLabelFont', bgc=(colYellow5[0], colYellow5[1], colYellow5[2]))
cmds.columnLayout(adj=1)
cmds.button(l='Loop To Curves', c=partial(cEdegloopToCurves), bgc=(colYellow4[0], colYellow4[1], colYellow4[2]))

cmds.rowColumnLayout(nc=7, cw=[(1, 60), (2, 110), (3, 10), (4, 50), (5, 50), (6, 50), (7, 110)])
cmds.button(l='Cutter >>', c=partial(cFillField, 'tfCutter'), bgc=(colYellow2[0], colYellow2[1], colYellow2[2]))
cmds.textField('tfCutter', ed=0, tx='curve1', bgc=(0,0,0))
cmds.text(' ', bgc=(colYellow5[0], colYellow5[1], colYellow5[2]))
cmds.radioCollection('rcCutXYZ')
cmds.radioButton('rbCutX', label='X', bgc=(colYellow5[0], colYellow5[1], colYellow5[2]))
cmds.radioButton('rbCutY', label='Y', bgc=(colYellow5[0], colYellow5[1], colYellow5[2]))
cmds.radioButton('rbCutZ', label='Z', sl=1, bgc=(colYellow5[0], colYellow5[1], colYellow5[2]))
cmds.button(l='Cut As Start', c=partial(cCutAsStart), bgc=(colYellow2[0], colYellow2[1], colYellow2[2]))


cmds.setParent('layAdj')
cmds.frameLayout('flJntsOnCurves', l='JOINTS ON CURVES', fn='smallPlainLabelFont', bgc=(colGreen[0], colGreen[1], colGreen[2]))
# cmds.columnLayout(adj=1)
cmds.rowColumnLayout(nc=4, cw=[(1, 40), (2, 180), (3, 110), (4, 110)])
cmds.intField('fBonesNumber', v=10) 
cmds.button(l='... JNTs On Curve As Motionpath', c=partial(cBonesOnCurve, 'bonesMP'), bgc=(colGreenL[0], colGreenL[1], colGreenL[2]))
cmds.button(l='... Just Place', c=partial(cBonesOnCurve, 'bonesOnly'), bgc=(colGreen[0], colGreen[1], colGreen[2]))
cmds.button(l='... On Curve CVs', c=partial(cBonesOnCurve, 'bonesCV'), bgc=(colGreenL[0], colGreenL[1], colGreenL[2]))


cmds.setParent('layAdj')
cmds.frameLayout('flJntPivots', l='SET JNT PIVOT', fn='smallPlainLabelFont', bgc=(colYellow5[0], colYellow5[1], colYellow5[2]))
cmds.rowColumnLayout(nc=8, cw=[(1, 30), (2, 50), (3, 90), (4, 10), (5, 50), (6, 50), (7, 50), (8, 110)], bgc=(colYellow5[0], colYellow5[1], colYellow5[2]))
# cmds.rowColumnLayout(nc=7, cw=[(1, 80), (2, 90), (3, 10), (4, 50), (5, 50), (6, 50), (7, 110)], bgc=(colYellow5[0], colYellow5[1], colYellow5[2]))

cmds.button(l='LC', c=partial(cCreateNode, 'spaceLocator'), bgc=(colYellow4[0], colYellow4[1], colYellow4[2]))
cmds.button(l='LC >>', c=partial(cFillField, 'tfPivot'), bgc=(colYellow2[0], colYellow2[1], colYellow2[2]))
cmds.textField('tfPivot', ed=0, tx='', bgc=(0,0,0))
cmds.text(' ')
cmds.checkBox('cbX', l='X', v=0)
cmds.checkBox('cbY', l='Y', v=1)
cmds.checkBox('cbZ', l='Z', v=1)
cmds.button(l='Adjust Pivot', c=partial(cAdjustPivot), bgc=(colYellow2[0], colYellow2[1], colYellow2[2]))


cmds.setParent('layAdj')
cmds.frameLayout('flJntOperations', l='MAKE JOINT CHAINS', fn='smallPlainLabelFont', bgc=(colGreen[0], colGreen[1], colGreen[2]))
cmds.rowColumnLayout(nc=4, cw=[(1, 90), (2, 170), (3, 90)])
cmds.button(l='Jnts To Chain', c=partial(cJntsToChain), bgc=(colGreen[0], colGreen[1], colGreen[2]))
cmds.button(l='Jnts From Selection And Parent', c=partial(cJntsFromSelection, 1), bgc=(colGreenL[0], colGreenL[1], colGreenL[2]))
cmds.setParent('..')


cmds.setParent('layAdj')
cmds.frameLayout('flCTRLs', l='CTRLs', fn='smallPlainLabelFont', bgc=(colYellow5[0], colYellow5[1], colYellow5[2]))

cmds.rowColumnLayout(nc=4, cw=[(1, 90), (2, 90), (3, 150), (4, 110)])

cmds.text('U To CTRL', bgc=(colYellow5[0], colYellow5[1], colYellow5[2]))
cmds.button(l='Control >>', c=partial(cFillField, 'tfControl'), bgc=(colYellow2[0], colYellow2[1], colYellow2[2]))
cmds.textField('tfControl', ed=0, tx='curve1', bgc=(0,0,0))
cmds.button(l='Mo Path Offset', c=partial(cAssembleAttributes, 'motionPath'), bgc=(colYellow4[0], colYellow4[1], colYellow4[2]))

cmds.setParent('layAdj')

cmds.rowColumnLayout(nc=8, cw=[(1, 60), (2, 60), (3, 60), (4, 50), (5, 50), (6, 50), (7,50), (8, 60)], bgc=(colYellow5[0], colYellow5[1], colYellow5[2]))
cmds.button(l='Cube', c=partial(cMakeCtrl, 'cube'), bgc=(colYellow4[0], colYellow4[1], colYellow4[2]))
cmds.button(l='Nail', c=partial(cMakeCtrl, 'nail'), bgc=(colYellow2[0], colYellow2[1], colYellow2[2]))
cmds.button(l='Circle', c=partial(cMakeCtrl, 'circle'), bgc=(colYellow4[0], colYellow4[1], colYellow4[2]))
cmds.radioCollection('rcXYZ')
cmds.radioButton('rbOrientX', label='X')
cmds.radioButton('rbOrientY', label='Y', sl=1)
cmds.radioButton('rbOrientZ', label='Z')
cmds.button(l='Scale', c=partial(cScaleIcon), bgc=(colYellow4[0], colYellow4[1], colYellow4[2]))
cmds.floatField('fScaleIcon', v=2, ed=1, pre=1, bgc=(0,0,0))


cmds.setParent(top=1)
cmds.textField('tfFeedback', tx='', ed=0, bgc=(colDark2[0], colDark2[1], colDark2[2]))


cmds.showWindow(myWindow)
cmds.window(myWindow, w=440, h=20, e=1)

# tkLostAnimHelper.py

from functools import partial 
import maya.cmds as cmds
import maya.mel as mel
import random as random

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
        # print match

        cmds.select(str(sp[0]) + '*' + str(sp[2]), r=1)

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

def cIncrementPos(fieldDriven, fieldPos, fieldCheck, *args):
    """
    check increments position 
    """

    text = ''
    sp = []
    driven = cmds.textField(fieldDriven, tx=1, q=1)
    countPos = cmds.intField(fieldPos, v=1, q=1)


    isNmSpc = driven.split(':')
    # print 'len:' + str(len(isNmSpc))

    if len(isNmSpc) == 1:
        sp = driven.split('_')

  
    if len(isNmSpc) == 2:
        baseName = str(isNmSpc[0]) + ':'
        sp = isNmSpc[-1].split('_')

        for i in range(0, countPos, 1):
            text += sp[i] + '_'
            text += ' <count> _'

        for i in range(countPos+1, len(sp)-1, 1):
            text += sp[i] + '_'
        text += sp[-1]
        # print 'len was 1, text = ' + str(text)


        text = str(isNmSpc[0]) + ':' 
        for i in range(0, countPos, 1):
            text += sp[i] + '_'
        text += ' <count> _'

        for i in range(countPos+1, len(sp)-1, 1):
            text += sp[i] + '_'
        text += sp[-1]
        # print 'len was 2, text = ' + str(text)

    cmds.textField(fieldCheck, tx=text, e=1)


def cIncrementPos_OLD(fieldDriven, fieldPos, fieldCheck, *args):
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

def cResetField(field, value, *args):
    """
    reset field to value
    """

    cmds.floatField(field, v=value, e=1)

def cRandom(action, incrPerGuide, *args):
    """
    Randomize attributes

    Input
        action:         increment
                        random
        incrPerGuide:  increment per mainGroup

    """

    # print 'incrPerGuide: ' + str(incrPerGuide)

    mySel = cmds.ls(os=1)
    attributes = cmds.textField('tfAttrChange', tx=1, q=1).split(' ')
    fromValue = cmds.floatField('fFromValue', v=1, q=1)
    incrValue = cmds.floatField('fIncrement', v=1, q=1)

    newValue = fromValue + incrPerGuide
    if action == 'increment':
        # print 'increment...'
        for sel in mySel:
            newValue = newValue + incrValue
            for i in range(0, len(attributes),1):
                # print 'newValue: ' + str(newValue)
                cmds.setAttr(sel + '.' + attributes[i], newValue)

    if action == 'random':
        # print 'random...'
        for sel in mySel:
            for i in range(0, len(attributes),1):
                newValue = random.uniform(fromValue, incrValue)
                # print 'sel: ' + str(sel)
                # print 'newValue: ' + str(newValue)
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
    sp = []
    drivenList = []
    driver = cmds.textField(fieldDriver, tx=1, q=1)

    isNmSpc = driver.split(':')
    if len(isNmSpc) == 1:
        sp = driver.split('_')
        for i in range(0, fieldPos+1, 1):
            baseName += sp[i] + '_'

    if len(isNmSpc) == 2:
        baseName = str(isNmSpc[0]) + ':'
        sp = isNmSpc[-1].split('_')

        for i in range(0, fieldPos+1, 1):
            baseName += sp[i] + '_'



    # for i in range(0, fieldPos+1, 1):
    #     baseName += sp[i] + '_'

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



















ver = 'v 1.0';
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
myWindow = cmds.window('win_tkLostAnimHelper', t=('Lost In Space Anim Helper ' + ver), s=1, wh=(windowStartHeight, windowStartWidth ))


cmds.columnLayout(adj=1, bgc=(colUI2[0], colUI2[1], colUI2[2]))
cmds.frameLayout('flExpressions', l='WAVE EXPRESSIONS', fn='smallPlainLabelFont', bgc=(colUI2[0], colUI2[1], colUI2[2]), cll=1, cl=0, cc=partial(cShrinkWin, 'win_tkLostAnimHelper'))

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
cmds.intField('ifDrivenStart', ed=0, v=0, bgc=(colYellow5[0], colYellow5[1], colYellow5[2]))
cmds.text('End', bgc=(colYellow3[0], colYellow3[1], colYellow3[2]))
cmds.intField('ifDrivenEnd', v=8,  ed=0, bgc=(colYellow5[0], colYellow5[1], colYellow5[2]))

cmds.setParent('layAdjExpr')
cmds.rowColumnLayout(nc=3, cw=[(1, 90), (2, 20), (3, 330)])
cmds.button(l='Increment Pos', c=partial(cIncrementPos, 'tfDriven', 'ifDriverCountPos', 'tfCheck'), bgc=(colYellow3[0], colYellow3[1], colYellow3[2]))
cmds.intField('ifDriverCountPos', v=2, cc=partial(cIncrementPos, 'tfDriven', 'ifDriverCountPos', 'tfCheck'))
cmds.textField('tfCheck', tx='', ed=0, bgc=(colUI1[0], colUI1[1], colUI1[2]))



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



cmds.setParent(top=1)
cmds.frameLayout('flSelectionSets', l='SELECTION SETS', fn='smallPlainLabelFont', bgc=(colUI2[0], colUI2[1], colUI2[2]), cll=1, cl=1, cc=partial(cShrinkWin, 'win_tkLostAnimHelper'))

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



cmds.showWindow(myWindow)
cmds.window(myWindow, w=440, h=20, e=1)

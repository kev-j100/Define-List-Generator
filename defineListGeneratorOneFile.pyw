from hashlib import new
from logging import exception
import PySimpleGUI as sg
import csv
import pathlib

#------
#This program is for generating define lists used
#for Decipher programming.
#-----

#Take in string and turn it into a define list
def defineListMakerSingle(rowsString, defineLabelString, rowLabelString):
    splitRows = []
    DefineListString = ''

    splitRows = rowsString.split('\n')

    DefineListString += "<define label='%s'>\n" %defineLabelString
    rowNum = 1

    for rowText in splitRows:
        if rowText != '':
            DefineListString += ("<row label='"+ rowLabelString.strip() + str(rowNum) + "'>" + rowText + "</row>\n")
            rowNum +=1

    DefineListString += "</define>"

    return DefineListString

# Takes in a list of strings and returns a list of lists
def listOfStringsToListOfLists(ListStrings):
    ListOfLists = []
    for x in ListStrings:
        ListOfLists.append(x.split('\n'))

    return ListOfLists

def defineListMakerStylevarGroup(LabelStrings, ListStrings, StartNum):
    RowTextSplit = []
    splitStylevars = []
    DefineListString = ''
    stylevarCleaned = []

#    RowTextSplit = ListStrings[0].split('\n')
    RowTextSplit = ListStrings[0]

    if len(ListStrings) > 1:
        for x in ListStrings[1:]:
            splitStylevars.append(x)
    
        for stylevarRow in range(0,len(splitStylevars[0])):
            stylevarString = ''
            for x,label in zip(range(0,len(LabelStrings[2:])),LabelStrings[2:]):
                stylevarString += "%s='" %(label).strip()
                stylevarString += "%s' " %splitStylevars[x][stylevarRow].replace('\t',',').strip()
            stylevarCleaned.append(stylevarString)

    
        for x in range(2,len(LabelStrings)):
            DefineListString += "<stylevar name='%s'/>\n" %LabelStrings[x]
    else:
        stylevarCleaned = RowTextSplit
        
    DefineListString += "<define label='%s'>\n" %LabelStrings[0]
    
    rowNum = StartNum
    for rowText,stylevar in zip(RowTextSplit,stylevarCleaned):
        if rowText != '':
            if len(ListStrings) > 1:
                DefineListString += ("<row label='%s%s' %s>%s</row>\n" %(LabelStrings[1],rowNum,stylevar,rowText.replace('&','&amp;').strip()))
            else:
                DefineListString += ("<row label='%s%s'>%s</row>\n" %(LabelStrings[1],rowNum,rowText.replace('&','&amp;').strip()))
            rowNum += 1
    DefineListString += "</define>"

    return DefineListString

def defineListDupesSingle(rowsString):
    splitRows = []
    splitRowsCleaned = []
    dupesCollection = []

    splitRows = rowsString.split('\n')

    for rowText in splitRows:
        if rowText != '':
            splitRowsCleaned.append((rowText.strip()).lower())

    for x in range(0, len(splitRowsCleaned)):
        for y in range(0,len(splitRowsCleaned)):
            if splitRowsCleaned[x] == splitRowsCleaned[y] and x!=y and splitRowsCleaned[x] not in dupesCollection:
                dupesCollection.append(splitRowsCleaned[x])

    return dupesCollection

# Takes in a list with duplicate items and returns a deduped list
def returnDedupedList(dupeList):
    dedupedList = []
    for x in dupeList:
        if x not in dedupedList:
            dedupedList.append(x)

    return dedupedList

# Takes the file name, opens the file, and adds elements of the file to a list.
# This should be either a list for a single row or a list of lists a file with more than one column.
def fileToLists(fileName):
    fileList = []
    with open(fileName) as givenFile:
        givenFileRender = csv.reader(givenFile, delimiter='\t')

        for brand in givenFileRender:    
            fileList.append(brand)

    return fileList

#This will check the list for Dupes and returns the list
#It takes in the List and the column number to check
def listDupes(fileList, columnNumber):
    dupesCollection = []
    for x in range(0,len(fileList)):
        for y in range(0,len(fileList)):
            if x != y and fileList[x][columnNumber].lower() == fileList[y][columnNumber].lower() and not fileList[y][columnNumber] in dupesCollection:
                dupesCollection.append(fileList[y][columnNumber])
            
    return dupesCollection

#### Takes in a list of lists and checks the length to see if they match.
#### Boolian is returned True if the same and False if differnt lengths
def listLengthCheck(listsList):

    currentLength = 0
    returnCheck = True
    if len(listsList) > 0:
        currentLength = len(listsList[0])

    for x in listsList:
        if currentLength != len(x):
            returnCheck = False

    return returnCheck

### Takes in a list of lists. Returns a list of the lists lengths.
def listLengthOutput(listsList):
    listLengths = []

    for x in listsList:
        listLengths.append(len(x))

    return listLengths

### Takes in a list of lists. Returns a list of Lists with a deduped text list and combined stylevar list
def colapseList(listsList):

    #Creates new List of lists and adds in the number of lists needed
    ColapsedList = []
    
    for list in listsList:
        ColapsedList.append([])

    #Add values to the new list of lists
    for rowTextNum in range(0,len(listsList[0])):
        #Check if row text has been added yet. If it has not then add it in.
        if not listsList[0][rowTextNum] in ColapsedList[0]:
            for listNum in range(0,len(listsList)):
                ColapsedList[listNum].append(listsList[listNum][rowTextNum])
        #If the row text has been already added, then the stylevars values need to be added to the existing ones.
        if (listsList[0][rowTextNum] in ColapsedList[0]) and len(listsList) > 1:
            for colListRowNum in range(0,len(ColapsedList[0])):
                if listsList[0][rowTextNum] == ColapsedList[0][colListRowNum]:
                    for styleVarNum in range(1,len(listsList)):
                        if not listsList[styleVarNum][rowTextNum] in ColapsedList[styleVarNum][colListRowNum]:
                            ColapsedList[styleVarNum][colListRowNum] += "," + listsList[styleVarNum][rowTextNum]

    return ColapsedList

##
## GUI side functions
##
##

def windowLayoutCreation(StyleVarNum):


    NormalLabelsInput = [sg.Text('Define List Label'), sg.Input(size=(10,1), key="DLLabel"),sg.Text('Label Prefix'), sg.Input(size=(10,1), key="LabelPre", default_text="r"), sg.Text('Row Start Number'), sg.Input(size=(10,1), key="StartNum", default_text="1")]
    StylevarInput = []
    ListInputs = [sg.Col([[sg.Text("Row Text List")],[sg.Multiline(size = (20,20), key="RowText")]])]

    if StyleVarNum > 0:
        for x in range(1,StyleVarNum+1):
            StylevarInput.append(sg.Text('Stylevar label %s' %x))
            StylevarInput.append(sg.Input(default_text="cs:", size=(10,1), key="StylevarLabel_%s" %x))
            ListInputs.append(sg.Col([[sg.Text("Stylevar %s" %x)],[sg.Multiline(size = (20,20), key="StylevarList_%s" %x)], [sg.Button("Replace Text", key="StyleVarReplace_%s" %x)]]))
        
    StylevarInput.append(sg.Button('Add Stylevar'))
    StylevarInput.append(sg.Button('Remove Stylevar'))
    ListInputs.append(sg.Col([[sg.Text("Output")],[sg.Output(size = (20,20), key='-OUTOUT-')]]))

    layoutReturn = [
        NormalLabelsInput, 
        StylevarInput,
        ListInputs,
        [sg.Button('Create'), sg.Button('Clear'), sg.Button('Save to file')], 
        [sg.Button('Exit')]
    ]

    return layoutReturn

###
##  Text replace stylevar items. 
##  Takes in all of the chosen stylevar string list, makes a dictionary of item, 
##  and outputs a string to replace the current string list
###

def createReplaceSylevarValue(originalString):
    #Change string to list
    originalStringList = []
    originalStringList = originalString.split('\n')

    #Dedupe the list
    dedupedList = []
    dedupedList = returnDedupedList(originalStringList)

    #Create window with inputs for each deduped item
    StyleVarItems = []

    for svitem in dedupedList:
        StyleVarItems.append([sg.Text(svitem), sg.Input(size=(10,1), key=svitem, default_text=svitem)])
    
    StyleVarItems.append([sg.Button('Replace'), sg.Button('Cancel')])
    replacementWindow = sg.Window('Replace Text', StyleVarItems)

    newStringList = []
    while True:
        repev, repvals = replacementWindow.read(timeout=100)

        
    #On completion close the window and update the stylevar
        if repev == 'Replace':
            for x in originalStringList:
                newStringList.append(repvals[x])
            break

        elif repev == 'Cancel' or repev == sg.WIN_CLOSED or repev == 'Exit':
            break

    replacementWindow.close()

    return newStringList
#
# GUI setup
#
#

SVNum = 0

window1 = sg.Window('Decipher Define List Generator Tool', windowLayoutCreation(SVNum))
#win2_active = False
ListOutput = ''


while True:
    ev1, vals1 = window1.read(timeout=100)
    
    if ev1 == 'Add Stylevar':

        dLLabel = vals1['DLLabel']
        LabelPre = vals1['LabelPre']
        StartNum = vals1['StartNum']
        RowText = vals1['RowText']

        StyleVarLabels = []
        StyleVarLists = []

        if SVNum > 0:
            for x in range(1,SVNum+1):
                StyleVarLabels.append(vals1['StylevarLabel_%s' %x])
                StyleVarLists.append(vals1['StylevarList_%s' %x])

        SVNum += 1
        window2 = sg.Window('Define List With Stylevar Group', windowLayoutCreation(SVNum), finalize=True)
        window1.Close()
        window1 = window2

        window1['DLLabel'].update(dLLabel)
        window1['LabelPre'].update(LabelPre)
        window1['StartNum'].update(StartNum)
        window1['RowText'].update(RowText)

        if SVNum > 1:
            for x in range(0,SVNum-1):
                window1['StylevarLabel_%s' %(x+1)].update(StyleVarLabels[x])
                window1['StylevarList_%s' %(x+1)].update(StyleVarLists[x])

    elif ev1 == 'Remove Stylevar' and SVNum > 0:

        dLLabel = vals1['DLLabel']
        LabelPre = vals1['LabelPre']
        StartNum = vals1['StartNum']
        RowText = vals1['RowText']

        StyleVarLabels = []
        StyleVarLists = []

        if SVNum > 0:
            for x in range(1,SVNum+1):
                StyleVarLabels.append(vals1['StylevarLabel_%s' %x])
                StyleVarLists.append(vals1['StylevarList_%s' %x])

        SVNum -= 1
        window2 = sg.Window('Define List With Stylevar Group', windowLayoutCreation(SVNum), finalize=True)
        window1.Close()
        window1 = window2

        window1['DLLabel'].update(dLLabel)
        window1['LabelPre'].update(LabelPre)
        window1['StartNum'].update(StartNum)
        window1['RowText'].update(RowText)

        if SVNum > 0:       
            for x in range(0,SVNum-1):
                window1['StylevarLabel_%s' %(x+1)].update(StyleVarLabels[x])
                window1['StylevarList_%s' %(x+1)].update(StyleVarLists[x])

    elif ev1 == 'Create':

        LabelsList = []
        ListsList= []

        LabelsList.append(vals1['DLLabel'])
        LabelsList.append(vals1['LabelPre'])
        ListsList.append(vals1['RowText'])

        if SVNum > 0:
            for x in range(1,SVNum+1):
                LabelsList.append(vals1['StylevarLabel_%s' %x])
                ListsList.append(vals1['StylevarList_%s' %x])

        ListsToCheck = listOfStringsToListOfLists(ListsList)

        if SVNum > 0 and not listLengthCheck(ListsToCheck):
            listLengths = listLengthOutput(ListsToCheck)

            listLengthsString = ''
            for x in listLengths:
                listLengthsString += "%s" %x
                listLengthsString += " "

            sg.Popup('The Length of of the inputs are different. Please revise. Here are the lengths in order: %s' %listLengthsString)
            
        else:

            dupesForPopup = []
            dupesForPopup = defineListDupesSingle(ListsList[0])
            
            ListsList = listOfStringsToListOfLists(ListsList)
            if len(dupesForPopup) > 0:
                if sg.popup_yes_no('There are some duplicates in the Row Text List. Do you want to dedupe and/or colapse the lists?',) == 'Yes':
                # Colapse the lists
                    ListsList = colapseList(ListsList)

            text_input = defineListMakerStylevarGroup(LabelsList,ListsList,int(vals1['StartNum']))        
            ListOutput = text_input
            print (text_input)

    elif ev1 == 'Save to file':
        saveFileName = ''
        saveFileName = sg.popup_get_file('Please enter a file name')
        
        if saveFileName not in ['',None]:
            #print(saveFileName)
            try:
                if '/' in saveFileName or '\\' in saveFileName:
                     saveFile = open( saveFileName, 'w+')                   
                else:
                    saveFile = open( '%s/%s' %(pathlib.Path().absolute(),saveFileName), 'w+')
                saveFile.writelines(ListOutput)
                saveFile.close()
            except:
                print(exception)
    
    elif 'StyleVarReplace_' in ev1:
        stylevarNum = ev1
        replacementStyleVarList = []
        replacementStyleVarList = createReplaceSylevarValue(vals1["StylevarList_%s" %stylevarNum.split('_')[1]])
        
        if len(replacementStyleVarList) > 0:
            window1["StylevarList_%s" %stylevarNum.split('_')[1]].update('\n'.join(replacementStyleVarList))

    elif ev1 == 'Clear':
        window1['-OUTOUT-'].update('')

    if ev1 == sg.WIN_CLOSED or ev1 == 'Exit':
            break


window1.close()
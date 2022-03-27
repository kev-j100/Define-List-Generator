import PySimpleGUI as sg
import csv

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

def listOfStringsToListOfLists(ListStrings):
    ListOfLists = []
    for x in ListStrings:
        ListOfLists.append(x.split('\n'))

    return ListOfLists

def defineListMakerStylevarGroup(LabelStrings, ListStrings):
    RowTextSplit = []
    splitStylevars = []
    DefineListString = ''
    
    RowTextSplit = ListStrings[0].split('\n')
    
    for x in ListStrings[1:]:
        splitStylevars.append(x.split('\n'))
    
    stylevarCleaned = []
    for stylevarRow in range(0,len(splitStylevars[0])):
        stylevarString = ''
        for x,label in zip(range(0,len(LabelStrings[2:])),LabelStrings[2:]):
            stylevarString += "%s='" %(label).strip()
            stylevarString += "%s' " %splitStylevars[x][stylevarRow].replace('\t',',').strip()
        stylevarCleaned.append(stylevarString)

    
    for x in range(2,len(LabelStrings)):
        DefineListString += "<stylevar name='%s'/>\n" %LabelStrings[x]

    DefineListString += "<define label='%s'>\n" %LabelStrings[0]
    
    rowNum = 1
    for rowText,stylevar in zip(RowTextSplit,stylevarCleaned):
        if rowText != '':
            DefineListString += ("<row label='%s%s' %s>%s</row>\n" %(LabelStrings[1],rowNum,stylevar,rowText.replace('&','&amp;').strip()))
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


layout = [[sg.Button('Simple Design List')],
 [sg.Button('Design List With Stylevar Group'), sg.Spin([i for i in range(1,11)], initial_value=1), sg.Text('Stylevar Number')]]
window1 = sg.Window('Decipher Define List Generator Tool', layout)
win2_active = False


while True:
    ev1, vals1 = window1.read(timeout=100)
    
    if ev1 == sg.WIN_CLOSED:
        break

####-------------------------------------------------------####
# Creates a simple Design List
#
####-------------------------------------------------------####
    if ev1 == 'Simple Design List' and not win2_active:
        win2_active = True
        
        window1.Hide()

        layout2 = [[sg.Text('Define List Label'), sg.Input(),sg.Text('Label Prefix'), sg.Input()],
                [sg.Col([[sg.Text("Row Text List")],[sg.Multiline(size = (20,20))]]), sg.Col([[sg.Text("Output")],[sg.Output(size = (20,20), key='-OUTOUT-')]])],
                [sg.Submit(), sg.Button('Clear')], 
                [sg.Button('Exit')]]
        
        window2 = sg.Window('Simple Define List', layout2)
        while True:
            ev2, vals2 = window2.read()
    
            dupesForPopup = []
            dupesForPopup = defineListDupesSingle(vals2[2])

            if len(dupesForPopup) > 0:
                sg.Popup('There are some duplicates in the list')

            text_input = defineListMakerSingle(vals2[2],vals2[0],vals2[1])
            print (text_input)

            if ev2 == 'Clear':
                 window2['-OUTOUT-'].update('')

            if ev2 == sg.WIN_CLOSED or ev2 == 'Exit':
                window2.close()
                win2_active = False
                window1.UnHide()
                break

##### ------------------------------------------------------------- #####
# Crates a Design list with any number of Stylevar
# 
#####---------------------------------------------------------------#####
    elif ev1 == 'Design List With Stylevar Group' and not win2_active:
        win2_active = True
        window1.Hide()

        NormalLabelsInput = [sg.Text('Define List Label'), sg.Input(size=(10,1), key="DLLabel"),sg.Text('Label Prefix'), sg.Input(size=(10,1), key="LabelPre", default_text="r")]
        StylevarInput = []
        ListInputLabels = [sg.Text("Row Text List", size=(20,1)), sg.Text("Stylevar 1", size=(20,1))]
        ListInputs = [sg.Col([[sg.Text("Row Text List")],[sg.Multiline(size = (20,20), key="RowText")]])]

        if vals1[0] > 0:
            for x in range(1,vals1[0]+1):
                StylevarInput.append(sg.Text('Stylevar label %s' %x))
                StylevarInput.append(sg.Input(default_text="cs:", size=(10,1), key="StylevarLabel_%s" %x))

                ListInputLabels.append(sg.Text("Stylevar %s" %x, size=(20,1)))
                ListInputs.append(sg.Col([[sg.Text("Stylevar %s" %x)],[sg.Multiline(size = (20,20), key="StylevarList_%s" %x)]]))
        

        ListInputLabels.append(sg.Text('Output', size=(20,1)))
        ListInputs.append(sg.Col([[sg.Text("Output")],[sg.Output(size = (20,20), key='-OUTOUT-')]]))

        layout2 = [ NormalLabelsInput, 
        StylevarInput,
        ListInputs,
        [sg.Submit(), sg.Button('Clear')], 
        [sg.Button('Exit')]]

        window2 = sg.Window('Define List With Stylevar Group', layout2)
        while True:
            ev2, vals2 = window2.read()

            LabelsList = []
            ListsList= []

            LabelsList.append(vals2['DLLabel'])
            LabelsList.append(vals2['LabelPre'])
            ListsList.append(vals2['RowText'])

            for x in range(1,vals1[0]+1):
                LabelsList.append(vals2['StylevarLabel_%s' %x])
                ListsList.append(vals2['StylevarList_%s' %x])

            ListsToCheck = listOfStringsToListOfLists(ListsList)

            if not listLengthCheck(ListsToCheck):
                listLengths = listLengthOutput(ListsToCheck)

                listLengthsString = ''
                for x in listLengths:
                    listLengthsString += "%s" %x
                    listLengthsString += " "

                sg.Popup('The Length of of the inputs are different. Please revise. Here are the lengths in order: %s' %listLengthsString)
            
            else:

                dupesForPopup = []
                dupesForPopup = defineListDupesSingle(ListsList[0])

                if len(dupesForPopup) > 0:
                    sg.Popup('There are some duplicates in the list')

                text_input = defineListMakerStylevarGroup(LabelsList,ListsList)
                print (text_input)

            if ev2 == 'Clear':
                 window2['-OUTOUT-'].update('')

            if ev2 == sg.WIN_CLOSED or ev2 == 'Exit':
                window2.close()
                win2_active = False
                window1.UnHide()
                break

window1.close()
#!/usr/bin/env python
# -*- coding: utf-8 -*-

JAMENDO_APP_NAME    = "jamloader"
JAMENDO_APP_VERSION = "3.0.4"
    
#big try around all the file to catch all the errors
try:
    ####
    #
    # Setup the include path
    #
    
    import os,sys, locale, shutil, exceptions
    #sys.stdout = sys.stderr = open("logfile.txt", "a")
    
    
    #go to jamloader3/ directory
    if (not os.path.isfile( os.path.join("resources", "icon_16.png") ) ):
        os.chdir(os.path.dirname(sys.executable));
    if (not os.path.isfile( os.path.join("resources", "icon_16.png") )):
        os.chdir(os.path.dirname(__name__ == '__main__' and sys.argv[0] or __file__))
        
    #find a pyjamlib copy
    if os.path.isdir( os.path.join( '..', 'pyjamlib') ):
        sys.path.insert(0, os.path.join( '..', 'pyjamlib'))
    else :
        sys.path.insert(0, 'pyjamlib')
    
    
    ####
    #
    # Next first thing, init debug
    #
    
    try:
        from jamendo.lib.DebugReport import DebugReportThread
    except Exception,e:
        print e
        print "Couldn't find PyJamLib. Check your jamloader installation."
        sys.exit(1)
    
    Debug = DebugReportThread(False,False,JAMENDO_APP_NAME,JAMENDO_APP_VERSION,"",True,True)
    Debug.start()
    
    
    
    
    ####
    #
    # Import some more python modules
    #
    
    import time, Queue
    
    
    ####
    #
    # Import QT
    #
    
    try:
        from PyQt4 import QtCore, QtGui, uic
    except Exception,e:
        Debug.error(2,"You need PyQt4 to run jamloader! (%s)" % e)
        time.sleep(5)
        sys.exit(1)
    
    Debug.debug("Default language is %s" % QtCore.QLocale().name())
    
    
    ####
    #
    # Import PyJamLib
    #
    
    try:
        from jamendo.lib.FlacEncoder import FlacEncoder
        from jamendo.lib.cdrip import CdRipper
        from jamendo.lib.ContentUploader import ContentUploaderThread
        from jamendo.lib import LocalPlatform
        from jamendo.lib.DebugReport import DebugReport
        from jamendo.lib.VersionCheck import VersionCheckThread
        from jamendo.lib.ContentUploadCheck import ContentUploadCheck
        
        from mainWindow import Ui_MainWindow
        
        
    except Exception,e:
        Debug.error(1, "Your PyJamLib installation looks corrupt or out of date, please reinstall jamloader : %s" % e)
        
        
    
    
    
    
    class jamloader3(QtGui.QApplication):
            ####
            #
            # Main Init function
            #
            def loadUI(self):
                
                self.mainWindow=QtGui.QMainWindow()
                self.ui = Ui_MainWindow()
                self.ui.setupUi(self.mainWindow)
                self.userHasFinished = False
                self.popupOpened = False
                self.sendRetry = {}
                self.sendRetryLimit = 3
                
                
                
                try :
                    
                    ###
                    #
                    # Some manual UI tweaks that crash 'pyuic' when done through qtDesigner 
                    #
                    self.setWindowIcon(QtGui.QIcon( os.path.join("resources", "icon_16.png") ))    
                    
                    self.ui.bottomFrame.hide()
                    
    
                    
                    ###
                    #
                    # Don't use os.path.join to retrieve the logo picture because QtCore has its own internal path convertion routine
                    #
                    self.ui.logoLabel.hide()
                    logoUrl = os.path.join("resources", "jamloader_logo.png")
                    self.ui.logoWidget.setStyleSheet("* {background-image : url(./resources/jamloader_logo.png); background-repeat: none}") 
                        
                    # Simulate a href with 'forgot your password' button
                    self.ui.lostPasswordButton.setStyleSheet("* {text-decoration : underline; color : blue}")
                    
                    ####
                    #
                    # Set the message 'drag your files here'
                    #
                    self.setInfoInList()
                    
                    self.ui.treeWidget.setRootIsDecorated(False)
                    self.ui.treeWidget.setAutoFillBackground(True)
                    self.ui.treeWidget.setDragEnabled(True)
                    self.ui.treeWidget.setAcceptDrops(True)
                    
                    ###
                    #
                    # clear treeview column title
                    #
                    emptyLabels = QtCore.QStringList("")
                    self.ui.treeWidget.setHeaderLabels(emptyLabels)
                    
                    ###
                    #
                    # Connect events to functions
                    #
                    self.connect(self.ui.pushButton_2, QtCore.SIGNAL("clicked()"), self.uploadButton_clicked)
                    self.connect(self.ui.passwordLineEdit, QtCore.SIGNAL("returnPressed()"), self.uploadButton_clicked)
                    self.connect(self.ui.pushButton_3, QtCore.SIGNAL("clicked()"), self.minusButton_clicked)
                    self.connect(self.ui.pushButton_4, QtCore.SIGNAL("clicked()"), self.plusButton_clicked)
                    self.connect(self.ui.lostPasswordButton, QtCore.SIGNAL("clicked()"), self.lostPasswordButton_clicked)
                
                    self.ui.treeWidget.__class__.dragEnterEvent = self.treeWidget_dragEnterEvent
                    self.ui.treeWidget.__class__.dragLeaveEvent = self.treeWidget_dragLeaveEvent
                    self.ui.treeWidget.__class__.dragMoveEvent = self.treeWidget_dragMoveEvent
                    self.ui.treeWidget.__class__.dropEvent = self.treeWidget_dropEvent
                    self.ui.treeWidget.__class__.mouseMoveEvent = self.treeWidget_mouseMoveEvent
                
                
                except Exception,e :
                    Debug.error(3,"during ui modification : " + str(e) )
                    
                self.isEncoding = False
                self.isRipping = False
                    
                self.finished = False
                
                self.prepareForLogin()
                self.mainWindow.show()
            
            
            def timerSetUp(self):
                ###
                #
                # setup the ²er function used to sync threads
                #
                try :
                    self.timer = QtCore.QTimer(self)
                    self.connect(self.timer, QtCore.SIGNAL("timeout()"), self.checker)
                    self.timer.start(2) # interval in msec
                except Exception, e:
                    Debug.error(3,"timer setup : " + str(e))
            
            
            
            def prepareForLogin(self):
                #print "Prepare for login"
                self.ui.frame_3.hide()
                self.step="login"
            
            def prepareForSending(self):
                self.ui.widgetTopSpacer.hide()
                self.ui.widgetBottomSpacer.hide()
                self.ui.frame_3.show()
                self.ui.label_2.show()
                #self.ui.label_2.hide()
                self.ui.frame_2.hide()
                self.ui.logoWidget.hide()
                # logoLabel visible
                self.ui.pushButton_2.setText( tr("I have no more track to send") )
                self.ui.pushButton_2.setDisabled(True)
            
            
            def setInfoInList(self):
                self.listCleaned = False
                for i in range(5):
                    newItem = QtGui.QTreeWidgetItem(self.ui.treeWidget)
                newItem2 = QtGui.QTreeWidgetItem(self.ui.treeWidget)
                newItem2.setTextColor(0, QtGui.QColor(128, 128, 128) )
                newItem2.setText(0, tr("Drag your files here,") )
                newItem2.setTextAlignment(0, 4)
                font = newItem2.font(0)
                font.setPixelSize(18)
                newItem2.setFont(0, font)
                newItem3 = QtGui.QTreeWidgetItem(self.ui.treeWidget)
                newItem3.setTextColor(0, QtGui.QColor(128, 128, 128) )
                newItem3.setFont(0, font)
                newItem3.setText(0, tr("click 'add file' or") )
                newItem3.setTextAlignment(0, 4)
                newItem3 = QtGui.QTreeWidgetItem(self.ui.treeWidget)
                newItem3.setTextColor(0, QtGui.QColor(128, 128, 128) )
                newItem3.setFont(0, font)
                newItem3.setText(0, tr("insert an audio CD") )
                newItem3.setTextAlignment(0, 4)
    
            def cleanList(self):
                foundItems = self.ui.treeWidget.findItems(QtCore.QString("*"), QtCore.Qt.MatchWildcard , 0)
                for i in range( len(foundItems) ) :
                    itemToDelete = foundItems[i]
                    self.ui.treeWidget.takeTopLevelItem(self.ui.treeWidget.indexOfTopLevelItem(itemToDelete))
                    
                self.ui.treeWidget.setColumnCount(4)
                self.ui.treeWidget.setColumnHidden(3, True)
                self.ui.treeWidget.setColumnWidth(0, 200)
                self.ui.treeWidget.setColumnWidth(1, 80 )
                self.ui.treeWidget.setColumnWidth(2, 45)
                self.ui.treeWidget.setAlternatingRowColors(True)
                labels = QtCore.QStringList( tr("Source") )
                labels.append( tr("Status") )
                labels.append( tr("%") )
                self.ui.treeWidget.setHeaderLabels(labels)
                    
                self.listCleaned = True
            
            def treeWidget_dragEnterEvent(self, event):
                
                accept=False
                
                if event.mimeData().hasText():
                    if event.mimeData().text() == "jamloader3-fileToDelete":
                        accept=True
                if event.mimeData().hasUrls():
                    accept=True
                
                if accept:
                    self.ui.treeWidget.setBackgroundRole(QtGui.QPalette.Highlight)
                    event.acceptProposedAction()
        
            def treeWidget_dragMoveEvent(self, event):
                if event.mimeData().hasText():
                    if event.mimeData().text() == "jamloader3-fileToDelete":
                        event.acceptProposedAction()
                if event.mimeData().hasUrls():
                    event.acceptProposedAction()
           
            def treeWidget_dragLeaveEvent(self, event):
                
                self.ui.treeWidget.setBackgroundRole(QtGui.QPalette.Window)
           
            def treeWidget_dropEvent(self, event):
                
                if event.mimeData().hasText():
                    if event.mimeData().text() == "jamloader3-fileToDelete":
                        event.accept()
                elif event.mimeData().hasUrls():
                   urlList = event.mimeData().urls()
                   url = urlList.pop(0)
                   qurl = QtCore.QUrl(url)
                   url = qurl.toLocalFile()
                   url = str( url.toLatin1() )
                   
                   result = ContentUploadCheck( url )
                   if result[1] > 0 or result[0]=="aiff":
                       (path , file) = os.path.split( url )
                       self.addFileToTree(file, url)
                       event.accept()
                   else :
                       QtGui.QMessageBox.warning(self.mainWindow, tr("Format error"), tr("This file is not supported <br>") + result[2] )
                   
                   
            def treeWidget_mouseMoveEvent(self,event):
                drag = QtGui.QDrag(self.ui.treeWidget)
                mimeData =  QtCore.QMimeData()
                mimeData.setText("jamloader3-fileToDelete")
                drag.setMimeData(mimeData)
                dropAction = drag.start(QtCore.Qt.MoveAction)
                if dropAction == 0:
                    #dropped to another widget, so we can delete it
                    itemToDelete = self.ui.treeWidget.selectedItems().pop(0)
                    self.ui.treeWidget.takeTopLevelItem(self.ui.treeWidget.indexOfTopLevelItem(itemToDelete))
                    self.setCancelStatus(itemToDelete)
                    
            def deleteSelectedItem(self):
                itemToDelete = self.ui.treeWidget.selectedItems().pop(0)  
                self.ui.treeWidget.takeTopLevelItem(self.ui.treeWidget.indexOfTopLevelItem(itemToDelete))
                self.setCancelStatus(itemToDelete)
    
            def setCancelStatus(self, itemToDelete):
                for i in range( len( track_list) ) :
                    if str(track_list[i]) == str(itemToDelete.text(3)) :
                        track_status[i] = "cancelled"
                    #print "       " + str(track_list[i]) + " -> " + str(track_status[i])
    
                
        
            def addFileToTree(self, fileName, id):
                if not self.listCleaned :
                    self.cleanList()
                
                # copy the track to a temporary folder with a unique filename then imediatelly add file to process list
                if not id[0:7]=="cdda://" :
                    try :
                        fileName = os.path.splitext(fileName)[0]
                    except Exception, e:
                        Debug.debug("Cannot remove file extension in %s" % fileName)
                    
                    try :
                        newFile = os.path.join(profile, "uploads" , "hdFile"+str(len( track_list)+1) )
                        shutil.copy( id, newFile )
                        id = newFile
                    except Exception, e:
                        Debug.debug("Cannot copy file from %s to %s" % (id, newFile) )
                    
                        
                newItem = QtGui.QTreeWidgetItem(self.ui.treeWidget)
                newItem.setText(0, fileName)
                newItem.setText(1, tr("Pending") )
                newItem.setText(2, "0 %")
                newItem.setText(3, id)
                self.ui.treeWidget.addTopLevelItem(newItem)
                
                self.addFileFromHDToProcessList(id)
                self.ui.pushButton_2.setDisabled(True)
                self.finished = False
                
    
            def setStatusForTrack(self, id, message):
                foundItems = self.ui.treeWidget.findItems(QtCore.QString(id), QtCore.Qt.MatchExactly, 3)
                foundItems[0].setText(1, message)
            
            def getTrackName(self, id):
                foundItems = self.ui.treeWidget.findItems(QtCore.QString(id), QtCore.Qt.MatchExactly, 3)
                return unicode(foundItems[0].text(0))
                
            def setPercentForTrack(self, id, percent):
                foundItems = self.ui.treeWidget.findItems(QtCore.QString(id), QtCore.Qt.MatchExactly, 3)
                foundItems[0].setText(2, str(percent) + " %")
    
            def updatePathColInList(self, old, new):
                #print "setting " + str(old) + " to " + str(new)
                foundItems = self.ui.treeWidget.findItems(QtCore.QString(old), QtCore.Qt.MatchExactly, 3)
                foundItems[0].setText(3, new)
                
    
            def minusButton_clicked(self):
                self.deleteSelectedItem()
        
        
            def plusButton_clicked(self):
                global last_opened_folder
                dlg = QtGui.QFileDialog.getOpenFileName(app.mainWindow, QtCore.QString( tr("Add sound file") ), last_opened_folder, QtCore.QString( tr("Audio files")+"(*.wav *.aiff *.aif *.flac);;"+ tr("All files" ) +"(*.*)"))
        
                if dlg :
                    dlg = unicode( dlg )
                    result = ContentUploadCheck( dlg )
                    if result[1] > 0 or result[0] == "aiff" :
                        (path, file) = os.path.split( dlg )
                        last_opened_folder = path
                        app.addFileToTree(file, dlg)
                    else :
                        QtGui.QMessageBox.warning(self.mainWindow, tr("Format error"), tr("This file is not supported <br>") + result[2] )
    
        
            def lostPasswordButton_clicked(self):
                if not LocalPlatform.openInBrowser("http://www.jamendo.com/fr/member/resendlp/") :
                    Debug.error(4, "Error while opening browser to track list : ")
                    dlg = QtGui.QMessageBox.warning(self.mainWindow, tr("No Browser found") , tr("Your browser was not found, you must go to <u>http://www.jamendo.com/fr/member/resendlp/</u>") )
                    
            
            def showRipDialog(self, device):
                dlg = QtGui.QMessageBox.question(self.mainWindow, QtCore.QString( tr("Cd detection") ), QtCore.QString( tr("A cd audio has been detected, do you want to add it to the playlist?" ) ), QtGui.QMessageBox.Cancel|QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
                if dlg == QtGui.QMessageBox.Ok :
                    cdRipperQueueIn.put(["getAudioTracks", device])
                    
            def addCddaTracksToList(self, count):
                if count > 0:
                    for i in range(count):
                        self.addFileToTree( tr("Cd audio track ")+str(i+1) , "cdda://"+str(i) )
                #self.addCddaToTrackToProcessList()
                
            def uploadButton_clicked(self):
                if self.step=="login":
                    self.loginStepButton()
                elif self.step=="sending":
                    self.sendingStepButton()
    
            def loginStepButton(self):
    
                user = self.ui.loginLineEdit.text()
                password = self.ui.passwordLineEdit.text()
                
                rep = False
                
                try : 
                    contentUploader.setCredentials(user, password)
                    rep = contentUploader.getSessionId()
                    
                except Exception, e: 
                    dlg = QtGui.QMessageBox.warning(self.mainWindow, tr("Authentication error"), tr("Your nickname or password seem invalid") )
                
                if rep:
                    cdRipperQueueIn.put(["startDetection"])
                    self.timerSetUp()
                    self.prepareForSending()
                    self.step = "sending"
                    #self.startFilesProcessing()
               
                        
            def sendingStepButton(self):
                Debug.debug("User clicked 'no more track to send' button")
                #self.userHasFinished = True
                if self.popupOpened :
                    self.openJamendo()
                
                #if not self.isProcessing :
                    #    foundItems  = app.ui.treeWidget.findItems(QtCore.QString("*"), QtCore.Qt.MatchWildcard , 2)
                    
                #    self.startFilesProcessing()
                        
                #else :
                    #    process already launched
                    #    dlg = QtGui.QMessageBox.warning(self.mainWindow, tr("Processing error") , tr("An upload is already processing") )
            '''                        
            def addCddaToTrackToProcessList(self):
                foundItems  = app.ui.treeWidget.findItems(QtCore.QString("*"), QtCore.Qt.MatchWildcard , 2)
                self.ui.progressBar.setMaximum( len(foundItems) )
                self.isProcessing = True
                ###
                #
                # ok we prepare the track_list 
                #
                for i in range( len(foundItems) ):
                    track_num = foundItems[i].text(3).toLatin1()
                    if str(track_num).startswith("cdda://") :
                        track_list.append(track_num)
                        track_status.append("not ripped")
            '''    
            def addFileFromHDToProcessList(self, trackId):
                    if str(trackId).startswith("cdda://") :
                        track_list.append( trackId )
                        track_status.append("not ripped")
                    else :
                        track_list.append( trackId )
                        track_status.append("not flac")
                
            def startFilesProcessing(self):
                '''
                foundItems  = app.ui.treeWidget.findItems(QtCore.QString("*"), QtCore.Qt.MatchWildcard , 2)
                self.ui.progressBar.setMaximum( len(foundItems) )
                self.isProcessing = True
                ###
                #
                # ok we prepare the track_list 
                #
                for i in range( len(foundItems) ):
                    track_num = foundItems[i].text(3).toLatin1()
                    if str(track_num).startswith("cdda://") :
                        track_list.append(track_num)
                        track_status.append("not ripped")
                    else :
                        track_list.append(track_num)
                        track_status.append("not flac")
                '''
                ###
                #
                # now we start the good threads for each tracks
                #
                #self.launchNextRip()
                #self.launchNextEncoding()
    
            ###
            #
            # this functions parse the track_list and launch the processes
            #
            def launchNextRip(self):
                for i in range(len(track_list) ) :
                        if track_status[i]=="not ripped" and not app.isRipping :
                            cdRipperQueueIn.put(["extractTrackToFile", self.cdDevice, str(track_list[i]).lstrip("cdda://"), os.path.join(profile, "uploads" , "output"+ str(track_list[i]).lstrip("cdda://") +".wav" ) ])
                            app.isRipping = True
    
    
            def launchNextEncoding(self):
                for i in range(len(track_list) ) :
                        if track_status[i]=="not flac" and not app.isEncoding :
                            flacEncoderQueueIn.put(["toFlac", str(track_list[i]), self.verifyDestPath( str(track_list[i]) +"_flac") ])
                            self.isFlacingTrack = track_list[i];
                            app.isEncoding = True
    
            ####
            #
            # flac files encoded from wav need that in order to not be outputed in orig directory
            #
            def verifyDestPath(self, url):
                # Qt use unix path separator even on win32 (it's compiled on top of Mingw)
                # so we have to convert url to win32 style
                if current_os == "windows" :
                    url = url.replace("/", "\\")
                (path, filename) = os.path.split(url)
                if path != os.path.join(profile, "uploads") :
                    return os.path.join(profile, "uploads", filename)
                return url
    
            ###
            #
            # the main function call by the QTimer
            #
            def checker(self):
                
                self.launchNextRip()
                self.launchNextEncoding()
                
                if not cdRipperQueueOut.empty():
                    msg = cdRipperQueueOut.get()
    
                    if msg[0]=="cd_detect_mount":
                        self.cdDevice = msg[1]
                        app.showRipDialog(self.cdDevice)
    
                    elif msg[0]=="cd_tracks":
                        self.addCddaTracksToList( len(msg[1]) )
                        
                    elif msg[0]=="cd_extract_start":
                        self.isRipping=True
                        self.isRippingTrack="cdda://" + msg[1]
                        
                    elif msg[0]=="cd_extract_stop":
                        self.isRipping=False
                        
                        ###
                        #
                        # update the status of the track in the hidden column
                        #
                        for i in range( len(track_list) ) :
                            if track_list[i]==self.isRippingTrack:
                                if track_status[track_list.index( self.isRippingTrack )] != "cancelled" :
                                    track_list[i]=os.path.join(profile, "uploads", "output" + self.isRippingTrack.lstrip("cdda://") +".wav")
                                    app.updatePathColInList(self.isRippingTrack, os.path.join(profile, "uploads", "output"+ self.isRippingTrack.lstrip("cdda://") +".wav") )
                                    track_status[i] = "not flac"
                                self.launchNextRip()
                                self.launchNextEncoding()
                        
                    
                    elif msg[0]=="cd_extract_progress":
                        if track_status[track_list.index( self.isRippingTrack )] != "cancelled" :
                            self.setPercentForTrack(self.isRippingTrack, msg[1])
                            self.setStatusForTrack(self.isRippingTrack, "Extracting")
                      
                    elif msg[0]=="error":
                        if msg[1]!="no cd found":
                            Debug.error(5,"cdrip error : " + msg[1])
                        else : 
                            Debug.debug("cdrip error : " + msg[1])
                        
                        
                if not versionCheckQueueOut.empty():
                    msg = versionCheckQueueOut.get()
                    
                    #display a warning about no net connection?
                    if msg[0]=="error":
                        Debug.debug("versionCheck failed : %s" % msg[1])
                        dlg = QtGui.QMessageBox.critical(self.mainWindow, tr("Network error"), tr("Jamloader3 couldn't connect to internet, please verify your network") )                    
                        
                    elif msg[0]=="result":
                        Debug.debug("versionCheck success : %s" % msg[1])
                        
                        if msg[1]["upgrade"]=="must":
                            
                            dlg = QtGui.QMessageBox.critical(self.mainWindow, tr("Software update"), tr("This version of Jamloader3 is out of date, and is not allowed to run anymore. Please download and install the new version.") )
                            
                            if not LocalPlatform.openInBrowser("http://www.jamendo.com/jamloader/") :
                                Debug.error(8,"Error while opening browser during must upgrade")
                                dlg = QtGui.QMessageBox.warning(self.mainWindow, tr("No Browser found") , tr("Your browser was not found, you must go to http://www.jamendo.com/jamloader/") )
                        
                            exitJamloader()
                            pass
                        elif msg[1]["upgrade"]=="should":
                            #popup ok/cancel ; if ok redirect to "jamendo.com/software_update/"+JAMENDO_APP_NAME
                            dlg = QtGui.QMessageBox.warning(self.mainWindow, tr("Software update"), tr("This version of Jamloader3 is out of date, please download and install the new version. Do you want to go to Jamloader download area now ?") , QtGui.QMessageBox.Ok|QtGui.QMessageBox.Cancel, QtGui.QMessageBox.Ok)
                            if dlg == QtGui.QMessageBox.Ok :
                            
                                if not LocalPlatform.openInBrowser("http://www.jamendo.com/jamloader/") :
                                    Debug.error(8,"Error while opening browser during should upgrade")
                                    dlg = QtGui.QMessageBox.warning(self.mainWindow, tr("No Browser found"), tr("Your browser was not found, you must go to http://www.jamendo.com/jamloader/") )
                        
                                    exitJamloader()
                            
                            pass
                        
                    
    
                if not flacEncoderQueueOut.empty():
                    msg = flacEncoderQueueOut.get()
                    
                    
                    if msg[0]=="flac_done":
                        #contentUploaderQueuein.put()
                        pass
                    
                    elif msg[0]=="flac_error":
                        Debug.error(6, "Error during flac encoding : "+ msg[1])
                        dlg = QtGui.QMessageBox.warning(self.mainWindow, tr("File corrupted"), tr("Your file seems corrupted, a report was sent to the technical team.") + msg[1] )
                        track_status[track_list.index( self.isFlacingTrack )] = "cancelled"
                        self.setStatusForTrack( self.isFlacingTrack, "Error")
                        self.isEncoding = False
                        self.launchNextEncoding()
                        
                    if msg[0]=="flac_progress":
                        if track_status[track_list.index( self.isFlacingTrack )] != "cancelled" :
                            self.setStatusForTrack( self.isFlacingTrack, "Converting")
                            self.setPercentForTrack( self.isFlacingTrack, msg[1])
                        #we need to update status until extract is finished
                        if msg[1]==100:
                            for i in range( len(track_list) ) :
                                if track_list[i]==self.isFlacingTrack:
                                    if track_status[track_list.index( self.isFlacingTrack )] != "cancelled" :
                                        # don't change file extension if it was a flac already
                                        if ContentUploadCheck( self.isFlacingTrack )[0] != "flac":
                                            app.updatePathColInList(self.isFlacingTrack, self.verifyDestPath( str(self.isFlacingTrack) ) +"_flac")
                                            track_list[i] =  self.verifyDestPath( str(self.isFlacingTrack) ) + "_flac"

                                        #print "setvalue : ", str(i+1)
                                        self.ui.progressBar.setValue(i+1)
                                        track_status[i] = "not sent"
                            self.isEncoding = False
                            self.launchNextEncoding()
                
                if not self.isSending:
                    for i in range( len(track_list) ) :
                            if track_status[i] == "not sent" and not self.isSending:
                                self.isSending = True   
                                #contentUploader.setUploadTrack(track_list[i])
                                #print "send : %s -- %s" % ( track_list[i], self.getTrackName(track_list[i]) )
                                contentUploaderQueueIn.put(["addTrack", track_list[i], self.getTrackName(track_list[i]) ])
                                self.sendingTrack = track_list[i]
                    
                
                
                if not contentUploaderQueueOut.empty():           
                    msg = contentUploaderQueueOut.get()
                    #print ["msg from cu : ", msg]
                    # messages from from getSessionId
                    if msg[0]=="Error":
                        exeptionReturn = msg[1]
                        if isinstance( exeptionReturn, exceptions.Exception ) : 
                            if exeptionReturn.message[0]==10 : # it's a md5 error  put this file in contentuploader queue to upload it again
                                if not self.sendingTrack in self.sendRetry :
                                    self.sendRetry[self.sendingTrack] = 0
                                else :
                                    self.sendRetry[self.sendingTrack] += 1
                                
                                if self.sendRetry[self.sendingTrack] < self.sendRetryLimit :
                                    contentUploaderQueueIn.put(["addTrack", self.sendingTrack, self.getTrackName(track_list[i])])
                                    Debug.debug("error while finallizing %s : md5 do not match will retry!" % self.sendingTrack )
                                else :
                                    self.setStatusForTrack( self.sendingTrack, "Error" )
                                    Debug.error(7,"error while finallizing %s : md5 do not match , max retry reach !" % self.sendingTrack )
                        else :
                            Debug.error(7,"while sending : "+ str(exeptionReturn) )
                            #dlg = QtGui.QMessageBox.warning(self.mainWindow, tr("Network error"), tr("An error occurs while sending file. Please verify your network connection.") )
                        
                    if msg[0]=="debug":
                        Debug.debug("Warning while sending : "+ str(msg[1]) )
                    if msg[0]=="sessionid":
                        Debug.debug( "sess id : " + msg[1])
                    # messages from uploadNow
                    if msg[0]=="trackid":
                        Debug.debug("track id : " + str(msg[1]) )
                    # messages from uploadTrackToXmlrpcServer
                    if msg[0]=="status":
                        #print "status -> ",
                        value = msg[1]
                        if value[0] == "hashing":
                            Debug.debug( "hashing" )
                        if value[0] == "finalizing":
                            Debug.debug( "finalizing" )
                            for i in range( len(track_list) ) :
                                if track_list[i] == value[1]:
                                    if track_status[track_list.index( self.sendingTrack )] != "cancelled" :
                                        track_status[i] = "sent"                                
                                        self.setStatusForTrack( self.sendingTrack, "Finished" )
                                        # sometime track upload flags himself finished with a percentage < 100 % because percentage increased to fast to be catched
                                        self.setPercentForTrack( self.sendingTrack, str( 100 ) )
                                    
                                    self.isFinished()
                            self.isSending = False
                        if value[0] == "uploading":
                            percentage = value[1]
                            #self.setPercentForTrack( self.sendingTrack, str( int(percentage) ) + " %" )
                            #print self.sendingTrack
                            if percentage > 99 :
                                percentage = 100
                            if track_status[track_list.index( self.sendingTrack )] != "cancelled" :
                                self.setPercentForTrack( self.sendingTrack, str( int(percentage) ) )
                                self.setStatusForTrack( self.sendingTrack, "Sending" )
                            #print "uploading : " + str(percentage)
                            
                if self.finished and self.userHasFinished and not self.popupOpened :
                    self.popupOpened = True
                    self.openJamendo()
                    
            def openJamendo(self):
                if not LocalPlatform.openInBrowser("http://www.jamendo.com/upload/") :
                        Debug.error(8,"Error while opening browser to track list ")
                        dlg = QtGui.QMessageBox.warning(self.mainWindow, tr("No Browser found"), tr("Your browser was not found, you must go to http://www.jamendo.com/upload/") )   
     
                    
            def isFinished(self) :
                if not self.finished :
                    somethingToSendRemain = False
                    for i in range( len(track_list) ) :
                        if not (track_status[i] == "sent" or track_status[i] == "cancelled") :
                            somethingToSendRemain = True
                            
            
                    if not somethingToSendRemain :
                        self.userHasFinished = True
                        self.finished = True;
                        print " ---> nothingRemain"
                        self.ui.pushButton_2.setDisabled(False)
                                 
    
    
       
    ###
    #
    # Create the profile : ~/(.)jamendo/jamloader2
    #
    def createProfile(curOs):
        if curOs == "windows":
            profile = os.path.join(os.path.expanduser("~"),
                                                 "jamendo", "jamloader3")
        else:
            profile = os.path.join(os.path.expanduser("~"),
                                                ".jamendo", "jamloader3")
    
        #testing
        if False:
            profile = os.path.join(profile,'I\xf1t\xebrn\xe2ti\xf4n\xe0liz\xe6ti\xf8n')
                
        uploads = os.path.join(profile, "uploads")
        if not os.path.exists(uploads):
            # Create the profile dirs
            os.makedirs(uploads)
        else :
            # Erase file remaining from previous session
            if curOs=="windows":
                os.system("del \"" + os.path.join(profile, "uploads") + "\*\" /q")
            else :
                os.system("rm -Rf " + os.path.join(profile, "uploads") + "/* ")
            
        return profile
            
    
    current_os = LocalPlatform.getOS()
         
    
    # Create profile dirs
    profile = createProfile(current_os)  
    
    last_opened_folder = os.path.expanduser("~")
    
    track_list=[]
    track_status=[]
    
    app = jamloader3(sys.argv)
    app.isProcessing = False
    
    if current_os == "windows" :
        app.setStyle(QtGui.QStyleFactory.create("Cleanlooks")) 
    
    ###
    #
    # convenience function for translation 
    #
    def tr(code) : 
        return QtGui.QApplication.translate("@default", code , None, QtGui.QApplication.UnicodeUTF8)
    
    
    try :
        translator = QtCore.QTranslator()
        translator.load("./locale/" + str(QtCore.QLocale().name()) + ".qm")
        app.installTranslator(translator)
    except Exeption, e:
        Debug.error(9,"in translation process : " + str(e))
    
    
    
    try:
        versionCheckQueueOut = Queue.Queue(2)
        versionCheck = VersionCheckThread(versionCheckQueueOut,JAMENDO_APP_NAME,JAMENDO_APP_VERSION)
        versionCheck.start()
    except Exception,e:
        Debug.error(3,"during versionCheck thread launch" + str(e))
    
    try :
        cdRipperQueueIn = Queue.Queue(10000)
        cdRipperQueueOut = Queue.Queue(10000)
        cdripper = CdRipper(cdRipperQueueIn, cdRipperQueueOut)
        cdripper.start()
    except Exception, e: 
        Debug.error(3,"during cdripper thread launch" + str(e))
    
    try :
        flacEncoderQueueIn = Queue.Queue(10000)
        flacEncoderQueueOut = Queue.Queue(10000)
        flacEncoder = FlacEncoder(flacEncoderQueueIn, flacEncoderQueueOut)
        flacEncoder.start()
    except Exception, e:
        Debug.error(3,"during flacEncoder thread launch" + str(e))
    
    app.isSending = False
    try :
        contentUploaderQueueIn = Queue.Queue(10000)
        contentUploaderQueueOut = Queue.Queue(10000)
        contentUploader = ContentUploaderThread(contentUploaderQueueIn, contentUploaderQueueOut)
        contentUploader.contentUploader.setClientInfo({"type":JAMENDO_APP_NAME,"version":JAMENDO_APP_VERSION,"string":"PyJamLib/Jamloader"})
        contentUploader.start()
    except Exception,e :
        Debug.error(3,"during contentuploader thread launch" + str(e))
    
    
    
    #try :
    app.loadUI()
    
    
    def exitJamloader() :
        try :
            cdRipperQueueIn.put(["exit"])
            flacEncoderQueueIn.put(["exit"])
            contentUploaderQueueIn.put(["exit"])
        except Exception, e :
            Debug.error(10,"error while destoying threads >" + str(e))
        else :
            Debug.debug("application ends normally")
            time.sleep(2)
            #import threading
            #print threading.enumerate()
            sys.exit(1)
            
            
    app.exec_()
    #except Exception, e :
    #    debug("error during app run : " + str(e))
    exitJamloader()







#normal exit
except SystemExit,v:
    sys.exit(v)

#there was an unexpected error. Try to send an independent bug report.
except Exception,e:
    
    print e
    try:
        import sys,os
        
        #find a pyjamlib copy
        if os.path.isdir( os.path.join( '..', 'pyjamlib') ):
            sys.path.insert(0, os.path.join( '..', 'pyjamlib'))
        else :
            sys.path.insert(0, 'pyjamlib')
        from jamendo.lib.DebugReport import DebugReport
        
        synchronousDebug = DebugReport(JAMENDO_APP_NAME,JAMENDO_APP_VERSION,"",True,True)

        
        import traceback
        errorstring = str(traceback.format_exception(sys.exc_type, sys.exc_value, sys.exc_traceback))
        
        
        synchronousDebug.error(11,"Fatal error in Jamloader : "+errorstring)
        
        print "\n\nThere was an error while running Jamloader. A report has been sent. We'll do our best to fix this bug in the next Jamloader version. In the meantime, please use our web uploader here : http://www.jamendo.com/upload/\n\n"
    except Exception,ee:
        
        import traceback, sys
        errorstring = str(traceback.format_exception(sys.exc_type, sys.exc_value, sys.exc_traceback))
        
        print "\n\nThere was an error while running Jamloader. A report could not be sent to our servers. Please email us this error report at jamloader@jamendo.com . In the meantime, please use our web uploader here : http://www.jamendo.com/upload/\n\n"+errorstring
        
    

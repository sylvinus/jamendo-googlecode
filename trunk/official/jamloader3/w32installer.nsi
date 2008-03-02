; w32installer.nsi
;
; This script installs jamloader3


!define JAMLOADER_VERSION "3.0.4"


;--------------------------------
;Include Modern UI

  !include "MUI.nsh"

;--------------------------------
;Variables

  Var MUI_TEMP
  Var STARTMENU_FOLDER

;--------------------------------
;General

  ;Name and file
Name "Jamloader3"
SetDatablockOptimize on
CRCCheck on
OutFile "Jamloader3Installer-${JAMLOADER_VERSION}.exe"

  ;Default installation folder
  InstallDir "$PROGRAMFILES\Jamloader\${JAMLOADER_VERSION}"
  
  ;Get installation folder from registry if available
  InstallDirRegKey HKCU "Software\Jamloader\${JAMLOADER_VERSION}" ""

;--------------------------------
;Interface Settings

  !define MUI_ABORTWARNING
  !define MUI_HEADERIMAGE
  !define MUI_HEADERIMAGE_BITMAP "${NSISDIR}\Contrib\Graphics\Header\nsis.bmp" ; optional

;--------------------------------
;Language Selection Dialog Settings

  ;Remember the installer language
  !define MUI_LANGDLL_REGISTRY_ROOT "HKCU" 
  !define MUI_LANGDLL_REGISTRY_KEY "Software\Jamloader\${JAMLOADER_VERSION}" 
  !define MUI_LANGDLL_REGISTRY_VALUENAME "Installer Language"




;Function .onGUIInit
;BgImage::SetBg /NOUNLOAD /GRADIENT 0xFF 0xFF 0xFF 0xFF 0xFF 0xFF
;BgImage::SetBg /NOUNLOAD /GRADIENT 0xFF 0xFF 0xFF 0xFF 0xFF 0xFF
;BgImage::AddImage /NOUNLOAD resources\jamendo_logo.bmp 0 0
;	CreateFont $R0 "Trebuchet MS" 50 700
;	BgImage::SetBg /GRADIENT 255 255 255 255 255 255
;	BgImage::AddImage /NOUNLOAD resources\jamendo_logo.bmp 100 100
;	BgImage::AddText /NOUNLOAD "Jamloader3 Installation" $R0 0 0 0 40 40 60 60
;	BgImage::Redraw /NOUNLOAD
;FunctionEnd
; 
;Function .onGUIEnd
;	; Destroy must not have /NOUNLOAD so NSIS will be able to unload and delete BgImage before it exits
;	BgImage::Destroy
;FunctionEnd



;--------------------------------
;Pages

  !insertmacro MUI_PAGE_LICENSE "misc\LICENSE"
  !insertmacro MUI_PAGE_DIRECTORY

  ;Start Menu Folder Page Configuration
  !define MUI_STARTMENUPAGE_REGISTRY_ROOT "HKCU" 
  !define MUI_STARTMENUPAGE_REGISTRY_KEY "Software\Jamloader\${JAMLOADER_VERSION}" 
  !define MUI_STARTMENUPAGE_REGISTRY_VALUENAME "Start Menu Folder"
  
  !insertmacro MUI_PAGE_STARTMENU Application $STARTMENU_FOLDER

  !insertmacro MUI_PAGE_INSTFILES
  
  !insertmacro MUI_UNPAGE_CONFIRM
  !insertmacro MUI_UNPAGE_INSTFILES

;--------------------------------
;Languages

  !insertmacro MUI_LANGUAGE "English" # first language is the default language
  !insertmacro MUI_LANGUAGE "French"
;  !insertmacro MUI_LANGUAGE "German"
;  !insertmacro MUI_LANGUAGE "Spanish"
;  !insertmacro MUI_LANGUAGE "SimpChinese"
;  !insertmacro MUI_LANGUAGE "TradChinese"
;  !insertmacro MUI_LANGUAGE "Japanese"
;  !insertmacro MUI_LANGUAGE "Korean"
;  !insertmacro MUI_LANGUAGE "Italian"
;  !insertmacro MUI_LANGUAGE "Dutch"
;  !insertmacro MUI_LANGUAGE "Danish"
;  !insertmacro MUI_LANGUAGE "Swedish"
;  !insertmacro MUI_LANGUAGE "Norwegian"
;  !insertmacro MUI_LANGUAGE "Finnish"
;  !insertmacro MUI_LANGUAGE "Greek"
;  !insertmacro MUI_LANGUAGE "Russian"
;  !insertmacro MUI_LANGUAGE "Portuguese"
;  !insertmacro MUI_LANGUAGE "PortugueseBR"
;  !insertmacro MUI_LANGUAGE "Polish"
;  !insertmacro MUI_LANGUAGE "Ukrainian"
;  !insertmacro MUI_LANGUAGE "Czech"
;  !insertmacro MUI_LANGUAGE "Slovak"
;  !insertmacro MUI_LANGUAGE "Croatian"
;  !insertmacro MUI_LANGUAGE "Bulgarian"
;  !insertmacro MUI_LANGUAGE "Hungarian"
;  !insertmacro MUI_LANGUAGE "Thai"
;  !insertmacro MUI_LANGUAGE "Romanian"
;  !insertmacro MUI_LANGUAGE "Latvian"
;  !insertmacro MUI_LANGUAGE "Macedonian"
;  !insertmacro MUI_LANGUAGE "Estonian"
;  !insertmacro MUI_LANGUAGE "Turkish"
;  !insertmacro MUI_LANGUAGE "Lithuanian"
;  !insertmacro MUI_LANGUAGE "Catalan"
;  !insertmacro MUI_LANGUAGE "Slovenian"
;  !insertmacro MUI_LANGUAGE "Serbian"
;  !insertmacro MUI_LANGUAGE "SerbianLatin"
;  !insertmacro MUI_LANGUAGE "Arabic"
;  !insertmacro MUI_LANGUAGE "Farsi"
;  !insertmacro MUI_LANGUAGE "Hebrew"
;  !insertmacro MUI_LANGUAGE "Indonesian"
;  !insertmacro MUI_LANGUAGE "Mongolian"
;  !insertmacro MUI_LANGUAGE "Luxembourgish"
;  !insertmacro MUI_LANGUAGE "Albanian"
;  !insertmacro MUI_LANGUAGE "Breton"
;  !insertmacro MUI_LANGUAGE "Belarusian"
;  !insertmacro MUI_LANGUAGE "Icelandic"
;  !insertmacro MUI_LANGUAGE "Malay"
;  !insertmacro MUI_LANGUAGE "Bosnian"
;  !insertmacro MUI_LANGUAGE "Kurdish"

;--------------------------------
;Reserve Files
  
  ;These files should be inserted before other files in the data block
  ;Keep these lines before any File command
  ;Only for solid compression (by default, solid compression is enabled for BZIP2 and LZMA)
  
  !insertmacro MUI_RESERVEFILE_LANGDLL

;--------------------------------
;Installer Sections

Section "Dummy Section" SecDummy

  

  SetOutPath "$INSTDIR"

  WriteUninstaller "Uninstall.exe"



  SetOutPath "$INSTDIR"

  File "dist\*.*"

  SetOutPath "$INSTDIR\resources"
  File "dist\resources\*.*"

  SetOutPath "$INSTDIR\locale"
  File "dist\locale\*.*"

  SetOutPath "$INSTDIR\bin_pyjamlib"
  File "dist\bin_pyjamlib\*.*"
  
  SetOutPath "$INSTDIR\bin_pyjamlib\file"
  File "dist\bin_pyjamlib\file\*.*"

  !insertmacro MUI_STARTMENU_WRITE_BEGIN Application
    
    ;Create shortcuts
    CreateDirectory "$SMPROGRAMS\$STARTMENU_FOLDER"
    CreateShortCut "$SMPROGRAMS\$STARTMENU_FOLDER\Jamloader ${JAMLOADER_VERSION}.lnk" "$INSTDIR\jamloader3.exe"
    CreateShortCut "$SMPROGRAMS\$STARTMENU_FOLDER\Uninstall ${JAMLOADER_VERSION}.lnk" "$INSTDIR\Uninstall.exe"
  
  !insertmacro MUI_STARTMENU_WRITE_END


  ;Store installation folder
  WriteRegStr HKCU "Software\Jamloader" "" $INSTDIR
  

SectionEnd

;--------------------------------
;Installer Functions

Function .onInit



	# the plugins dir is automatically deleted when the installer exits
	InitPluginsDir
	File /oname=$PLUGINSDIR\splash.bmp "resources\jamendo_logo.bmp"

	splash::show 1500 $PLUGINSDIR\splash

  !insertmacro MUI_LANGDLL_DISPLAY

FunctionEnd

Function .onInstSuccess
	Exec '"$INSTDIR\jamloader3.exe"'
FunctionEnd

;--------------------------------
;Descriptions

  ;USE A LANGUAGE STRING IF YOU WANT YOUR DESCRIPTIONS TO BE LANGAUGE SPECIFIC

  ;Assign descriptions to sections
  !insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
    !insertmacro MUI_DESCRIPTION_TEXT ${SecDummy} "A test section."
  !insertmacro MUI_FUNCTION_DESCRIPTION_END

 
;--------------------------------
;Uninstaller Section

Section "Uninstall"


  RMDir /r "$INSTDIR"

  DeleteRegKey HKCU "Software\Jamloader\${JAMLOADER_VERSION}"
  DeleteRegKey HKCU "Software\Jamloader"




  !insertmacro MUI_STARTMENU_GETFOLDER Application $MUI_TEMP
    
  Delete "$SMPROGRAMS\$MUI_TEMP\Uninstall ${JAMLOADER_VERSION}.lnk"
  Delete "$SMPROGRAMS\$MUI_TEMP\Jamloader ${JAMLOADER_VERSION}.lnk"

  ;Delete empty start menu parent diretories
  StrCpy $MUI_TEMP "$SMPROGRAMS\$MUI_TEMP"
 
  startMenuDeleteLoop:
	ClearErrors
    RMDir $MUI_TEMP
    GetFullPathName $MUI_TEMP "$MUI_TEMP\.."
    
    IfErrors startMenuDeleteLoopDone
  
    StrCmp $MUI_TEMP $SMPROGRAMS startMenuDeleteLoopDone startMenuDeleteLoop
  startMenuDeleteLoopDone:


SectionEnd

;--------------------------------
;Uninstaller Functions

Function un.onInit

  !insertmacro MUI_UNGETLANGUAGE
  
FunctionEnd






; NSIS installer script for TRANSKRYBER
; Requires NSIS to build: https://nsis.sourceforge.io/

Name "TRANSKRYBER"
OutFile "TRANSKRYBER_Installer.exe"
InstallDir "$PROGRAMFILES\\TRANSKRYBER"
RequestExecutionLevel admin

Section "Install"
  SetOutPath "$INSTDIR"
  ; Copy files
  File "..\\dist\\TRANSKRYBER.exe"
  File "..\\run_transkryber.vbs"
  File "..\\run_gui.bat"
  File "..\\README.md"
  File "..\\LICENSE"

  ; Create Desktop shortcut
  CreateShortCut "$DESKTOP\\TRANSKRYBER.lnk" "$INSTDIR\\TRANSKRYBER.exe" "" "$INSTDIR\\TRANSKRYBER.exe" 0

  ; Optionally add install dir to system PATH (requires admin)
  ; Read existing PATH
  ReadRegStr $0 HKLM "SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment" "Path"
  StrCpy $1 "$0;$INSTDIR"
  WriteRegStr HKLM "SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment" "Path" "$1"
  System::Call 'Kernel32::SetEnvironmentVariableA(t, t) i ("Path", "$1")'
SectionEnd

Section "Uninstall"
  Delete "$INSTDIR\\TRANSKRYBER.exe"
  Delete "$INSTDIR\\run_transkryber.vbs"
  Delete "$INSTDIR\\run_gui.bat"
  Delete "$INSTDIR\\README.md"
  Delete "$INSTDIR\\LICENSE"
  Delete "$DESKTOP\\TRANSKRYBER.lnk"
  RMDir "$INSTDIR"
SectionEnd

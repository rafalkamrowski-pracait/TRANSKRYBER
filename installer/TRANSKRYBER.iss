; Inno Setup script for TRANSKRYBER
; Requires Inno Setup: https://jrsoftware.org/isinfo.php

[Setup]
AppName=TRANSKRYBER
AppVersion=1.0
DefaultDirName={pf}\TRANSKRYBER
DisableProgramGroupPage=yes
OutputBaseFilename=TRANSKRYBER_Installer
Compression=lzma
SolidCompression=yes
PrivilegesRequired=admin

[Files]
Source: "..\dist\TRANSKRYBER.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\run_transkryber.vbs"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\run_gui.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\LICENSE"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\TRANSKRYBER"; Filename: "{app}\TRANSKRYBER.exe"
Name: "{userdesktop}\TRANSKRYBER"; Filename: "{app}\TRANSKRYBER.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\TRANSKRYBER.exe"; Description: "Uruchom TRANSKRYBER"; Flags: nowait postinstall skipifsilent

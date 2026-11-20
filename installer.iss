; Define a fallback version for when you build locally
#ifndef MyAppVersion
  #define MyAppVersion "1.0.0"
#endif

#define MyAppName "Vista"
#define MyAppPublisher "Steven Ondieki"
#define MyAppExeName "Vista.exe"

[Setup]
AppId={3D8F02F1-8D5D-4F77-B0C7-3D5BFA7B88C}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}

DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}

OutputDir=installer
OutputBaseFilename={#MyAppName}_Setup_{#AppVersion}

Compression=lzma2
SolidCompression=yes
WizardStyle=modern

ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

PrivilegesRequired=admin

SetupIconFile=assets\icon.ico
LicenseFile=LICENSE.txt
UninstallDisplayIcon={app}\{#MyAppExeName}


[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; Flags: unchecked

[Files]
Source: "dist\Vista\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Vista"; Filename: "{app}\Vista.exe"
Name: "{autodesktop}\Vista"; Filename: "{app}\Vista.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\Vista.exe"; Description: "Launch Vista"; Flags: nowait postinstall skipifsilent
; Script gerado pelo Inno Setup para o SUAP-CD

[Setup]
AppName=SUAP-CD
AppVersion={#AppVersion}
AppPublisher=Sua Organização
AppSupportURL=https://ifmt.edu.br
AppUpdatesURL=https://ifmt.edu.br
DefaultDirName={autopf}\SUAP-CD
DefaultGroupName=SUAP-CD
OutputDir=dist
OutputBaseFilename=suap-cd-{#AppVersion}-Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\suapcd.exe
LicenseFile=LICENSE
PrivilegesRequired=admin

[Languages]
Name: "portuguese"; MessagesFile: "compiler:Languages\Portuguese.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\suapcd.exe"; DestDir: "{app}"; Flags: ignoreversion
; Source: "LICENSE"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\SUAP-CD"; Filename: "{app}\suapcd.exe"
Name: "{group}\{cm:UninstallProgram,SUAP-CD}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\SUAP-CD"; Filename: "{app}\suapcd.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\suapcd.exe"; Description: "{cm:LaunchProgram,SUAP-CD}"; Flags: nowait postinstall skipifsilent
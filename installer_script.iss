[Setup]
AppName=Combination Generator
AppVersion=1.0
DefaultDirName={userdocs}\Combination Generator
DefaultGroupName=Combination Generator
OutputDir=C:\Users\maxyb\Desktop\Installers
OutputBaseFilename=Combination Generator Setup

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional Options"

[Files]
Source: "C:\Users\maxyb\Desktop\Finale\Combination Generator.exe"; DestDir: "{app}"

[Icons]
Name: "{group}\Combination Generator"; Filename: "{app}\Combination Generator.exe"; Tasks: desktopicon
Name: "{commondesktop}\Combination Generator"; Filename: "{app}\Combination Generator.exe"; Tasks: desktopicon

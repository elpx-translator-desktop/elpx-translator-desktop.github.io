#define MyAppName "ELPX Translator Desktop"
#define MyAppPublisher "Juan José de Haro"
#define MyAppURL "https://github.com/elpx-translator-desktop/elpx-translator-desktop.github.io"
#define MyAppExeName "ELPXTranslatorDesktop.exe"
#ifndef MyAppVersion
  #define MyAppVersion "0.0.0"
#endif
#ifndef MyAppSource
  #define MyAppSource "dist\\ELPXTranslatorDesktop"
#endif
#ifndef MyOutputDir
  #define MyOutputDir "dist-installer"
#endif

[Setup]
AppId={{8F8E9BA1-A415-4A64-83A1-E1A2AF5D2C85}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}/releases
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
LicenseFile=LICENSE
OutputDir={#MyOutputDir}
OutputBaseFilename=elpx-translator-desktop-windows-{#MyAppVersion}
Compression=lzma
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional icons:"

[Files]
Source: "{#MyAppSource}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent

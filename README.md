# Frida Server (Android)

This is a Magisk Module that installs [Frida server](https://www.frida.re), a popular reverse-engineering tool.

## Features

* Detects connected device to download correct architecture
* Creates Magisk Module that automatically starts frida_server after device boot


## Installation

```
pip install -r requirements.txt
python build_module.py
```

Afterwards, use adb push to copy the .zip file over to your device and install through the Magisk Manager app.
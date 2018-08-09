#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: TheCjw<thecjw@live.com>
# Created on 2016.10.17

__author__ = "TheCjw & TheDauntless, content from Frida"

import json
import lzma
import os
import requests
import shutil
import zipfile
import subprocess


def download_file(download_url, path):
    if os.path.exists(path):
        print("File {0} exists, using cache.".format(os.path.basename(path)))
        return

    print("Downloading", download_url)
    response = requests.get(download_url, stream=True)
    with open(path, "wb") as out:
        shutil.copyfileobj(response.raw, out)
    del response
    print("Done.")


def extract_file(archive, file_name):
    with lzma.open(archive) as f:
        file_content = f.read()
        path = os.path.dirname(file_name)
        if not os.path.exists(path):
            os.makedirs(path)
        with open(file_name, "wb") as out:
            out.write(file_content)


def get_devices():
    # Code based on https://github.com/AndroidTamer/frida-push/blob/master/frida_push/command.py
    cmd = 'adb devices -l | tail -n+2'
    output = subprocess.check_output(cmd, shell=True).strip().decode("utf-8").replace("\r", "").split("\n")

    devices = []
    for device in output:
        info = device.strip().split()
        deviceSerial = info[0]
        deviceType = info[1]
        deviceInfo = {x.split(":")[0]:x.split(":")[1] for x in info[2:]}

        devices.append({"serial": deviceSerial, "type": deviceType, "info": deviceInfo})
    return devices

def get_device_architecture(device_id):
    # Code based on https://github.com/AndroidTamer/frida-push/blob/master/frida_push/command.py
    adbcmd = "adb -s {} shell getprop ro.product.cpu.abi".format(device_id)

    output = subprocess.check_output(adbcmd, shell=True).lower().strip().decode("utf-8")
    if output == "arm64-v8a":
        return "arm64"
    elif output in ["armeabi", "armeabi-v7a"]:
        return "arm"
    return output

def get_device_info():

    arch = ""

    devices = get_devices()

    if len(devices) == 0:
        print("No attached devices found.")
        return ""

    device = devices[0]
    print("Using device: {}".format(device["info"]["model"]))

    device["info"]["arch"] = get_device_architecture(device["serial"])

    return device



def main():
    base_path = os.path.abspath(os.path.dirname(__file__))

    frida_release_url = "https://api.github.com/repos/frida/frida/releases/latest"

    response = requests.get(frida_release_url).text
    config = json.loads(response)

    version = config["tag_name"]
    release_notes = config["body"]
    print("Latest Frida version:", version)
    print("Release notes:", release_notes)

    module_prop = """id=FridaServer
name=Frida Server
version={version}
versionCode={version_code}
author={author}
description={notes}
support=http://www.frida.re/
donate=
cacheModule=false
minMagisk=1500
    """.format(version=version,
               version_code=version.replace(".", ""),
               notes=release_notes,
               author=__author__)
    with open("module.prop", "w") as f:
        f.write(module_prop)

    device = get_device_info()

    frida_server = "frida-server-{}-android-{}.xz".format(version, device["info"]["arch"])


    download_url = "https://github.com/frida/frida/releases/download/{}/".format(version)

    cache_path = os.path.join(base_path, "cache")
    frida_server_path = os.path.join(cache_path, frida_server)


    download_file(download_url + frida_server, frida_server_path)


    # arm frida.
    extract_file(frida_server_path, os.path.join(base_path,
                                                    "system/etc/frida/frida_server"))


    file_list = ["common/service.sh",
                 "common/post-fs-data.sh",
                 "common/post-fs.sh",
                 "common/file_contexts_image",
                 "META-INF/com/google/android/update-binary",
                 "META-INF/com/google/android/updater-script",
                 "system/etc/frida/frida_server",
                 "config.sh",
                 "changelog.txt",
                 "module.prop"]

    print("Building Magisk module.")
    targetZip = os.path.join(cache_path,
                                      "Magisk-Frida-Server-{0}.zip".format(version))
    with zipfile.ZipFile(targetZip, "w") as zf:
        for file_name in file_list:
            path = os.path.join(base_path, file_name)
            if not os.path.exists(path):
                print("{0} not found, skipping.".format(path))
                continue
            zf.write(path, arcname=file_name)

    print("Done. Install using adb push {} /sdcard/Download".format(targetZip))


if __name__ == "__main__":
    main()

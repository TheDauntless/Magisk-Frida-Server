#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: TheCjw<thecjw@live.com>
# Created on 2016.10.17

__author__ = "TheCjw"

import json
import lzma
import os
import requests
import shutil
import zipfile


def download_file(download_url, path):
    if os.path.exists(path):
        print("{0} is exists, skip...".format(path))
        return

    print("Downloading", download_url)
    response = requests.get(download_url, stream=True)
    with open(path, "wb") as out:
        shutil.copyfileobj(response.raw, out)
    del response
    print("done.")


def extract_file(archive, file_name):
    with lzma.open(archive) as f:
        file_content = f.read()
        path = os.path.dirname(file_name)
        if not os.path.exists(path):
            os.makedirs(path)
        with open(file_name, "wb") as out:
            out.write(file_content)


def main():
    base_path = os.path.dirname(__file__)

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
author=Frida
description={notes}
support=http://www.frida.re/
donate=
cacheModule=false
    """.format(version=version,
               version_code=version.replace(".", ""),
               notes=release_notes)
    with open("module.prop", "w") as f:
        f.write(os.path.join(base_path, module_prop))

    frida_server_32 = "frida-server-{0}-android-arm.xz".format(version)
    frida_server_64 = "frida-server-{0}-android-arm64.xz".format(version)

    download_url = "https://github.com/frida/frida/releases/download/{0}/".format(version)

    cache_path = os.path.join(base_path, "cache")
    frida_server_32_path = os.path.join(cache_path, frida_server_32)
    frida_server_64_path = os.path.join(cache_path, frida_server_64)

    download_file(download_url + frida_server_32, frida_server_32_path)
    download_file(download_url + frida_server_64, frida_server_64_path)

    # arm frida.
    extract_file(frida_server_32_path, os.path.join(base_path,
                                                    "system/xbin/frida_server_32"))

    extract_file(frida_server_64_path, os.path.join(base_path,
                                                    "system/xbin/frida_server_64"))

    file_list = ["common/service.sh",
                 "common/post-fs-data.sh",
                 "common/post-fs.sh",
                 "common/file_contexts_image",
                 "META-INF/com/google/android/update-binary",
                 "META-INF/com/google/android/updater-script",
                 "system/xbin/frida_server_32",
                 "system/xbin/frida_server_64",
                 "system/xbin/debug_server",
                 "system/xbin/debug_server64",
                 "config.sh",
                 "changelog.txt",
                 "module.prop"]

    print("Building Magisk module.")
    with zipfile.ZipFile(os.path.join(cache_path,
                                      "Magisk-Frida-Server-{0}.zip".format(version)), "w") as zf:
        for file_name in file_list:
            path = os.path.join(base_path, file_name)
            if not os.path.exists(path):
                print("{0} is not exists, skip...".format(path))
                continue
            zf.write(path, arcname=file_name)

    print("Done.")


if __name__ == "__main__":
    main()

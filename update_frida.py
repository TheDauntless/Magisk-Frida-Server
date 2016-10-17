#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: TheCjw<thecjw@live.com>
# Created on 2016.10.17

__author__ = "TheCjw"

import json
import lzma
import os
import requests
import shutil


def download_file(download_url, file_name):
    response = requests.get(download_url, stream=True)
    with open(file_name, "wb") as out:
        shutil.copyfileobj(response.raw, out)
    del response


def extract_file(archive, file_name):
    with lzma.open(archive) as f:
        file_content = f.read()
        path = os.path.dirname(file_name)
        if not os.path.exists(path):
            os.makedirs(path)
        with open(file_name, "wb") as out:
            out.write(file_content)


def main():
    frida_release_url = "https://api.github.com/repos/frida/frida/releases/latest"

    response = requests.get(frida_release_url).text
    config = json.loads(response)

    version = config["tag_name"]
    print("Latest Frida version:", version)

    frida_server_32 = "frida-server-{0}-android-arm.xz".format(version)
    frida_server_64 = "frida-server-{0}-android-arm64.xz".format(version)

    download_url = "https://github.com/frida/frida/releases/download/{0}/".format(version)

    # download_file(download_url + frida_server_32, frida_server_32)
    # download_file(download_url + frida_server_64, frida_server_64)

    # arm frida.
    extract_file(frida_server_32, os.path.join(os.path.dirname(__file__),
                                               "system/xbin/frida_server_32"))

    extract_file(frida_server_64, os.path.join(os.path.dirname(__file__),
                                               "system/xbin/frida_server_64"))

    # Update config

    # Build zip archive


if __name__ == "__main__":
    main()

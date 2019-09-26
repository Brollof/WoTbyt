import os
import sys
import wget
import winreg
import argparse
import tempfile
import subprocess
from zipfile import ZipFile


XVM_URL = "https://nightly.modxvm.com/download/wot-1.6.0/latest_xvm.zip"
SETTINGS_FILE = "settings.cfg"
DL_DST = tempfile.gettempdir()
THIS_SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))


def exit(msg, ex):
    print(msg)
    print(ex)
    sys.exit(1)


def download_file(url, dst):
    print(f"Downloading {url} to {dst} ...")
    try:
        file_path = wget.download(url, dst)
    except Exception as ex:
        exit("Failed to download!", ex)
    else:
        print("Downloading OK!")
        return file_path


def get_wot_install_path():
    settings_path = os.path.join(THIS_SCRIPT_DIR, SETTINGS_FILE)

    try:
        with open(settings_path, "r") as file:
            print("Settings file found, reading WoT path...")
            data = file.readlines()
            return data[0]
    except FileNotFoundError:
        print("Settings file not found. Searching WoT path in Registry...")
    except Exception as ex:
        exit("Settings file read failed!", ex)

    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Uninstall\WOT.EU.PRODUCTION")
        wot_path =  winreg.QueryValueEx(key, "InstallLocation")[0]

        with open(settings_path, "w") as file:
            file.write(wot_path)

        print(f"WoT path found in Registry, saving to: {settings_path}")
        return wot_path
    except Exception as ex:
        exit("Registry searching failed!", ex)


def extract_xvm(src, dst):
    try:
        print(f"Extracting xvm to: {dst}...")
        with ZipFile(src, "r") as archive:
            archive.extractall(dst)
    except Exception as ex:
        exit("Extracting failed!", ex)


def cleanup(zip_path):
    try:
        os.remove(zip_path)
    except Exception as ex:
        exit("Cleanup failed!", ex)

    print("Cleanup OK!")


def run_post_script_actions(actions):
    if actions:
        print("Running post script actions...")
        for action in actions:
            print(f"action: {action}")
            subprocess.run(action, shell=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--post_scripts", nargs="+", help="Post script actions")
    args = parser.parse_args()

    # Download xvm package
    xvm_zip_path = download_file(XVM_URL, DL_DST)

    # Get WoT installation directory
    wot_path = get_wot_install_path()

    # Apply xvm
    extract_xvm(xvm_zip_path, wot_path)

    # Cleanup
    cleanup(xvm_zip_path)

    print("XVM has been successfully installed!")

    run_post_script_actions(args.post_scripts)

if __name__ == "__main__":
    main()
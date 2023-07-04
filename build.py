import os
import subprocess

if __name__ == "__main__":
    print("creating temporary build environment")
    os.mkdir("build")
    os.system("cd build")
    os.system("python3.11 -m venv venv")
    os.system("cd ..")
    os.system("./build/venv/bin/activate")
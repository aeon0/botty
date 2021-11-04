import os
import shutil
import argparse
import sys
from src.version import __version__

# Note: Before building you must add cv2 to python path:
# e.g. C:\Users\USER\miniconda3\envs\botty\lib\site-packages\cv2

# clean up
def clean_up():
    if os.path.exists("run.dist"):
        shutil.rmtree("run.dist")
    if os.path.exists("run.build"):
        shutil.rmtree("run.build")
    if os.path.exists("run.onefile"):
        shutil.rmtree("run.onefile")
    if os.path.exists("run.onefile-build"):
        shutil.rmtree("run.onefile-build")
    if os.path.exists("run.exe"):
        os.remove("run.exe")

clean_up()
installer_cmd = f"python -m nuitka --mingw --standalone --onefile --plugin-enable=numpy src/run.py" 
os.system(installer_cmd)

botty_dir = f"botty_v{__version__}"
if os.path.exists(botty_dir):
    os.remove(botty_dir)
os.system(f"mkdir {botty_dir}")
shutil.copy("run.exe", f"{botty_dir}/")
shutil.copy("ui.ini", f"{botty_dir}/")
shutil.copy("params.ini", f"{botty_dir}/")
shutil.copy("README.md", f"{botty_dir}/")
shutil.copytree("assets", f"{botty_dir}/assets")
clean_up()

import os
import shutil
from pathlib import Path
import sys
from src.version import __version__

# Note: Before building you must add cv2 to python path:
# e.g. C:\Users\USER\miniconda3\envs\botty\lib\site-packages\cv2

# change version
new_dev_version_code = None
if len(sys.argv) == 2:
    print(f"Releasing new version: {sys.argv[1]}")
    version_code = ""
    with open('src/version.py', 'r') as f:
        version_code = f.read()
    version_code = version_code.split("=")
    new_version_code = f"{version_code[0]}= '{sys.argv[1]}'"
    new_dev_version_code = f"{version_code[0]}= '{sys.argv[1]}-dev'"
    with open('src/version.py', 'w') as f:
        f.write(new_version_code)

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

botty_dir = f"botty_v{__version__}"
if os.path.exists(botty_dir):
    for path in Path(botty_dir).glob("**/*"):
        if path.is_file():
            os.remove(path)
        elif path.is_dir():
            shutil.rmtree(path)
    shutil.rmtree(botty_dir)

installer_cmd = f"python -m nuitka --mingw64 --standalone --onefile --plugin-enable=numpy src/run.py" 
os.system(installer_cmd)

os.system(f"mkdir {botty_dir}")

with open(f"{botty_dir}/custom.ini", "w") as f: 
    f.write("; Add parameters you want to overwrite from param.ini here")
shutil.copy("run.exe", f"{botty_dir}/")
shutil.copy("game.ini", f"{botty_dir}/")
shutil.copy("params.ini", f"{botty_dir}/")
shutil.copy("README.md", f"{botty_dir}/")
shutil.copytree("assets", f"{botty_dir}/assets")
clean_up()

if new_dev_version_code is not None:
    with open('src/version.py', 'w') as f:
        f.write(new_dev_version_code)

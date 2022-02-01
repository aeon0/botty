import os
import shutil
from pathlib import Path
from src.version import __version__
import argparse
import getpass
import random
from cryptography.fernet import Fernet
import string


parser = argparse.ArgumentParser(description="Build Botty")
parser.add_argument(
    "-v" , "--version",
    type=str,
    help="New release version e.g. 0.4.2",
    default=""
)
parser.add_argument(
    "-c", "--conda_path",
    type=str,
    help="Path to local conda e.g. C:\\Users\\USER\\miniconda3",
    default=f"C:\\Users\\{getpass.getuser()}\\miniconda3")
parser.add_argument(
    "-r", "--random_name",
    action='store_true',
    help="Will generate a random name for the botty exe")
parser.add_argument(
    "-k", "--use_key",
    action='store_true',
    help="Will build with encryption key")
args = parser.parse_args()


# clean up
def clean_up():
    # pyinstaller
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("main.spec"):
        os.remove("main.spec")
    if os.path.exists("health_manager.spec"):
        os.remove("health_manager.spec")
    if os.path.exists("shopper.spec"):
        os.remove("shopper.spec")

if __name__ == "__main__":
    new_version_code = None
    if args.version != "":
        print(f"Releasing new version: {args.version}")
        os.system(f"git checkout -b new-release-v{args.version}")
        botty_dir = f"botty_v{args.version}"
        version_code = ""
        with open('src/version.py', 'r') as f:
            version_code = f.read()
        version_code = version_code.split("=")
        new_version_code = f"{version_code[0]}= '{args.version}'"
        with open('src/version.py', 'w') as f:
            f.write(new_version_code)
    else:
        botty_dir = f"botty_v{__version__}"
        print(f"Building version: {__version__}")

    clean_up()

    if os.path.exists(botty_dir):
        for path in Path(botty_dir).glob("**/*"):
            if path.is_file():
                os.remove(path)
            elif path.is_dir():
                shutil.rmtree(path)
        shutil.rmtree(botty_dir)

    for exe in ["main.py", "shopper.py"]:
        key_cmd = " "
        if args.use_key:
            key = Fernet.generate_key().decode("utf-8")
            key_cmd = " --key " + key
        installer_cmd = f"pyinstaller --onefile --distpath {botty_dir}{key_cmd} --exclude-module graphviz --paths .\\src --paths {args.conda_path}\\envs\\botty\\lib\\site-packages src\\{exe}"
        os.system(installer_cmd)

    os.system(f"cd {botty_dir} && mkdir config && cd ..")

    with open(f"{botty_dir}/config/custom.ini", "w") as f:
        f.write("; Add parameters you want to overwrite from param.ini here")
    shutil.copy("config/game.ini", f"{botty_dir}/config/")
    shutil.copy("config/params.ini", f"{botty_dir}/config/")
    shutil.copy("config/pickit.ini", f"{botty_dir}/config/")
    shutil.copy("config/shop.ini", f"{botty_dir}/config/")
    shutil.copy("README.md", f"{botty_dir}/")
    shutil.copytree("assets", f"{botty_dir}/assets")
    clean_up()

    if args.random_name:
        print("Generate random names")
        new_name = ''.join(random.choices(string.ascii_letters, k=random.randint(6, 14)))
        os.rename(f'{botty_dir}/main.exe', f'{botty_dir}/{new_name}.exe')

    if new_version_code is not None:
        os.system(f'git add .')
        os.system(f'git commit -m "Bump version to v{args.version}"')

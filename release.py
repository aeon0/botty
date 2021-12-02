import os
import shutil
from pathlib import Path
from src.version import __version__
import argparse
import getpass


parser = argparse.ArgumentParser(description="Release a new Botty Version")
parser.add_argument(
    "version",
    type=str,
    help="New release version e.g. 0.4.2"
)
parser.add_argument(
    "-c", "--conda_path",
    type=str,
    help="Path to local conda e.g. C:\\Users\\USER\\miniconda3",
    default=f"C:\\Users\\{getpass.getuser()}\\miniconda3")
args = parser.parse_args()


# clean up
def clean_up():
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("run.spec"):
        os.remove("run.spec")


if __name__ == "__main__":
    # change version
    new_dev_version_code = None
    print(f"Releasing new version: {args.version}")
    os.system(f"git checkout -b new-release-v{args.version}")
    botty_dir = f"botty_v{args.version}"
    version_code = ""
    with open('src/version.py', 'r') as f:
        version_code = f.read()
    version_code = version_code.split("=")
    new_version_code = f"{version_code[0]}= '{args.version}'"
    new_dev_version_code = f"{version_code[0]}= '{args.version}-dev'"
    with open('src/version.py', 'w') as f:
        f.write(new_version_code)

    clean_up()

    if os.path.exists(botty_dir):
        for path in Path(botty_dir).glob("**/*"):
            if path.is_file():
                os.remove(path)
            elif path.is_dir():
                shutil.rmtree(path)
        shutil.rmtree(botty_dir)

    installer_cmd = f"pyinstaller --onefile --distpath {botty_dir} --exclude-module graphviz --paths .\\src --paths {args.conda_path}\\envs\\botty\\lib\\site-packages src\\run.py"
    os.system(installer_cmd)
    os.system(f"mkdir {botty_dir}")

    with open(f"{botty_dir}/custom.ini", "w") as f: 
        f.write("; Add parameters you want to overwrite from param.ini here")
    shutil.copy("game.ini", f"{botty_dir}/")
    shutil.copy("params.ini", f"{botty_dir}/")
    shutil.copy("README.md", f"{botty_dir}/")
    shutil.copytree("assets", f"{botty_dir}/assets")
    clean_up()

    if new_dev_version_code is not None:
        with open('src/version.py', 'w') as f:
            f.write(new_dev_version_code)
        os.system(f'git add .')
        os.system(f'git commit -m "Bump version to v{args.version}"')

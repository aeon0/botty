import os

# automatically run everything inside this folder.

# get the folder we're currently in
folder = os.path.dirname(os.path.abspath(__file__)).split("\\")[-1]

# get all the python files in this folder and subfolders of this folder.
python_files = [f for f in os.listdir(os.path.dirname(os.path.abspath(__file__))) if f.endswith(".py")]
print(python_files)

for module in os.listdir(os.path.dirname(__file__)):
    if module == '__init__.py' or module == "utils.py" or module[-3:] != '.py':
        continue
    __import__(f"{folder}.{module[:-3]}", locals(), globals())
del module

# Dev Docu

## Dependencies
- Install miniconda (https://docs.conda.io/en/latest/miniconda.html)
- Install git (https://gitforwindows.org/)

## Getting started
```
git clone https://github.com/aeon0/botty.git
cd botty
conda env create environment.yml
python src/run.py
```

## Building from source
If you want to build a .exe from source you will have to first add the cv2 path to your PYTHONPATH:</br>
Edit System environment variables -> Enfironment Vriables... -> PYTHONPATH -> C:\Users\$USER\miniconda3\envs\botty\lib\site-packages\cv2
```python
# building .exe and bundeling all needed resource into one folder
python release.py
```
For changelog run: `git log <PREVIOUS_TAG>..HEAD --oneline --decorate`

## Folder Structure
**/**</br>
In the root is docu, param files and development specific stuff such as .gitignore</br>

**assets**</br>
Contains all data for the project that is not source code</br>
**assets/docs**</br>
Images you can see in the .md files and logos</br>
**assets/items**</br>
Screenshot of item names that should be picked up. The filename must then be added to the param.ini</br>
**assets/npc**</br>
Templates of npcs in different poses</br>
**assets/templates**</br>
Templates for different UIs and key points. Also contains folders of "pathes" that were generated with the utils/node_creator.py</br>

**src**</br>
All python source files go here</br>
**src/char**</br>
Want to implement a new char or build. Check this folder out. You will have to inherit from IChar and go from there</br>
**src/char**</br>
Utilities functions and scripts e.g. for easily creating templates to traverse nodes and automatically generate code for it</br>

## State Diagram
The core logic of the bot is determined by a state machine with these states and transations. The bot.py which contains all of the transitions should have little implementation code which should be hidden as much as possible in the "manager" classes.
<img src="assets/docs/state_diagram.png" width="550"/>

## Coordinate System
There are different coordinate systems used and I tried my best to add these to the variable names.</br>
**Monitor**: It will have the origin at the top left of the first monitor</br>
**Screen**: Same as monitor for single monitor setups, otherwise origin at top left of the screen </br>
**Absolute**: Has its origin at the center of the screen, thus at the footpoint of your char </br>
**Relative**: Relative coordinates as the name suggest are relative to something. It is mostly used to express relative coordinates in relation to a tempalte that is found </br>
<img src="assets/docs/coordinate_systems.png" width="550"/>

import sys
from pathlib import Path
current_folder=Path(__file__).parent.absolute()
sys.path.append(str(current_folder))
print('append imgui',str(current_folder))
# print(str(current_folder.parent))
# print('G:\\work\\001Blender\\blender_init\\addons\\color_picker\\extern')
# import sys
# sys.path.append('G:\\work\\001Blender\\blender_init\\addons\\color_picker\\extern')

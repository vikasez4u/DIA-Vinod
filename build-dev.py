import os
import subprocess
import time
import shutil

CURRENT_DIRECTORY = os.getcwd()
directories = os.listdir(CURRENT_DIRECTORY)
NON_ANGULAR_DIRS = ['resources','static', 'templates', 'weights', 'venv', 'env', '__pycache__','uploads']
ANGULAR_PROJECT_PATH = ""
DIST_PATH = ""

for directory in directories:
    if "." not in directory and directory not in NON_ANGULAR_DIRS:
        ANGULAR_PROJECT_PATH = os.path.join(CURRENT_DIRECTORY, directory)
        DIST_PATH = os.path.join(ANGULAR_PROJECT_PATH, 'dist', directory)

FLASK_STATIC_PATH = os.path.join(CURRENT_DIRECTORY, 'static')
FLASK_TEMPLATES_PATH = os.path.join(CURRENT_DIRECTORY, 'templates')

dir_exists = True

if dir_exists:
    try:
        subprocess.call(('cd ' + ANGULAR_PROJECT_PATH + ' && ng build --base-href /static/ --output-hashing=all &'), shell=True)
        for f in os.listdir(FLASK_STATIC_PATH):
          os.remove(os.path.join(FLASK_STATIC_PATH, f))
        print('Begin Transferring files')
        files = os.listdir(DIST_PATH)
        static_files = ""
        html_files = ""
        for file in files:
            if '.js' in file or '.js.map' in file or '.ico' in file or '.css' in file or '.jpg' in file or '.woff' in file or '.woff2' in file:
                static_files = file
                print(DIST_PATH + '\\' + static_files, FLASK_STATIC_PATH + '\\' + static_files)
                (shutil.move(DIST_PATH + '\\' + static_files, FLASK_STATIC_PATH + '\\' + static_files))
                if os.path.exists(DIST_PATH + '\\' + static_files):
                    os.remove(DIST_PATH + '\\' + static_files)
            if '.html' in file:
                html_files = file
                if os.path.exists(FLASK_TEMPLATES_PATH + '\\' + html_files):
                  os.remove(FLASK_TEMPLATES_PATH + '\\' + html_files)
                print(DIST_PATH + '\\' + html_files, FLASK_TEMPLATES_PATH + '\\' + html_files)
                (shutil.move(DIST_PATH + '\\' + html_files, FLASK_TEMPLATES_PATH + '\\' + html_files))
                if os.path.exists(DIST_PATH + '\\' + html_files):
                  os.remove(DIST_PATH + '\\' + html_files)
    except Exception as e:
        dir_exists = False
        print(e)

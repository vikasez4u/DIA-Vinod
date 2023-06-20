import os
import subprocess
import time
import shutil

CURRENT_DIRECTORY = os.getcwd()
directories = os.listdir(CURRENT_DIRECTORY)
NON_ANGULAR_DIRS = ['static', 'templates', 'weights', 'venv', 'env']

for directory in directories:
    if "." not in directory and directory not in NON_ANGULAR_DIRS:
        ANGULAR_PROJECT_PATH = os.path.join(CURRENT_DIRECTORY, directory)
        DIST_PATH = os.path.join(ANGULAR_PROJECT_PATH, 'dist', directory)

FLASK_STATIC_PATH = os.path.join(CURRENT_DIRECTORY, 'static')
FLASK_TEMPLATES_PATH = os.path.join(CURRENT_DIRECTORY, 'templates')

subprocess.call(('cd ' + ANGULAR_PROJECT_PATH + ' && ng build --watch --base-href /static/ &'), shell=True)

dir_exists = True

while dir_exists:
    try:
        print('Begin Transfering files')
        files = os.listdir(DIST_PATH)
        static_files = ""
        html_files = ""
        for file in files:
            if '.js' in file or '.js.map' in file or '.ico' in file:
                static_files += (file + ' ')
            if '.html' in file:
                html_files += (file + ' ')
        print(html_files)
        if len(static_files) > 0:
            print('cd ' + DIST_PATH + ' &&' + ' mv ' + static_files + FLASK_STATIC_PATH)
            subprocess.call(('cd ' + DIST_PATH + ' &&' + ' mv ' + static_files + FLASK_STATIC_PATH), shell=True)
        if len(html_files) > 0:
            print('cd ' + DIST_PATH + ' &&' + ' mv ' + html_files + FLASK_TEMPLATES_PATH)
            print(DIST_PATH + '\\' + html_files, FLASK_TEMPLATES_PATH + '\\' + html_files)
            subprocess.call((shutil.move(DIST_PATH + '\\' + html_files, FLASK_TEMPLATES_PATH + '\\' + html_files)))
    except Exception as e:
        dir_exists = False
        print(e)
    time.sleep(1.0)

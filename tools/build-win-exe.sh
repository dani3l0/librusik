#!/bin/sh
# ./tools/build-win-exe.sh

set -xe

# pytonga pod wine instaluje się tak samo jak pytonga na windowsie
# t.j. instalka ze strony
WINE_PYTHON="$HOME/.wine/drive_c/users/`whoami`/AppData/Local/Programs/Python/Python*/python.exe"
WINE_PYINSTALLER="$HOME/.wine/drive_c/users/`whoami`/AppData/Local/Programs/Python/Python*/Scripts/pyinstaller.exe"

collect_data=`cut -f1 -d= < ./requirements.txt | xargs printf '--collect-data %s '`
collect_files=`find ./lib ./static ./html -type f -exec sh -c 'printf -- "--add-data %s;%s " {} $(dirname {} | sed s!\./!!)' ';'`
# ↑ shellcheck płacze teehee :3333

#$WINE_PYTHON -m pip install pyinstaller
#$WINE_PYTHON -m pip install -r ./requirements.txt

$WINE_PYINSTALLER -F -n librusik-serwer \
  $collect_files \
  $collect_data \
  ./librusik.py

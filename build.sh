poetry run python -m nuitka --mingw64 --onefile --include-data-files=ignorelist=ignorelist doublons.py
rm -r *.build *.dist *.onefile-build
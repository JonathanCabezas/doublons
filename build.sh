poetry run python -m nuitka --mingw64 --onefile \
       --include-data-files=doublons/whitelist=whitelist \
       --include-data-files=doublons/blacklist=blacklist \
       doublons/doublons.py
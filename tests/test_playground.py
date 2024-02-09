import os
import shutil
import doublons

from pathlib import Path


def test_playground():
    # Setup
    shutil.rmtree("playground_copy", ignore_errors=True)
    shutil.copytree("playground", "playground_copy")
    # Change current working directory to playground_copy
    os.chdir("playground_copy")
    print(f"Current working directory: {os.getcwd()}")

    # Test
    doublons.delete_duplicates(confirm=False)
    playground_after_delete_duplicates = [str(f) for f in Path(".").glob("**/*")]
    print(playground_after_delete_duplicates)
    assert playground_after_delete_duplicates == [
        ".picasa.ini",
        "b.txt",
        "c.txt",
        "d.txt",
        "f (1).txt",
        "f.txt",
        "g.txt",
        "test",
        "trash",
        "test\\.picasa.ini",
        "test\\a.txt",
        "test\\IMG_3.txt",
        "test\\test",
        "test\\test\\e.txt",
        "trash\\20200716213010.txt",
        "trash\\e (2).txt",
        "trash\\e (4).txt",
        "trash\\e - Copie.txt",
        "trash\\g (1).txt",
        "trash\\test",
        "trash\\test\\c (2).txt",
        "trash\\test\\g (1).txt",
        "trash\\test\\test",
        "trash\\test\\test\\b (1).txt",
    ]

    # Teardown
    os.chdir("..")
    shutil.rmtree("playground_copy")

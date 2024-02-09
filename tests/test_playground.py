import os
import shutil
import doublons

from pathlib import Path


def test_playground():
    # Setup
    shutil.rmtree("trash", ignore_errors=True)
    shutil.rmtree("playground_copy", ignore_errors=True)
    shutil.copytree("playground", "playground_copy")

    # Test
    doublons.delete_duplicates(root=Path("playground_copy"), confirm=False)
    playground_after_delete_duplicates = [
        str(f) for f in Path("playground_copy").glob("**/*")
    ]
    print(playground_after_delete_duplicates)
    assert playground_after_delete_duplicates == [
        "playground_copy\\.picasa.ini",
        "playground_copy\\b.txt",
        "playground_copy\\c.txt",
        "playground_copy\\d.txt",
        "playground_copy\\f (1).txt",
        "playground_copy\\f.txt",
        "playground_copy\\g.txt",
        "playground_copy\\test",
        "playground_copy\\test\\.picasa.ini",
        "playground_copy\\test\\a.txt",
        "playground_copy\\test\\IMG_3.txt",
        "playground_copy\\test\\test",
        "playground_copy\\test\\test\\e.txt",
    ]

    trash_after_delete_duplicates = [str(f) for f in Path("trash").glob("**/*")]
    print(trash_after_delete_duplicates)
    assert trash_after_delete_duplicates == [
        "trash\\playground_copy",
        "trash\\playground_copy\\20200716213010.txt",
        "trash\\playground_copy\\e (2).txt",
        "trash\\playground_copy\\e (4).txt",
        "trash\\playground_copy\\e - Copie.txt",
        "trash\\playground_copy\\g (1).txt",
        "trash\\playground_copy\\test",
        "trash\\playground_copy\\test\\c (2).txt",
        "trash\\playground_copy\\test\\g (1).txt",
        "trash\\playground_copy\\test\\test",
        "trash\\playground_copy\\test\\test\\b (1).txt",
    ]

    # Teardown
    shutil.rmtree("trash")
    shutil.rmtree("playground_copy")

import os
import shutil
import doublons


def test_playground(self):
    # Setup
    shutil.rmtree("playground_copy")
    shutil.copytree("playground", "playground_copy")
    # Change current working directory to playground_copy
    os.chdir("playground_copy")

    # Test
    doublons.delete_duplicates(confirm=False)
    print(Path(".").glob("**/*"))

    # Teardown
    # assert()

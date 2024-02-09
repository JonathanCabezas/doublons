In playground, here are what the files test:

- `a.txt` is a **normal file**
- `b (1).txt` is a duplicate of `b (1).txt` **(duplicate with same name)**
- `c.txt` is present twice with different names **(duplicate with different name)**
- `d.txt` is alone with a name to shorten **(no duplicate but duplicate-like name)**
- `e.txt` is present a lot of times **(multiple duplicates)**
- `f.txt` is present twice with different names and different content (`f.txt` and `f (1).txt` are different files)
  which means `f (1).txt` can't be renamed `f.txt` **(no duplicate but duplicate-like name but can't shorten)**
- `g (1).txt` is present twice as duplicates at 2 locations, which means you can't move it to the root of the trash folder.

  Because of this case I think it's better to keep the full folder hierarchy when moving to the trash. **(2 duplicates with same name)**

- `.picasa.ini` has duplicates but this file should be ignored since it's a configuration for a software. **(duplicates in ignorelist)**
- The `.git` and `.vscode` folders which might be present should of course be completely ignored aswell.

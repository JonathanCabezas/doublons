In playground, here are what the files test:

- `a.txt` is a normal file
- `b (1).txt` is present twice with the same name
- `c.txt` is present twice with different names
- `d.txt` is alone with a name to shorten
- `e.txt` is present a lot of times
- `f.txt` is present twice with different names and different content (`f.txt` and `f (1).txt` are different files)
  which means `f (1).txt` can't be renamed `f.txt`
- `g (1).txt` is present twice as duplicates at 2 locations, which means you can't move it to the root of the trash folder.

  Because of this case I think it's better to keep the full folder hierarchy when moving to the trash.

- `.picasa.ini` has duplicates but this file should be ignored since it's a configuration for a software.
- The `.git` and `.vscode` folders which might be present should of course be completely ignored aswell.

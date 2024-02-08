# Duplicate Finder

This program finds duplicates files in a directory and removes them.
For example, if you have the following files:

- test.txt
- test - Copie.txt
- test (2).txt

The program will remove the last two files if they have the same content as the first one.

It will also change the name of the files to remove the suffixes, for example:

- test - Copie.txt -> test.txt
- test (2).txt -> test.txt

Even if the files don't have duplicates.

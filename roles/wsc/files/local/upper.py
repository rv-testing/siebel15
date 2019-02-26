#!/usr/bin/python
import os, sys
with open(sys.argv[1], "r+b") as file:
    content = file.read()
    file.seek(0)
    file.write(content.upper())

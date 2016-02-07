#!/usr/bin/env python

from subprocess import call

call("cactus RM2.in | tee cactus.log", shell=True)

#!/usr/bin/env python

from subprocess import call

call("cactus RM2.in | tee log.cactus", shell=True)

# Integration of Fast Forward with the Unified Planning Library

This project contains a slightly modified version of the FF v2.3 planner (from https://fai.cs.uni-saarland.de/hoffmann/ff/FF-v2.3.tgz).
The modifications involved:
(a) Defining some variables as extern to get the planner to compile, and 
(b) Adding a parameter for writing the resulting plan to a given plan file name

It also includes a thin Python wrapper for integrating this into the Unified Planning Framework (https://github.com/aiplan4eu/unified-planning)

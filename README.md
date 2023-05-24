# CS 131 Spring 2023: Brewin Interpreter Version 2

This is the repository for the second stage of the quarter-long project for the CS 131 course at UCLA. The project specs are as follows:

[Project 2 Spec](https://docs.google.com/document/d/1simlDMO0TK-YNDPYjkuU1C3fcaBpbIVYRaKD1pdqJj8/edit?usp=sharing)

The top-level interpreterv2.py file exports the Interpreter class that implements the features detailed in the project spec, with support from the additional `.py` modules included in the repository.

# Known Issues

For classes that are derived from parent classes, the case in which a function in the parent class calls a method in the object with the 'me' keyword is not handled correctly (i.e. does not call the most derived version of a method)

## Licensing and Attribution

This is an unlicensed repository; even though the source code is public, it is **not** governed by an open-source license.

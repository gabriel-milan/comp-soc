# -*- coding: utf-8 -*-
import subprocess


def main():
    """
    Lint all python files in the project.
    """
    command = "pdoc3 --html --html-dir docs carona_parque"
    subprocess.run(command, shell=True)

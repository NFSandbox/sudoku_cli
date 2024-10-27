import sys
import subprocess

from loguru import logger


@logger.catch()
def main():
    subprocess.run("pyinstaller main.py", shell=True)
    subprocess.run(r"robocopy ./ ./dist/main .sudokurc", shell=True)
    subprocess.run(r"robocopy ./docs ./dist/main/docs /E /MIR", shell=True)


if __name__ == "__main__":
    main()

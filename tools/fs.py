import os

def make_parent_dir(filePath, mode = 0o777):
    head, _ = os.path.split(filePath)
    makedir(head, mode)

def makedir(dirpath, mode = 0o777):

    if not os.path.isdir(dirpath):
        head, _ = os.path.split(dirpath)
        if os.path.dirname(dirpath) == dirpath:
            # can't go to parent
            return

        if head != "":
            makedir(head, mode)

        os.makedirs( dirpath, mode = mode, exist_ok=True )
#!/usr/bin/env python
"""
Assorted functions used by multiple files.
"""
import os
import subprocess

def ensure_folder_exists(dirpath: str, folder_name: str) -> tuple:
    """ Create requested folder in requested path, if it's not already there.

    Args:
        - dirpath - path to parent directory

    Returns:
        - tuple of (return_code, full path to new folder).
          Return_code = 0 means success.
    """
    folder_path = os.path.join(dirpath, folder_name)
    return_tuple = (0, folder_path)

    if not os.path.exists(folder_path):
        try:
            os.makedirs(folder_path)
        except Exception as e:
            print(e)
            print(e.args)
            print(f"Couldn't make {folder_name=} in {dirpath}.  Error:\n {e}")
            try:
                print("Try using subprocess")
                subprocess.call(['sudo', 'mkdir', '-p', folder_path])
            except:
                print(e)
                print(e.args)
                print("Subprocess didn't work either! Huh...")
                # @@@ ECLC - consider throwing exception here, rather than
                # letting code keep trying to run.  Calling code should
                # decide if it cares
                return (1, folder_path)
    print(f"{folder_name=} now exists in {dirpath}? {return_tuple[0] == 0}")
    return(return_tuple)

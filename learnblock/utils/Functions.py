# -*- coding: utf-8 -*-
import os, sys, json
from learnblock.blocks import pathImgBlocks
from importlib import import_module
from learnblock import PATHFUNCTIONSSRC, PATHFUNCTIONSCONF

__localFunctionsPath = os.path.join(os.getenv('HOME'), ".learnblock", "functions")
__localConfigPath = os.path.join(os.getenv('HOME'), ".learnblock", "block")

ignore = [
    '__init__.py',
    'visual_auxiliary.py'
]


def getFunctions():
    functions = {}
    dirnames = [PATHFUNCTIONSSRC, __localFunctionsPath]
    sys.path.append(PATHFUNCTIONSSRC)
    for dirname in dirnames:
        if not os.path.exists(dirname):
            continue
        for filename in os.listdir(dirname):
            fullname = os.path.join(dirname, filename)
            name, extension = os.path.splitext(filename)
            _type = os.path.basename(dirname)
            if dirname == __localFunctionsPath:
                _type = "basics"
            if (os.path.isfile(fullname) and extension != '.py') or filename in ignore:
                continue
            if os.path.isdir(fullname):
                dirnames.append(fullname)
                continue
            sys.path.append(dirname)
            module_name = name
            try:
                func = getattr(import_module(module_name), name)
                # args = inspect.getargspec(func)
                functions[name] = dict(function=func, type=_type)
            except Exception as e:
                print("error", e, module_name, name, fullname)
    return functions


def load_blocks_Config(file=None):
    blocks = {}
    pathsConfig = [PATHFUNCTIONSCONF,
                   __localConfigPath
                   ]
    if file is None:
        for path in pathsConfig:
            if not os.path.exists(path):
                continue
            for f in os.listdir(path):
                if os.path.splitext(f)[-1] == ".conf":
                    file = os.path.join(path, f)
                    with open(file, "rb") as f:
                        text = f.read()
                    readblock = json.loads(text)
                    for b in readblock:
                        for i in range(len(b["img"])):
                            b["img"][i] = os.path.join(pathImgBlocks, b["img"][i])
                    blocks[file] = readblock
    else:
        with open(file, "r") as f:
            text = f.read()
        blocks = json.loads(text)
    return blocks



if __name__ == '__main__':
    blocks = load_blocks_Config()
    functions = getFunctions()
    nameconfigBlocks = [x["name"] for x in blocks]
    for x in nameconfigBlocks:
        if x not in functions:
            print(x)

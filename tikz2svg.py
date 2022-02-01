# import latextools
#!/usr/bin/env python
#
# author: github.com/jbenet
# license: MIT
#
# tikz2svg: convert tikz input into svg
# depends on:
# - pdflatex: comes with your tex dist
# - pdf2svg: brew install pdf2svg

import os
import sys
import hashlib
import functools
from subprocess import Popen, PIPE
import pdf2image


def deleteDir(dirPath):
    deleteFiles = []
    deleteDirs = []
    for root, dirs, files in os.walk(dirPath):
        for f in files:
            deleteFiles.append(os.path.join(root, f))
        for d in dirs:
            deleteDirs.append(os.path.join(root, d))
    for f in deleteFiles:
        os.remove(f)
    for d in deleteDirs:
        os.rmdir(d)
    os.rmdir(dirPath)


class cmds(object):
    pdflatex = "pdflatex --shell-escape -file-line-error -interaction=nonstopmode --"
    pdf2svg = "pdf2svg texput.pdf out.svg"


latex_doc = r"""
\documentclass[tikz]{standalone}

\usepackage{times}
\usepackage{tikz}
\usetikzlibrary{shapes}
\usetikzlibrary{mindmap,shadows,backgrounds,decorations.pathmorphing, decorations.text,positioning}
\usepackage{hyperref}



%(header)s
\begin{document}
%(tikzpicture)s

\end{document}
    """


# util to run command in a subprocess, and communicate with it.
def run(cmd, stdin=None, exit_on_error=True):
    # print '>', cmd
    p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    if stdin:
        p.stdin.write(stdin)
        p.stdin.close()
    p.wait()

    # error out if necessary
    if p.returncode != 0:
        print(">", cmd)
        print("Error.")
        if p.stdout:
            print("\n" * 5 + "-" * 20, "STDOUT")
            print(p.stdout.read().decode())

        if p.stderr:
            print("\n" * 5 + "-" * 20, "STDERR")
            print(p.stderr.read().decode())

        if p.stdin:
            print("-" * 20, "STDIN")
            print(stdin.decode())

        if exit_on_error:
            sys.exit(p.returncode)

    return p.stdout.read()


# memoize with a file cache.
def memoize_in_file(fn):
    @functools.wraps(fn)
    def memoized(*args, **kwds):
        i = fn.__name__ + str(*args) + str(**kwds)
        i = i.encode("utf-8")
        h = hashlib.sha1(i).hexdigest()
        if os.path.exists(h):
            with open(h) as f:
                return f.read()

        out = fn(*args, **kwds)
        with open(h, "w") as f:
            f.write(out)
        return out

    return memoized


# conversion functions
def tikz2tex(tikz):
    if "documentclass[tikz]{standalone}" not in str(tikz):
        header, picture = tikz.split("\\begin{tikzpicture}")
        picture = "\\begin{tikzpicture}" + picture
        return latex_doc % {"header": header, "tikzpicture": picture}
    else:
        print("Document already formatted")
        return tikz


def tex2pdf(tex):
    return run(cmds.pdflatex.split(" "), stdin=tex)


def pdf2svg():
    run(cmds.pdf2svg)
    with open("out.svg") as f:
        return f.read()


def tikz2img(tikz):
    curdir = os.getcwd()
    tmp_d = chdir(tikz)
    tex = tikz2tex(tikz)
    tex2pdf(tex.encode("utf-8"))
    image = pdf2image.convert_from_path("texput.pdf")
    os.chdir(curdir)
    deleteDir(tmp_d)
    print(f"Removed tmp directory {tmp_d}")
    image = image[0]
    return image


# @memoize_in_file
def tikz2svg(tikz):
    curdir = os.getcwd()
    tmp_d = chdir(tikz)
    tex = tikz2tex(tikz)
    tex2pdf(tex.encode("utf-8"))
    svg = pdf2svg()
    os.chdir(curdir)
    deleteDir(tmp_d)
    print(f"Removed tmp directory {tmp_d}")
    return svg


# move to tmp because latex litters :(
def chdir(inp):
    hash_dir = hashlib.sha1(inp.encode("utf-8")).hexdigest()
    tmp_d = "/tmp/%s" % hash_dir
    print(f"Compiling latex in {tmp_d}")
    run("mkdir -p %s" % tmp_d, exit_on_error=False)
    os.chdir(tmp_d)
    return tmp_d


def save_svg(svgcontent, filename):
    with open(filename, "w") as f:
        f.write(svgcontent)


def compile2svg(tiks_code):
    curdir = os.getcwd()
    tmp_d = chdir(tiks_code)
    svg_content = tikz2svg(tiks_code)
    os.chdir(curdir)
    deleteDir(tmp_d)
    print(f"Removed tmp directory {tmp_d}")
    try:
        os.remove("out.svg")
    except OSError:
        pass
    outfile_name = fileinput.filename().split(".")[0] + ".svg"
    save_svg(svg_content, outfile_name)
    print(f"Saved in {outfile_name}")


if __name__ == "__main__":
    if "-h" in sys.argv or "--help" in sys.argv:
        print("Usage: %s [<file>]" % sys.argv[0])
        print("Outputs svg conversion of tikz input (files or stdin).")
        sys.exit(0)

    import fileinput

    lines = "".join([l for l in fileinput.input()])
    # compile2svg(lines)
    image = tikz2img(lines)
    print(image)
    # pdf2image.

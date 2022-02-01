from tkinter import *
import re
import os
import urllib.request
import signal
import argparse
import json
import sys


class ToolTip(object):
    def __init__(self, widget):
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0

    def showtip(self, text):
        "Display text in tooltip window"
        self.text = text
        if self.tipwindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 57
        y = y + cy + self.widget.winfo_rooty() + 27
        self.tipwindow = tw = Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = Label(
            tw,
            text=self.text,
            justify=LEFT,
            background="#ffffe0",
            foreground="#000",
            relief=SOLID,
            borderwidth=1,
        )
        label.config(font=("Arial", 10))
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()


def add_tooltip(widget, text, max_length=45):
    """Add a small tooltip window to a widget."""
    if text:
        toolTip = ToolTip(widget)

        def enter(event):
            toolTip.showtip(cut_text(text, max_length))

        def leave(event):
            toolTip.hidetip()

        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)


def cut_text(text, max_length):
    """Cut a string at about 'max_length' chars into multiple lines."""
    words = text.split(" ")
    new_text = ""
    line_lenght = 0
    for word in words:

        # If specific linebreak is given, reset length count and continue
        if "\n" in word:
            line_lenght = 0
            new_text += word + " "
            continue

        if line_lenght + len(word) > max_length:
            line_lenght = 0
            new_text += "\n"
        new_text += word + " "
        line_lenght += len(word)
    return new_text


def entry_to_json(entry):
    """Convert an entry to a dictionary object."""
    json_dict = {}
    json_dict["color"] = entry.color
    json_dict["label"] = entry.label
    json_dict["inner_level"] = vars(entry.inner_level)
    json_dict["outer_level"] = vars(entry.outer_level)
    return json_dict

def scale_image_to_width(image, width):
    from PIL import Image
    old_width, old_height = image.size
    scale = width / old_width
    image_height = int(old_height * scale)
    image = image.resize(size=(width, image_height), resample=Image.ANTIALIAS)
    return image


def create_url(url):
    """
    From the given url, produce a URL that is compatible with Github's REST API. Can handle blob or tree paths.
    """
    repo_only_url = re.compile(r"https:\/\/github\.com\/[a-z\d](?:[a-z\d]|-(?=[a-z\d])){0,38}\/[a-zA-Z0-9]+$")
    re_branch = re.compile("/(tree|blob)/(.+?)/")

    # Check if the given url is a url to a GitHub repo. If it is, tell the
    # user to use 'git clone' to download it
    if re.match(repo_only_url,url):
        print("✘ The given url is a complete repository. Use 'git clone' to download the repository")
        sys.exit()

    # extract the branch name from the given url (e.g master)
    branch = re_branch.search(url)
    download_dirs = url[branch.end():]
    api_url = (url[:branch.start()].replace("github.com", "api.github.com/repos", 1) +
              "/contents/" + download_dirs + "?ref=" + branch.group(2))
    return api_url, download_dirs


def download_methods(repo_url, flatten=False, output_dir="methods"):
    """ Downloads the files and directories in repo_url. If flatten is specified, the contents of any and all
     sub-directories will be pulled upwards into the root folder. """

    # generate the url which returns the JSON data
    api_url, download_dirs = create_url(repo_url)

    # To handle file names.
    if not flatten:
        if len(download_dirs.split(".")) == 0:
            dir_out = os.path.join(output_dir, download_dirs)
        else:
            dir_out = os.path.join(output_dir, "/".join(download_dirs.split("/")[:-1]))
    else:
        dir_out = output_dir

    try:
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        urllib.request.install_opener(opener)
        response = urllib.request.urlretrieve(api_url)
    except KeyboardInterrupt:
        # when CTRL+C is pressed during the execution of this script,
        # bring the cursor to the beginning, erase the current line, and dont make a new line
        print("✘ Got interrupted")
        sys.exit()

    if not flatten:
        # make a directory with the name which is taken from
        # the actual repo
        os.makedirs(dir_out, exist_ok=True)

    # total files count
    total_files = 0
    existing_methods = os.listdir(output_dir)
    new_methods = []
    with open(response[0], "r") as f:
        data = json.load(f)
        # getting the total number of files so that we
        # can use it for the output information later
        total_files += len(data)

        # If the data is a file, download it as one.
        if isinstance(data, dict) and data["type"] == "file":
            try:
                # download the file
                opener = urllib.request.build_opener()
                opener.addheaders = [('User-agent', 'Mozilla/5.0')]
                urllib.request.install_opener(opener)
                urllib.request.urlretrieve(data["download_url"], os.path.join(dir_out, data["name"]))
                # bring the cursor to the beginning, erase the current line, and dont make a new line
                print("Downloaded: {}".format(data["name"]))

                return total_files
            except KeyboardInterrupt:
                # when CTRL+C is pressed during the execution of this script,
                # bring the cursor to the beginning, erase the current line, and dont make a new line
                print("✘ Got interrupted")
                sys.exit()

        for file in data:
            file_name = file["name"]
            if file_name in existing_methods:
                print(f"Found already existing {file_name}, not retrieving it")
                continue

            file_url = file["download_url"]
            if flatten:
                path = os.path.basename(file["path"])
            else:
                path = file["path"]
            dirname = os.path.dirname(path)

            if dirname != '':
                os.makedirs(os.path.dirname(path), exist_ok=True)
            else:
                pass

            if file_url is not None:
                try:
                    opener = urllib.request.build_opener()
                    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
                    urllib.request.install_opener(opener)
                    # download the file
                    urllib.request.urlretrieve(file_url, path)

                    # bring the cursor to the beginning, erase the current line, and dont make a new line
                    print("Downloaded: {}".format(file_name))
                    new_methods.append(file_name)

                except KeyboardInterrupt:
                    # when CTRL+C is pressed during the execution of this script,
                    # bring the cursor to the beginning, erase the current line, and dont make a new line
                    print("✘ Got interrupted")
                    sys.exit()
            else:
                download(file["html_url"], flatten, dir_out)

    return existing_methods, new_methods


# print(download_methods("https://github.com/k4ntz/cleva_methods/tree/master/methods"))

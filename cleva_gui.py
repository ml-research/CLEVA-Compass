#!/usr/bin/env python3
import json

try:
    from tkinter import *
    from tkinter import filedialog as fd
    from tkinter import simpledialog as sd
    from tkinter import messagebox
    from tkinter import ttk
    from tkinter import font
except:
    print(
        "Error - Could not import tkinter. Please make sure 'tkinter' is installed in your system."
    )
    exit(1)


from create_compass import read_json_entries, fill_template
from levels import CompassEntry
from collections import OrderedDict

try:
    # Try to import ImageTk from pillow
    from PIL import ImageTk

    MISSING_PIL = False
except ImportError:
    MISSING_PIL = True


try:
    # Try to import tikz2svg (pdf2img)
    from tikz2svg import tikz2img, tikz2svg, save_svg

    MISSING_PDF2IMG = False
except ImportError:
    MISSING_PDF2IMG = True

from gui_utils import add_tooltip, entry_to_json, scale_image_to_width, download_methods
from tkinter.colorchooser import askcolor


root = Tk()
root.configure(bg="white")
root.title("CLEVA Compass Generator")
# Add a frame to set the size of the window
root = Frame(root)
root.pack(fill=BOTH, expand=True, ipadx=10, ipady=10)

def_font = font.nametofont("TkDefaultFont")
def_font.configure(
    size=10,
    family="Arial",
)
try:
    from ttkthemes import ThemedStyle
    from tkinter.ttk import *

    style = ThemedStyle(root)
    style.theme_use("adapta")
except ImportError:
    print("Install ttkthemes for a nicer theme")
    style = ttk.Style(root)
    if "clam" in style.theme_names():
        style.theme_use("clam")

# bg = style.lookup('TFrame', 'background')
# bg = "#e7e7e7"
bg = "white"
root.configure(background="white")

padx = 5
pady = 1

header_label_kwargs = dict(padx=10, pady=10, sticky=W)


ttk.Style().configure("Default.TRadiobutton", background=bg, foreground="black")

ttk.Style().configure("Default.TCheckbutton", background=bg, foreground="black")

definitions = json.load(open("definition.json"))


# Define outer level elements (checkboxes)
outer_levels = [
    "compute_time",
    "mac_operations",
    "communication",
    "forgetting",
    "forward_transfer",
    "backward_transfer",
    "openness",
    "parameters",
    "memory",
    "stored_data",
    "generated_data",
    "optimization_steps",
    "per_task_metric",
    "task_order",
    "data_per_task",
]

# Define inner level elements (radiobuttons)
inner_levels = [
    "multiple_models",
    "federated",
    "online",
    "open_world",
    "multiple_modalities",
    "active_data_query",
    "task_order_discovery",
    "task_agnostic",
    "episodic_memory",
    "generative",
    "uncertainty",
]

outer_level_cbs = {}
inner_level_rbs = {}

# Header
label = ttk.Label(root, text="CLEVA Compass Generator", background=bg)
label.grid(row=0, column=0, columnspan=4, sticky=W + E, padx=padx + 5, pady=pady + 5)
label.config(font=("Arial", 18))

# Label for element in compass
ttk.Label(root, text="Label", background=bg).grid(row=1, column=0, padx=padx, pady=pady, sticky=W)
val_label = StringVar()
entry_label = ttk.Entry(root, textvariable=val_label)
entry_label.grid(row=1, column=1, columnspan=3, sticky=W + E, padx=padx, pady=pady)

# Color selection
ttk.Label(root, text="Color", background=bg).grid(row=1, column=4, padx=padx, pady=pady, sticky=W)
color_val = StringVar(root, "magenta")


colors = ["magenta", "green", "blue", "orange", "cyan", "brown"]
colors_val = ["#f364b8", "#62b162", "#3879e6", "#ec953f", "#74c9ea", "#d7a269"]
rbs = []
for i, (color, color_bg) in enumerate(zip(colors, colors_val)):
    ttk.Style().configure(
        f"{color}.TRadiobutton",
        background=color_bg,
        foreground="black",
    )
    row_n = 1
    rb = ttk.Radiobutton(
        root,
        text=" " + color,
        variable=color_val,
        width=10,
        value=color,
        style=f"{color}.TRadiobutton",
    )
    rbs.append(rb)
    rb.grid(row=row_n, column=5 + i, padx=padx, pady=pady)

    # root.columnconfigure(i+1, minsize=300, pad=0)


# def select_color():
#     ncolor_bg = askcolor(title="Tkinter Color Chooser")[1]
#     color_name = sd.askstring("Color Name", "What's the color name ?")
#     print(ncolor_bg)
#     ttk.Style().configure(
#         f"{color_name}.TRadiobutton",
#         background=ncolor_bg,
#         foreground="black",
#     )
#     rb = ttk.Radiobutton(
#         root,
#         text=" " + color_name,
#         variable=color_val,
#         width=10,
#         value=color_name,
#         style=f"{color_name}.TRadiobutton",
#     )
#     rb.grid(row=row_n+1, column=i%5+2, padx=padx, pady=pady)
#     return rb


class ExtraColorChooser():
    extra_colors = OrderedDict({"lime": "#bfff00", "pink": "#ffc0c1",
                                "purple": "#be0040", "teal": '#008080',
                                "lightgray": "#bfbfbf"})
    row_n = 2
    added_colors = []
    def __init__(self):
        self.win = Toplevel()
        self.win.wm_title("Choose another color")
        first_av = next(iter(self.extra_colors))  # first available elem
        self.e_color_val = StringVar(root, first_av)
        for i, color in enumerate(self.extra_colors):
            color_bg = self.extra_colors[color]
            ttk.Style().configure(
                f"{color}.TRadiobutton",
                background=color_bg,
                foreground="black",
            )
            rb = ttk.Radiobutton(
                self.win,
                text=" " + color,
                variable=self.e_color_val,
                width=10,
                value=color,
                style=f"{color}.TRadiobutton",
            )
            rbs.append(rb)
            rb.grid(row=0, column=i, padx=padx, pady=pady)
        b = ttk.Button(self.win, text="Okay", command=self.quit)
        b.grid(row=1, column=0)

    def quit(self):
        self.win.destroy()
        selected_color = self.e_color_val.get()
        selected_value = self.extra_colors.pop(selected_color)
        ttk.Style().configure(
            f"{selected_color}.TRadiobutton",
            background=selected_value,
            foreground="black",
        )
        rb = ttk.Radiobutton(
            root,
            text=" " + selected_color,
            variable=color_val,
            width=10,
            value=selected_color,
            style=f"{selected_color}.TRadiobutton",
        )
        j = len(self.added_colors) % 5 + 1
        self.added_colors.append(selected_color)
        rb.grid(row=2, column=5+j, padx=padx, pady=pady)
        rbs.append(rb)
        if self.extra_colors:
            add_color_b.grid(row=2, column=5+j+1, padx=padx, pady=pady)
        else:
            add_color_b.grid_forget()


def add_color():
    elem = ExtraColorChooser()


add_color_b = ttk.Button(root, text='+', command=add_color)
add_color_b.grid(row=row_n+1, column=6, padx=padx, pady=pady)

# Create label for inner ring
inner_level_start_row = row_n + 1
label = ttk.Label(root, text="Inner Level", background=bg)
label.grid(row=inner_level_start_row, column=0, columnspan=4, **header_label_kwargs)
label.config(font=("Arial", 16))
hintext = "(mouse-over items for info tooltips)"
hint = ttk.Label(root, text=hintext, background=bg)
hint.grid(row=inner_level_start_row, column=1, columnspan=3, sticky=W + E, padx=padx, pady=pady)
hint.config(font=("Arial", 8))

# Create label and radiobutton for inner ring elements
for i, il in enumerate(inner_levels, start=inner_level_start_row + 1):
    val = IntVar(root, 0)
    label = ttk.Label(root, text=il.replace("_", " "), background=bg)
    label.grid(row=i, column=0, padx=padx, pady=pady + 10, sticky=W)
    inner_defs = definitions["InnerLevel"]
    add_tooltip(label, text=inner_defs[il.replace("_", " ")])
    ttk.Radiobutton(
        root, text="Unsupervised", variable=val, value=2, style="Default.TRadiobutton"
    ).grid(row=i, column=1, padx=padx, pady=pady)
    ttk.Radiobutton(
        root, text="Supervised", variable=val, value=1, style="Default.TRadiobutton"
    ).grid(row=i, column=2, padx=padx, pady=pady)
    ttk.Radiobutton(root, text="None", variable=val, value=0, style="Default.TRadiobutton").grid(
        row=i, column=3, padx=padx, pady=pady
    )
    inner_level_rbs[il] = val

# Create label for Outer Level
# outer_level_start_row = len(inner_levels) + inner_level_start_row + 1
outer_level_start_row = 2
outer_level_start_col = 4
label = ttk.Label(root, text="Outer Level", background=bg)
label.grid(
    row=outer_level_start_row,
    column=outer_level_start_col,
    columnspan=2,
    **header_label_kwargs,
)
label.config(font=("Arial", 16))

# Create label and checkbutton for outer ring elements
for i, ol in enumerate(outer_levels):
    val = BooleanVar()
    label = ttk.Label(root, text=ol.replace("_", " "), background=bg)
    label.grid(
        row=outer_level_start_row + 1 + i // 4,
        column=outer_level_start_col + (i * 2) % 8,
        padx=padx,
        pady=pady,
        sticky=E,
    )
    cb = ttk.Checkbutton(root, variable=val, style="Default.TCheckbutton")
    cb.grid(
        row=outer_level_start_row + 1 + i // 4,
        column=outer_level_start_col + 1 + (i * 2) % 8,
        padx=padx,
        pady=pady,
        sticky=W,
    )
    outer_level_cbs[ol] = val
    outer_defs = definitions["OuterLevel"]
    add_tooltip(label, text=outer_defs[ol.replace("_", " ")])


def parse_state() -> CompassEntry:
    """
    Parse the current state of the color/label/inner-outer level selections into a CompassEntry
    """
    d = {}
    d["outer_level"] = {}
    for ol, val in outer_level_cbs.items():
        d["outer_level"][ol] = val.get()

    d["inner_level"] = {}
    for il, val in inner_level_rbs.items():
        d["inner_level"][il] = val.get()

    d["color"] = color_val.get()
    d["label"] = val_label.get()

    entry = read_json_entries([d])[0]
    return entry


global_entries = []


def on_press_download_methods_button():
    methods_url = "https://github.com/k4ntz/cleva_methods/tree/master/methods"
    existing_methods, new_methods = download_methods(methods_url)
    if new_methods:
        msg = f"Downloaded {len(new_methods)} new methods.\n" + \
            f"{len(existing_methods)} methods already in `methods`."
    else:
        msg = "No new method found on the repo.\n" + \
            f"{len(existing_methods)} methods already in `methods`."
    messagebox.showinfo(
        title="Download info", message=msg
    )


def on_press_add_entry_button():
    entry = parse_state()
    global_entries.append(entry)

    # Add to listbox
    lb.insert(len(global_entries), entry.label + " (" + entry.color + ")")

    # Reset values
    for ol, val in outer_level_cbs.items():
        val.set(0)

    for il, val in inner_level_rbs.items():
        val.set(0)

    val_label.set("")
    color_val.set("magenta")


def on_press_update_button():
    entry = parse_state()
    active = lb.get(ACTIVE)
    if lb.size() > 0:
        idx = lb.get(0, END).index(active)
        global_entries[idx] = entry
        lb.delete(idx)
        lb.insert(idx, entry.label + " (" + entry.color + ")")
        on_press_generate_image()


def on_press_delete_button():
    active = lb.get(ACTIVE)
    if lb.size() > 0:
        idx = lb.get(0, END).index(active)
        lb.delete(idx)
        global_entries.pop(idx)
        on_press_generate_image()


def on_press_export_button():
    active = lb.get(ACTIVE)
    if lb.size() > 0:
        idx = lb.get(0, END).index(active)
        selected_entry = global_entries[idx]
        json_dict = entry_to_json(selected_entry)
        json_text = json.dumps({"entries": [json_dict]})
        output_filename = fd.asksaveasfilename(initialfile=f"{selected_entry.label}.json")
        # Write output to the desired destination
        with open(output_filename, "w") as f:
            f.write(json_text)

        messagebox.showinfo(
            title="Info", message=f"Successfully saved CLEVA Compass to {output_filename}"
        )
    else:
        messagebox.showinfo(title="Info", message=f"There were no entries in the list.")


def on_press_import_button(filenames=None):
    if filenames is None:
        filenames = fd.askopenfilenames(
            filetypes=[
                ("JSON format", ".json"),
            ]
        )
    for filename in filenames:
        entries_json = json.load(open(filename))["entries"]
        entries = read_json_entries(entries_json)
        for entry in entries:
            global_entries.append(entry)
            # Add to listbox
            lb.insert(len(global_entries), entry.label + " (" + entry.color + ")")
    on_press_generate_image()


def on_press_generate_compass():
    output_filename = fd.asksaveasfilename(initialfile="cleva_filled.tex")

    template_path = "cleva_template.tex"
    tex_output = fill_template(template_path, global_entries)

    # Write output to the desired destination
    with open(output_filename, "w") as f:
        f.write(tex_output)

    messagebox.showinfo(
        title="Info", message=f"Successfully saved CLEVA Compass to {output_filename}"
    )


def on_press_export_image():
    if not libraries_available():
        warn_missing_libraries()
        return
    output_filename = fd.asksaveasfilename(
        initialfile="cleva_filled.svg",
        filetypes=(
            ("Scalable Vector Graphics", "*.svg"),
            ("Portable Network Graphics", "*.png"),
        ),
    )
    if output_filename[-4:] == ".svg":
        template_path = "cleva_template.tex"
        tex_output = fill_template(template_path, global_entries)
        svg_image = tikz2svg(tex_output)
        save_svg(svg_image, output_filename)
    elif output_filename[-4:] == ".png":
        image = on_press_generate_image()
        image = scale_image_to_width(image, width=2400)
        image.save(output_filename)
    else:
        msg = "Unsupported file format, please choose one of [svg, png]"
        messagebox.showinfo(title="Info", message=msg)
        return
    # # Write output to the desired destination
    # with open(output_filename, "w") as f:
    #     f.write(tex_output)

    messagebox.showinfo(
        title="Info", message=f"Successfully saved CLEVA Compass to {output_filename}"
    )


def set_state(entry: CompassEntry):
    color_val.set(entry.color)
    for ol, new_val in vars(entry.outer_level).items():
        val = outer_level_cbs[ol]
        val.set(new_val)
    for il, new_val in vars(entry.inner_level).items():
        val = inner_level_rbs[il]
        val.set(new_val)


def on_select_method(evt):
    """On click for when a method was selected in the listbox."""
    # Note here that Tkinter passes an event object to onselect()
    w = evt.widget
    if len(w.curselection()) == 0:
        return
    index = int(w.curselection()[0])
    selected_entry = global_entries[index]
    entry_label.delete(0, END)
    entry_label.insert(0, selected_entry.label)
    set_state(selected_entry)


def libraries_available():
    """Check if all external libraries are available."""
    return (not MISSING_PDF2IMG) and (not MISSING_PIL)


def warn_missing_libraries():
    """Put a warning messagebox telling the user that some libraries are missing."""
    messagebox.showinfo(
        title="Warning",
        message="Some libraries are missing. Please ensure, that you have the Python packages 'pdf2image' and 'pillow', as well as the system library 'poppler' installed.",
    )


def on_press_generate_image():
    if not libraries_available():
        warn_missing_libraries()
        return
    template_path = "cleva_template.tex"
    tex_output = fill_template(template_path, global_entries)
    comp_image = update_background(tikz2img(tex_output))
    old_width = image.image.width()
    image.image = ImageTk.PhotoImage(scale_image_to_width(comp_image, width=500))
    image.configure(image=image.image)
    if image.image.width() != old_width:
        x = root.winfo_height()
        y = root.winfo_width() + image.image.width() - old_width
        root.geometry("{}x{}".format(y, x))
    return comp_image


# Image on right side
def update_background(img):

    pixdata = img.load()
    for y in range(img.size[1]):
        for x in range(img.size[0]):
            if pixdata[x, y] == (255, 255, 255):
                pixdata[x, y] = (250, 250, 250)
    return img


button_starting_row = 1

buttons = []

# Add button: add entries to the list of compass entries
btn_add_entry = ttk.Button(
    root,
    text="← Add Compass Entry",
    command=on_press_add_entry_button,
)
add_tooltip(
    btn_add_entry,
    text="Adds a new entry with the current selection of inner and outer level options.",
)

btn_delete_entry = ttk.Button(
    root,
    text="← Delete Compass Entry",
    command=on_press_delete_button,
)
add_tooltip(btn_delete_entry, text="Deletes the selected compass entry from the list below.")

btn_update_entry = ttk.Button(
    root,
    text="← Update Compass Entry",
    command=on_press_update_button,
)
add_tooltip(
    btn_update_entry,
    text="Update the selected compass entry with the current selection of inner and outer level options, label, and color.",
)

btn_export_entry = ttk.Button(
    root,
    text="← Export Entry to File",
    command=on_press_export_button,
)
add_tooltip(btn_export_entry, text="Export the selected entry in the list to a JSON file.")

btn_export_to_image = ttk.Button(
    root,
    text="Export to Image →",
    command=on_press_export_image,
)
add_tooltip(
    btn_export_to_image,
    text="Export the current preview of the CLEVA Compass to an image (SVG/PNG)",
)

btn_import_entry = ttk.Button(
    root,
    text="← Import Ent. from File(s)",
    command=on_press_import_button,
)
add_tooltip(btn_import_entry, text="Import CLEVA Compass entries from one or multiple JSON files.")

btn_export_to_tex = ttk.Button(
    root,
    text="Export to Tex File →",
    command=on_press_generate_compass,
)
add_tooltip(btn_export_to_tex, text="Export the CLEVA Compass as Tikz code into a LaTeX file.")

btn_reload_preview = ttk.Button(
    root,
    text="Reload Preview →",
    command=on_press_generate_image,
)
add_tooltip(
    btn_reload_preview,
    text="Reload the CLEVA Compass preview, based on the current list of entries.",
)


btn_download_methods = ttk.Button(
    root,
    text="Download methods ↓",
    command=on_press_download_methods_button,
)
add_tooltip(
    btn_download_methods,
    text="Rerieve the methods from the github repo and place them in `methods` directory",
)

buttons = [
    btn_add_entry,
    btn_delete_entry,
    btn_update_entry,
    btn_reload_preview,
    btn_download_methods,
    btn_import_entry,
    btn_export_entry,
    btn_export_to_image,
    btn_export_to_tex,
]

kwargs = dict(columnspan=2, padx=0, pady=0, sticky=W + E)

# Entry buttons
btn_add_entry.grid(row=len(inner_levels) + 6, column=4, **kwargs)
btn_delete_entry.grid(row=len(inner_levels) + 7, column=4, **kwargs)
btn_update_entry.grid(row=len(inner_levels) + 8, column=4, **kwargs)
btn_export_entry.grid(row=len(inner_levels) + 9, column=4, **kwargs)
btn_import_entry.grid(row=len(inner_levels) + 10, column=4, **kwargs)

# Export Buttons
btn_export_to_image.grid(row=outer_level_start_row + 6, column=4, **kwargs)
btn_export_to_tex.grid(row=outer_level_start_row + 7, column=4, **kwargs)
btn_reload_preview.grid(row=outer_level_start_row + 8, column=4, **kwargs)
btn_download_methods.grid(row=outer_level_start_row + 11, column=4, **kwargs)

# Assign buttons in a 4x2 grid
# for i, btn in enumerate(buttons):
#     btn.grid(
#         row=button_starting_row + 1 + i // 4,
#         column=4 + (i * 2) % 8,
#         **kwargs,
#     )

# Listbox to list already added elements
label = ttk.Label(root, text="Compass Entries", background=bg)
label.grid(row=len(inner_levels) + 5, column=0, columnspan=4, **header_label_kwargs)
label.config(font=("Arial", 16))

hint = ttk.Label(root, text="(select to delete/update)", background=bg)
hint.grid(row=len(inner_levels) + 5, column=2, sticky=W + E, padx=padx, pady=pady)
hint.config(font=("Arial", 8))

lb = Listbox(root, exportselection=False)
lb.configure(
    background="white",
    foreground="black",
)
lb.grid(
    row=len(inner_levels) + 6,
    column=0,
    rowspan=5,
    columnspan=4,
    sticky=W + E + N + S,
    padx=padx + 5,
    pady=0,
)
lb.bind("<<ListboxSelect>>", on_select_method)


template_path = "cleva_template.tex"
tex_output = fill_template(template_path, global_entries)

if libraries_available():
    # img = tikz2img(tex_output)
    # img = update_background(img)
    # photo = ImageTk.PhotoImage(scale_image_to_width(img, width=500))
    image = Label(root, image=None, background=bg, border=4, relief="ridge")
    image.image = None
    image_start_row = outer_level_start_row + 5
    image_start_col = outer_level_start_col + 2
    image_colspan = 6
    image_rowspan = len(outer_levels)
    image.grid(
        row=image_start_row,
        column=image_start_col,
        columnspan=image_colspan,
        rowspan=image_rowspan,
        padx=padx,
        pady=pady,
        ipadx=3,
        ipady=3,
    )
else:
    warn_missing_libraries()

# Add some dummy example
def init_load_dummy_entry():
    entry = parse_state()
    entry.color = "green"
    entry.label = "Example Method (Author et al., 2021)"
    entry.inner_level.federated = 1
    entry.inner_level.multiple_models = 2
    entry.inner_level.uncertainty = 1
    entry.inner_level.generative = 1
    entry.inner_level.generative = 1
    entry.inner_level.task_agnostic = 2
    entry.inner_level.task_order_discovery = 2
    entry.inner_level.active_data_query = 1
    entry.inner_level.episodic_memory = 1
    entry.outer_level.mac_operations = True
    entry.outer_level.communication = True
    entry.outer_level.forgetting = True
    entry.outer_level.data_per_task = True
    entry.outer_level.task_order = True
    entry.outer_level.per_task_metric = True
    entry.outer_level.stored_data = True
    entry_label.insert(0, entry.label)
    set_state(entry)
    global_entries.append(entry)
    lb.insert(len(global_entries), entry.label + " (" + entry.color + ")")
    import PIL.Image
    image.image = ImageTk.PhotoImage(PIL.Image.open(".dummy.png"))
    image.configure(image=image.image)
    # on_press_generate_image()


init_load_dummy_entry()
root.mainloop()

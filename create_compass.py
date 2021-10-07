#!/usr/bin/env python3
import json
from dataclasses import dataclass
from typing import List
import math
import argparse

# Constants
D = 11  # Number of protocol dimensions
EV = 15  # Number of evaluation measures
A = 360 / D  # Angle between method axes
B = 360 / EV  # Angle between evaluation measure axes


def parse_arguments():
    """Parse commandline arguments."""
    parser = argparse.ArgumentParser(
        description="CLEVA-Compass Generator.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--template", default="cleva_template.tex", help="Tikz template file.",
    )
    parser.add_argument(
        "--output", default="cleva_filled.tex", help="Tikz filled output file.",
    )
    parser.add_argument(
        "--data", default="data.json", help="Entries as JSON file.",
    )

    return parser.parse_args()


@dataclass
class InnerLevel:
    """Inner CLEVA-Compass level with method attributes."""

    multiple_models: int
    federated: int
    online: int
    open_world: int
    multiple_modalities: int
    active_data_query: int
    task_order_discovery: int
    task_agnostic: int
    episodic_memory: int
    generative: int
    uncertainty: int

    def __iter__(self):
        """
        Defines the iteration order. This needs to be the same order as defined in the
        cleva_template.tex file.
        """
        for item in [
            self.multiple_models,
            self.federated,
            self.online,
            self.open_world,
            self.multiple_modalities,
            self.active_data_query,
            self.task_order_discovery,
            self.task_agnostic,
            self.episodic_memory,
            self.generative,
            self.uncertainty,
        ]:
            yield item


@dataclass
class OuterLevel:
    """Outer CLEVA-Compass level with measurement attributes."""

    compute_time: bool
    mac_operations: bool
    communication: bool
    forgetting: bool
    forward_transfer: bool
    backward_transfer: bool
    openness: bool
    parameters: bool
    memory: bool
    stored_data: bool
    generated_data: bool
    optimization_steps: bool
    per_task_metric: bool
    task_order: bool
    data_per_task: bool

    def __iter__(self):
        """
        Defines the iteration order. This needs to be the same order as defined in the
        cleva_template.tex file.
        """
        for item in [
            self.parameters,
            self.compute_time,
            self.mac_operations,
            self.communication,
            self.forgetting,
            self.forward_transfer,
            self.backward_transfer,
            self.openness,
            self.data_per_task,
            self.task_order,
            self.per_task_metric,
            self.optimization_steps,
            self.generated_data,
            self.stored_data,
            self.memory,
        ]:
            yield item


@dataclass
class CompassEntry:
    """Compass entry containing color, label, and attributes."""

    color: str  # Color, can be one of [magenta, green, blue, orange, cyan, brown]
    label: str  # Legend label
    inner_level: InnerLevel
    outer_level: OuterLevel


def mapcolor(color):
    """Maps the given simple colors string to a specific color for latex."""
    return {
        "magenta": "magenta",
        "green": "green!50!black",
        "blue": "blue!70!black",
        "orange": "orange!90!black",
        "cyan": "cyan!90!black",
        "brown": "brown!90!black",
    }[color]


def insert_legend(template, entries):
    """Insert the CLEVA-Compass legend below the compass."""

    # Skip if no entries are given (else the empty tabular will produce compile errors)
    if len(entries) == 0:
        return template

    # Compute number of rows/columns with max. three elements per row
    n_rows = math.ceil(len(entries) / 3)
    n_cols = 3 if len(entries) >= 3 else len(entries)

    # Begin legend tabular
    legend_str = ""
    legend_str += r"\begin{tabular}{" + " ".join(["l"] * n_cols) + "} \n"

    for i, e in enumerate(entries):
        # x/y coordinates of the entry
        x = i % 3
        y = round(i // 3)

        # Actual entry which uses \lentry defined in the tikz template
        legend_str += r"\lentry{" + mapcolor(e.color) + "}{" + e.label + "}"

        # Depending on last column/row
        is_last_column = x == n_cols - 1
        is_last_row = y == n_rows - 1
        if not is_last_column:
            # Add & for next element in row
            legend_str += r" & "
        else:
            if not is_last_row:
                # Add horizontal space if there is another row
                legend_str += " \\\\[0.15cm] \n"
            else:
                # Add no horizontal space if this is the last row
                legend_str += " \\\\ \n"

    # End legend tabular
    legend_str += "\end{tabular} \n"

    # Replace the generated string in template
    template = template.replace("%-$LEGEND$", legend_str)
    return template


def insert_outer_level(template, entries: List[CompassEntry]):
    """Insert outer level attributes."""
    oc_str = ""
    M = len(entries)
    for e_idx, e in enumerate(entries):
        # Add comment for readability
        s = "% Entry for: " + e.label + "\n"

        # For each outer level attribute
        for ol_idx, has_attribute in enumerate(e.outer_level):
            # If attribute is not present, skip and leave white
            if not has_attribute:
                continue

            # Build \pic command with coordinates depending on ol_idx and e_idx
            # Use variables defined in the template
            # angle_start = f"{ol_idx}*\B+{e_idx}*\BM"
            # angle_end = f"{ol_idx}*\B+{e_idx + 1}*\BM"

            # Compute dimensions here and insert angle directly
            angle_start = str(ol_idx * B + e_idx * B / M)
            angle_end = str(ol_idx * B + (e_idx + 1) * B / M)

            # Invert stripe direction when in the lower half (index larger than 7)
            if ol_idx > 7:
                angle_start, angle_end = angle_end, angle_start

            shell = e.color + "shell"
            s += (
                "\pic at (0,0){strip={\Instrip,"
                + angle_start
                + ","
                + angle_end
                + ","
                + shell
                + ", black, {}}};\n"
            )
        oc_str += s + "\n"

    template = template.replace("%-$OUTER-CIRCLE$", oc_str)
    return template


def insert_inner_level(template, entries: List[CompassEntry]):
    """Insert inner level path connections."""
    ir_str = ""
    for e in entries:
        path = " -- ".join(f"(D{i+1}-{irv})" for i, irv in enumerate(e.inner_level))
        ir_str += f"\draw [color={mapcolor(e.color)},line width=1.5pt,opacity=0.6, fill={mapcolor(e.color)}!10, fill opacity=0.4] {path} -- cycle;\n"

    template = template.replace("%-$INNER-CIRCLE$", ir_str)
    return template


def insert_number_of_methods(template, entries: List[CompassEntry]):
    """Insert number of methods as newcommand \M."""
    n_methods_str = r"\newcommand{\M}{" + str(len(entries)) + "}"
    template = template.replace("%-$NUMBER-OF-METHODS$", n_methods_str)
    return template


def read_json_entries():
    """Read the compass entries from a json file."""
    entries = []
    entries_json = json.load(open(args.data))["entries"]
    for d in entries_json:
        dil = d["inner_level"]
        dol = d["outer_level"]
        entry = CompassEntry(
            color=d["color"],
            label=d["label"],
            inner_level=InnerLevel(
                multiple_models=dil["multiple_models"],
                federated=dil["federated"],
                online=dil["online"],
                open_world=dil["open_world"],
                multiple_modalities=dil["multiple_modalities"],
                active_data_query=dil["active_data_query"],
                task_order_discovery=dil["task_order_discovery"],
                task_agnostic=dil["task_agnostic"],
                episodic_memory=dil["episodic_memory"],
                generative=dil["generative"],
                uncertainty=dil["uncertainty"],
            ),
            outer_level=OuterLevel(
                compute_time=dol["compute_time"],
                mac_operations=dol["mac_operations"],
                communication=dol["communication"],
                forgetting=dol["forgetting"],
                forward_transfer=dol["forward_transfer"],
                backward_transfer=dol["backward_transfer"],
                openness=dol["openness"],
                parameters=dol["parameters"],
                memory=dol["memory"],
                stored_data=dol["stored_data"],
                generated_data=dol["generated_data"],
                optimization_steps=dol["optimization_steps"],
                per_task_metric=dol["per_task_metric"],
                task_order=dol["task_order"],
                data_per_task=dol["data_per_task"],
            ),
        )
        entries.append(entry)
    return entries


if __name__ == "__main__":
    args = parse_arguments()

    # Read the compass entry from the given json data file
    entries = read_json_entries()

    # Read template content
    template_path = args.template
    with open(template_path) as f:
        template = "".join(f.readlines())

    # Replace respective parts in template
    output = template
    output = insert_legend(output, entries)
    output = insert_outer_level(output, entries)
    output = insert_inner_level(output, entries)
    output = insert_number_of_methods(output, entries)

    # Write output to the desired destination
    with open(args.output, "w") as f:
        f.write(output)

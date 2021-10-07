# The Continual Learning EValuation Assessment (CLEVA) Compass

This repository contains a template and code to automatically generate the Continual Learning EValuation Assessment (CLEVA) Compass. 

The CLEVA-Compass provides the visual means to both identify how continual learning approaches are practically reported and how works can simultaneously be contextualized in the broader literature landscape. In addition to promoting compact specification in the spirit of recent replication trends, the CLEVA-Compass thus provides an intuitive chart to understand the priorities of individual systems, where they resemble each other, and what elements are missing towards a fair comparison. 

Please visit our paper for more details and include a reference if you make use of the CLEVA-Compass in your work:

> Martin Mundt, Steven Lang, Quentin Delfosse, Kristian Kersting
> "CLEVA-Compass: A Continual Learning EValuation Assessment Compass to Promote Research Transparency and Comparability"
> arxiv ... (pending) 
 


For convenience, we provide two ways for practical future use of the CLEVA-Compass:

1. We include an automated Python script to generate the CLEVA-Compass diagram.
2. If you do not want to use Python to automatically generate the compass as described below, you can also base your compass on the supplied `cleva_flled.tex` example and modify the LaTeX source directly to your needs. 

## Create the CLEVA-Compass using Python 

You can use the `create_compass.py` python script to generate a compass and specify how it is filled for each continual approach in a JSON file:

``` sh
$ python create_compass.py -h
usage: create_compass.py [-h] [--template TEMPLATE] [--output OUTPUT] [--data DATA]

CLEVA-Compass Generator.

optional arguments:
  -h, --help           show this help message and exit
  --template TEMPLATE  Tikz template file. (default: cleva_template.tex)
  --output OUTPUT      Tikz filled output file. (default: cleva_filled.tex)
  --data DATA          Entries as JSON file. (default: data.json)
```

For this purpose we provide the template file `cleva_template.tex`.


### Example Usage
The default reads the template file from `cleva_template.tex` and writes the filled output file into `cleva_filled.tex` with the data specified via `--data <JSON_FILE>`:

``` sh
$ python --data examples/compass_data_0.json
```

An "empty" CLEVA-Compass, generated with [`examples/compass_data_0.json`](./examples/compass_data_0.json), looks like this:

<p align="center">
 <img src="./examples/example-0.svg">
</p>

In the next section, we specify how to add methods to the json file to fill the compass.

### JSON Data Format

The JSON file specifies a list of `entries`, where each element defines a `color`, `label` (can contain escaped TeX commands, such as citations), `inner_level`, and `outer_level`. The latter two specify the attributes visualized in the compass. 

- `color`: Can be one of `["magenta", "green", "blue", "orange", "cyan", "brown"]`.
- `label`: A label describing the compass entry (can contain arbitrary, escaped TeX commands such as citations).
- `inner_level`: Specifies the inner compass level attributes. Attribute values must be on of:
    - `0`: does not apply
    - `1`: supervised
    - `2`: unsupervised
- `outer_level`: Specifies the outer compass level attributes. Attribute values must boolean (`true`/`false`).

The [`compass_data_1.json`](./examples/compass_data_1.json) file is given as an example:
``` json
{
  "entries": [
    {
      "color": "magenta",
      "label": "FedWeIT",
      "inner_level": {
        "multiple_models": 1,
        "federated": 2,
        "online": 0,
        "open_world": 0,
        "multiple_modalities": 0,
        "active_data_query": 0,
        "task_order_discovery": 0,
        "task_agnostic": 0,
        "episodic_memory": 0,
        "generative": 0,
        "uncertainty": 0
      },
      "outer_level": {
        "compute_time": false,
        "mac_operations": false,
        "communication": true,
        "forgetting": true,
        "forward_transfer": false,
        "backward_transfer": true,
        "openness": false,
        "parameters": true,
        "memory": true,
        "stored_data": false,
        "generated_data": false,
        "optimization_steps": true,
        "per_task_metric": true,
        "task_order": false,
        "data_per_task": true
      }
    }
  ]
}
```

The resulting file `compass_filled.tex` can then be included into any LaTeX document, e.g.:

```tex
\begin{figure}
    \input{compass_filled.tex}
    \caption{CLEVA-Compass for methods Foo, Bar, and Baz.}
\end{figure}
```

With the above example, this results in the following visualization:

<p align="center">
 <img src="./examples/example-1.svg">
</p>


A JSON file with multiple entries ([`examples/compass_data_3.json`](./examples/compass_data_3.json)) produces the following compass:

<p align="center">
 <img src="./examples/example-3.svg">
</p>

If you want to directly modify a filled template without using the Python script described below, we also provide `cleva_filled.tex` as an example with three entries, which corresponds to the results of `python create_compass.py --data examples/compass_data_3.json`.

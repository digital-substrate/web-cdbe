# Web CDBE (web-cdbe)

A Flask web application that demonstrates how to build a **Commit Database Editor** on top of `dsviper` — pure HTML5, no JavaScript.

## Documentation

Full documentation: https://docs.digitalsubstrate.io/reference-apps/

Part of the [DevKit ecosystem](https://docs.digitalsubstrate.io/).

## Prerequisites

- Python 3.14+
- A Viper commit database (`.rapmc` or equivalent) to point the server at

## Installation

```bash
pip install -r requirements.txt
```

This installs `dsviper` (the Viper Python binding, from [PyPI](https://pypi.org/project/dsviper/)) along with `flask`.

## Usage

The server opens the database pointed to by the `database.link` symlink in the project root. Create it first:

```bash
ln -s /path/to/your/database.rapmc database.link
```

Then launch the server:

```bash
flask run --debug
```

```
* Database: /path/to/your/database.rapmc
 * Running on http://127.0.0.1:5000
```

## Routes

```
> flask routes

Endpoint        Methods  Rule
--------------  -------  ----------------------------------------------------------------------------------------------------
abstractions    GET      /
documents       GET      /documents/<uuid:abstraction_runtime_id>/<uuid:concept_runtime_id>/<uuid:instance_id>
documents_node  GET      /documents_node/<uuid:abstraction_runtime_id>/<uuid:concept_runtime_id>/<uuid:instance_id>/<uuid:node_uuid>
keys            GET      /keys/<uuid:abstraction_runtime_id>
static          GET      /static/<path:filename>
update          POST     /update
```

## License

This project is licensed under the MIT License — see [LICENSE](LICENSE).

## Runtime dependency

At runtime, this project depends on the `dsviper` Python package
(distributed on PyPI), which is **proprietary** (PyPI classifier
`License :: Other/Proprietary License`). See
[https://pypi.org/project/dsviper/](https://pypi.org/project/dsviper/)
for the package's licensing posture and contact information.

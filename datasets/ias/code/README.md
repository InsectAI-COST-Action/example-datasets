# Description

A fully reproducible example of the conversion from a data dump from the internal IAS (Invasive Alien Species) database to Camtrap DP 1.0.2 using the [`trap-schema`]() package.

# Setup

This example uses `uv` and **Python 3.13+**.

> [!TIP]
> If you don't have `uv` already it can be installed with:
> ```bash
> curl -LsSf https://astral.sh/uv/install.sh | sh
> ```
> Just remember to restart your terminal if it doesn't register properly.

## Installation

```bash
uv sync
uv run ipython kernel install --user --env VIRTUAL_ENV $(pwd)/.venv --name=jupyter_server
```

## Usage

To start using the notebooks first start a Jupyter server with `uv`:

```bash
uv run --with jupyter jupyter lab --NotebookApp.allow_origin='*' --NotebookApp.ip='0.0.0.0'
```

You should see something like:

```bash
    To access the server, open this file in a browser:
        file:/home/au644314/.local/share/jupyter/runtime/jpserver-41397-open.html
    Or copy and paste one of these URLs:
        http://<USER>:8888/lab?token=<TOKEN>
        http://127.0.0.1:8888/lab?token=<TOKEN>
```

Open the Jupyter notebook in your IDE (editor) and under select kernel choose: [`Existing Jupyter Server`](https://code.visualstudio.com/docs/datascience/jupyter-kernel-management#_existing-jupyter-server) and select `Enter URL of the running Jupyter Server` and paste one of the URL's, then select the `jupyter_server` kernel.
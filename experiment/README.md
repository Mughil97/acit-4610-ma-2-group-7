# experiment/

A scratch space for prototyping in notebooks before moving code into `app/`. Nothing in `app/` imports from here.

| Notebook      | Purpose                                                                  |
|---------------|--------------------------------------------------------------------------|
| `vega.ipynb`  | VEGA implementation checklist, prototype cells and sanity checks, then port to `app/algorithms/vega.py` |

## Running

The notebooks use the repo's `.venv` as their kernel. Jupyter support is only needed for experimenting, so it is not in
`requirements.txt`:

```bash
uv pip install --python .venv/bin/python ipykernel
```

Then open the notebook in VS Code and choose the `.venv` kernel. It works whether the working directory is the repo root
or `experiment/`.

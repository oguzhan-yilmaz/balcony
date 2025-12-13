```bash
source .venv/bin/activate
uv pip install -e .
uv pip show balcony

balcony info

typer balcony.cli utils docs  --output typer.README.md
```





```bash
# uv version --bump minor
uv version --bump patch
uv build
```
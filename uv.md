```bash
source .venv/bin/activate
uv pip install -e .
uv pip show balcony

balcony info

# gen readme 
typer balcony.cli utils docs  --output typer.README.md
```





```bash
# uv version --bump minor
uv version --bump patch
uv build
git tag v0.3.5 && git push --tags
uv publish
```
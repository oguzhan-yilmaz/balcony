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
# git commit 
rm dist/*.whl
rm dist/*.tar.gz

uv build

# export UV_PUBLISH_TOKEN=pypi-
uv publish
echo "tagging: v$(uv version --short)"
git tag v$(uv version --short) && git push --tags
# create gh release
```
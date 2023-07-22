# Publishing Python Package to PyPI

```bash
python3 balcony/cli.py terraform-import-support-matrix --no-md-render > docs/terraform-import-support-matrix.md
poetry publish --build --username $PYPI_USERNAME --password $PYPI_PASSWORD --skip-existing
```
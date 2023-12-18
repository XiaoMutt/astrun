echo "remove old dist folder"
rm -fr dist
echo "upgrade build"
venv/bin/python3 -m pip install --upgrade build
echo "building..."
venv/bin/python3 -m build
echo "publish to PyPi"
venv/bin/python3 -m twine upload --repository testpypi dist/*

readme: 
	pandoc -t rst -o README.rst README.md

dist: readme
	python setup.py sdist

wheel: dist
	python setup.py bdist_wheel --universal

all: wheel dist
	twine upload dist/*

testpypi: wheel dist
	twine upload --repository testpypi dist/*


all: docu sdist rpm

docu:
	epydoc --show-imports -o doc PyFoam/

sdist: docu
	python setup.py sdist --force-manifest

rpm:
	python setup.py bdist_rpm 

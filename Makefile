
all: docu sdist rpm

docu:
#	epydoc --graph=all --output=doc PyFoam --parse-only -v --include-log --css=grayscale
	epydoc --output=doc PyFoam --parse-only -v --include-log --css=grayscale

sdist: docu
	python setup.py sdist --force-manifest

rpm:
	python setup.py bdist_rpm 

dpkg:
	dpkg-buildpackage
#	dpkg-buildpackage -us -uc

source-dpkg:
	dpkg-buildpackage -S

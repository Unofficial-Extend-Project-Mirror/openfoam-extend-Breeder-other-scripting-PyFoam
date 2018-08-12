all: docu sdist rpm

docuold:
#	epydoc --graph=all --output=doc PyFoam --parse-only -v --include-log --css=grayscale
#	epydoc --output=doc PyFoam --parse-only -v --include-log --css=grayscale
	epydoc --output=doc.old PyFoam --introspect-only -v --include-log --inheritance=grouped --show-imports --include-log --graph=umlclasstree

docu:
	sphinx-apidoc --separate -o doc/api PyFoam
	(cd doc; make html)

docset: docu
	doc2dash -I index.html -n PyFoam doc/_build/html

sdist: docu ReleaseNotes.md ReleaseNotes.html
	python setup.py sdist

wheel: sdist
	python setup.py bdist_wheel --universal

rpm:
	python setup.py bdist_rpm

dpkg:
	dpkg-buildpackage
#	dpkg-buildpackage -us -uc

source-dpkg:
	dpkg-buildpackage -S

ReleaseNotes.md: ReleaseNotes
	pandoc --from=org --to=markdown ReleaseNotes -o ReleaseNotes.md

ReleaseNotes.html: ReleaseNotes
	pandoc --from=org --to=html ReleaseNotes -o ReleaseNotes.html

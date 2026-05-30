LIBRARY_VERSION=$(shell grep version library/setup.cfg | awk -F" = " '{print $$2}')
LIBRARY_NAME=$(shell grep name library/setup.cfg | awk -F" = " '{print $$2}')

.PHONY: usage check tag python-readme python-license python-clean

usage:
	@echo "Library: ${LIBRARY_NAME}"
	@echo "Version: ${LIBRARY_VERSION}\n"
	@echo "Usage: make <target>, where target is one of:\n"
	@echo "check:         perform basic integrity checks on the codebase"
	@echo "python-readme: regenerate library/README.md from README.md + library/CHANGELOG.txt"
	@echo "python-clean:  clean python build and dist directories"
	@echo "tag:           tag the repository with the current version"

check:
	@echo "Checking for trailing whitespace"
	@! grep -IUrn --color "[[:blank:]]$$" --exclude-dir=sphinx --exclude-dir=.tox --exclude-dir=.git --exclude=PKG-INFO
	@echo "Checking for DOS line-endings"
	@! grep -lIUrn --color "\r" --exclude-dir=sphinx --exclude-dir=.tox --exclude-dir=.git --exclude=Makefile
	@echo "Checking library/CHANGELOG.txt"
	@cat library/CHANGELOG.txt | grep ^${LIBRARY_VERSION}
	@echo "Checking library/${LIBRARY_NAME}/__init__.py"
	@cat library/${LIBRARY_NAME}/__init__.py | grep "^__version__ = '${LIBRARY_VERSION}'"

tag:
	git tag -a "v${LIBRARY_VERSION}" -m "Version ${LIBRARY_VERSION}"

python-readme: library/README.md

python-license: library/LICENSE.txt

library/README.md: README.md library/CHANGELOG.txt
	cp README.md library/README.md
	printf "\n# Changelog\n" >> library/README.md
	cat library/CHANGELOG.txt >> library/README.md

library/LICENSE.txt: LICENSE
	cp LICENSE library/LICENSE.txt

python-clean:
	-rm -r library/dist
	-rm -r library/build
	-rm -r library/*.egg-info

# Voice Recorder Documentation Makefile
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD  ?= sphinx-build
SOURCEDIR    = docs/sphinx
BUILDDIR     = docs/sphinx/_build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile docs-clean docs-html docs-serve

# Documentation targets
docs-html:
	@echo "Building HTML documentation..."
	@$(SPHINXBUILD) -b html "$(SOURCEDIR)" "$(BUILDDIR)/html" $(SPHINXOPTS) $(O)
	@echo "Build finished. The HTML pages are in $(BUILDDIR)/html."

docs-serve: docs-html
	@echo "Starting documentation server at http://localhost:8000"
	@echo "Press Ctrl+C to stop the server"
	@cd "$(BUILDDIR)/html" && python -m http.server 8000

docs-clean:
	@echo "Cleaning documentation build directory..."
	@rm -rf "$(BUILDDIR)"
	@echo "Documentation build directory cleaned."

# Catch-all target: route all unknown targets to Sphinx-Makefile
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
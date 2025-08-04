# Voice Recorder Documentation Makefile
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD  ?= sphinx-build
SOURCEDIR    = docs
BUILDDIR     = docs/_build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile docs-clean docs-html docs-serve

# Documentation targets
docs-html:
	@echo "Building HTML documentation..."
	@echo "Cleaning previous HTML files..."
	@find docs -name "*.html" -delete 2>/dev/null || true
	@rm -rf docs/_static docs/_sources docs/_modules docs/objects.inv docs/searchindex.js docs/.doctrees 2>/dev/null || true
	@$(SPHINXBUILD) -b html "$(SOURCEDIR)" "$(BUILDDIR)/html" $(SPHINXOPTS) $(O)
	@echo "Moving HTML files to docs root..."
	@cp -r "$(BUILDDIR)/html"/* docs/
	@rm -rf "$(BUILDDIR)"
	@echo "Build finished. The HTML pages are in docs/."

docs-serve: docs-html
	@echo "Starting documentation server at http://localhost:8000"
	@echo "Press Ctrl+C to stop the server"
	@cd docs && python -m http.server 8000

docs-clean:
	@echo "Cleaning documentation build directory..."
	@find docs -name "*.html" -delete 2>/dev/null || true
	@rm -rf docs/_static docs/_sources docs/_modules docs/objects.inv docs/searchindex.js docs/.doctrees docs/_build 2>/dev/null || true
	@echo "Documentation build directory cleaned."

# Catch-all target: route all unknown targets to Sphinx-Makefile
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
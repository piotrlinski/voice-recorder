# Voice Recorder Documentation Makefile
# Professional documentation build system with best practices
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?= --keep-going
SPHINXBUILD  ?= sphinx-build
SOURCEDIR    = docs
BUILDDIR     = docs/_build
DEPLOYDIR    = docs

# Colors for output
COLOR_RESET   = \033[0m
COLOR_BOLD    = \033[1m
COLOR_GREEN   = \033[32m
COLOR_BLUE    = \033[34m
COLOR_YELLOW  = \033[33m
COLOR_RED     = \033[31m

# Put it first so that "make" without argument is like "make help".
help:
	@echo "$(COLOR_BOLD)📚 Voice Recorder Documentation Build System$(COLOR_RESET)"
	@echo ""
	@echo "$(COLOR_BLUE)Available targets:$(COLOR_RESET)"
	@echo "  $(COLOR_GREEN)docs-html$(COLOR_RESET)     - Build HTML documentation for production"
	@echo "  $(COLOR_GREEN)docs-dev$(COLOR_RESET)      - Build HTML documentation for development (faster)"
	@echo "  $(COLOR_GREEN)docs-clean$(COLOR_RESET)    - Clean all generated documentation files"
	@echo "  $(COLOR_GREEN)docs-serve$(COLOR_RESET)    - Build and serve documentation locally"
	@echo "  $(COLOR_GREEN)docs-check$(COLOR_RESET)    - Validate documentation without building"
	@echo "  $(COLOR_GREEN)docs-linkcheck$(COLOR_RESET) - Check for broken links"
	@echo "  $(COLOR_GREEN)docs-deploy$(COLOR_RESET)   - Build and prepare for GitHub Pages deployment"
	@echo ""
	@echo "$(COLOR_YELLOW)Examples:$(COLOR_RESET)"
	@echo "  make docs-html        # Production build"
	@echo "  make docs-serve       # Local development"
	@echo "  make docs-deploy      # Prepare for deployment"

.PHONY: help Makefile docs-clean docs-html docs-dev docs-serve docs-check docs-linkcheck docs-deploy docs-validate

# Validate environment and dependencies
docs-validate:
	@echo "$(COLOR_BLUE)🔍 Validating documentation environment...$(COLOR_RESET)"
	@python -c "import sphinx; print(f'✅ Sphinx {sphinx.__version__}')" || (echo "$(COLOR_RED)❌ Sphinx not installed$(COLOR_RESET)" && exit 1)
	@python -c "import voice_recorder; print('✅ Package importable')" || (echo "$(COLOR_RED)❌ Package not importable$(COLOR_RESET)" && exit 1)
	@test -f "$(SOURCEDIR)/conf.py" || (echo "$(COLOR_RED)❌ Missing conf.py$(COLOR_RESET)" && exit 1)
	@test -f "$(SOURCEDIR)/index.rst" || (echo "$(COLOR_RED)❌ Missing index.rst$(COLOR_RESET)" && exit 1)
	@echo "$(COLOR_GREEN)✅ Environment validation complete$(COLOR_RESET)"

# Production HTML build with comprehensive validation
docs-html: docs-validate
	@echo "$(COLOR_BOLD)🏗️  Building production HTML documentation...$(COLOR_RESET)"
	@echo "$(COLOR_BLUE)📋 Build Configuration:$(COLOR_RESET)"
	@echo "  Source: $(SOURCEDIR)"
	@echo "  Build:  $(BUILDDIR)/html"
	@echo "  Deploy: $(DEPLOYDIR)"
	@echo ""
	@echo "$(COLOR_YELLOW)🧹 Cleaning previous builds...$(COLOR_RESET)"
	@rm -rf "$(BUILDDIR)" 2>/dev/null || true
	@find "$(DEPLOYDIR)" -name "*.html" -delete 2>/dev/null || true
	@rm -rf "$(DEPLOYDIR)/_static" "$(DEPLOYDIR)/_sources" "$(DEPLOYDIR)/_modules" "$(DEPLOYDIR)/objects.inv" "$(DEPLOYDIR)/searchindex.js" "$(DEPLOYDIR)/.doctrees" 2>/dev/null || true
	@echo "$(COLOR_BLUE)🔨 Building Sphinx documentation...$(COLOR_RESET)"
	@$(SPHINXBUILD) -b html "$(SOURCEDIR)" "$(BUILDDIR)/html" $(SPHINXOPTS) $(O)
	@echo "$(COLOR_YELLOW)📦 Preparing deployment files...$(COLOR_RESET)"
	@cp -r "$(BUILDDIR)/html"/* "$(DEPLOYDIR)/"
	@touch "$(DEPLOYDIR)/.nojekyll"
	@echo "$(COLOR_GREEN)✅ Production build complete!$(COLOR_RESET)"
	@echo "$(COLOR_BLUE)📊 Build Summary:$(COLOR_RESET)"
	@echo "  HTML files: $$(find "$(DEPLOYDIR)" -name "*.html" | wc -l | tr -d ' ')"
	@echo "  Total size: $$(du -sh "$(DEPLOYDIR)" | cut -f1)"
	@echo "  Deploy dir: $(DEPLOYDIR)/"

# Development build (faster, less validation)
docs-dev:
	@echo "$(COLOR_BOLD)🚀 Building development documentation...$(COLOR_RESET)"
	@$(SPHINXBUILD) -b html "$(SOURCEDIR)" "$(BUILDDIR)/html" -E
	@cp -r "$(BUILDDIR)/html"/* "$(DEPLOYDIR)/"
	@touch "$(DEPLOYDIR)/.nojekyll"
	@echo "$(COLOR_GREEN)✅ Development build complete!$(COLOR_RESET)"

# Build and serve locally
docs-serve: docs-dev
	@echo "$(COLOR_BOLD)🌐 Starting local documentation server...$(COLOR_RESET)"
	@echo "$(COLOR_BLUE)📋 Server Information:$(COLOR_RESET)"
	@echo "  URL: http://localhost:8000"
	@echo "  Directory: $(DEPLOYDIR)/"
	@echo "  Press Ctrl+C to stop"
	@echo ""
	@cd "$(DEPLOYDIR)" && python -m http.server 8000

# Clean all generated files
docs-clean:
	@echo "$(COLOR_YELLOW)🧹 Cleaning documentation build directory...$(COLOR_RESET)"
	@rm -rf "$(BUILDDIR)" 2>/dev/null || true
	@find "$(DEPLOYDIR)" -name "*.html" -delete 2>/dev/null || true
	@rm -rf "$(DEPLOYDIR)/_static" "$(DEPLOYDIR)/_sources" "$(DEPLOYDIR)/_modules" "$(DEPLOYDIR)/objects.inv" "$(DEPLOYDIR)/searchindex.js" "$(DEPLOYDIR)/.doctrees" 2>/dev/null || true
	@echo "$(COLOR_GREEN)✅ Documentation build directory cleaned$(COLOR_RESET)"

# Check documentation for issues
docs-check: docs-validate
	@echo "$(COLOR_BLUE)🔍 Checking documentation for issues...$(COLOR_RESET)"
	@$(SPHINXBUILD) -b dummy "$(SOURCEDIR)" "$(BUILDDIR)/dummy" -W --keep-going
	@echo "$(COLOR_GREEN)✅ Documentation check complete$(COLOR_RESET)"

# Check for broken links
docs-linkcheck: docs-validate
	@echo "$(COLOR_BLUE)🔗 Checking for broken links...$(COLOR_RESET)"
	@$(SPHINXBUILD) -b linkcheck "$(SOURCEDIR)" "$(BUILDDIR)/linkcheck" $(SPHINXOPTS)
	@echo "$(COLOR_GREEN)✅ Link check complete$(COLOR_RESET)"

# Deploy target (production build + deployment preparation)
docs-deploy: docs-html
	@echo "$(COLOR_BOLD)🚀 Preparing for GitHub Pages deployment...$(COLOR_RESET)"
	@echo "$(COLOR_BLUE)📋 Deployment checklist:$(COLOR_RESET)"
	@test -f "$(DEPLOYDIR)/index.html" && echo "  ✅ index.html exists" || echo "  ❌ index.html missing"
	@test -f "$(DEPLOYDIR)/.nojekyll" && echo "  ✅ .nojekyll exists" || echo "  ❌ .nojekyll missing"
	@test -d "$(DEPLOYDIR)/_static" && echo "  ✅ _static directory exists" || echo "  ❌ _static directory missing"
	@test -f "$(DEPLOYDIR)/search.html" && echo "  ✅ search.html exists" || echo "  ❌ search.html missing"
	@echo "$(COLOR_GREEN)✅ Ready for deployment!$(COLOR_RESET)"
	@echo "$(COLOR_YELLOW)📋 Next steps:$(COLOR_RESET)"
	@echo "  1. Commit changes: git add docs/ && git commit -m 'docs: update documentation'"
	@echo "  2. Push to GitHub: git push origin main"
	@echo "  3. GitHub Actions will deploy automatically"

# Catch-all target: route all unknown targets to Sphinx-Makefile
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
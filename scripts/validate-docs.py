#!/usr/bin/env python3
"""
Documentation validation script for Voice Recorder project.

This script performs comprehensive validation of the built documentation
to ensure it meets production quality standards.
"""

import os
import sys
import json
import urllib.request
import urllib.error
from pathlib import Path
from typing import List, Dict, Any
import re
import html.parser


class DocumentationValidator:
    """Comprehensive documentation validator."""
    
    def __init__(self, docs_dir: str = "docs"):
        self.docs_dir = Path(docs_dir)
        self.issues: List[Dict[str, Any]] = []
        self.stats = {
            "total_html_files": 0,
            "total_size_mb": 0,
            "broken_links": 0,
            "missing_meta": 0,
            "accessibility_issues": 0,
        }
    
    def log_issue(self, severity: str, category: str, message: str, file: str = ""):
        """Log a validation issue."""
        self.issues.append({
            "severity": severity,
            "category": category,
            "message": message,
            "file": file
        })
    
    def validate_file_structure(self) -> bool:
        """Validate basic file structure."""
        print("🔍 Validating file structure...")
        
        required_files = [
            "index.html",
            "search.html", 
            "genindex.html",
            "_static/theme.css",
            "searchindex.js",
            ".nojekyll"
        ]
        
        all_good = True
        for file in required_files:
            file_path = self.docs_dir / file
            if not file_path.exists():
                self.log_issue("error", "structure", f"Missing required file: {file}")
                all_good = False
            else:
                print(f"  ✅ {file}")
        
        # Count HTML files
        html_files = list(self.docs_dir.rglob("*.html"))
        self.stats["total_html_files"] = len(html_files)
        
        # Calculate total size
        total_size = sum(f.stat().st_size for f in self.docs_dir.rglob("*") if f.is_file())
        self.stats["total_size_mb"] = round(total_size / (1024 * 1024), 2)
        
        print(f"  📊 Found {len(html_files)} HTML files ({self.stats['total_size_mb']} MB total)")
        
        return all_good
    
    def validate_html_content(self) -> bool:
        """Validate HTML content quality."""
        print("🔍 Validating HTML content...")
        
        html_files = list(self.docs_dir.rglob("*.html"))
        issues_found = False
        
        for html_file in html_files:
            try:
                content = html_file.read_text(encoding='utf-8')
                
                # Check for basic HTML structure
                if not re.search(r'<html[^>]*>', content):
                    self.log_issue("error", "html", "Missing HTML tag", str(html_file))
                    issues_found = True
                
                if not re.search(r'<head[^>]*>.*</head>', content, re.DOTALL):
                    self.log_issue("error", "html", "Missing or incomplete HEAD section", str(html_file))
                    issues_found = True
                
                # Check for meta viewport (mobile responsiveness)
                if 'viewport' not in content:
                    self.log_issue("warning", "mobile", "Missing viewport meta tag", str(html_file))
                    self.stats["missing_meta"] += 1
                
                # Check for title
                if not re.search(r'<title[^>]*>.*</title>', content):
                    self.log_issue("warning", "seo", "Missing title tag", str(html_file))
                    self.stats["missing_meta"] += 1
                
                # Check for alt attributes on images
                img_tags = re.findall(r'<img[^>]*>', content)
                for img in img_tags:
                    if 'alt=' not in img:
                        self.log_issue("warning", "accessibility", f"Image missing alt text in {html_file.name}")
                        self.stats["accessibility_issues"] += 1
                
            except Exception as e:
                self.log_issue("error", "html", f"Error reading file: {e}", str(html_file))
                issues_found = True
        
        if not issues_found:
            print("  ✅ HTML content validation passed")
        
        return not issues_found
    
    def validate_internal_links(self) -> bool:
        """Validate internal links."""
        print("🔍 Validating internal links...")
        
        html_files = list(self.docs_dir.rglob("*.html"))
        broken_links = []
        
        for html_file in html_files:
            try:
                content = html_file.read_text(encoding='utf-8')
                
                # Find internal links (href attributes)
                internal_links = re.findall(r'href=["\']([^"\']*\.html[^"\']*?)["\']', content)
                
                for link in internal_links:
                    if link.startswith('http'):
                        continue  # Skip external links
                    
                    # Remove anchor fragments
                    link_path = link.split('#')[0]
                    if not link_path:
                        continue
                    
                    # Resolve relative path
                    if link_path.startswith('/'):
                        target_path = self.docs_dir / link_path[1:]
                    else:
                        target_path = (html_file.parent / link_path).resolve()
                    
                    if not target_path.exists():
                        broken_links.append(f"{html_file.name} -> {link}")
                        self.stats["broken_links"] += 1
                        
            except Exception as e:
                self.log_issue("error", "links", f"Error checking links: {e}", str(html_file))
        
        if broken_links:
            print(f"  ❌ Found {len(broken_links)} broken internal links")
            for link in broken_links[:5]:  # Show first 5
                print(f"    - {link}")
            if len(broken_links) > 5:
                print(f"    ... and {len(broken_links) - 5} more")
            return False
        else:
            print("  ✅ All internal links valid")
            return True
    
    def validate_search_functionality(self) -> bool:
        """Validate search functionality."""
        print("🔍 Validating search functionality...")
        
        search_html = self.docs_dir / "search.html"
        searchindex_js = self.docs_dir / "searchindex.js"
        
        if not search_html.exists():
            self.log_issue("error", "search", "Missing search.html")
            return False
        
        if not searchindex_js.exists():
            self.log_issue("error", "search", "Missing searchindex.js")
            return False
        
        # Check if search index has content
        try:
            search_content = searchindex_js.read_text(encoding='utf-8')
            if len(search_content) < 100:  # Very basic check
                self.log_issue("warning", "search", "Search index appears empty or very small")
            else:
                print("  ✅ Search functionality appears functional")
                return True
        except Exception as e:
            self.log_issue("error", "search", f"Error reading search index: {e}")
            return False
    
    def validate_api_documentation(self) -> bool:
        """Validate API documentation."""
        print("🔍 Validating API documentation...")
        
        api_index = self.docs_dir / "api" / "index.html"
        if not api_index.exists():
            self.log_issue("warning", "api", "Missing API documentation index")
            return False
        
        try:
            content = api_index.read_text(encoding='utf-8')
            if 'voice_recorder' not in content:
                self.log_issue("warning", "api", "API documentation may not contain expected content")
            else:
                print("  ✅ API documentation appears valid")
                return True
        except Exception as e:
            self.log_issue("error", "api", f"Error reading API documentation: {e}")
            return False
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive validation report."""
        
        # Count issues by severity
        errors = [i for i in self.issues if i["severity"] == "error"]
        warnings = [i for i in self.issues if i["severity"] == "warning"]
        
        report = {
            "validation_status": "passed" if not errors else "failed",
            "summary": {
                "total_issues": len(self.issues),
                "errors": len(errors),
                "warnings": len(warnings),
            },
            "statistics": self.stats,
            "issues": self.issues,
            "recommendations": []
        }
        
        # Add recommendations
        if errors:
            report["recommendations"].append("❌ Fix all errors before deployment")
        if warnings:
            report["recommendations"].append("⚠️ Consider addressing warnings for better quality")
        if self.stats["accessibility_issues"] > 0:
            report["recommendations"].append("♿ Improve accessibility by adding alt text to images")
        if self.stats["total_size_mb"] > 50:
            report["recommendations"].append("📏 Consider optimizing documentation size")
        
        return report
    
    def validate_all(self) -> bool:
        """Run all validations."""
        print("🏥 Starting comprehensive documentation validation...")
        print("=" * 60)
        
        validations = [
            self.validate_file_structure,
            self.validate_html_content,
            self.validate_internal_links,
            self.validate_search_functionality,
            self.validate_api_documentation,
        ]
        
        all_passed = True
        for validation in validations:
            try:
                if not validation():
                    all_passed = False
            except Exception as e:
                print(f"❌ Validation error: {e}")
                all_passed = False
            print()  # Empty line between validations
        
        return all_passed


def main():
    """Main validation function."""
    validator = DocumentationValidator()
    
    if not validator.docs_dir.exists():
        print(f"❌ Documentation directory '{validator.docs_dir}' does not exist")
        print("Run 'make docs-html' to build documentation first")
        sys.exit(1)
    
    # Run validations
    success = validator.validate_all()
    
    # Generate and display report
    report = validator.generate_report()
    
    print("📊 VALIDATION REPORT")
    print("=" * 60)
    print(f"Status: {'✅ PASSED' if success else '❌ FAILED'}")
    print(f"Total Issues: {report['summary']['total_issues']}")
    print(f"  - Errors: {report['summary']['errors']}")
    print(f"  - Warnings: {report['summary']['warnings']}")
    print()
    
    print("📈 STATISTICS")
    print("-" * 30)
    for key, value in report["statistics"].items():
        print(f"{key.replace('_', ' ').title()}: {value}")
    print()
    
    if report["recommendations"]:
        print("💡 RECOMMENDATIONS")
        print("-" * 30)
        for rec in report["recommendations"]:
            print(f"  {rec}")
        print()
    
    # Save report to file
    report_file = validator.docs_dir / "validation-report.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"📋 Detailed report saved to: {report_file}")
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
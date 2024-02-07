# Configuration file for the Sphinx documentation builder.


import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(".", "..", "..", "src")))

import pysikuli as sik

# -- Project information

project = "pysikuli"
copyright = "2024, Oleg Smoliakov"
author = "Oleg Smoliakov"

release = ""
version = sik.__version__

# -- General configuration

extensions = [
    "sphinx.ext.duration",
    "sphinx.ext.doctest",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
]
autoclass_content = "both"
autodoc_default_flags = ["members", "undoc-members", "inherited-members"]
autodoc_member_order = "bysource"
autodoc_mock_imports = [
    # Standard libs. Prevents errors from Py2 incompatible imports in Py3 code.
    "collections",
]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "sphinx": ("https://www.sphinx-doc.org/en/master/", None),
}
intersphinx_disabled_domains = ["std"]

templates_path = ["_templates"]

# -- Options for HTML output

html_theme = "sphinx_rtd_theme"

# -- Options for EPUB output
epub_show_urls = "footnote"

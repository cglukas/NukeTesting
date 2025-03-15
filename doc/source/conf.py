# ruff: noqa: INP001
# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "Nuke Testing"
copyright = "2024, Gilles Vink, Lukas Wieg"  # noqa: A001
author = "Gilles Vink, Lukas Wieg"
release = "0.0"
html_last_updated_fmt = "%B %d, %Y"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "myst_parser",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.autodoc",
    "sphinx_copybutton",
    "autoapi.extension",
]

templates_path = ["_templates"]
exclude_patterns = ["nuke_objects.inv"]

# -- Api documentation options -----------------------------------------------
autoapi_dirs = ["../../src"]
autoapi_options = [
    "members",
    "undoc-members",
    # "private-members", Not needed for us.
    "show-inheritance",
    "show-module-summary",
    "special-members",
    "imported-members",
]
autoapi_ignore = []
autoapi_member_order = "alphabetical"
napoleon_google_docstring = True

python_maximum_signature_line_length = 120

add_module_names = False

intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "nuke": (
        "https://learn.foundry.com/nuke/developers/151/pythondevguide/",
        "_static/nuke_objects.inv",
    ),
}

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
html_static_path = ["_static"]

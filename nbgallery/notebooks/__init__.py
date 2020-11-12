"""
Load notebook documents stored in nbgallery

This module contains functions to access notebook documents stored in a local
nbgallery.  The notebook_cache_dir must be set in the nbgallery configuration.

It is recommended that you use the from_* functions in this module to obtain a
notebook document from whatever information you have.  However, you can also
instantiate a document directly.

The NotebookDocument interface is a light abstraction in case support for
additional notebook types is added to nbgallery (iodide, RStudio, etc.).
Currently only Jupyter notebooks (ipynb format) are supported.
"""

import os

import nbgallery.config as nbgcfg

from .interface import NotebookDocument
from .jupyter import JupyterNotebook

def from_model(model):
    """
    Load a notebook from an nbgallery ORM Notebook model.  The
    notebook_cache_dir must be set in config.
    """
    uuid = model.uuid
    notebook_type = 'jupyter'
    return from_uuid(uuid, notebook_type)

def from_uuid(uuid, notebook_type):
    """
    Load a notebook using its nbgallery uuid. The notebook_cache_dir must be
    set in config; file extension is determined from notebook type.
    """
    cache = nbgcfg.config['nbgallery'].get('notebook_cache_dir')
    if not cache:
        raise RuntimeError('notebook_cache_dir must be set in config')
    basename = uuid + '.' + type_to_extension(notebook_type)
    filename = os.path.join(cache, basename)
    return from_file(filename, notebook_type)

def from_file(filename, notebook_type=None):
    """
    Load a notebook from a file.  The notebook type is determined from
    the file extension unless otherwise specified.
    """
    if not notebook_type:
        ext = os.path.splitext(filename)[1][1:]
        notebook_type = extension_to_type(ext)
    with open(filename) as f:
        content = f.read()
    return from_string(content, notebook_type)

def from_string(s, notebook_type):
    """
    Load a notebook from a string; notebook type must be specified.
    """
    if notebook_type == 'jupyter':
        return JupyterNotebook(s)
    raise RuntimeError(f"unknown notebook type {notebook_type}")

def extension_to_type(ext):
    """
    Return the notebook type for a given file extension
    """
    if ext == 'ipynb':
        return 'jupyter'
    raise RuntimeError(f"unknown file extension {ext}")

def type_to_extension(notebook_type):
    """
    Return the file extension for a given notebook type
    """
    if notebook_type == 'jupyter':
        return 'ipynb'
    raise RuntimeError(f"unknown notebook type {notebook_type}")

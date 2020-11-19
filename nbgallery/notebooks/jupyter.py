import nbformat
import nbstripout

from .interface import NotebookDocument

class JupyterNotebook(NotebookDocument):
    """
    A Jupyter notebook document (ipynb file) stored in nbgallery
    """

    def __init__(self, s, notebook_type='jupyter', **kwargs):
        super().__init__(s, notebook_type, **kwargs)
        self.notebook = nbformat.reads(s, as_version=4)

    def content(self):
        return nbformat.writes(self.notebook)

    def validate(self):
        nbformat.validate(self.notebook)

    def clean(self):
        nbstripout.strip_output(self.notebook, False, False)

    def cells(self, **kwargs):
        for cell in self.notebook.cells:
            yield cell

    def sources(self, **kwargs):
        for cell in self.cells(**kwargs):
            yield cell.source

    def code_sources(self):
        for cell in self.cells():
            if cell.cell_type == 'code':
                yield cell.source

    def doc_sources(self):
        for cell in self.cells():
            if cell.cell_type == 'markdown':
                yield cell.source

    def metadata(self):
        return self.notebook.metadata

    def language_version(self):
        meta = self.metadata()
        try:
            return (meta.language_info.name, meta.language_info.version)
        except:
            try:
                return (meta.kernelspec.language, None)
            except:
                return (None, None)

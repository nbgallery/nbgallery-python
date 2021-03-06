from abc import ABC, abstractmethod

class NotebookDocument(ABC):
    """
    Interface to support documents of different types (jupyter, iodide, etc.).
    This class defines operations useful in nbgallery that are common to most
    notebook types. 
    """

    @abstractmethod
    def __init__(self, s, notebook_type, **kwargs):
        """
        Create an notebook from a string and type of notebook (jupyter, iodide, etc.).
        """
        self.notebook_type = notebook_type

    def __str__(self):
       try:
           snippet = next(self.sources())
       except:
           snippet = ''
       if len(snippet) > 40:
           snippet = snippet[:40] + '...'
       return f"<{self.__class__.__name__} [{self.language()}] '{snippet}'>"

    @abstractmethod
    def content(self):
        """
        Return the raw content of the notebook in its native format, suitable
        for writing to disk.
        """
        return None

    @abstractmethod
    def validate(self):
        """
        Verify the notebook is well-formed according to its format specification.
        Raise an exception if the notebook is invalid.
        """
        pass

    @abstractmethod
    def clean(self):
        """
        Remove output and extraneous metadata from the notebook.
        """
        pass

    @abstractmethod
    def cells(self, **kwargs):
        """
        Return each cell of the notebook.  Subclasses may use kwargs to
        implement filtering. Note the cell structure depends on the type of
        notebook.
        """
        return []

    @abstractmethod
    def sources(self, **kwargs):
        """
        Return the source (e.g. code) from each cell.  Subclasses may use
        kwargs to implement filtering.  This should return an iterable of
        strings regardless of notebook type.
        """
        return []

    @abstractmethod
    def code_sources(self):
        """
        Return the source from code cells only, as an iterable of strings.
        """
        return []

    @abstractmethod
    def doc_sources(self):
        """
        Return the source from documentation cells only, as an iterable of strings.
        """
        return []

    @abstractmethod
    def metadata(self):
        """
        Return metadata about the notebook.  Structure may depend on the type
        of notebook.
        """
        return {}

    @abstractmethod
    def language_version(self):
        """
        Return the language and version of the notebook as a tuple; e.g.
        ('python', '3.8').
        """
        return (None, None)

    def language(self):
        """
        Return the language of the notebook.
        """
        return self.language_version()[0]

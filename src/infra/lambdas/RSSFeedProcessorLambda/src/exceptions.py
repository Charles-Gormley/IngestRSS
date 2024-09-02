class RSSProcessingError(Exception):
    """Exception raised for errors in the RSS processing."""
    pass

class ArticleExtractionError(Exception):
    """Exception raised for errors in the article extraction."""
    pass

class DataStorageError(Exception):
    """Exception raised for errors in data storage operations."""
    pass
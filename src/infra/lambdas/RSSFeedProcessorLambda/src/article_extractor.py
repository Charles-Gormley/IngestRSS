import newspaper
import logging



logger = logging.getLogger()

def extract_article(url):
    """
    Extracts the title and text of an article from the given URL.
    
    Args:
        url (str): The URL of the article.
    Returns:
        A tuple containing the title and text of the article, respectively.
    """
    logger.debug(f"Starting Newspaper Article Extraction {url}")
    config = newspaper.Config()
    config.request_timeout = 60
    article = newspaper.Article(url)
    
    try:
        article.download()
        logger.debug(f"Downloaded Article {url}")
        article.parse()
        logger.debug(f"Parsed Article {url}")    
        
        return article.title, article.text
    except Exception as e:
        logger.error(f"Failed to extract article {url}: {str(e)}")
        return None, None
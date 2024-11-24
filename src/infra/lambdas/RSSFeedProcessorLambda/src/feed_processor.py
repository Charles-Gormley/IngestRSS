import feedparser
from datetime import datetime
from dateutil import parser
import queue
import threading
import logging
from utils import generate_key
from article_extractor import extract_article
from article_cleaning import clean_text

logger = logging.getLogger()

def process_feed(feed: dict):
    output_queue = queue.Queue()
    stop_thread = threading.Event()
    thread = threading.Thread(target=extract_feed_threading, args=(feed, output_queue, stop_thread))
    thread.daemon = True
    thread.start()
    
    logger.debug(f"Thread Started: {feed['u']}")
    thread.join(timeout=90)
    
    if thread.is_alive():
        stop_thread.set()
        logger.debug(f"Killing Thread: {feed['u']}")
        return None
    else:
        try:
            output = output_queue.get_nowait()
            logger.info(f"Thread Succeeded: {feed['u']}")
            return output
        except queue.Empty:
            logger.info(f"Thread Failed: {feed['u']}")
            return None
        
def extract_feed_threading(rss: dict, output_queue, stop_thread):
    articles = []
    feed_url = rss['u']
    last_date = rss['dt']
    max_date = last_date

    try:
        feed = feedparser.parse(feed_url)
        for entry in feed['entries']:
            if stop_thread.is_set():
                break
            
            pub_date = parse_pub_date(entry['published'])
            
            if pub_date > last_date:
                title, text = extract_article(entry.link)
                title, text = clean_text(title), clean_text(text)
                article = {
                    'link': entry.link,
                    'rss': feed_url,
                    'title': title,
                    'content': text,
                    'unixTime': pub_date,
                    'rss_id': generate_key(feed_url),
                    'article_id': generate_key(entry.link),
                    'llm_summary': None,
                    'embedding': None
                }
                articles.append(article)
                max_date = max(max_date, pub_date)

        output = {
            'articles': articles,
            'max_date': max_date,
            'feed': rss
        }
        output_queue.put(output)
    except Exception as e:
        logger.error(f"Feed: {entry}")
        logger.error(f"Feed failed due to error: {e}")

def extract_feed(rss: dict):
    articles = []
    feed_url = rss['u']
    last_date = rss['dt']
    max_date = last_date

    try:
        feed = feedparser.parse(feed_url)
        for entry in feed['entries']:
            pub_date = parse_pub_date(entry['published'])
            
            if pub_date > last_date:
                title, text = extract_article(entry.link) 
                article = {
                    'link': entry.link,
                    'rss': feed_url,
                    'title': title,
                    'content': text,
                    'unixTime': pub_date,
                    'rss_id': generate_key(feed_url),
                    'article_id': generate_key(entry.link),
                    'llm_summary': None,
                    'embedding': None
                }
                articles.append(article)
                max_date = max(max_date, pub_date)

        output = {
            'articles': articles,
            'max_date': max_date,
            'feed': rss
        }
        print(output)
        return output
    except Exception as e:
        logger.error(f"Feed: {entry}")
        logger.error(f"Feed failed due to error: {e}")

def parse_pub_date(entry:dict):

    if 'published' in entry:
        date_string = entry['published']       

        try:
            return int(datetime.strptime(date_string, "%a, %d %b %Y %H:%M:%S %z").timestamp())
        except ValueError:
            try:
                return int(datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%SZ").timestamp())
            except ValueError:
                try:
                    return int(parser.parse(date_string).timestamp())
                except ValueError:
                    pass

    return int(datetime.now().timestamp()) # Return current time if no date is found
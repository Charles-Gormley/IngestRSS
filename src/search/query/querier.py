import boto3
import pandas as pd
from typing import Optional, Dict, List, Any
import json
import os
from datetime import datetime
from string import Template
import logging

class ArticleQuerier:
    """Class for querying RSS articles using Amazon Athena"""
    
    DEFAULT_CONFIG = {
        "region": "${AWS_REGION}",
        "database": "${RSS_DATABASE_NAME}",
        "table": "${RSS_TABLE_NAME}",
        "output_location": "s3://${RSS_BUCKET_NAME}/athena-output/"
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the ArticleQuerier
        
        Args:
            config_path: Optional path to config file. If None, uses environment variables.
        """
        self.logger = logging.getLogger(__name__)
        self.config = self._load_config(config_path)
        self._validate_config()
        
        self.athena = boto3.client('athena', region_name=self.config['region'])
        self.logger.info(f"Initialized ArticleQuerier with database: {self.config['database']}")
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, str]:
        """Load and process configuration"""
        if config_path and os.path.exists(config_path):
            with open(config_path) as f:
                template = Template(f.read())
        else:
            template = Template(json.dumps(self.DEFAULT_CONFIG))
            
        env_vars = {
            'AWS_REGION': os.getenv('AWS_REGION', 'eu-west-3'),
            'RSS_DATABASE_NAME': os.getenv('RSS_DATABASE_NAME', 'rss_articles'),
            'RSS_TABLE_NAME': os.getenv('RSS_TABLE_NAME', 'articles'),
            'RSS_BUCKET_NAME': os.getenv('RSS_BUCKET_NAME', 'your-bucket'),
        }
        
        config_str = template.safe_substitute(env_vars)
        
        try:
            return json.loads(config_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON config after variable substitution: {str(e)}")
    
    def _validate_config(self) -> None:
        """Validate the configuration"""
        required_fields = ['region', 'database', 'table', 'output_location']
        missing_fields = [field for field in required_fields if field not in self.config]
        
        if missing_fields:
            raise ValueError(f"Missing required config fields: {', '.join(missing_fields)}")
            
        if not self.config['output_location'].startswith('s3://'):
            raise ValueError("output_location must be an S3 URL (s3://...)")
    
    def search(self, 
              title: Optional[str] = None,
              content: Optional[str] = None,
              source: Optional[str] = None,
              date_from: Optional[str] = None,
              date_to: Optional[str] = None,
              limit: int = 100) -> pd.DataFrame:
        """
        Search articles using various filters
        
        Args:
            title: Search in article titles
            content: Search in article content
            source: Filter by source
            date_from: Start date (YYYY-MM-DD)
            date_to: End date (YYYY-MM-DD)
            limit: Maximum number of results
            
        Returns:
            DataFrame containing the results
        """
        conditions = []
        if title:
            conditions.append(f"LOWER(title) LIKE LOWER('%{title}%')")
        if content:
            conditions.append(f"LOWER(content) LIKE LOWER('%{content}%')")
        if source:
            conditions.append(f"source = '{source}'")
        if date_from:
            conditions.append(f"published_date >= TIMESTAMP '{date_from}'")
        if date_to:
            conditions.append(f"published_date <= TIMESTAMP '{date_to}'")
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        query = f"""
        SELECT *
        FROM {self.config['database']}.{self.config['table']}
        WHERE {where_clause}
        ORDER BY published_date DESC
        LIMIT {limit}
        """
        
        return self.query(query)

    def query(self, query: str) -> pd.DataFrame:
        """
        Execute custom SQL query
        
        Args:
            query: SQL query string
            
        Returns:
            DataFrame containing the results
        """
        try:
            self.logger.debug(f"Executing query: {query}")
            response = self.athena.start_query_execution(
                QueryString=query,
                QueryExecutionContext={'Database': self.config['database']},
                ResultConfiguration={'OutputLocation': self.config['output_location']}
            )
            
            return self._get_query_results(response['QueryExecutionId'])
        except Exception as e:
            self.logger.error(f"Query execution failed: {str(e)}")
            raise

    def get_sources(self) -> pd.DataFrame:
        """
        Get list of sources and their article counts
        
        Returns:
            DataFrame with source statistics
        """
        query = f"""
        SELECT 
            source,
            COUNT(*) as article_count,
            MIN(published_date) as earliest_article,
            MAX(published_date) as latest_article
        FROM {self.config['database']}.{self.config['table']}
        GROUP BY source
        ORDER BY article_count DESC
        """
        return self.query(query)

    def _get_query_results(self, query_id: str) -> pd.DataFrame:
        """Helper method to get query results"""
        while True:
            status = self.athena.get_query_execution(QueryExecutionId=query_id)
            state = status['QueryExecution']['Status']['State']
            
            if state == 'SUCCEEDED':
                break
            elif state in ['FAILED', 'CANCELLED']:
                error_message = status['QueryExecution']['Status'].get('StateChangeReason', 'Unknown error')
                raise Exception(f"Query failed: {error_message}")

        results = []
        columns = None
        paginator = self.athena.get_paginator('get_query_results')
        
        for page in paginator.paginate(QueryExecutionId=query_id):
            if not columns:
                columns = [col['Name'] for col in page['ResultSet']['ResultSetMetadata']['ColumnInfo']]
            for row in page['ResultSet']['Rows'][1:]:
                results.append([field.get('VarCharValue', '') for field in row['Data']])

        return pd.DataFrame(results, columns=columns)
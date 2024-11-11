import boto3
import pandas as pd
from typing import Optional, List, Dict, Union, Any
import json
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import logging
from string import Template

class S3BatchDownloader:
    """Class for batch downloading RSS articles from S3"""
    
    DEFAULT_CONFIG = {
        "region": "${AWS_REGION}",
        "bucket": "${RSS_BUCKET_NAME}",
        "prefix": "${RSS_PREFIX}",
        "max_workers": 10
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the S3BatchDownloader
        
        Args:
            config_path: Optional path to config file. If None, uses environment variables.
        """
        self.logger = logging.getLogger(__name__)
        self.config = self._load_config(config_path)
        self._validate_config()
        
        self.s3 = boto3.client('s3', region_name=self.config['region'])
        self.logger.info(f"Initialized S3BatchDownloader for bucket: {self.config['bucket']}")
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load and process configuration"""
        if config_path and os.path.exists(config_path):
            with open(config_path) as f:
                template = Template(f.read())
        else:
            template = Template(json.dumps(self.DEFAULT_CONFIG))
            
        env_vars = {
            'AWS_REGION': os.getenv('AWS_REGION', 'eu-west-3'),
            'RSS_BUCKET_NAME': os.getenv('RSS_BUCKET_NAME', 'your-bucket'),
            'RSS_PREFIX': os.getenv('RSS_PREFIX', 'articles/'),
        }
        
        config_str = template.safe_substitute(env_vars)
        
        try:
            config = json.loads(config_str)
            # Ensure max_workers is an integer
            config['max_workers'] = int(config.get('max_workers', 10))
            return config
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON config after variable substitution: {str(e)}")
    
    def _validate_config(self) -> None:
        """Validate the configuration"""
        required_fields = ['region', 'bucket', 'prefix']
        missing_fields = [field for field in required_fields if field not in self.config]
        
        if missing_fields:
            raise ValueError(f"Missing required config fields: {', '.join(missing_fields)}")
    
    def download_to_csv(self, 
                       output_path: str,
                       prefix: Optional[str] = None,
                       start_date: Optional[str] = None,
                       end_date: Optional[str] = None,
                       batch_size: int = 1000) -> str:
        """
        Download articles from S3 to CSV file
        
        Args:
            output_path: Path to save CSV file
            prefix: Optional S3 prefix filter
            start_date: Optional start date filter (YYYY-MM-DD)
            end_date: Optional end date filter (YYYY-MM-DD)
            batch_size: Number of objects to process in each batch
            
        Returns:
            Path to the saved CSV file
        """
        self.logger.info(f"Starting batch download to {output_path}")
        
        # Convert dates if provided
        start_ts = datetime.strptime(start_date, '%Y-%m-%d') if start_date else None
        end_ts = datetime.strptime(end_date, '%Y-%m-%D') if end_date else None
        
        # Get list of all objects
        objects = self._list_objects(prefix)
        
        # Filter by date if specified
        if start_ts or end_ts:
            objects = [
                obj for obj in objects
                if self._is_in_date_range(obj['LastModified'], start_ts, end_ts)
            ]
        
        self.logger.info(f"Found {len(objects)} objects to process")
        
        # Process in batches
        all_data = []
        for i in range(0, len(objects), batch_size):
            batch = objects[i:i + batch_size]
            self.logger.info(f"Processing batch {i//batch_size + 1}/{(len(objects)-1)//batch_size + 1}")
            
            # Download batch in parallel
            with ThreadPoolExecutor(max_workers=self.config['max_workers']) as executor:
                results = list(executor.map(self._download_object, batch))
            
            # Add successful downloads to results
            for result in results:
                if result is not None:
                    all_data.extend(result if isinstance(result, list) else [result])
        
        # Convert to DataFrame and save
        df = pd.DataFrame(all_data)
        df.to_csv(output_path, index=False)
        
        self.logger.info(f"Successfully downloaded {len(df)} articles to {output_path}")
        return output_path
    
    def _list_objects(self, prefix: Optional[str] = None) -> List[Dict]:
        """List objects in S3 bucket"""
        objects = []
        paginator = self.s3.get_paginator('list_objects_v2')
        
        try:
            for page in paginator.paginate(
                Bucket=self.config['bucket'],
                Prefix=prefix or self.config['prefix']
            ):
                if 'Contents' in page:
                    objects.extend(page['Contents'])
                    
            return objects
            
        except Exception as e:
            self.logger.error(f"Error listing objects: {str(e)}")
            raise
    
    def _download_object(self, obj: Dict) -> Optional[Union[Dict, List[Dict]]]:
        """Download and parse single S3 object"""
        try:
            response = self.s3.get_object(
                Bucket=self.config['bucket'],
                Key=obj['Key']
            )
            content = response['Body'].read().decode('utf-8')
            
            # Handle both single JSON objects and arrays
            data = json.loads(content)
            return data if isinstance(data, list) else [data]
            
        except Exception as e:
            self.logger.error(f"Error downloading {obj['Key']}: {str(e)}")
            return None
    
    def _is_in_date_range(self, 
                         ts: datetime,
                         start: Optional[datetime],
                         end: Optional[datetime]) -> bool:
        """Check if timestamp is within date range"""
        if start and ts < start:
            return False
        if end and ts > end:
            return False
        return True
    
    def get_storage_stats(self) -> Dict[str, Union[int, float]]:
        """
        Get storage statistics
        
        Returns:
            Dict containing total objects, total size, etc.
        """
        objects = self._list_objects()
        return {
            'total_objects': len(objects),
            'total_size_mb': sum(obj['Size'] for obj in objects) / (1024 * 1024),
            'average_size_kb': sum(obj['Size'] for obj in objects) / len(objects) / 1024 if objects else 0
        }
import boto3
import pandas as pd
from typing import Optional, List, Dict, Union, Any
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import logging
from string import Template

class S3BatchDownloader:
    """Class for batch downloading RSS articles from S3"""
    
    DEFAULT_CONFIG = {
        "region": "${AWS_REGION}",
        "bucket": "${RSS_BUCKET_NAME}",
        "prefix": "${RSS_PREFIX}",
        "max_workers": os.cpu_count() or 10
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
            'AWS_REGION': os.getenv('AWS_REGION', 'us-east-1'),
            'RSS_BUCKET_NAME': os.getenv('S3_BUCKET_NAME')
        }
        
        config_str = template.safe_substitute(env_vars)
        
        try:
            config = json.loads(config_str)
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
    
    def download_to_file(self, 
                        output_path: str,
                        file_format: str = 'csv',
                        start_date: Optional[str] = None,
                        end_date: Optional[str] = None) -> str:
        """
        Download articles from S3 to a consolidated file
        
        Args:
            output_path: Path to save the output file.
            file_format: Format to save the file ('csv' or 'json').
            start_date: Optional start date filter (YYYY-MM-DD).
            end_date: Optional end date filter (YYYY-MM-DD).
            
        Returns:
            Path to the saved file.
        """
        self.logger.info(f"Starting batch download to {output_path}")
        
        # Convert date strings to UTC datetime
        start_ts = datetime.strptime(start_date, '%Y-%m-%d').replace(tzinfo=timezone.utc) if start_date else None
        end_ts = datetime.strptime(end_date, '%Y-%m-%d').replace(tzinfo=timezone.utc) if end_date else None
        
        # List and filter objects
        objects = self._list_objects()
        
        if start_ts or end_ts:
            objects = [
                obj for obj in objects
                if self._is_in_date_range(obj['LastModified'], start_ts, end_ts)
            ]
        self.logger.info(f"Found {len(objects)} objects to process")
        
        # Download and merge data
        all_data = []
        with ThreadPoolExecutor(max_workers=self.config['max_workers']) as executor:
            future_to_obj = {executor.submit(self._download_object, obj): obj for obj in objects}
            for future in as_completed(future_to_obj):
                result = future.result()
                if result is not None:
                    all_data.extend(result if isinstance(result, list) else [result])
        
        # Save to file
        self._save_to_file(all_data, output_path, file_format)
        self.logger.info(f"Successfully downloaded {len(all_data)} articles to {output_path}")
        return output_path

    def _list_objects(self) -> List[Dict]:
        """List objects in S3 bucket"""
        objects = []
        paginator = self.s3.get_paginator('list_objects')
        try:
            for page in paginator.paginate(Bucket=self.config['bucket']):
                if 'Contents' in page:
                    objects.extend(page['Contents'])
            return objects
        except Exception as e:
            self.logger.error(f"Error listing objects: {str(e)}")
            raise
    
    def _download_object(self, obj: Dict) -> Optional[Union[Dict, List[Dict]]]:
        """Download and parse single S3 object"""
        try:
            response = self.s3.get_object(Bucket=self.config['bucket'], Key=obj['Key'])
            content = response['Body'].read().decode('utf-8')
            data = json.loads(content)
            metadata = response.get('Metadata', {})
            if isinstance(data, dict):
                data.update(metadata)
                return [data]
            elif isinstance(data, list):
                for item in data:
                    item.update(metadata)
                return data
        except Exception as e:
            self.logger.error(f"Error downloading {obj['Key']}: {str(e)}")
            return None
    
    def _is_in_date_range(self, ts: datetime, start: Optional[datetime], end: Optional[datetime]) -> bool:
        """Check if timestamp is within the date range"""
        return (not start or ts >= start) and (not end or ts <= end)
    
    def _save_to_file(self, data: List[Dict], output_path: str, file_format: str) -> None:
        """Save data to file"""
        df = pd.DataFrame(data)
        if file_format == 'csv':
            df.to_csv(output_path, index=False)
        elif file_format == 'json':
            df.to_json(output_path, orient='records', lines=True)
        else:
            raise ValueError(f"Unsupported file format: {file_format}")
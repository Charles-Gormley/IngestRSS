import boto3
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from collections import defaultdict

def get_s3_object_creation_dates(bucket_name):
    s3 = boto3.client('s3')
    creation_dates = []

    # List all objects in the bucket
    paginator = s3.get_paginator('list_objects_v2')
    for page in paginator.paginate(Bucket=bucket_name):
        for obj in page.get('Contents', []):
            creation_dates.append(obj['LastModified'].date())

    return creation_dates

def plot_creation_dates(dates):
    # Count objects created on each date
    date_counts = defaultdict(int)
    for date in dates:
        date_counts[date] += 1

    # Sort dates and get counts
    sorted_dates = sorted(date_counts.keys())
    counts = [date_counts[date] for date in sorted_dates]

    # Create the plot
    plt.figure(figsize=(15, 8))
    bars = plt.bar(sorted_dates, counts)
    plt.title('S3 Object Creation Dates')
    plt.xlabel('Date')
    plt.ylabel('Number of Objects Created')
    plt.xticks(rotation=45, ha='right')

    # Label each bar with its height
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                 f'{int(height)}',
                 ha='center', va='bottom')

    plt.tight_layout()

    # Save the plot
    plt.savefig('s3_object_creation_dates.png', dpi=300, bbox_inches='tight')
    print("Graph saved as 's3_object_creation_dates.png'")

def main():
    bucket_name = 'open-rss-articles-us-east-1'
    dates = get_s3_object_creation_dates(bucket_name)
    plot_creation_dates(dates)

if __name__ == "__main__":
    main()
# IngestRSS 🗞️💦

OpenRSS is an AWS-based RSS feed processing system that automatically fetches, processes, and stores articles from specified RSS feeds.




## Customization

- To modify the CloudFormation templates, edit the YAML files in `src/infra/cloudformation/`.
- To change the Lambda function's behavior, modify the Python files in `src/lambda_function/src/`.
- To add or remove RSS feeds, update the `rss_feeds.json` file.


## Monitoring
The Lambda function logs its activities to CloudWatch Logs. You can monitor the function's performance and any errors through the AWS CloudWatch console.

## Contributing
We are still working on a contribution framework. But they are more than welcome! Feel free to submit a PR which will be approved by the team.
Check

## License
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

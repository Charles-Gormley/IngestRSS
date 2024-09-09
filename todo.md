# 🚀 IngestRSS - 🗞️💵⚖️

![Header](wallpaper.png)

IngestRSS is an AWS-based RSS feed processing system that automatically fetches, processes, and stores articles from specified RSS feeds. This project is designed to support social scientists in progressing research on news and media.

## 🎯 Purpose

The primary goal of IngestRSS is to provide researchers with a robust, scalable solution for collecting and analyzing large volumes of news data. By automating the process of gathering articles from diverse sources, this tool enables social scientists to focus on their research questions and data analysis, rather than the complexities of data collection.

## 🚀 Getting Started

### Prerequisites

- Python 3.12
- AWS account with necessary permissions
- AWS CLI configured with your credentials

### Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/IngestRSS.git
   cd IngestRSS
   ```

2. Install required packages:
   ```
   python -m pip install -r requirements.txt
   ```

3. Set up your environment variables:
   - Find the file named `template.env` in your folder.
   - Make a copy of this file in the same folder.
   - Rename the copy to `.env` (make sure to include the dot at the start).
   - Open the `.env` file and fill in your information where you see `***`.
   
   Here's what you need to fill in:
   ```
   AWS_REGION=***
   AWS_ACCOUNT_ID=***
   AWS_ACCESS_KEY_ID=***
   AWS_SECRET_ACCESS_KEY=***
   ```
   
   The other settings in the file are already set up for you, but you can change them if you need to.

4. Launch the application:
   ```
   python launch.py
   ```

## 🛠️ Configuration

- RSS feeds can be modified in the `rss_feeds.json` file.
- CloudFormation templates are located in `src/infra/cloudformation/`.
- Lambda function code is in `src/lambda_function/src/`.

## 📊 Monitoring

The Lambda function logs its activities to CloudWatch Logs. You can monitor the function's performance and any errors through the AWS CloudWatch console.

## 🤝 Contributing

We welcome contributions! Please feel free to submit a Pull Request.

## 📄 License

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📁 Project Structure

```
CHANGELOG.md
├── CONTRIBUTING.md
├── README.md
├── launch.py
├── requirements.txt
├── rss_feeds.json
├── src
│   ├── article_storage
│   ├── feed_management
│   ├── infra
│   │   ├── cloudformation
│   │   ├── lambdas
│   │   │   ├── RSSFeedProcessorLambda
│   │   │   ├── RSSQueueFiller
│   │   │   └── lambda_utils
│   ├── launch
│   └── utils
├── template.env
├── tmp
├── todo.md
├── tree.md
└── wallpaper.png
```

## 🙏 Acknowledgements

This project is made possible thanks to the contributions of researchers and developers committed to advancing the field of media studies and social science research.
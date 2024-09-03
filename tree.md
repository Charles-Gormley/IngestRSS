.
├── README.md
├── launch.py
├── requirements.txt
├── rss_feeds.json
├── src
│   ├── article_storage
│   │   ├── __pycache__
│   │   │   └── initialize.cpython-310.pyc
│   │   ├── create_index.py
│   │   └── initialize.py
│   ├── feed_management
│   │   ├── __pycache__
│   │   │   └── upload_rss_feeds.cpython-312.pyc
│   │   └── upload_rss_feeds.py
│   ├── infra
│   │   ├── __pycache__
│   │   │   └── deploy_infrastructure.cpython-312.pyc
│   │   ├── cloudformation
│   │   │   ├── dynamo.yaml
│   │   │   ├── lambda_role.yaml
│   │   │   ├── rss_lambda_stack.yaml
│   │   │   ├── s3.yaml
│   │   │   └── sqs.yaml
│   │   ├── deploy_infrastructure.py
│   │   ├── lambdas
│   │   │   ├── RSSFeedProcessorLambda
│   │   │   │   ├── __pycache__
│   │   │   │   │   ├── deploy_lambda.cpython-310.pyc
│   │   │   │   │   ├── deploy_lambda.cpython-311.pyc
│   │   │   │   │   ├── deploy_lambda.cpython-312.pyc
│   │   │   │   │   ├── deploy_rss_feed_lambda.cpython-312.pyc
│   │   │   │   │   ├── update_env_vars.cpython-310.pyc
│   │   │   │   │   ├── update_lambda_env_vars.cpython-310.pyc
│   │   │   │   │   ├── update_lambda_env_vars.cpython-311.pyc
│   │   │   │   │   └── update_lambda_env_vars.cpython-312.pyc
│   │   │   │   ├── deploy_rss_feed_lambda.py
│   │   │   │   ├── layers
│   │   │   │   │   └── requirements.txt
│   │   │   │   └── src
│   │   │   │       ├── __pycache__
│   │   │   │       │   └── utils.cpython-310.pyc
│   │   │   │       ├── article_extractor.py
│   │   │   │       ├── config.py
│   │   │   │       ├── data_storage.py
│   │   │   │       ├── exceptions.py
│   │   │   │       ├── feed_processor.py
│   │   │   │       ├── lambda_function.py
│   │   │   │       ├── metrics.py
│   │   │   │       └── utils.py
│   │   │   ├── RSSQueueFiller
│   │   │   │   ├── deploy_sqs_filler_lambda.py
│   │   │   │   └── lambda
│   │   │   │       └── lambda_function.py
│   │   │   └── lambda_utils
│   │   │       ├── __pycache__
│   │   │       │   └── update_lambda_env_vars.cpython-312.pyc
│   │   │       ├── lambda_layer
│   │   │       │   └── lambda_layer_cloud9.sh
│   │   │       └── update_lambda_env_vars.py
│   │   └── tmp
│   └── utils
│       ├── __pycache__
│       │   ├── create_lambda_layer.cpython-310.pyc
│       │   ├── create_lambda_layer.cpython-311.pyc
│       │   ├── create_lambda_layer.cpython-312.pyc
│       │   ├── create_s3_bucket.cpython-310.pyc
│       │   ├── kms_update.cpython-310.pyc
│       │   ├── kms_update.cpython-311.pyc
│       │   ├── kms_update.cpython-312.pyc
│       │   ├── retry_logic.cpython-310.pyc
│       │   ├── retry_logic.cpython-311.pyc
│       │   ├── retry_logic.cpython-312.pyc
│       │   ├── upload_rss_feeds.cpython-310.pyc
│       │   ├── upload_rss_feeds.cpython-311.pyc
│       │   └── upload_rss_feeds.cpython-312.pyc
│       └── retry_logic.py
├── template.env
├── tmp
├── todo.md
└── tree.md

# After Public Launch
* Monthly Kaggle Dataset Publishing.

* Vector Database Initialization at earlier phase. [ Done ]
* Test out Vector Databases at Small Scale. 
    * [x] Testing 
        * [x] Fix OpenAI Error.
        * [x] Fix Pinecone Error
        * [x] Fix input error.
    * [ ] Let it run for a day
        * [x] Check Open AI Bill
        * [x] Check Vector Database Bill
        * [ ] Figure out Vector Database Bug. 
    * [ ] Figure out best way to store articles since metadata or in S3. 
* [ ] Decreae the cost of cloudwatch Logs
* [ ] Test out Vector Databases at Scale. 
* [ ] Add in text cleaning before after ingesting article but before storage.
* [ ] Automate the monthly data ingestion job
* [ ] Lambda Optimization


* Monthly ingestion job
* Protocol for annotating data. 
    * [ ] DSPy Integration
    * [ ] LLMRouter integration
    * [ ] Main topic/Category ( list )
    * [ ] Writing Stley ( e.g. Informal, professional, etc...)
    * [ ] Promotional Material ( 0=Not Promotional, 1=Promotional)
    * [ ] Stuff that is news ( 0= Not News, 1=News)
    * [ ] Stuff that is news but like a list of news topics. ( 0=Opposite,  1=News Topic Lists)
    * [ ] Annotating Entities ( List of Key entities with entity specific sentiment )
    * [ ] List of Major Events ( e.g. Ukraine War, Israel Palestine, etc... )
    * [ ] List of Minor Event ( e.g. Specific Battle, Court Case step, etc..)
    * [ ] Novelty Factor ( Scale from 0(Not Interesting) -> 100(Interesting))
    * [ ] Annotating Podcast Scripts or Video Scripts ( 0=is not a script, 1=Is a script)
    * [ ] Political Quadrant ( Or that eight dimensional thing that guy had. )
Also we need to specify a consistent output format

* Estimation Algorithm for annotation cost. 
* Open Source Protocol for running this. 

graph-rag-telecom/
│
├── README.md
├── requirements.txt
├── .env                  # chứa URI Neo4j, password, OpenAI key, vLLM URL...
├── config/
│   ├── neo4j.yaml        # config kết nối Neo4j
│   ├── rag.yaml          # config weight, top-k, embedding model...
│   ├── schema.json       # schema của 4 json file
│   └── logging.conf
│
├── data/
│   ├── raw/              # 4 file JSON gốc
│   │   ├── Subscriber.json
│   │   ├── BalanceAgent.json
│   │   ├── Product.json
│   │   └── Group.json
│   ├── processed/        # data đã làm sạch
│   └── graph/            # export graph từ Neo4j (tuỳ chọn)
│
├── notebooks/
│   ├── 01-explore-json.ipynb         # khảo sát file json & schema
│   ├── 02-visualize-kg.ipynb         # visualize KG bằng Neo4j GDS
│   ├── 03-embedding-test.ipynb       # test embedding
│   └── 04-community-detection.ipynb
│
├── src/
│   ├── etl/
│   │   ├── loader.py                 # load json → python dict
│   │   ├── transformer.py            # validate & làm sạch
│   │   ├── neo4j_writer.py           # viết dữ liệu vào neo4j
│   │   └── run_etl.py                # runner ETL chính
│   │
│   ├── graph/
│   │   ├── schema.py                 # định nghĩa Node/Edge
│   │   ├── embeddings.py             # fastRP/node2vec/LLM embedding
│   │   ├── summary_generator.py      # community summary (GraphRAG)
│   │   └── graph_index.py            # build graph index tổng hợp
│   │
│   ├── ner/
│   │   ├── telecom_ner.py            # NER: msisdn, productId...
│   │   └── pattern_matcher.py        # regex fallback
│   │
│   ├── retrieval/
│   │   ├── cypher_queries.py         # các câu Cypher chuẩn
│   │   ├── subgraph_retrieval.py     # query subgraph theo entity
│   │   ├── context_builder.py        # convert subgraph → text chunk
│   │   └── reranker.py               # optional
│   │
│   ├── llm/
│   │   ├── prompt.py                 # system prompt + templates
│   │   ├── llm_client.py             # openai/vllm
│   │   └── reasoning.py              # combine context + question
│   │
│   ├── api/
│   │   └── server.py                 # FastAPI endpoint cho UI
│   │
│   ├── utils/
│   │   ├── logger.py
│   │   ├── helpers.py
│   │   └── validators.py
│   │
│   └── ui/
│       └── streamlit_app.py          # giao diện chatbot
│
├── tests/
│   ├── test_etl.py
│   ├── test_retrieval.py
│   ├── test_llm.py
│   └── test_ner.py
│
└── docker/
    ├── Dockerfile
    └── docker-compose.yaml           # chứa neo4j + app

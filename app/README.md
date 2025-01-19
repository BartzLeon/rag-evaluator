# Eval Process

## Models
test-set generation model default gpt-3.5-turbo
vektor store embeddings model default text-embedding-3-large

model to be tested

model evaluating the answers


## Documents
- create from input
- saved in pkl

## Vektor store
- DocArrayInMemorySearch
- - created from docs

- ChromaDBFactory
- - needs to be created with name
- - or loaded by name



```bash
curl -X POST "http://localhost:9876/process/" \
-H "Content-Type: application/json" \
-d '{
"model_type": "openai",
"dataset": 1,
"testset": 1
}'
```

<br>

```bash
curl -X POST "http://localhost:9876/documents/" \
-H "Content-Type: application/json" \
-d '{
    "name": "web-scraping-005",
    "sources": [
        {
            "name": "products",
            "type": "url",
            "url": "https://web-scraping.dev/products"
        },
        {
            "name": "reviews",
            "type": "url",
            "url": "https://web-scraping.dev/reviews"
        }
    ]
}'
```

```bash
curl -X POST "http://localhost:9876/testsets/" \
-H "Content-Type: application/json" \
-d '{
    "model_type": "gpt-3.5-turbo",
    "document": 1,
    "name": "web-scraping-001-001"
}'
```
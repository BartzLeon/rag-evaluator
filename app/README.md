Eval Process

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
"dataset": 9,
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
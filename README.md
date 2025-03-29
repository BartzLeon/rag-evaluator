# Eval Process

## Models
- test-set generation model default gpt-4-turbo
- vektor store embeddings model default text-embedding-3-large
- model to be tested
- model evaluating the answers default gpt-4-turbo

## Questions
How many parameters do we want to use?
do we want to use multiple judges?
What kind of vectore stores do we want to use?
https://docs.ragas.io/en/stable/howtos/customizations/testgenerator/_persona_generator/
Do want to detect hallucinations?

---

## Documents
- create from input
- saved in pkl

## Vektor store
- DocArrayInMemorySearch
- - created from docs

- ChromaDBFactory
- - needs to be created with name
- - or loaded by name

---


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
    "model_type": "deepseek-r1:7b",
    "document": 1,
    "name": "web-scraping-001-001",
    "num_questions": 100,
    "agent_description": "A chatbot answering questions about products and reviews"
}'
```

    
```bash
curl -X POST "http://localhost:9876/process/" \
-H "Content-Type: application/json" \
-d '{
"model_type": "deepseek",
"testset": 1
}'
```

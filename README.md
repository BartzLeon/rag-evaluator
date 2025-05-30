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
    "name": "web-scraping-006",
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
    ],
    "embedding_model": "openai/text-embedding-3-large"
}'

# Create a document with uploaded files (using JSON body)
curl -X POST "http://localhost:9876/documents/" \
-H "Content-Type: application/json" \
-d '{
    "name": "document-with-files",
    "embedding_model": "ollama/nomic-embed-text:latest",
    "file_ids": [1, 2]
}'
```

openai/gpt-4-turbo
ollama/deepseek-r1:7b

```bash
curl -X POST "http://localhost:9876/testsets/" \
-H "Content-Type: application/json" \
-d '{
    "model_type": "openai/gpt-4-turbo",
    "embedding_model": "openai/text-embedding-3-large",
    "document": 17,
    "name": "story-001-001",
    "num_questions": 10,
    "agent_description": "A chatbot answering questions about a story"
}'
```

```bash
curl -X POST "http://localhost:9876/testsets/" \
-H "Content-Type: application/json" \
-d '{
    "model_type": "ollama/deepseek-r1:32b",
    "embedding_model": "ollama/nomic-embed-text:latest",
    "document": 135,
    "name": "d4f-100doc-odeep32bnomic-001-001",
    "num_questions": 50,
    "agent_description": "Ein Chatbot welcher Fragen für das Startup Develop 4 Future beantwortet."
}'
```

    
```bash
curl -X POST "http://localhost:9876/process/" \
-H "Content-Type: application/json" \
-d '{
"llm_to_be_evaluated_type": "ollama/deepseek-r1:32b",
"judge_llm_type": "ollama/deepseek-r1:32b",
"testset": 36
}'
```

```bash
curl -X POST "http://localhost:9876/process/" \
-H "Content-Type: application/json" \
-d '{
"llm_to_be_evaluated_type": "openai/gpt-4-turbo",
"judge_llm_type": "openai/gpt-4-turbo",
"testset": 36
}'
```

# models/embeddings needed
## Documents
1. Vectorstore

## Testset
1. KnowledgeBase for question generation

## Eval
1. Vectorstore
2. KnowledgeBase
3. Model to be evaluated
4. Evaluator


Embedding dimensions must be the same so we will take the same embeddings from the documents in Testsets and Evaluation

Vectorstore => embeddings
KnowledgeBase => llm & embedding
Evaluator => llm
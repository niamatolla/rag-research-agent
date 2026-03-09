.PHONY: install install-dev test smoke-openai smoke-ingestion smoke-retrieval smoke-llm smoke-all

install:
	python3 -m pip install -r requirements.txt

install-dev:
	python3 -m pip install -r requirements-dev.txt

test:
	python3 -m pytest

smoke-openai:
	python3 -m tests.smoke_openai

smoke-ingestion:
	python3 -m tests.smoke_ingestion

smoke-retrieval:
	python3 -m tests.smoke_retrieval

smoke-llm:
	python3 -m tests.smoke_llm_answer

smoke-all: smoke-openai smoke-ingestion smoke-retrieval smoke-llm

"""Entry point for the online question-answering pipeline.

Orchestrates:

user query -> retrieval -> prompt construction -> GPT-4o answer generation -> displayed results
"""

from __future__ import annotations

import argparse

from config.settings import settings
from llm.answer import SYSTEM_PROMPT, build_prompt
from llm.openai_client import OpenAIClient
from retrieval.search import search_chunks


def run_online_qa(query: str, top_k: int = 5) -> dict:
	"""Run the end-to-end online QA flow for one user query."""

	if not isinstance(query, str) or not query.strip():
		raise ValueError("question must be a non-empty string")

	if top_k <= 0:
		raise ValueError("top_k must be greater than 0")

	clean_query = query.strip()
	retrieved_chunks = search_chunks(clean_query, top_k=top_k)

	if not retrieved_chunks:
		return {
			"answer": "I could not find relevant context to answer this question.",
			"sources": [],
		}

	prompt = build_prompt(clean_query, retrieved_chunks)
	client = OpenAIClient().get_client()

	response = client.chat.completions.create(
		model=settings.AZURE_OPENAI_CHAT_DEPLOYMENT,
		messages=[
			{"role": "system", "content": SYSTEM_PROMPT.strip()},
			{"role": "user", "content": prompt},
		],
		temperature=0.0,
		max_tokens=300,
	)

	answer_text = response.choices[0].message.content or ""
	answer_text = answer_text.strip() or "The answer is not available in the provided context."

	sources = [
		{
			"document_id": chunk["document_id"],
			"chunk_id": chunk["chunk_id"],
		}
		for chunk in retrieved_chunks
	]

	return {
		"answer": answer_text,
		"sources": sources,
	}


def parse_args() -> argparse.Namespace:
	"""Parse CLI arguments for the QA entry point."""

	parser = argparse.ArgumentParser(description="Run online RAG question answering.")
	parser.add_argument(
		"--question",
		required=True,
		type=str,
		help="Question to ask the RAG system.",
	)
	parser.add_argument(
		"--top-k",
		default=5,
		type=int,
		help="Number of chunks to retrieve from Azure AI Search (default: 5).",
	)
	return parser.parse_args()


def main() -> None:
	"""CLI entry point."""

	args = parse_args()
	result = run_online_qa(query=args.question, top_k=args.top_k)

	print("Question:", args.question)
	print("\nAnswer:")
	print(result["answer"])
	print("\nSources:")

	if not result["sources"]:
		print("- None")
		return

	for source in result["sources"]:
		print(f"- {source['document_id']} - chunk {source['chunk_id']}")


if __name__ == "__main__":
	main()

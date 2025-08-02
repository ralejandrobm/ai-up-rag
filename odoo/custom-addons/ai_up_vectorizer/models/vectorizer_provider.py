from odoo import models, fields
from typing import Optional

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import VectorStore


stores = {}


class AiUpVectorizerProvider(models.Model):
    _name = "ai_up.vectorizer.provider"
    _description = "AI UP Vectorizer Provider"
    _order = "id"

    name = fields.Char(string="Name", required=True, translate=True)
    slug = fields.Char(
        string="Slug",
        required=True,
        translate=False,
        index=True,
        copy=False,
    )
    code = fields.Selection(
        string="Code",
        help="The technical code of this vectorizer provider.",
        selection=[("none", "No Provider Set")],
        default="none",
        required=True,
    )

    _sql_constraints = [("slug_unique", "unique(slug)", "Slug must be unique.")]

    def _get_embeddings(self) -> Embeddings:
        """Initialize HuggingFaceEmbeddings only once
        :param collection: The collection name.
        :return: Embeddings object.
        """
        raise NotImplementedError

    def _get_vector_store(self, collection: str, embeddings: Embeddings) -> VectorStore:
        """Initialize PGVector only once

        :param collection: The collection name.
        :return: Vector store object.
        """
        raise NotImplementedError

    def _get_cached_vector_store(self, collection: str) -> VectorStore:
        """
        Get the cached vector store.

        :param collection: The collection name.
        :return: Vector store object.
        """
        if collection not in stores:
            embeddings = self._get_embeddings()
            vector_store = self._get_vector_store(collection, embeddings)
            stores[collection] = vector_store

        return stores[collection]

    def upsert_documents(self, *, collection: str, documents: list[Document]):
        """
        Inserts or updates documents in the pg_vector index.

        :param collection: The collection name.
        :param documents: List of dictionaries representing the documents.
        :return: List of document ids.
        """
        vector_store = self._get_cached_vector_store(collection)

        # add or update documents with the given ids
        ids = vector_store.add_documents(
            documents=documents["documents"],
            ids=documents["ids"],
        )

        return ids

    def delete_documents(self, *, collection: str, ids: list[str]):
        """
        Deletes documents from the pg_vector index.

        :param collection: The collection name.
        :param ids: List of document ids.
        :return: True if the operation was successful.
        """
        vector_store = self._get_cached_vector_store(collection)
        return vector_store.delete(ids=[str(id) for id in ids])

    def similarity_search(
        self,
        *,
        collection: str,
        query: str,
        documents_number: int = 4,
        metadata_filter: Optional[dict] = None,
    ):
        """
        Performs a semantic search on the documents using pg_vector.

        :param collection: The collection name.
        :param query: The search query string.
        :param documents_number: The number of search results to return.
        :param filter: Optional Filter by metadata. Defaults to None.
        :return: List of search results.
        """
        vector_store = self._get_cached_vector_store(collection)
        return vector_store.similarity_search(
            query,
            k=documents_number,
            filter=metadata_filter,
        )

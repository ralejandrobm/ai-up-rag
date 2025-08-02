from odoo import models, api

from typing import Optional
import logging

_logger = logging.getLogger(__name__)


class AiUpVectorizerMixin(models.AbstractModel):
    _name = "ai_up.vectorizer.mixin"
    _description = "AI UP Vectorizer Mixin"

    # TODO: Implement delete and unlink methods

    @api.model_create_multi
    def create(self, values_list):
        records = super().create(values_list)

        self._generate_embeddings(
            records=[records] if not isinstance(records, list) else records,
        )
        return records

    def write(self, values):
        records = super().write(values)

        self._generate_embeddings(
            records=[self] if not isinstance(self, list) else self,
        )
        return records

    def unlink(self):
        records = super().unlink()

        self._delete_embeddings(
            records=[self] if not isinstance(self, list) else self,
        )

        return records

    def _ensure_definitions(self):
        if not hasattr(self, "_get_provider"):
            self._report_event("Method '_get_provider' not implemented")
            return False

        if not hasattr(self, "_generate_documents"):
            self._report_event("Method '_generate_documents' not implemented")
            return False

        if not hasattr(self, "_get_collection_name"):
            self._report_event("Method '_get_collection_name' not implemented")
            return False

        return True

    def _generate_embeddings(self, *, records: list):
        if not self._ensure_definitions():
            return

        collection = self._get_collection_name()
        vectorizer_provider = self._get_provider()

        if not vectorizer_provider:
            self._report_event("Vectorizer provider not found")
            return

        documents = self._generate_documents(records)
        ids = vectorizer_provider.upsert_documents(
            collection=collection,
            documents=documents,
        )

        return ids

    def _delete_embeddings(self, *, records: list):
        if not self._ensure_definitions():
            return

        collection = self._get_collection_name()
        vectorizer_provider = self._get_provider()

        if not vectorizer_provider:
            self._report_event("Vectorizer provider not found")
            return

        ids = [record.id for record in records]
        vectorizer_provider.delete_documents(
            collection=collection,
            ids=ids,
        )

        return True

    @api.model
    def similarity_search(
        self,
        *,
        query: str,
        documents_number: int = 4,
        metadata_filter: Optional[dict] = None,
    ):
        """
        Performs a semantic search on the documents using pg_vector.

        :param query: The query string.
        :param documents_number: The number of documents to return.
        :param metadata_filter: The metadata filter.
        :return: List of document ids.
        """
        if not self._ensure_definitions():
            return

        collection = self._get_collection_name()
        vectorizer_provider = self._get_provider()

        if not vectorizer_provider:
            self._report_event("Vectorizer provider not found")
            return

        return vectorizer_provider.similarity_search(
            collection=collection,
            query=query,
            documents_number=documents_number,
            metadata_filter=metadata_filter,
        )

    def _get_provider(self):
        """
        Get the vectorizer provider.

        :return: Vectorizer provider object.
        """
        raise NotImplementedError

    def _generate_documents(self, instances) -> dict:
        """
        Generate documents from instances.

        :param instances: Instances to generate documents from.
        :return: Dictionary containing the documents and their ids.

        Example:
        {
            'documents': [
                Document(
                    page_content='Title: "Title". Description: "Description".',
                    metadata={
                        'id': 1,
                        'title': 'Title',
                        'description': 'Description',
                    }
                )
            ],
            'ids': [1]
        }
        """
        raise NotImplementedError

    def _get_collection_name(self) -> str:
        """
        Get the collection name.

        :return: Collection name.
        """
        raise NotImplementedError

    def _report_event(self, message):
        _logger.error(f"[⚠️] {message}")
        return False

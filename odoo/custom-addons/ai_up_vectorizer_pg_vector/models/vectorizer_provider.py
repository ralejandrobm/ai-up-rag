import logging
from odoo import models, fields
from odoo import tools

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.embeddings import Embeddings
from langchain_postgres.vectorstores import PGVector

_logger = logging.getLogger(__name__)


class AiUpVectorizerProvider(models.Model):
    _inherit = "ai_up.vectorizer.provider"

    code = fields.Selection(
        selection_add=[("pg_vector", "PG Vector")],
        ondelete={"pg_vector": "set default"},
    )
    pg_vector_same_db = fields.Boolean(
        string="Use Same DB for pg_vector",
        default=True,
        required=True,
        help="If checked, pg_vector will use the same database connection.",
    )
    pg_vector_host = fields.Char(
        string="pg_vector Host",
        help="Host for pg_vector if not using the same database.",
    )
    pg_vector_port = fields.Char(
        string="pg_vector Port",
        help="Port for pg_vector if not using the same database.",
    )
    pg_vector_user = fields.Char(
        string="pg_vector User", help="User for connecting to the pg_vector database."
    )
    pg_vector_password = fields.Char(
        string="pg_vector Password",
        help="Password for the pg_vector database.",
    )

    def _get_embeddings(self) -> HuggingFaceEmbeddings:
        if self.code != "pg_vector":
            return super()._get_embeddings()

        return HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-mpnet-base-v2",
            cache_folder="/var/lib/ai-models",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": False},
        )

    def _get_vector_store(self, collection: str, embeddings: Embeddings) -> PGVector:
        if self.code != "pg_vector":
            return super()._get_embeddings()

        connection = None

        if self.pg_vector_same_db:
            connection = "postgresql+psycopg2://{}:{}@{}:{}/{}".format(
                tools.config["db_user"],
                tools.config["db_password"],
                tools.config["db_host"],
                tools.config["db_port"],
                self.env.cr.dbname,
            )
        else:
            connection = "postgresql+psycopg2://{}:{}@{}:{}/{}".format(
                self.pg_vector_user,
                self.pg_vector_password,
                self.pg_vector_host,
                self.pg_vector_port,
                self.env.cr.dbname,
            )

        return PGVector(
            embeddings=embeddings,
            collection_name=collection,
            connection=connection,
            use_jsonb=True,
        )

{
    "name": "AI UP Vectorizer Pg Vector",
    "version": "18.0.0.1.0",
    "summary": "Integrates pg_vector functionality with AI UP Vectorizer Provider",
    "description": """
        This module extends the AI UP Vectorizer Provider to integrate with pg_vector.
        It adds additional configuration fields for pg_vector and implements the upsert and semantic search methods.
    """,
    "author": "wrsbyte",
    "website": "https://wrsbyte.com",
    "category": "Tools",
    "depends": ["ai_up_vectorizer"],
    "data": [
        "views/vectorizer_provider_views.xml",
    ],
    "demo": [],
    "installable": True,
    "application": False,
    "auto_install": False,
    "license": "LGPL-3",
}

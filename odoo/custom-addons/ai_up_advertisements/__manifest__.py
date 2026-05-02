{
    "name": "AI UP Advertisements",
    "version": "18.0.0.1.0",
    "summary": "Manage advertisements and interested parties",
    "description": """
        Advanced advertisement management system with sequence tracking
        and interested party management
    """,
    "author": "wrsbyte",
    "website": "https://wrsbyte.com",
    "category": "Tools",
    "depends": ["base", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "views/interested_party_views.xml",
        "views/advertisement_views.xml",
        "data/advertisement_sequence_data.xml",
    ],
    "demo": [],
    "installable": True,
    "application": False,
    "auto_install": False,
    "license": "LGPL-3",
}

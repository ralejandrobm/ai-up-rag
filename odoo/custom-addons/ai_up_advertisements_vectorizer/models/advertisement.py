from odoo import models

from langchain_core.documents import Document


class AiUpAdvertisement(models.Model):
    _name = "ai_up.advertisement"
    _inherit = [
        "ai_up.advertisement",
        "ai_up.vectorizer.mixin",
    ]

    def _get_provider(self):
        provider = "advertisement-pg-vector"
        return self.env["ai_up.vectorizer.provider"].search(
            [("slug", "=", provider), ("code", "=", "pg_vector")], limit=1
        )

    def _generate_documents(self, instances):
        formatted_values = [
            {
                "id": instance.id,
                "title": instance.title,
                "description": instance.description,
                "interested_party": instance.interested_parties_ids.mapped("name"),
                "create_date": instance.create_date.strftime("%Y-%m-%d %H:%M:%S"),
                "write_date": instance.write_date.strftime("%Y-%m-%d %H:%M:%S"),
            }
            for instance in instances
        ]

        return {
            "documents": [
                Document(
                    page_content='Title: "{}". Description: "{}". Some interested parties: "{}". Was created on: "{}". Last updated on: "{}".'.format(
                        v["title"],
                        v["description"],
                        ", ".join(v["interested_party"]),
                        v["create_date"],
                        v["write_date"],
                    ),
                    metadata=v,
                )
                for v in formatted_values
            ],
            "ids": [formatted_value["id"] for formatted_value in formatted_values],
        }

    def _get_collection_name(self):
        return "ai_up_advertisement_vectors"

from odoo import models, fields


class AiUpInterestedParty(models.Model):
    _name = "ai_up.interested.party"
    _description = "Interested Party"

    name = fields.Char(string="Name", required=True)
    active = fields.Boolean(string="Active", default=True)

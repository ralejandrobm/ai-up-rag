from odoo import models, fields, api, _


class AiUpAdvertisement(models.Model):
    _name = "ai_up.advertisement"
    _description = "Advertisement"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "sequence_number DESC"

    sequence_number = fields.Char(
        string="Order Reference",
        required=True,
        readonly=True,
        copy=False,
        default=lambda self: _("New"),
    )
    title = fields.Char(string="Title", required=True, tracking=True)
    description = fields.Text(string="Description", required=True, tracking=True)
    active = fields.Boolean(string="Active", default=True, tracking=True)
    interested_parties_ids = fields.Many2many(
        "ai_up.interested.party",
        string="Interested Parties",
        required=True,
        tracking=True,
    )

    @api.model_create_multi
    def create(self, values_list):
        for v in values_list:
            if v.get("sequence_number", _("New")) == _("New"):
                v["sequence_number"] = self.env["ir.sequence"].next_by_code(
                    "ai_up.advertisement"
                ) or _("New")

        return super().create(values_list)

    @api.constrains("interested_parties_ids")
    def _check_interested_parties(self):
        for record in self:
            if len(record.interested_parties_ids) != 0:
                continue

            raise models.ValidationError(
                _("An advertisement must have at least one interested party")
            )

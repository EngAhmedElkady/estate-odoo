from odoo import models,fields,api
from datetime import datetime, timedelta

class EstatePropertyOffer(models.Model):
    _name="estate.property.offer"

    price = fields.Float(string="Price")
    status = fields.Selection(
        [
            ("accepted", "Accepted"),
            ("refused", "Refused")
        ]
        ,
        string="Status",
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Partner",
    )
    property_id=fields.Many2one(
        comodel_name="estate.property",
        string="Property",
        ondelete="cascade",
        index=True
    )
   
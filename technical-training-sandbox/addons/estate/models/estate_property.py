from datetime import datetime, timedelta
from odoo import models, fields, api


class EstateProperty(models.Model):
    """
    This class represents a real estate property in the system.
    It contains various fields such as name, description, postcode, selling price, etc.
    """

    _name = "estate.property"
    _description = "Estate Property"

    name = fields.Char(string="Title", required=True, default="Unknown")
    description = fields.Text(string="Description")
    postcode = fields.Char(string="Postcode")
    selling_price = fields.Float(string="Selling Price", readonly=True, copy=False)
    date_availability = fields.Date(
        string="Available From",
        copy=False,
        default=lambda self: (datetime.today() + timedelta(days=90)).strftime(
            "%Y-%m-%d"
        ),
    )
    expected_price = fields.Float(string="Expected Price", required=True)
    bedrooms = fields.Integer(string="Bedrooms", default=2)
    living_area = fields.Integer(string="Living Area")
    facades = fields.Integer(string="Facades")
    garage = fields.Boolean(string="Garages", default=False)
    garden = fields.Boolean(string="Garden", default=False)
    garage_area = fields.Integer(string="Garage Area")
    total_area = fields.Integer(string="Total Area", compute="_compute_total_area")
    property_type_id = fields.Many2one(
        comodel_name="estate.property.type",
        string="Property Type",
    )
    buyer_id = fields.Many2one(comodel_name="res.partner", string="Buyer", index=True)
    seller_id = fields.Many2one(
        "res.users",
        string="Salesperson",
        index=True,
        tracking=True,
        default=lambda self: self.env.user,
    )
    tag_ids = fields.Many2many(
        comodel_name="estate.property.tag",
        relation="property_tag_rel",
        column1="property_id",
        column2="tag_id",
        string="Tags",
    )
    offer_ids = fields.One2many(
        comodel_name="estate.property.offer",
        inverse_name="property_id",
        string="Offers",
    )
    garage_orientation = fields.Selection(
        [
            ("north", "North"),
            ("south", "South"),
            ("east", "East"),
            ("west", "West"),
        ]
    )
    last_seen = fields.Datetime(string="Last Seen", default=lambda self: datetime.now())
    active = fields.Boolean(string="Active", default=False, reversed=True)
    status = fields.Selection(
        [
            ("new", "New"),
            ("sold", "Sold"),
            ("offer received,", "Offer Received"),
            ("offer accepted", "Offer Accepted"),
            ("cancelled", "Cancelled"),
        ],
        required=True,
        default="new",
        copy=False,
    )
    best_price = fields.Float(
        string="Best Offer", compute="_compute_best_price", default=0
    )

    @api.model
    def search(self, args, offset=0, limit=None, order=None):
        """
        Overrides the search method to only return active properties.
        """
        args += [("active", "=", True)]
        return super(EstateProperty, self).search(
            args, offset=offset, limit=limit, order=order
        )

    @api.depends("living_area", "facades")
    def _compute_total_area(self):
        """
        This method computes the total area by adding the living area and facades.
        """
        for rec in self:
            rec.total_area = rec.living_area + rec.facades

    @api.depends("offer_ids.price")
    def _compute_best_price(self):
        for rec in self:
            max_price=0
            for offer in rec.offer_ids:
                if offer.price > max_price:
                    max_price = offer.price
            rec.best_price = max_price

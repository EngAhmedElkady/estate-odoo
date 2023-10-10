from odoo.exceptions import ValidationError
from odoo import api, fields, models


class CustomerContract(models.Model):
    _name = "customer.contract"
    _description = "Customer Contract"

    customer = fields.Many2one(
        comodel_name="res.partner", string="Customer", required=True
    )
    start_date = fields.Date(string="Start Date",required=True)
    end_date = fields.Date(string="End Date", required=True)
    price = fields.Float(string="Price", required=True)
    average_price = fields.Float(string="Average Price",compute="_compute_average_price")
    status = fields.Selection(
        [
            ("draft", "Draft"),
            ("confirmed", "Confirmed"),
            ("ended", "Ended"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",required=True
    )
    last_change_status_by = fields.Many2one('res.users', string='Last Change Status By')

    @api.constrains("customer")
    def _check_customer_contract(self):
        for record in self:
            if self.search_count([("customer", "=", record.customer.id)]) > 1:
                raise ValidationError("A contract already exists for this customer.")

    @api.constrains("start_date", "end_date")
    def _check_date(self):
        for record in self:
            if record.start_date > record.end_date:
                raise ValidationError("Start date must be before end date.")
            
    @api.onchange('status')
    def _onchange_status(self):
        self.last_change_status_by = self.env.user


    @api.onchange("start_date")
    def _compute_start_date(self):
        self.end_date=None

    @api.depends("start_date","end_date","price")
    def _compute_average_price(self):
        for record in self:
            if record.start_date and record.end_date :
                days_difference = (record.end_date - record.start_date).days
                record.average_price = record.price / days_difference
            else:
                record.average_price = 0.0

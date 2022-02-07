
from datetime import datetime
from email.policy import default
from odoo import models,fields,api
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError,UserError


    


class estatepropertymyproperty(models.Model):
       _name = 'estate.property.myproperty'
       _description = 'estate property myproperty'

       def _get_description(self) :
        if self.env.context.get('is_my_property') :
            return self.env.user.name + "'s property'"

       
       name = fields.Char(string="Name") 
       partner_name = fields.Many2one('res.partner',default=lambda self:self.env.user.partner_id.id,readonly=True)
       
       
       Description = fields.Text(default=_get_description)
       postcode = fields.Char()
       expected_price = fields.Float()
       selling_price = fields.Float()
       bedrooms = fields.Integer(default=True)
       living_area = fields.Integer()
       facades = fields.Integer()
       garage = fields.Boolean()
       garden = fields.Boolean()
       garden_area = fields.Integer()
       date_avaliable = fields.Date()

       garden_orientation = fields.Selection([
       
       ('north','North'),
       ('west','West'),
       ('east','East'),
       ('south','South')
       
       ])
       active = fields.Boolean(default=True)
       image = fields.Image()
       property_type_id = fields.Many2one('estate.property.type')
       salesman_id = fields.Many2one('res.users',default=lambda self:self.env.user)
       buyer_id = fields.Many2one('res.partner')
       property_tag_ids = fields.Many2many('estate.property.tag')
       property_offer_ids =  fields.One2many('estate.property.offer','property_id')
       total_area = fields.Integer(compute="_compute_area", inverse="_inverse_area")
       best_price =  fields.Float(compute="_compute_best_price")




class estatepropertytype(models.Model):
       _name = 'estate.property.type'
       _description = 'estate property type'

       name = fields.Char()
       property_id = fields.One2many('estate.property','property_type_id')

class estatepropertyoffer(models.Model):
       _name = 'estate.property.offer'
       _description = 'estate property offer'



       offer_person=fields.Many2one('res.partner')
       offer_date=fields.Date(default = lambda self:fields.datetime.now(),copy=False)
       offer_status=fields.Selection([('accept','Accept'),('reject','Reject')])
       price = fields.Float()
       status = fields.Selection([('accepted','Accepted'),('refuse','Refuse')])
       partner_id = fields.Many2one('res.partner')
       valid_days=  fields.Integer(default=7)
       valid_till= fields.Date(compute="_valid_till_date")


       property_id =  fields.Many2one('estate.property')
       def action_accepted(self):
        for record in self:
            record.status='accepted'

       def action_refused(self):
        for record in self:
            record.status='refused'

       @api.depends("offer_date","valid_days")
       def _valid_till_date(self):
              for record in self:
                     record.valid_till = fields.Date.add(record.offer_date,days=record.valid_days)



class estateproperty(models.Model):
       _name = 'estate.property'
       _inherit = 'portal.mixin'
       _description = 'estate property'
       
       name = fields.Char(required=True,string="Name",default="unknown")     
       description = fields.Text()
       postcode = fields.Char()
       date_avaliable = fields.Date()
       expected_price = fields.Float()
       selling_price = fields.Float()
       bedrooms = fields.Integer(default=True)
       living_area = fields.Integer()
       state=fields.Selection([('new','New'),('sold','Sold'),('cancel','Cancel')], default='new')

       facades = fields.Integer()
       garage = fields.Boolean()
       garden = fields.Boolean()
       garden_area = fields.Integer()
       garden_orientation = fields.Selection([
       
       ('north','North'),
       ('west','West'),
       ('east','East'),
       ('south','South')
       
       ])
       active = fields.Boolean(default=True)
       image = fields.Image()
       property_type_id = fields.Many2one('estate.property.type')
       salesman_id = fields.Many2one('res.users')
       buyer_id = fields.Many2one('res.partner')
       property_tag_ids = fields.Many2many('estate.property.tag')
       property_offer_ids =  fields.One2many('estate.property.offer','property_id')
       total_area = fields.Integer(compute="_compute_area",inverse="_inverse_area")
       best_price =  fields.Float(compute="_compute_best_price")
       
       def open_offers(self):
        view_id_all = self.env.ref('estate.estate_property_offer_tree').id
        return {
            "name":"Offers",
            "type":"ir.actions.act_window",
            "res_model":"estate.property.offer",
            "views":[[view_id_all, 'tree']],
            "target":"new",
            "domain": [('property_id', '=', self.id)]
            }

       def open_confirm_offers(self):
        view_id_accept = self.env.ref('estate.estate_property_offer_tree').id
        return {
            "name":"Offers",
            "type":"ir.actions.act_window",
            "res_model":"estate.property.offer",
            "views":[[view_id_accept, 'tree']],
            "domain": [('property_id', '=', self.id),('status','=','accepted')]
            }



       @api.onchange('garden')
       def _onchange_garden(self):
              for record in self:
                   if record.garden:
                      record.garden_area = 10
                      record.garden_orientation ='north'
                   else:
                       record.garden_area = 0
                       record.garden_orientation = None

       
       @api.depends('property_offer_ids.price')
       def _comput_best_price(self):
              for record in self:
                     max_price=0
                     for offer in record.property_offer_ids:
                            if offer.price > max_price:
                                   max_price=offer.price
                     record.best_price = max_price
       
       @api.depends('living_area','garden_area')
       def _compute_area(self):
              for record in self:
                     record.total_area = record.living_area + record.garden_area


       
       def _inverse_area(self):
           for record in self:
               record.living_area = record.garden_area = record.total_area / 2


       @api.constrains('living_area','garden_area')
       def check_garden_area(self):
              for record in self:
                  if record.living_area < record.garden_area:
                         raise ValidationError("garden can not be bigger then living area.")



       def action_sold(self):
           for record in self:
              if record.state=='cancel':
                 raise UserError("Cancel Property cannot be sold")
              record.state = 'sold'

       def action_cancel(self):
           for record in self:
              if record.state=='sold':
                  raise UserError("Sold Property cannot be canceled")
              record.state = 'cancel'
       
      
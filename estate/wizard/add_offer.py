from odoo import _,api,fields,models

class  Addoffer(models.Model):
    _name= "property.offer.wizard"
    _description = 'property offer wizard'

    price= fields.Char()
    partner = fields.Many2one('res.partner')
    status= fields.Selection([('accepted','Accepted'),('refuse','Refuse')])
   

    def action_make_offer(self):
        self.ensure_one()
        offer= self.env['estate.property.offer']
        activeIds=self.env.context.get('active_ids')
        data ={
            'price':self.price,
            'partner_id':self.partner.id,
            'status':self.status

        }
        for property in self.env['estate.property'].browse(activeIds):
            data['property_id']=property.id
            offer.create(data)
           
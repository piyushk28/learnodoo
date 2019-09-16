# -*- coding: utf-8 -*-

from flectra import models, fields, api



class Contact(models.Model):
    _inherit            = 'res.partner'
    type = fields.Selection(
    [('contact', 'Contact'),
        ('invoice', 'Invoice address'),
        ('delivery', 'Shipping address'),
        ('other', 'Other address'),
        ("private", "Private Address"),
        ("recycle","E-Waste Recycle Address")
    ], string='Address Type',
    default='contact',
    help="Used by Sales and Purchase Apps to select the relevant address depending on the context.")
    

class Truck(models.Model):
    _name           = 'recycle.truck_types'
    _description    = 'Define the Truck Types'

    name            = fields.Char(string='Truck Type')
    weight          = fields.Integer(string ='Weight')
    price           = fields.Integer(string='Price')


class Services(models.Model):
    _name           = 'recycle.service_types'
    _description    =  'Types of services provided for Inbound Orders'

    name            = fields.Char(string='Service Type')
    price           = fields.Integer(string='Cost')



class Packages(models.Model):
    _name           = 'recycle.package_types'
    _description    = 'Types of packages'

    name            = fields.Char(string= 'Package Type')


class InboundOrders(models.Model):
    _name               = 'recycle1.inbound_orders'
    _description        = 'Inbound Orders'

    name                = fields.Char()

    image               = fields.Binary()    
    customer            = fields.Many2one('res.partner', ondelete='set null', string='Customer')
    representative      = fields.Char(string='REP',required=True)
    warehouse_id        = fields.Many2one('stock.warehouse', ondelete = 'set null', string='Warehouse')
    # recycle_address     = fields.Selection(selection='_onchange_customer_recycle')
    # contact_address     = fields.Selection(selection='_onchange_customer_contact') 
    street              = fields.Char()
    street2             = fields.Char()
    # change_default=True
    zip                 = fields.Char()
    city                = fields.Char()
    state_id            = fields.Many2one("res.country.state", string='State', ondelete='restrict', domain="[('country_id', '=?', country_id)]")
    country_id          = fields.Many2one('res.country', string='Country', ondelete='restrict')

    logistic_type       = fields.Selection([
                                            ('self-trucking','Self Trucking'),
                                            ('common carrier','Common Carrier'),
                                            ('drop-shipping','Client Drop off')
                                            ],string='Logistic Types', required=True, default="self-trucking")

    state = fields.Selection([
                                ('draft', 'RFQ'),
                                ('sent', 'RFQ Sent'),
                                ('to approve', 'To Approve'),
                                ('purchase', 'Purchase Order'),
                                ('done', 'Locked'),
                                ('cancel', 'Cancelled')
    ], string='Status', readonly=True, index=True, copy=False, default='draft', track_visibility='onchange')

    bol                 = fields.Integer(string='BOL #')
    po                  = fields.Integer(string='PO #')
    billing             = fields.Char(default='Pending Settlement')
    internal_notes      = fields.Text(string="Internal Notes")
    service_type_id     = fields.Many2one('recycle.service_types',ondelete = 'set null', string="Service Type")

    # PickUp Details
    pickup_date_time    = fields.Datetime(string='Pickup Date-Time')
    truck_type_id       = fields.Many2one('recycle.truck_types',ondelete = 'set null',string='Truck Type')

    # Contact Details
    onside_contact_id           = fields.Many2one('res.partner',string='Onside Contact', ondelete='set null', required=True)
    alternative_contact_id      = fields.Many2one('res.partner', string='Alternative Contact', ondelete='set null', required= False)

    #Address Details
    # pickup_location     = fields.

    # Estimated Materials and Weights

    pallet_count        = fields.Integer(string='Pallet Count')
    total_weight        = fields.Integer(string='Total Weight  (Lbs)')
    package_type_id     = fields.Many2one('recycle.package_types',ondelete='set null',string='Package Type')
    condition           = fields.Selection([
                                            ('new commercial goods','New Commercial Goods'),
                                            ('used commercial goods','Used Commercial Goods'),
                                            ('old products','Old Products')
                                            ])
    dimensions_length            = fields.Integer(string='Length')
    dimensions_width             = fields.Integer(string='Width')
    dimensions_height            = fields.Integer(string='Height')

    # Order Lines

    order_lines         = fields.One2many("recycle.inbound_orders.lines","line_id","Order Lines", auto_join=True)
    
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('recycle1.inbound_orders') or '/'
            print('name is' + vals['name'])
        return super(InboundOrders, self).create(vals)

    @api.multi
    def get_report(self):
        # self.write({'state': "sent"})
        return self.env.ref('recycle.inbound_order_quotation').report_action(self)


    def send_email_quotation(self):
        self.ensure_one()
        ir_model_data   =self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('recycle', 'inbound_quotation_email_template')[1]
        except ValueError:
            template_id = False

        print(template_id)
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict(self.env.context or {})

        # email_temp = self.env.ref("recycle.inbound_quotation_email_template")
        # self.env['mail.template'].browse(email_temp.id).send_mail(self.id)

        ctx = {
        'default_model': 'recycle1.inbound_orders',
        'default_res_id': self.ids[0],
        'default_use_template': bool(template_id),
        'default_template_id': template_id,
        'default_composition_mode': 'comment',
        'mark_so_as_sent': True,
        'force_email': True
        }
        return {
        'type': 'ir.actions.act_window',
        'view_type': 'form',
        'view_mode': 'form',
        'res_model': 'mail.compose.message',
        'views': [(compose_form_id, 'form')],
        'view_id': compose_form_id,
        'target': 'new',
        'context': ctx,
    }





    @api.onchange('customer')
    def _on_change_customer(self):
        if self.customer.is_company and self.customer.child_ids:
            self.representative = self.customer.child_ids[0].name
            self.onside_contact_id = self.customer.child_ids[0]
        else:
            self.representative = self.customer.name
            self.onside_contact_id = self.customer
            

        # self.warehouse = self.customer.warehouse_id.name
        # self.onside_contact_id = self.customer
        found= False
        if  self.customer.child_ids:
            child= self.customer.child_ids
            for i in child:
                if i.type == 'recycle':                    
                    self.replace_fields(i)
                    found=True 
                    break
            
        if  not found:
            self.replace_fields(self.customer)

        # else:
        #     self.replace_fields(self.customer)

    def replace_fields(self,obj):
        if obj.street:
                self.street  = obj.street
            
        if obj.street2:
            self.street2  =  obj.street2
        
        if obj.zip:
            self.zip  = obj.zip
        
        if obj.city:
            self.city   = obj.city
            
        if obj.state_id:
            self.state_id   = obj.state_id
        
        if obj.country_id:
            self.country_id = obj.country_id


    # @api.onchange('customer')                
    # def _onchange_customer_recycle(self):
    #     return self.customer.child_ids.search([('type','=','recycle')])



class InboundOrderLines(models.Model):
    _name                           = "recycle.inbound_orders.lines"
    _description                    = "Inbound Orders Lines"

    # # product_id      = field.Many2one("product.product",)
    # product_id                      = fields.Many2one('product.product', string='Product', ondelete='restrict')
    # product_updatable               = fields.Boolean(compute='_compute_product_updatable', string='Can Edit Product', readonly=True, default=True)
    # product_uom_qty                 = fields.Float(string='Ordered Quantity', digits=dp.get_precision('Product Unit of Measure'), required=True, default=1.0)
    # product_uom                     = fields.Many2one('uom.uom', string='Unit of Measure')
    
    line_id                         = fields.Many2one('recycle1.inbound_orders', string='Order', ondelete='cascade') 
    product_id                      = fields.Many2one('product.product', string='Product') # Product name
    tax_id                          = fields.Many2many('account.tax', string='Taxes') # Product default taxes
    price                           = fields.Float(string='Price')
    description                     = fields.Text(string='Description')
    quantity                        = fields.Float(default=1.000)
    # sequence                        = fields.Integer(string='Sequence', default=10)

    @api.onchange('product_id')
    def _onchange_product_id(self):
        self.description= self.product_id.description_purchase
        self.price      = self.product_id.lst_price
        self.tax_id     = self.product_id.taxes_id

        
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    # @api.onchange('customer')
    # def _on_change_customer(self):
    #     self.representative = self.customer.name
    #     self.warehouse = self.customer.warehouse_id.name

    # Name Should be name as button to perform OnClick action
    # def create quotation(self):
    #     pass
        


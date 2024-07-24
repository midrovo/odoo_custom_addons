from odoo import models, fields, api  # type: ignore
from odoo.exceptions import ValidationError # type: ignore
from datetime import date

import logging
_logger = logging.getLogger(__name__)

class Deposit(models.Model):
    _name = 'custom.deposit'
    _description = 'Modelo para la gestion de depositos'

    ### atributos ###
    papeleta_deposito = fields.Char(
        string = 'Ref. del deposito',
    )
    
    cliente = fields.Many2one(
        string = 'Cliente',
        comodel_name = 'res.partner',
    )

    valor = fields.Monetary(
        string = 'Valor',
        currency_field = "moneda",
    )

    moneda = fields.Many2one(
        comodel_name = 'res.currency',
        default = lambda self: self.env['res.currency'].search([('name', '=', 'USD')]),
        readonly = True
    )

    fecha = fields.Date(
        string = 'Fecha',
        default = date.today(),
    )

    nota = fields.Char(
        string = 'Nota',
    )

    documento = fields.Binary(
        string = 'Documento',
    )

    proforma = fields.Char(
        string = 'Proforma',
    )

    cuenta_bancaria = fields.Many2one(
        string = 'Cuenta bancaria de la empresa',
        comodel_name = 'account.journal',
        domain=[('type','=','bank')]
    )

    numero_de_cuenta = fields.Char(
        string='Número de cuenta'
    )

    estado = fields.Selection(
        [('S', 'Subido'), ('C', 'Confirmado'), ('F', 'Facturado')],
        string = 'Estado',
    )
    
    vendedor = fields.Many2one(
        string = 'Vendedor',
        comodel_name = 'res.users',
        default = lambda self : self.env.user,
        readonly=True,
    )
    
    ### metodos ###

    
    # @api.onchange('cuenta_bancaria')
    # def _onchange_cuenta_bancaria(self):
    #     if self.cuenta_bancaria in self:
    #         cuenta_partner = self.env['res.partner.bank'].search([('id','=',self.cuenta_bancaria.bank_account_id.id)], 
    #         limit=1
    #         )

    #         self.numero_de_cuenta = cuenta_partner.acc_number
    
    @api.model
    def create(self, vals):            
        vals['estado'] = 'S'
            
        return super(Deposit, self).create(vals)
        
    
    def name_get(self):
        result = []
        for record in self:
            name = record.papeleta_deposito or 'Sin referencia'
            result.append((record.id, name))
        return result
    
    @api.model
    def load(self, fields, data):
        records = [ dict(zip(fields, record)) for record in data ]
        
        import_result = {
            'ids': [],
            'messages': [],
            'nextrow': len(data),
        }
        
        for record in records:            
            deposit_db = self.search([
                ('numero_de_cuenta', '=', record['numero_de_cuenta']),
                ('papeleta_deposito', '=', record['papeleta_deposito']),
                ('valor', '=', record['valor'])
            ])
            
            if deposit_db:
                deposit_db.write({ 'estado': 'C' })
                import_result['ids'].append(deposit_db.id)
            
        return import_result
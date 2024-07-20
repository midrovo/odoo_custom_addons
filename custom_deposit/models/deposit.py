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
        string = 'Cuenta bancaria',
        comodel_name = 'res.partner.bank',
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
    @api.model
    def create(self, vals):
        record = self.search([
            ('cuenta_bancaria', '=', vals['cuenta_bancaria']),
        ], limit = 1)
        
        if record:
            if record.cliente.id != vals['cliente'] and record.cuenta_bancaria.id == vals['cuenta_bancaria']:
                raise ValidationError('La cuenta bancaria pertenece a otro cliente')
            
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
            cuenta_bancaria = self.env['res.partner.bank'].search([
                ('acc_number', '=', record['cuenta_bancaria'].split('-')[0])
            ])
            
            deposit_db = self.search([
                ('cuenta_bancaria', '=', cuenta_bancaria.id),
                ('papeleta_deposito', '=', record['papeleta_deposito'])
            ])
            
            if deposit_db:
                if deposit_db.estado == 'S' and deposit_db.estado != 'F':
                    deposit_db.write({ 'estado': 'C' })
                    
                    import_result['ids'].append(deposit_db.id)
            
            else:
                partner_id = self.env['res.partner'].search([('name','=',record['cliente'])])
                
                if not partner_id:
                    cliente = {
                        'name': record['cliente'] 
                    }
                    
                    new_partner_id = self.env['res.partner'].create(cliente)
                    
                    cuenta = {
                        'acc_number': record['cuenta_bancaria'].split('-')[0],
                        'partner_id': new_partner_id.id,
                        'bank_id': False
                    }
                    
                    new_cuenta_bancaria = self.env['res.partner.bank'].create(cuenta)
                
                    new_deposit = {
                        'papeleta_deposito': record['papeleta_deposito'],
                        'cliente': new_partner_id.id,
                        'valor': record['valor'],
                        'fecha': record['fecha'],
                        'cuenta_bancaria': new_cuenta_bancaria.id,
                    }
                    
                    new_record = self.create(new_deposit)
                    
                    new_record.write({ 'estado': 'C' })
                    
                    _logger.info(f'ESTADO >>> { new_record.estado }')
                    
                    import_result['ids'].append(new_record.id)
            
        return import_result
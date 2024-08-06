import logging

from odoo import models, fields, api # type: ignore
from odoo.exceptions import UserError # type: ignore
from datetime import date, datetime, timedelta

_logger = logging.getLogger(__name__)

class Deposit(models.Model):
    _name = 'custom.deposit'
    _description = 'Modelo para la gestion de depositos'
    
    ### atributos ###
    papeleta_deposito = fields.Char(
        string = 'No. de Deposito',
        required = True
    )
    
    cliente = fields.Many2one(
        string = 'Cliente',
        comodel_name = 'res.partner',
        required = True
    )

    monto = fields.Monetary(
        string = 'Monto',
        currency_field = "moneda",
        required = True
    )
    
    moneda = fields.Many2one(
        comodel_name = 'res.currency',
        default = lambda self: self.env['res.currency'].search([('name', '=', 'USD')]),
        readonly = True
    )

    fecha = fields.Date(
        string = "default",
        default = fields.Date.context_today,
    )
    
    fecha_char = fields.Char(
        string = 'Fecha',
    )

    nota = fields.Char(
        string = 'Nota',
    )

    doc_deposit = fields.Binary(
        string = 'Documento de Deposito',
    )

    proforma = fields.Char(
        string = 'No. de Proforma',
        required = True
    )

    nombre_banco = fields.Char(
        string = 'Banco',
    )
    
    cuenta_bancaria = fields.Many2one(
        comodel_name = 'account.journal',
        string = 'Cuenta Bancaria de la Empresa',
        domain="[('type','=','bank')]"        
    )
    
    numero_cuenta = fields.Char(
        string = 'No. de Cuenta',
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
    @api.onchange('cuenta_bancaria')
    def onchange_cuenta_bancaria(self):
        if self.cuenta_bancaria:
            self.numero_cuenta = self.cuenta_bancaria.bank_account_id.acc_number
            self.nombre_banco = self.cuenta_bancaria.bank_account_id.bank_id.name
    
    @api.model
    def create(self, vals):
        deposito_existente = self.search([
            ('papeleta_deposito', '=', vals['papeleta_deposito']),
            ('numero_cuenta', '=', vals['numero_cuenta'])
        ])
        
        if deposito_existente:
            papeleta = deposito_existente.papeleta_deposito
            banco = deposito_existente.cuenta_bancaria.bank_account_id.bank_id.name
            
            raise UserError(
                f'La papeleta de deposito con este numero: { papeleta }  ya existe en { banco }.'
            )
        
        if 'cuenta_bancaria' in vals:
            cuenta_bancaria = self.env['account.journal'].browse(vals['cuenta_bancaria'])
            if cuenta_bancaria.bank_account_id:
                vals['nombre_banco'] = cuenta_bancaria.bank_account_id.bank_id.name
                 
        vals['estado'] = 'S'
        
        fecha = datetime.strptime(vals['fecha'], '%Y-%m-%d')
        
        vals['fecha_char'] = fecha.strftime('%d/%m/%Y')
            
        return super(Deposit, self).create(vals)        
    
    def name_get(self):
        result = []
        for record in self:
            name = record.papeleta_deposito or 'Sin referencia'
            result.append((record.id, name))
        return result
    
    @api.model
    def load(self, fields, data):
        fecha_actual = date.today()
        sheet = self.env.context.get('sheet', False)
        
        buscar_cuenta = self.search([('numero_cuenta', '=', sheet)])
        
        if not buscar_cuenta:
            raise UserError(f'El número de cuenta ingresada no existe o es incorrecta { sheet }')
        
        number_account = sheet
                
        records = [ dict(zip(fields, record)) for record in data ]
       
        import_result = {
            'ids': [],
            'messages': [],
            'nextrow': len(data),
        }
        
        self.parsear_fechas(records)
                
        for record in records:
            fecha_record = record['fecha_char']
            
            if '/' in fecha_record:
                fecha_date = datetime.strptime(fecha_record, '%d/%m/%Y').date()
                fecha_record = fecha_date.strftime('%Y-%m-%d')
                fecha_record = datetime.strptime(fecha_record, '%Y-%m-%d').date()
                record['fecha_char'] = fecha_record
                
            else:
                fecha_date = datetime.strptime(fecha_record, '%Y-%m-%d').date()
                fecha_record = fecha_date
                
            dia = fecha_record.day
            mes = fecha_record.month
            anio = fecha_record.year
            
            if dia <= fecha_actual.month:
                fecha_record = fecha_record.replace(month=dia, day=mes)
            
            record['fecha_char'] = fecha_record
            
            fecha_format = record['fecha_char']
            _logger.info(f'OBTENIENDO FECHA { fecha_format }')
                                                             
            deposit_db = self.search([
                ('numero_cuenta', '=', number_account),
                ('papeleta_deposito', '=', record['papeleta_deposito']),
                ('fecha', '=', record['fecha_char']),
                ('monto', '=', record['monto'])
            ])
            
            if deposit_db:
                deposit_db.write({ 'estado': 'C' })
                import_result['ids'].append(deposit_db.id)
           
        return import_result
    
    def parsear_fechas(self, records):
        for record in records:
            fecha_record = record['fecha_char']
            if '/' not in fecha_record and '-' not in fecha_record:
                number_days = int(fecha_record)
                record['fecha_char'] = self.excel_date_to_datetime(number_days)
                     
    def excel_date_to_datetime(self, excel_date):
        fecha_parseada = datetime(1899,12,30).date() + timedelta(days=(excel_date))
        fecha_formateada = fecha_parseada.strftime('%d/%m/%Y')
        return fecha_formateada
                
class CustomBaseImport(models.TransientModel):
    _inherit = 'base_import.import'

    def execute_import(self, fields, columns, options, dryrun=False):
        sheet = options.get('sheet', False)
        context = dict(self.env.context, sheet=sheet)
                
        return super(CustomBaseImport, self.with_context(context)).execute_import(fields, columns, options, dryrun)
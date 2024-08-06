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
        
        # if not buscar_cuenta:
        #     raise UserError(f'El número de cuenta ingresada no existe o es incorrecta { sheet }')
        
        number_account = sheet
                
        records = [ dict(zip(fields, record)) for record in data ]
       
        import_result = {
            'ids': [],
            'messages': [],
            'nextrow': len(data),
        }
        
        self.parsear_fechas(records)
        fechas = self.extraer_fechas(records)
        fechas_correctas = self.fechas_congruentes(fechas)

        _logger.info(f'FECHAS CORRECTAS >>> { fechas_correctas }')
                
        for record in records:
            fecha_record = record['fecha_char']
                                                             
            deposit_db = self.search([
                # ('numero_cuenta', '=', number_account),
                # ('papeleta_deposito', '=', record['papeleta_deposito']),
                ('fecha', '=', record['fecha_char']),
                # ('monto', '=', record['monto'])
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

            if '/' in fecha_record:
                fecha_record = datetime.strptime(fecha_record, '%Y-%m-%d').date()
                record['fecha_char'] = fecha_record
                     
    def excel_date_to_datetime(self, excel_date):
        fecha_convertida = datetime(1899,12,30).date() + timedelta(days=(excel_date))
        return fecha_convertida

    def extraer_fechas(self, records):
        fechas = []

        for record in records:
            fecha_record = datetime.strptime(record['fecha_char'], '%Y-%m-%d').date()
            fechas.append(fecha_record)

        return fechas
    
    def fechas_congruentes(self, fechas):
        fechas_congruentes = []
        for fecha in fechas:
            _logger.info(f'FECH >>> { fecha }')
            if fecha.day >= 1 and fecha.day <= 31:
                fechas_congruentes.append(fecha)

        return fechas_congruentes



        
                
class CustomBaseImport(models.TransientModel):
    _inherit = 'base_import.import'

    def execute_import(self, fields, columns, options, dryrun=False):
        sheet = options.get('sheet', False)
        context = dict(self.env.context, sheet=sheet)
                
        return super(CustomBaseImport, self.with_context(context)).execute_import(fields, columns, options, dryrun)
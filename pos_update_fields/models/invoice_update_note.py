from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)



class InvoiceUpdateNote(models.Model):
    _inherit = "pos.order"

    @api.model
    def get_note(self, nota):
        invoice = super(InvoiceUpdateNote, self).create_from_ui

        _logger.info(f'OBTENIENDO INVOICE >>> { invoice }')
        _logger.info(f'OBTENIENDO NOTA >>> { nota }')

        return nota
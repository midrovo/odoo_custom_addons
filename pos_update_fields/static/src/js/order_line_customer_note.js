odoo.define('pos_update_fields.order_line_customer_note', function(require) {
    'use strict';

    const OrderlineCustomerNoteButton = require('point_of_sale.OrderlineCustomerNoteButton');
    const Registries = require('point_of_sale.Registries');
    const NoteService = require('pos_update_fields.note_service')

    const OrderlineCustomerNoteButtonExtend = OrderlineCustomerNoteButton => class extends OrderlineCustomerNoteButton {
        setup() {
            super.setup();
        }
        async onClick() {
            const { confirmed, payload: inputNote } = await this.showPopup('TextAreaPopup', {
                title: this.env._t('Agregar Nota'),
            });

            if (confirmed) {
                console.log(`OBTENIENDO INPUT NOTE >>> ${ inputNote }`)
                NoteService.setNote(inputNote);
                
            }
        }
    }

    Registries.Component.extend(OrderlineCustomerNoteButton, OrderlineCustomerNoteButtonExtend);

    return OrderlineCustomerNoteButton;
});

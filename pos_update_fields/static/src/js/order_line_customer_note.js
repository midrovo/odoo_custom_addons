odoo.define('pos_update_fields.order_line_customer_note', function(require) {
    'use strict';

    const OrderlineCustomerNoteButton = require('point_of_sale.OrderlineCustomerNoteButton');
    const Registries = require('point_of_sale.Registries');

    const OrderlineCustomerNoteButtonExtend = OrderlineCustomerNoteButton => class extends OrderlineCustomerNoteButton {
        setup() {
            super.setup();
        }
        async onClick() {
            const { confirmed, payload: inputNote } = await this.showPopup('TextAreaPopup', {
                // startingValue: selectedOrderline.get_customer_note(),
                title: this.env._t('Agregar Nota'),
            });

            if (confirmed) {
                // selectedOrderline.set_customer_note(inputNote);
                console.log(`OBTENIENDO INPUT NOTE >>> ${ inputNote }`)
                this.trigger('note-update', { note: inputNote })
            }
        }
    }

    Registries.Component.add(OrderlineCustomerNoteButton, OrderlineCustomerNoteButtonExtend);

    return OrderlineCustomerNoteButton;
});

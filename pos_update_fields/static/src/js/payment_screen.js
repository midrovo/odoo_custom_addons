odoo.define('pos_update_fields.payment_screen', function (require) {
    'use strict';

    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const Registries = require('point_of_sale.Registries');
    const NoteService = require('pos_update_fields.note_service')

    const PaymentScreenExtend = PaymentScreen => class extends PaymentScreen {
        setup() {
            super.setup();
        }

        async validateOrder(isForceValidate) {

            console.log(`MOSTRANDO NOTA DESDE PAYMENT >>> ${ NoteService.getNote() }`)

            return await super.validateOrder(isForceValidate)

        }

    }

    Registries.Component.extend(PaymentScreen, PaymentScreenExtend);

    return PaymentScreen;
});

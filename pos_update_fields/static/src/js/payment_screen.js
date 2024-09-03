odoo.define('pos_update_fields.payment_screen', function (require) {
    'use strict';

    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const { useListener } = require("@web/core/utils/hooks");
    const Registries = require('point_of_sale.Registries');

    const PaymentScreenExtend = PaymentScreen => class extends PaymentScreen {
        setup() {
            super.setup();
            useListener('note-update', this.getNote);
        }

        getNote(event) {
            console.log(`EVENTO >>> ${ event }`);
        }

    }

    Registries.Component.extend(PaymentScreen, PaymentScreenExtend);

    return PaymentScreen;
});

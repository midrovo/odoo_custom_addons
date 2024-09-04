odoo.define('pos_update_fields.payment_screen', function (require) {
    'use strict';

    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const Registries = require('point_of_sale.Registries');
    const NoteService = require('pos_update_fields.note_service');
    const rpc = require('web.rpc')

    const PaymentScreenExtend = PaymentScreen => class extends PaymentScreen {
        setup() {
            super.setup();
        }

        async validateOrder(isForceValidate) {
            try {
                const orders = this.env.pos.selectedOrder
                const nota = NoteService.getNote()

                const result = await rpc.query({
                    model: "account.move",
                    method: "get_note",
                    args: [ nota ]
                })

                if(result) {
                    console.log(result)
                }

                console.log(orders)

                console.log(`MOSTRANDO NOTA DESDE PAYMENT >>> ${ NoteService.getNote() }`)

                return await super.validateOrder(isForceValidate)
                
            } catch (error) {
                console.log(error)
            }

        }

    }

    Registries.Component.extend(PaymentScreen, PaymentScreenExtend);

    return PaymentScreen;
});

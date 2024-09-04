odoo.define('pos_update_fields.note_service', (require) => {
    "use strict";

    class NoteService {
        constructor() {
            this.note = null;
        }

        setNote(note) {
            this.note = note;
        }

        getNote() {
            return this.note;
        }
    }

    return new NoteService();

});
odoo.define('website.form_editor_registry', function (require) {
'use strict';

var Registry = require('web.Registry');

return new Registry();

});

odoo.define('website.send_mail_form', function (require) {
'use strict';

var core = require('web.core');
var FormEditorRegistry = require('website.form_editor_registry');

var _t = core._t;

FormEditorRegistry.add('send_mail', {
    formFields: [{
        type: 'text',
        modelRequired: true,
        fillWith: 'subject',
        name: 'subject',
        string: 'Your Subject',
    },], 


});

});

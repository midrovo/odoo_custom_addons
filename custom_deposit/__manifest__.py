{
    'name': 'custom_deposit',

    'summary': """
        Modulo Account para la gestion de depositos""",

    'description': """
        Modulo deposito para la gestion de depositos
        1. No permite crear depositos desde un archivo de importacion
        2. Se ingresan los depositos en el formulario con estado subido
        3. Se verifica la importacion del registro contable de banco de acuerdo con los siguientes parametros
           fecha, ref de deposito, valor y cuenta bancaria si existe poner el estado confirmado""",

    'author': "Mauricio Idrovo",
    'images': ['static/description/icon-deposito.jpg'],
    'website': "https://www.callphone.com.ec",
    "category": "Tools",
    "depends": ['base','account','base_import'],
    "license": "AGPL-3",

    'data': [
        'security/security_access_data.xml',
        'security/ir.model.access.csv',
        'views/views.xml'
    ],
    
    'license': 'AGPL-3',
    'post_load': '',
    "installable": True,
    'auto_install': False,
    'application': True,
}
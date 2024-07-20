{
    'name': 'custom_deposit',

    'summary': """
        Modulo Account para la gestion de depositos""",

    'description': """
        Modulo Account para la gestion de depositos...""",

    'author': "Mauricio Idrovo",
    'images': ['static/description/elearning.png'],
    'website': "https://www.callphone.com.ec",
    "category": "",
    "depends": ['base'],
    "license": "AGPL-3",

    'data': [
        "views/views.xml",
        'security/ir.model.access.csv',
    ],
    
    'license': 'AGPL-3',
    'post_load': '',
    "installable": True,
    'auto_install': False,
    'application': True,
}
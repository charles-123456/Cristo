{
    'name': 'Rest API',
    'author': 'Boscosoft Technologies Pvt Ltd',
    'version': '1.0',
    'category': 'API',
    'depends': [
        'base',
        'web',
    ],
    'external_dependencies': {
        'python' : ['PyJWT'],
        },
    'data': [
        'security/ir.model.access.csv',
        'data/ir_cron_data.xml',
        'views/res_user_views.xml',
        'views/rest_api_access_history_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}

# Server Specific Configurations
server = {
    'port': '8554',
    'host': '0.0.0.0'
}

# Pecan Application Configurations
app = {
    'root': 'testhub_restapi.controllers.root.RootController',
    'modules': ['testhub_restapi.app'],
    'template_path': '%(confdir)s/testhub_restapi/templates',
    'debug': True,
    'errors': {
        '__force_dict__': True
    }
}

wsme = {
    'debug': True
}

logging = {
    'root': {'level': 'INFO', 'handlers': ['logfile']},
    'loggers': {
        'testhub_restapi': {'level': 'DEBUG', 'handlers': ['logfile'], 'propagate': False},
        'pecan': {'level': 'DEBUG', 'handlers': ['logfile'], 'propagate': False},
        'py.warnings': {'handlers': ['console']},
        '__force_dict__': True
    },
    'handlers': {
        'logfile': {
            'class': 'logging.handlers.RotatingFileHandler',
            'maxBytes': 1000000,
            'backupCount': 10,
            'filename': '/var/log/testhub_restapi/testhub_restapi.log',
            'level': 'DEBUG',
            'formatter': 'simple'
        },
       'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'color'
        }
    },
    'formatters': {
        'simple': {
            'format': ('%(asctime)s %(levelname)-5.5s [%(name)s]'
                       '[%(threadName)s] %(message)s')
        },
        'color': {
            '()': 'pecan.log.ColorFormatter',
            'format': ('%(asctime)s [%(padded_color_levelname)s] [%(name)s]'
                       '[%(threadName)s] %(message)s'),
        '__force_dict__': True
        }
    }
}


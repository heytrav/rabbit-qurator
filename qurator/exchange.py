from kombu import Exchange

exchange = Exchange('qurator',
                    type='direct',
                    durable=False)
task_exchange = Exchange('qurator_tasks',
                         type='direct')

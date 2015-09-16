from kombu import Exchange

exchange = Exchange(type='direct',
                    durable=False)
task_exchange = Exchange(type='direct')

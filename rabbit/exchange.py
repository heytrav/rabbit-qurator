from kombu import Exchange

exchange = Exchange('rabbitpy', 
                    type='direct',
                    durable=False)
task_exchange = Exchange('rabbitpy_tasks',
                         type='direct')

from kombu import Exchange

exchange = Exchange(name='amq.direct', 
                    type='direct',
                    durable=False)
task_exchange = Exchange(name='amq.direct', type='direct')

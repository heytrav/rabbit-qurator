from kombu import Exchange

exchange = Exchange('rabbitpy', 
                    #durable=False,
                    type='direct')

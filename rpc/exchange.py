from kombu import Exchange

exchange = Exchange('rabbitpy', 
                    type='direct', 
                    durable=False)

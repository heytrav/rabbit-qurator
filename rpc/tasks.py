import  simplejson as json
def hello_task(who="world"):
    message = "Hello %s" %(who, )
    return json.dumps({'message': message})



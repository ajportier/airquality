class Config (object):
            
    DEBUG = True
    SECRET_KEY = "changeThisKey"
    
    MONGODB_SETTINGS = {
    'db':'airquality',
    'host':'localhost',
    'port':27017,
    }
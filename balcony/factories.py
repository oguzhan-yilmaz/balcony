import boto3
try:
    from .utils import _create_boto_session
except ImportError:
    from utils import _create_boto_session
    
class Boto3SessionSingleton(object):
    _instance = None
    _session = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Boto3SessionSingleton, cls).__new__(cls)
            # Put any initialization here.
            # cls._session = _create_boto_session()

        return cls._instance


    def __init__(self):
        if not self._session:
            self._session = _create_boto_session()
    
    def get_session(self):
        return self._session
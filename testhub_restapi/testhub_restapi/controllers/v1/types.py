from oslo_utils import strutils
from wsme import types as wtypes

class TestInfoType(wtypes.UserType):
    basetype = wtypes.text
    name = 'testinfodata'
    __name__ = name

    @staticmethod
    def validate(value):
        return value

    @staticmethod
    def frombasetype(value):
        if value is None:
            return None
        return TestInfoType.validate(value)

testinfodata = TestInfoType()

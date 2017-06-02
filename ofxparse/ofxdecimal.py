import decimal

class Decimal(decimal.Decimal):

    def __new__(cls, value="0", context=None):
        if '.' not in value:
            value = value.replace(',', '.')
        return decimal.Decimal.__new__(cls, value, context)


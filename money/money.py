from decimal import Decimal as decimal

def money(n):
    return decimal(n).quantize(decimal('0.00'))

def rnd(n, dec):
    decimals = ''.join(['0' for n in range(0, dec ,1)])
    full_str_dec = '0.{}'.format(decimals)
    return decimal(n).quantize(decimal(full_str_dec))

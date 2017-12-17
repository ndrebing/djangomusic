import numpy as np
from django import template

register = template.Library()

@register.simple_tag
def get_random_number():
    return str(np.random.randint(0,10000))

import six
try:
    text_type = six.string_types
except NameError:
    text_type = str
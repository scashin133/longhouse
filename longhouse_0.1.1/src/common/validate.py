class Email(object):
    
    def Validate(self, email):
        """Throw a InvalidFormattedField exception if this is not formated
        like an email address"""
        # TODO: regex to check if email is formated correctly
        pass
    


class Error(Exception):
    """Base class for errors from this module."""
    pass


class InvalidFormattedField(Error):
    """A field was not formatted correctly"""
    def __init__(self, text):
        self.text = text



class Required(object):
    def Validate(self, object):
        if len(object[0]) == 0:
            raise InvalidFormattedField("Cannot be blank.")
    
        
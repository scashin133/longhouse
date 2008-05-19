class Redirect(object):
	"""Redirects the request to redirect_to"""
	
	def __init__(self, redirect_to):
		self.redirect_to = redirect_to
        
	def Handler(self, request):
		request.redirect(self.redirect_to)		


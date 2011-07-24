class ComponentRegistry(object):
	_components = {}
	_component_methods = {}
	def register(self, component, name=None):
		"""
		register a component to allow remote function to be called
		
		:param component: 
		:type component: Component
		
		:param name: The name of the component being registered
		:type name: string
		"""
		if name == None:
			name = component.__class__.__name__
		component._allowed_methods = self._component_methods
		self._components[name] = component
		self._component_methods = {}
	
	def addMethod(self, method, auth_level):
		self._component_methods[method] = auth_level
	
	def call(self, method, args):
		"""
		:param method: the component and components function to call in the form component.function
		:type method: string
		
		:param args: arguments for the function
		:type args: dict
		"""
		comp, func = method.split('.')
		try:
			auth_level = self._components[comp]._allowed_methods.get(func)
			"@todo: _allowed_methods could be a class which if the auth_level is not high enough for a specific action, could raise an exception"
		except:
			import logging
			logging.error("403 denied")
		fn = getattr(self._components[comp], func);
		return fn(**args)
componentManager = ComponentRegistry()

def remote(fn, auth_level=None):
	"""
	used by components to register functions that can be called remotely
	
	"""
	name = fn.func_name
	componentManager.addMethod(name, auth_level)
	return fn
	
class Component(object):
	_allowed_methods = None
	def __init__(self, component_name):
		"""
		registers the component with the component registry
		
		:param component_name: the name which will be used to refer to the component
		:type component_name: string
		"""
		componentManager.register(self, component_name) 
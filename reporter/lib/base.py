#-*- coding: utf-8 -*-
# vim: set bg=dark noet ts=4 sw=4 fdm=indent :


''' Base Element With Composite Design'''
__author__ = 'chutong'


from abc import ABCMeta, abstractmethod


class Component(object):
    ''' Composite design
    '''
	__metaclass__ = ABCMeta

	@abstractmethod
	def render(self, logger):
		pass


class Composite(Component):
	''' Composite design
	'''
	def __init__(self):
		self._components = []

	def add_component(self, component, logger):
		self._components.append(component)

	def delete_component(self, component, logger):
		self._components.remove(component)

	def get_component(self, index, logger):
		if 0 <= index <= len(self.components) - 1:
			return self._components[index]

	def render(self, logger):
		pass


class Leaf(Component):
	''' Composite design
	'''
	def render(self, logger):
		pass

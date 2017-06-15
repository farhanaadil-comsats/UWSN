#!/usr/bin/env python

from heapq import heappush, heappop
from random import uniform, gauss
from math import sqrt
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

class SimEnvironment:
	"""Manages a set of nodes and the communications between them"""
	def __init__(self, size, params = {}):
		"""Initialize the simulation environment
		size        -- dimensions (dimX, dimY, dimZ) of the simulation space
		            the simulation space is defined by the following ranges:
		                0 < x < dimX
		                0 < y < dimY
		            -dimZ < z < 0
		params      -- set of parameters, overrides the default parameters (default {})
		"""
		dimX, dimY, dimZ = size
		self.maxX = dimX
		self.maxY = dimY
		self.minZ = -dimZ
		self.params = {                 # default set of parameters
		    "sos":          1500,       # speed of sound in water (m/s)
		    "range":        1000,       # maximum range a signal can reach (m)
		    "reliability":  1,          # probability of a signal reaching its destination (0 to 1)
		    "sigma":		0.05,       # standard deviation of the time-of-arrival noise
		    "tick":         0.1         # duration between two activations of the nodes
		}
		self.params.update(params)      # let user-provided parameters override default parameters
		
		self.nodes = []
		self.events = []                # managed with heapq
		                                # events have the form (time, message, recipient)
		                                # if the message is empty then the function tick(time) is called for all nodes
		                                # otherwise the function receive(time, message) is called for the recipient
	
	def addNode(self, node):
		"""Adds a node to the simulation environment
		node        -- node to be added
		"""
		x, y, z = node.position
		if x < 0 or x > self.maxX or y < 0 or y > self.maxY or z < self.minZ or z > 0:  # if coordinates are out of bounds, random coordinates are assigned
			x = uniform(0, self.maxX)
			y = uniform(0, self.maxY)
			z = uniform(self.minZ, 0)
			node.position = (x,y,z)
		
		node.speedOfSound = self.params["sos"]
		
		self.nodes.append(node)
	
	def run(self, timeout):
		"""Runs the simulation
		timeout     -- duration of the simulation (s)
		"""
		heappush(self.events, (0, "", None))    # initialize the event list
		time = 0
		print "start..."
		while time <= timeout:
			time, message, recipient = heappop(self.events)
			if len(message) == 0:
				for node in self.nodes:
					transmission = node.tick(time)
					if len(transmission) > 0:
						self.broadcast(time, node.position, transmission)
				heappush(self.events, (time + self.params["tick"], "", None))
			else:
				recipient.receive(time, message)
		print "...end"
	
	def broadcast(self, time, position, message):
		"""Schedules a message to be recieved by all nodes in range
		time        -- date of transmission (s)
		position    -- position of broadcasting node (m,m,m)
		message     -- message to be broadcast
		"""
		for node in self.nodes:
			d = distance(node.position, position)
			if d > 0 and d <= self.params["range"] and uniform(0,1) < self.params["reliability"]:
				toa = time + gauss(1, self.params["sigma"]) * d / self.params["sos"]
				heappush(self.events, (toa, message, node))
	
	def show(self):
		"""Displays a 3D plot of the nodes"""
		# create the plot
		fig = plt.figure()
		ax = fig.add_subplot(111, projection='3d')
		# display the nodes
		for node in self.nodes:
			for x, y, z, c, m in node.representation():
				ax.scatter([x], [y], [z], c=c, edgecolor=c, marker=m)
		# add invisible points to give the plot the right size
		ax.scatter([0, self.maxX], [0, self.maxY], [self.minZ, 0], marker = '.', alpha=0)
		# display the plot
		plt.show()
	
def distance(position1, position2):
	"""Calculates an euclidian distance
	position1   -- X,Y,Z coordinates of the first point (m,m,m)
	position2   -- X,Y,Z coordinates of the second point (m,m,m)
	Returns the distance between two points
	"""
	x1,y1,z1 = position1
	x2,y2,z2 = position2
	dx = x1-x2
	dy = y1-y2
	dz = z1-z2
	return sqrt(dx*dx + dy*dy + dz*dz)
		

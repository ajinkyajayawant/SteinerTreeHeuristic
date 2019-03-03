# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
import numpy
import heapq
import shlex
import random
from Tkinter import Tk, Canvas, Frame, BOTH, NONE

class Node:
	def __init__(self,tag,name,location):
		self.tag = tag
		self.name = name
		self.location = location

	def GetName(self):
		return self.name

	def GetTag(self):
		return self.tag

	def GetLoc(self):
		return self.location

class Edge:
	def __init__(self,tag,points):
		self.tag=tag
		self.points=points
		self.length=RectDist(points[0],points[1])

	def GetTag(self):
		return self.tag

	def GetPoints(self):
		return self.points

	def GetLen(self):
		return self.length

	def GetGain(self):
		return self.gain
	def SetGain(self,gain):
		self.gain=gain

	def SetConnectNode(self,node):
		self.connectNode=node
	def GetConnectNode(self):
		return self.connectNode

	def SetMaxGainEdge(self,edge):
		self.maxGainEdge=edge
	def GetMaxGainEdge(self):
		return self.maxGainEdge

	def SetInfoPoints(self,points):
		self.infoPoints=points
	def GetInfoPoints(self):
		return self.infoPoints

	def __str__(self):
		return "({0},{1},{2},{3},{4},{5})".format(self.tag,self.points,self.length,self.gain,self.connectNode,self.maxGainEdge)

class EdgeList:
	edges=[]

	def __init__(self):
		self.curIndex=0

	def AddEdge(self,thisEdge):
		'''Here edge is just a 3 tuple.We will convert it
		to our edge object.'''
		if self.edges:
			self.edges.append(Edge(self.edges[len(self.edges)-1].GetTag()+1,thisEdge))
		else:
			self.edges.append(Edge(0,thisEdge))

	def RemoveEdge(self,thisIndex):
		'''Removes the edge correspoinding to this index.'''
		self.edges=[edge for edge in self.edges if edge.GetTag()!=thisIndex]
	
	def GetEdge(self,edgeIndex):
		for edge in self.edges:
			if edge.GetTag()==edgeIndex:
				return edge.GetPoints()

	def GetEntireEdge(self,edgeIndex):
		for edge in self.edges:
			if edge.GetTag()==edgeIndex:
				return edge

	def __iter__(self):
		self.curIndex=0#very important
		return self#.edges[self.curIndex]

	def next(self):
		if self.curIndex>=len(self.edges):
			raise StopIteration
		else:
			self.curIndex+=1
			return self.edges[self.curIndex-1]
	
	def __str__(self):
		edgesString=""
		for edge in self.edges:
			 edgesString+="{0}->{1}\n".format(edge.GetTag(),str(edge))
		return edgesString


class StTree:
	adjList = {}
	distanceHeap = []
	toIncludePoints = {}
	edges = EdgeList()
	edgeAdjList = {}

	def __init__(self,allNodes):
		self.nodes = allNodes

	def AddNode(self,ourNode):
		self.nodes.append(ourNode)

	def CreateAdjList(self):
		for node in self.nodes:
			self.adjList[node.GetLoc()]=[];

	def PrintAdjList(self):
		print 'Printing distance list'
		for node in self.nodes:
			print '{0}->{1}'.format(node.GetLoc(),self.adjList[node.GetLoc()])

	def BuildMST(self,tracks):
		for node1 in self.nodes:
			nodeDist=[(node2.GetLoc(),RectDist(node1.GetLoc(),node2.GetLoc())) for node2 in self.nodes if node1!=node2]
			self.adjList[node1.GetLoc()]=nodeDist
		for point in self.adjList.keys():
			self.toIncludePoints[point]=0 #value of 0 is not important
		nextPoint=self.toIncludePoints.keys()[0]
		while self.toIncludePoints:
			self.toIncludePoints.pop(nextPoint)
			#include all the points and their distances from the given
			#point, in a heap
			for distPoint in self.adjList[nextPoint]:
				heapq.heappush( self.distanceHeap,(distPoint[1],(distPoint[0],nextPoint)) )			
			popPoint=heapq.heappop(self.distanceHeap)
			#new node to attach should not already be in the tree formed
			while not((popPoint[1][0] in self.toIncludePoints) or (popPoint[1][1] in self.toIncludePoints)) and self.distanceHeap:
				popPoint=heapq.heappop(self.distanceHeap)
			point1=popPoint[1][0]
			point2=popPoint[1][1]
			if (point1 in self.toIncludePoints) and not(point2 in self.toIncludePoints):
				nextPoint=point1
				tracks.Connect3(point1,point2,DetermineVia(point1,point2))
				self.edges.AddEdge((point1,point2,DetermineVia(point1,point2)))
			elif not(point1 in self.toIncludePoints) and (point2 in self.toIncludePoints): 
				nextPoint=point2
				tracks.Connect3(point1,point2,DetermineVia(point1,point2))
				self.edges.AddEdge((point1,point2,DetermineVia(point1,point2)))
			else:
				print "Atleast one of the points has to already be present in the tree"
	
	def BuildSST(self,tracks):
		'''Builds spanning steiner tree. Steiner points are
		inserted in batched mode'''
		gainSorted=sorted(self.edges.edges,key=getKey,reverse=True)
		edgeSorted1=[edgeSorted for edgeSorted in gainSorted if getKey(edgeSorted)>0]
		print "The Sorted edges are {0}".format(edgeSorted1)
		for edgeIndex,edge in enumerate(edgeSorted1):
			edgePoints=self.edges.GetEdge(edge.GetMaxGainEdge())
			rootEdgePoints=edge.GetPoints()
			point4=rootEdgePoints[0]
			point5=rootEdgePoints[1]
			point6=rootEdgePoints[2]
			# we can update the edge adjacency list after our batched add and removal is done
			if edgePoints and tracks.DoesTrackExist3(point4,point5,point6):
				point1=edgePoints[0]
				point2=edgePoints[1]
				point3=edgePoints[2]
				if self.edges.GetEntireEdge(edge.GetMaxGainEdge()) not in edgeSorted1[0:edgeIndex]:
					tracks.Disconnect3(point1,point2,point3)
					self.edges.RemoveEdge(edge.GetMaxGainEdge())
					tracks.Connect3(edge.GetInfoPoints()[0],edge.GetConnectNode(),edge.GetInfoPoints()[1])
					self.edges.AddEdge((edge.GetInfoPoints()[0],edge.GetConnectNode(),edge.GetInfoPoints()[1]))
					self.AddNode(Node(None,None,edge.GetInfoPoints()[0]))
		self.CreateEdgeAdjList()

	def ComputeAllOperations(self,tracks):
		for edge in self.edges:
			edge.SetGain(0)
			edge.SetConnectNode(None)
			edge.SetMaxGainEdge(None)
			edge.SetInfoPoints((None,None))
			edgeTag=edge.GetTag()
			for adjEdge in self.edgeAdjList[edgeTag]:
				adjTag=adjEdge.GetTag()
				self.ComputeMaxGain(edgeTag,adjTag,adjTag,SupplyCommonPoint(edge.GetPoints(),adjEdge.GetPoints()),tracks)

	def ComputeMaxGain(self,rootEdge,currentEdge,maxGainEdge,commonPoint,tracks):
		'''Computes the max gain possible for a given edge and returns
		the max edge,node to connect and the gain corresponding to 
		this operation.Be sure to pass rootEdge from our basic
		datastructure so that it gets automatically updated.All 
		edges are represented as indexes in the edges list'''
		infoPoints=[]
		actCurEdge=self.edges.GetEdge(currentEdge)
		actRootEdge=self.edges.GetEdge(rootEdge)
		otherNode=FindOtherPoint(actCurEdge,commonPoint)
		newGain=self.ComputeGain(rootEdge,maxGainEdge,otherNode,tracks,infoPoints)
		if newGain>self.edges.GetEntireEdge(rootEdge).GetGain():
			self.edges.GetEntireEdge(rootEdge).SetGain(newGain)
			self.edges.GetEntireEdge(rootEdge).SetConnectNode(otherNode)
			self.edges.GetEntireEdge(rootEdge).SetMaxGainEdge(maxGainEdge)
			self.edges.GetEntireEdge(rootEdge).SetInfoPoints(infoPoints)
		adjEdges=[]
		for adjEdge in self.edgeAdjList[currentEdge]:
			if CheckPointInEdge(adjEdge.GetPoints(),FindOtherPoint(actCurEdge,commonPoint)):
				adjEdges.append(adjEdge)
		for adjEdge in adjEdges:
			newMaxGainEdge=maxGainEdge
			if tracks.FindGain3(adjEdge.GetPoints())>tracks.FindGain3(self.edges.GetEdge(maxGainEdge)):
				newMaxGainEdge=adjEdge.GetTag()
			self.ComputeMaxGain(rootEdge,adjEdge.GetTag(),newMaxGainEdge,SupplyCommonPoint(actCurEdge,adjEdge.GetPoints()),tracks)
		return

	def ComputeGain(self,rootEdge,maxGainEdge,otherNode,tracks,infoPoints):
		'''Compute the gain obtained by joining otherNode to root node
		and removing the maxGainEdge.'''
		actRootEdge=self.edges.GetEdge(rootEdge)
		nearPt=FindNearestPoint(actRootEdge,otherNode)
		viaPoints=SupplyViaPoints(nearPt,otherNode)
		feasibleViaPoints=[]
		for via in viaPoints:
			if tracks.IsPathAvailable3(nearPt,otherNode,via):
				feasibleViaPoints.append(via)
		if feasibleViaPoints==[]:
			gain=-500#just a large negative number
		else:
			gain=tracks.FindGain3(self.edges.GetEdge(maxGainEdge))-RectDist(nearPt,otherNode)
			infoPoints.append(nearPt)
			infoPoints.append(feasibleViaPoints[0])
		return gain

	def CreateEdgeAdjList(self):
		''' Creates a dictionary key for every edge. The value 
		correspondging to this key is a list of all edges connected
		to it. We make sure it is empty first so that we dont 
		keep adding elements to already non zero dict'''
		self.edgeAdjList={}

		for edge in self.edges:
			self.edgeAdjList[edge.GetTag()]=[]

		for key in self.edgeAdjList.keys():
			checkIndices=self.edgeAdjList.keys()
			checkIndices.remove(key)
			for index in checkIndices:
				edge1=self.edges.GetEdge(key)
				edge2=self.edges.GetEdge(index)
				if CheckCommonPoint(edge1,edge2):
					self.edgeAdjList[key].append(Edge(index,edge2))
	
	def PrintEdgeAdjList(self):
		print "Printing the edge adjacency list"
		for key in self.edgeAdjList.keys():
			printEdge=[str(edge) for edge in self.edgeAdjList[key]]
			print "{0}->{1}".format(self.edges.GetEdge(key),printEdge)

	def PrintEdges(self):
		print "Printing out the edges"
		print str(self.edges)

class Tracks:
	""" Just creates an easy to visualise connections
	corresponding to our graph. """
	def __init__(self,nodes):
		tempMax1=0
		tempMax2=0
		for node in nodes:
			tempMax1=max(tempMax1,node.location[0])
			tempMax2=max(tempMax2,node.location[1])
		self.circuitTracks=numpy.zeros((2*(tempMax1+1)-1,2*(tempMax2+1)-1))

	def PrintTracks(self):
		print "Printing the circuit connections"
		print numpy.rot90(self.circuitTracks)

	def Connect2(self,point1,point2):
		if point1[0]==point2[0]:
			lesserCoord=min(point1[1],point2[1])
			greaterCoord=max(point1[1],point2[1])
			self.circuitTracks[2*point1[0],2*lesserCoord:2*greaterCoord+1]+=1
		elif point1[1]==point2[1]:
			lesserCoord=min(point1[0],point2[0])
			greaterCoord=max(point1[0],point2[0])
			self.circuitTracks[2*lesserCoord:2*greaterCoord+1,2*point1[1]]+=1
		else:
			print "Cant connect {0} and {1}".format(point1,point2)

	def Connect3(self,point1,point2,viaPoint3):
		if viaPoint3==None:
			self.Connect2(point1,point2)
		else:
			self.Connect2(point1,viaPoint3)
			self.DecreaseWeight(viaPoint3)
			self.Connect2(viaPoint3,point2)

	def Disconnect2(self,point1,point2):
		if point1[0]==point2[0]:
			lesserCoord=min(point1[1],point2[1])
			greaterCoord=max(point1[1],point2[1])
			if numpy.all(self.circuitTracks[2*point1[0],2*lesserCoord:2*greaterCoord+1]>0):
				self.circuitTracks[2*point1[0],2*lesserCoord:2*greaterCoord+1]-=1
			else:
				print "There is a disconnection in track between {0} and {1}".format(point1,point2)
		elif point1[1]==point2[1]:
			lesserCoord=min(point1[0],point2[0])
			greaterCoord=max(point1[0],point2[0])
			if numpy.all(self.circuitTracks[2*lesserCoord:2*greaterCoord+1,2*point1[1]]>0):
				self.circuitTracks[2*lesserCoord:2*greaterCoord+1,2*point1[1]]-=1
			else:
				print "There is a disconnection in track between {0} and {1}".format(point1,point2)
		else:
			print "Cant connect {0} and {1}".format(point1,point2)

	def Disconnect3(self,point1,point2,viaPoint3):
		"""Disconnects the track joining point1 and point2 via
		viaPoint3."""
		if viaPoint3==None:
			self.Disconnect2(point1,point2)
		else:
			self.Disconnect2(point1,viaPoint3)
			self.IncreaseWeight(viaPoint3)
			self.Disconnect2(viaPoint3,point2)

	def DecreaseWeight(self,point):
		self.circuitTracks[2*point[0],2*point[1]]-=1;

	def IncreaseWeight(self,point):
		self.circuitTracks[2*point[0],2*point[1]]+=1;

	def FindLength(self):
		noVertices=numpy.count_nonzero(self.circuitTracks[::2,::2])
		total=numpy.count_nonzero(self.circuitTracks)
		return total-noVertices

	def IsPointAvailable(self,point):
		return self.circuitTracks[2*point[0],2*point[1]]==0

	def IsPathAvailable2(self,point1,point2):
		'''If we want to build a path from point1 to point2
		then do we intersect any tracks or points?'''
		if point1[0]==point2[0]:
			x1=2*point1[0]
			y1=2*min(point1[1],point2[1])+1
			x2=2*point2[0]
			y2=2*max(point1[1],point2[1])
			isAvailable=not numpy.any(self.circuitTracks[x1,y1:y2])
		elif point1[1]==point2[1]:
			x1=2*min(point1[0],point2[0])+1
			y1=2*point1[1]
			x2=2*max(point1[0],point2[0])
			y2=2*point2[1]
			isAvailable= not numpy.any(self.circuitTracks[x1:x2,y1])
		else:
			"Points {0} and {1} are not in a straight line and cannot be joined!".format(point1,point2)
			isAvailable=False
		return isAvailable

	def IsPathAvailable3(self,point1,point2,viaPoint3):
		'''If we want to build a path from point1 to point2
		via point 3 then do we intersect any tracks or points?'''
		if viaPoint3==None:
			isAvailable=self.IsPathAvailable2(point1,point2)
		else:
			isAvailable= self.IsPathAvailable2(point1,viaPoint3) and self.IsPathAvailable2(viaPoint3,point2) and self.IsPointAvailable(viaPoint3)
		return isAvailable

	def DoesTrackExist2(self,point1,point2):
		'''Checks whether there is an already existing track
		from point 1 to point 2.'''
		if point1[0]==point2[0]:
			minY=min(point1[1],point2[1])
			maxY=max(point1[1],point2[1])
			doesExist=numpy.all(self.circuitTracks[2*point1[0],2*minY:2*maxY+1])
		elif point1[1]==point2[1]:
			minX=min(point1[0],point2[0])
			maxX=max(point1[0],point2[0])
			doesExist=numpy.all(self.circuitTracks[2*minX:2*maxX+1,2*point1[1]])
		else:
			print "Points {0} and {1} are not inline".format(point1,point2)
			doesExist=False
		return doesExist

	def DoesTrackExist3(self,point1,point2,viaPoint3):
		'''Checks whether there is an already existing track
		from point 1 to point 2 through viaPoint3.'''
		if viaPoint3==None:
			doesExist=self.DoesTrackExist2(point1,point2)
		else:
			doesExist=self.DoesTrackExist2(point1,viaPoint3) and self.DoesTrackExist2(point2,viaPoint3)
		return doesExist

	def FindGain2(self,point1,point2):
		'''Find the gain acheived by removing the edge connecting
		point 1 and point 2.'''
		if point1[0]==point2[0]:
			track=self.circuitTracks[2*point1[0],2*min(point1[1],point2[1])+1:2*max(point1[1],point2[1]):2]
			gain=numpy.count_nonzero(track)-numpy.count_nonzero(track-1)
		elif point1[1]==point2[1]:
			track=self.circuitTracks[2*min(point1[0],point2[0])+1:2*max(point1[0],point2[0]):2,2*point1[1]]
			gain=numpy.count_nonzero(track)-numpy.count_nonzero(track-1)
		else:
			gain=0
			print "Points {0} and {1} are not inline for gain caculation".format(point1,point2)
		return gain

	def FindGain3(self,edge):
		'''Find the gain that we have after removing an edge.
		Note that this may not be always equal to the edge length
		due to overlapping edges.'''
		point1=edge[0]
		point2=edge[1]
		viaPoint3=edge[2]
		gain=0
		if viaPoint3==None:
			gain=self.FindGain2(point1,point2)
		else:
			gain=self.FindGain2(point1,viaPoint3)+self.FindGain2(point2,viaPoint3)
		return gain

def takeInputs(filePath):
	placements=open(filePath,"r")
	allFile=placements.read()
	print "The file is: \n",allFile
	placements.close()
	return allFile

def CreateNodes(allFile):
	splitComp=allFile.split('COMPONENTS');
	components=splitComp[1].split(';');
	noComponents=int(shlex.split(components[0])[0])
	components.pop(0)
	components.pop()
	allNodes=[]
	for component in components:
		singleComponent=shlex.split(component)
		position=(int(singleComponent[6]),int(singleComponent[7]))
		allNodes.append(Node(singleComponent[1],singleComponent[2],position))
	return allNodes

def getKey(edge):
	return edge.GetGain()

def RandomCreateNodes(width,height,sparsity):
	allNodes=[]
	for x in range(width):
		for y in range(height):
			if random.uniform(0,1)<=sparsity:
				allNodes.append(Node(None,None,(x,y)))
	return allNodes

def PrintNodes(allNodes):
	print 'Printing all nodes'
	for node in allNodes:
		print '{0} {1} {2}\n'.format(node.GetTag(), node.GetName(),node.GetLoc())

def RectDist(point1,point2):
	if point1!=None and point2!=None:
		dist=abs(point1[0]-point2[0])+abs(point1[1]-point2[1])	
	else:
		dist=500#just some large number so that this edge does not get considered for joining
	return dist

def ArePointsInline(point1,point2):
	return point1[0]==point2[0] or point1[1]==point2[1]

def SupplyViaPoints(point1,point2):
	viaPoints=[]
	if point1!=None and point2!=None:
		if ArePointsInline(point1,point2):
			viaPoints.append(None)
		else:
			viaPoints.append((point1[0],point2[1]))
			viaPoints.append((point1[1],point2[0]))
	return viaPoints

def DetermineVia(point1,point2):
	""" determine an intermediate point(via) through which the track
	passes to reach from point1 to point2. If point1 and point2 are in
	a straight line the the intermediate point will be None"""
	if point1[0]==point2[0] or point1[1]==point2[1]:
		point3=None
	else:
		if point1[0]>point2[0]:
			point3=(point1[0],point2[1])
		else:
			point3=(point2[0],point1[1])
	return point3

def SupplyCommonPoint(edge1,edge2):
	'''Ideally this can be merged with CheckCommonPoint
	function.'''
	if edge1[0]==edge2[0] or  edge1[0]==edge2[1]:
		commonPoint=edge1[0]
	elif edge1[1]==edge2[0] or edge1[1]==edge2[1]:
		commonPoint=edge1[1]
	else:
		commonPoint=None
		print "No point in common between {} and {}".format()
	return commonPoint

def CheckCommonPoint(edge1,edge2):
	'''edges are 3 tuples by default. We only check 
	whether the first 2 tuples of the 2 edges have 
	anything in common.'''
	if edge1[0]==edge2[0] or edge1[1]==edge2[1] or edge1[0]==edge2[1] or edge1[1]==edge2[0]:
		isCommon=True
	else:
		isCommon=False
	return isCommon

def FindNearestPoint(edge1,point1):
	'''Find the nearest point on the edge from the point.'''
	point1=edge1[0]
	point2=edge1[1]
	viaPoint3=edge1[2]
	if viaPoint3!=None:
		if point1[0]==viaPoint3[0]:
			minY=min(point1[1],viaPoint3[1])
			maxY=max(point1[1],viaPoint3[1])
			inBetwPoints1=[(point1[0],y) for y in range(minY+1,maxY)]
			minX=min(point2[0],viaPoint3[0])
			maxX=max(point2[0],viaPoint3[0])
			inBetwPoints2=[(x,point2[1]) for x in range(minX+1,maxX)]
			inBetwPoints=inBetwPoints1+inBetwPoints2+[viaPoint3]
			if inBetwPoints:
				edgeDist=[RectDist(point,point1) for point in inBetwPoints]
				nearestPoint=inBetwPoints[edgeDist.index(min(edgeDist))]
			else:
				nearestPoint=None
		elif point1[1]==viaPoint3[1]:
			minX=min(point1[0],viaPoint3[0])
			maxX=max(point1[0],viaPoint3[0])
			inBetwPoints2=[(x,point1[1]) for x in range(minX+1,maxX)]
			minY=min(point2[1],viaPoint3[1])
			maxY=max(point2[1],viaPoint3[1])
			inBetwPoints1=[(point2[0],y) for y in range(minY+1,maxY)]
			inBetwPoints=inBetwPoints2+inBetwPoints1+[viaPoint3]
			if inBetwPoints:
				edgeDist=[RectDist(point,point1) for point in inBetwPoints]
				nearestPoint=inBetwPoints[edgeDist.index(min(edgeDist))]
			else:
				nearestPoint=None
		else:
			print "Points {0} and {1} are not inline".format(point1,viaPoint3)
	else:
		if point1[0]==point2[0]:
			minY=min(point1[1],point2[1])
			maxY=max(point1[1],point2[1])
			inBetwPoints=[(point1[0],y) for y in range(minY+1,maxY)]
			if inBetwPoints:
				edgeDist=[RectDist(point,point1) for point in inBetwPoints]
				nearestPoint=inBetwPoints[edgeDist.index(min(edgeDist))]
			else:
				nearestPoint=None
		elif point1[1]==point2[1]:
			minX=min(point1[0],point2[0])
			maxX=max(point1[0],point2[0])
			inBetwPoints=[(x,point1[1]) for x in range(minX+1,maxX)]
			if inBetwPoints:
				edgeDist=[RectDist(point,point1) for point in inBetwPoints]
				nearestPoint=inBetwPoints[edgeDist.index(min(edgeDist))]
			else:
				nearestPoint=None
		else:
			print "Points {0} and {1} are not inline".format(point1,point2)
	return nearestPoint

def CheckPointInEdge(edge1,point1):
	'''assuming that edge here is just a 3 tuple of points.'''
	if edge1[0]==point1 or edge1[1]==point1:
		isPresent=True
	else:
		isPresent=False
	return isPresent

def FindOtherPoint(edge1,point1):
	'''If one point of the edge is point1, what is the 
	other point?'''
	if edge1[0]==point1:
		otherPoint=edge1[1]
	elif edge1[1]==point1:
		otherPoint=edge1[0]
	else:
		otherPoint=None
		print "Edge {0} does not contain the point {1}".format(edge1,point1)
	return otherPoint

class Example(Frame):
  
	def __init__(self, parent,tree,scaling):
		Frame.__init__(self, parent)   

		self.parent = parent        
		self.initUI(tree,scaling)

	def initUI(self,tree,scaling):
		self.parent.title("MST")        
		self.pack(fill=BOTH,expand=1)

		canvas = Canvas(self,width=10000,height=10000)
		#canvas.create_oval(10, 10, 15, 15, outline="red", fill="red", width=1)
		tempMax1=0
		tempMax2=0
		for node in tree.nodes:
			tempMax1=max(tempMax1,node.GetLoc()[0])
			tempMax2=max(tempMax2,node.GetLoc()[1])
		for x in range(tempMax1+1):
			for y in range(tempMax2+1):
				canvas.create_oval(scaling*(x+1)-1, scaling*(tempMax2-y+1)-1, scaling*(x+1)+1, scaling*(tempMax2-y+1)+1, outline="black", fill="black", width=1)			

		for edge in tree.edges:
			point1=edge.GetPoints()[0]
			point2=edge.GetPoints()[1]
			point3=edge.GetPoints()[2]
			canvas.create_oval(scaling*(point1[0]+1)-2, scaling*(tempMax2-point1[1]+1)-2, scaling*(point1[0]+1)+2, scaling*(tempMax2-point1[1]+1)+2, outline="red", fill="red", width=1)
			canvas.create_oval(scaling*(point2[0]+1)-2, scaling*(tempMax2-point2[1]+1)-2, scaling*(point2[0]+1)+2, scaling*(tempMax2-point2[1]+1)+2, outline="red", fill="red", width=1)
			if point3!=None:
				point3=edge.GetPoints()[2]
				canvas.create_line(scaling*(point1[0]+1), scaling*(tempMax2-point1[1]+1), scaling*(point3[0]+1), scaling*(tempMax2-point3[1]+1),fill="red")
				canvas.create_line(scaling*(point2[0]+1), scaling*(tempMax2-point2[1]+1), scaling*(point3[0]+1), scaling*(tempMax2-point3[1]+1),fill="red")
			else:
				canvas.create_line(scaling*(point1[0]+1), scaling*(tempMax2-point1[1]+1), scaling*(point2[0]+1), scaling*(tempMax2-point2[1]+1),fill="red")
		canvas.pack(fill=BOTH, expand=1)
		
		canvas.update()
		canvas.postscript(file="graph.6.ps",colormode='color')

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
import shlex

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

def PrintNodes(allNodes):
	print 'Printing all nodes'
	for node in allNodes:
		print '{0} {1} {2}\n'.format(node.GetTag(), node.GetName(),node.GetLoc())

def RectDist(point1,point2):
	return abs(point1[0]-point2[0])+abs(point1[1]-point2[1])

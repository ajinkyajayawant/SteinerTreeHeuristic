# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
from Tkinter import Tk
from steinerData import *

def SteinerTree():	
    #nodes=CreateNodes(takeInputs("placement2.txt"))
    nodes=RandomCreateNodes(50,50,0.2)
    PrintNodes(nodes)
    sttree=StTree(nodes)
    sttree.CreateAdjList()
    sttree.PrintAdjList()
    circTracks=Tracks(nodes)
    #circTracks.PrintTracks()
    #circTracks.Connect3((1,1),(2,2),(1,2))
    #circTracks.Connect3((2,2),(2,0),None)
    #circTracks.PrintTracks()
    #circTracks.Disconnect3((2,2),(2,0),None)
    #circTracks.PrintTracks()
    circTracks.PrintTracks()
    sttree.BuildMST(circTracks)
    sttree.PrintAdjList()
    #sttree.PrintEdges()
    sttree.CreateEdgeAdjList()
    #sttree.PrintEdgeAdjList()
    sttree.ComputeAllOperations(circTracks)#testing
    sttree.PrintEdges()#testing
    circTracks.PrintTracks()

    #print circTracks.IsPathAvailable3((4,3),(8,4),(8,3))
    #print FindNearestPoint(Edge(None,((6,5),(8,4),(8,5))),(7,0))#testing 0 is because I dont want to calculate length of edge
    #print FindNearestPoint(Edge(None,((3,4),(3,6),None)),(9,2))#testing 0 is because I dont want to calculate length of edge
    #print FindNearestPoint(Edge(None,((5,1),(6,1),None)),(9,2))#testing 0 is because I dont want to calculate length of edge
    #print circTracks.FindGain3(Edge(None,((3,6),(4,8),(4,6))))
    print circTracks.FindGain3(((8,9),(7,8),(8,8)))    
    scaling=6
    root = Tk()
    ex = Example(root,sttree,scaling)
    #root.geometry("330x220+300+300")
    print "MST length using Prims algorithm is {0}".format(circTracks.FindLength())
    sttree.BuildSST(circTracks)
    print "MST length using Steiner algorithm is {0}".format(circTracks.FindLength())
    root2=Tk()
    ex1 = Example(root2,sttree,scaling)
    root.geometry("330x220+300+300")
    root.mainloop()

if __name__ == "__main__":
    SteinerTree()

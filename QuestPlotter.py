import tkinter as tk
from tkinter import filedialog
from abc import ABC, abstractmethod
from Nodes import EventNode, GraphLabel
import configs
import json
configs.currentSelectedNode = None

class Plotter():

    def click(self,event):
        self.clearPlotter()
        if configs.currentSelectedNode is not None:
            eNode = EventNode(self.window, "Player Event","Event Node","Event Node",event.x - 50, event.y - 25)
            configs.currentSelectedNode.addChildNode(eNode)
            eNode.addParentNode(configs.currentSelectedNode)
            self.canvas.update()
            #print(f"Line Coords : {configs.currentSelectedNode.getXLocation(), configs.currentSelectedNode.getYLocation(),eNode.getXLocation(),eNode.getYLocation()}")
            self.canvas.create_line(configs.currentSelectedNode.getXLocation(), configs.currentSelectedNode.getYLocation(),eNode.getXLocation(),eNode.getYLocation(), width= 5)
            self.canvas.pack()
            configs.currentSelectedNode.removeBoarder()
            configs.currentSelectedNode = eNode
            configs.currentSelectedNode.addBoarder()
            self.nodes.append(eNode)

            
    def rightClick(self, event):
        #clear hanging controls/menus
        self.clearPlotter()
        #create menu
        frame = tk.Frame(self.window)
        frame.place(x = event.x, y= event.y)
        configs.menus.append(frame)
        #tk.Button(configs.menus[len(configs.menus)-1], text="Print Graph", command= lambda:[self.getGraph(),self.clearPlotter()]).pack()
        tk.Button(frame, text = "Add Node", command=lambda: [self.clearPlotter(), self.makeNode()]).pack()
        tk.Button(frame, text = "Add Label", command=lambda: [self.clearPlotter(), self.makeLabel()]).pack()

            #create frame
            #create buttons
            #flag for removal? 
        pass

    def makeNode(self):
        configs.currentSelectedNode = EventNode(self.window,  "Player Event","Event Node","Event Node",configs.plotter.canvas.winfo_pointerx() - configs.plotter.canvas.winfo_rootx() -50,configs.plotter.canvas.winfo_pointery() - configs.plotter.canvas.winfo_rooty() -25 )
        self.nodes.append(configs.currentSelectedNode)

    def makeLabel(self):
        self.Labels.append(GraphLabel(self.window, "New Label",configs.plotter.canvas.winfo_pointerx() - configs.plotter.canvas.winfo_rootx() ,configs.plotter.canvas.winfo_pointery() - configs.plotter.canvas.winfo_rooty()))

    def clearPlotter(self):
        for i in configs.menus:
            i.destroy()
        configs.menus.clear()
        self.organiseGraph()
        pass

    def drawLinkingLine(self, node1, node2):
        self.canvas.create_line(node1.getXLocation(), node1.getYLocation(),node2.getXLocation(),node2.getYLocation(), width= 5)

    def getGraph(self):
        #data = []
        #visited = []
        #for j in self.Start:
        #    if j.childNodes is not None:
        #        for i in j.childNodes:
        #            data += i.getChildren(visited)
        #    data = [j] + data
        #print(f"Graph Length = {len(data)}")
        #print(f"Nodes in graph = {data}")
        return self.nodes

    def onCanvasResize(self,event):
        self.canvas.addtag_all("all")
        xRatio = float(event.width)/self.canvas.winfo_width()
        yRatio = float(event.height)/self.canvas.winfo_height()
        self.canvas.config(width=event.width, height=event.height)
        self.canvas.scale("all", 0,0,xRatio,yRatio)
        self.canvas.pack()

    def openGraph(self):
        filePath = filedialog.askopenfilename()
        if filePath is not None:
            self.canvas.delete("all")
            toRemove = []
            for i in self.window.children.values():
                if type(i) is tk.Label:
                    toRemove.append(i)
            for i in range(len(toRemove)):
                toRemove[i].place_forget()
            self.makeGraphFromJson(filePath)
        self.currentFilePath = filePath 

        

    def makeGraphFromJson(self, filePath:str):
        self.canvas.delete("all")
        self.nodes.clear()
        workingNodes = []
        jsonString = open(filePath)
        data = json.load(jsonString)
        for i in data['nodes']:
            workingNodes.append(EventNode(self.window,i["TypeOfNode"],i["Data"],i["Text"],i["xLocation"],i["yLocation"]))
        for i in range(len(workingNodes)):
            for j in data['nodes'][i-1]["Parents"]:
                workingNodes[i-1].addParentNode(workingNodes[j-1])
            for j in data['nodes'][i-1]["Children"]:
                workingNodes[i-1].addChildNode(workingNodes[j-1])
        self.window.update()
        for i in range(len(workingNodes)):
            for j in data['nodes'][i-1]["Children"]:
                self.drawLinkingLine(workingNodes[i-1],workingNodes[j-1])            
        for i in workingNodes:
            if i.NodeType == "Property":
                i.reRenderPropertyNode()
        for i in data['lables']:
            self.Labels.append(GraphLabel(self.window,i['Text'],i['xLocation'],i['yLocation']))
        self.nodes = workingNodes
        configs.currentSelectedNode = self.nodes[0]
        configs.currentSelectedNode.addBoarder()
        self.organiseGraph()
        jsonString.close()


        
    def saveGraphAs(self):
        data = self.buildGraphJson()
        files = [('Graph', '*.grph')]
        file = filedialog.asksaveasfile(filetypes=files,defaultextension=files, initialdir="\Graphs")
        if file is None:
            return
        file.write(data)
        self.currentFilePath = file.name
        file.close()

    def saveGraph(self):
        data = self.buildGraphJson()
        files = [('Graph', '*.grph')]        
        if self.currentFilePath is None:
            self.saveGraphAs()
            return
        file = open(self.currentFilePath,'w')
        file.write(data)
        file.close()

    def buildGraphJson(self):
        nodes = self.getGraph()
        nodes = [*set(nodes)]
        data = {}
        data['nodes'] = []
        counter = 0
        for i in nodes:
            node = i.getSelfAsJson()
            data['nodes'].append(node)
            data['nodes'][counter] = node
            data['nodes'][counter]['Children'] = []
            data['nodes'][counter]['Parents'] = []
            for j in i.childNodes:
                data['nodes'][counter]['Children'].append(nodes.index(j)+1)
            for j in i.parentNodes:
                data['nodes'][counter]['Parents'].append(nodes.index(j)+1)
            #print(f"Node {counter + 1} = {json.dumps(data['nodes'][counter])}")
            counter +=1           
        data['nodes'][0]['StartNode'] = True
        data['lables'] = []
        for i in self.Labels:
            data['lables'].append(i.getSelfAsJson())
        return json.dumps(data)


    def organiseGraph(self):
        #print graph with algorithm
        self.canvas.delete("all")
        graphStructure = self.getGraph()
        self.DrawLinesFromList(graphStructure)
        pass
    
    def DrawLinesFromList(self, Nodes):
        for i in Nodes:
            for j in i.childNodes:
                self.drawLinkingLine(i,j)
        pass

    def start(self):
        self.window.mainloop()
    
    def newGraph(self):
        self.primarySelected = None
        self.seccondarySelected = None
        self.canvas.delete("all")
        for i in self.nodes:
            i.label.destroy()
        self.nodes = []
        for i in self.Labels:
            i.label.destroy()
        self.Labels = []
        self.nodes.append(EventNode(self.window,"Player Event","Event Node","Event Node", 10 ,self.window.winfo_height()/2 - 50))
        configs.currentSelectedNode = self.nodes[0]
        self.currentFilePath = None


    def __init__(self):
        self.primarySelected = None
        self.seccondarySelected = None
        self.currentFilePath = None
        self.window = tk.Tk()
        self.window.title("Quest Plotter")
        self.MenuBar = tk.Menu(self.window)
        self.fileMenu = tk.Menu(self.MenuBar, tearoff= 0)
        self.fileMenu.add_command(label= "New", command=self.newGraph)
        self.fileMenu.add_cascade(label= "Open", command= self.openGraph)
        self.fileMenu.add_command(label= "Save", command=self.saveGraph)
        self.fileMenu.add_command(label= "Save As", command=self.saveGraphAs)
        self.MenuBar.add_cascade(label="File", menu = self.fileMenu)
        self.window.config(menu=self.MenuBar)
        self.canvas = tk.Canvas(width=1000,height=800, border=None, highlightthickness=0)
        self.canvas.bind("<Button-1>",self.click)
        self.canvas.bind("<Button-3>", self.rightClick)
        self.canvas.bind("<Configure>", self.onCanvasResize)
        self.window.bind("<Control-s>", lambda e: [self.saveGraph()])
        self.window.bind("<Control-n>", lambda e: [self.newGraph()])
        self.canvas.pack(fill="both", expand=True)
        self.nodes = []
        self.Labels = []
        self.window.update()
        self.nodes.append(EventNode(self.window,"Player Event","Event Node","Event Node", 10 ,self.window.winfo_height()/2 - 50))
        configs.currentSelectedNode = self.nodes[0]
        configs.plotter = self
        


p = Plotter()
p.start()
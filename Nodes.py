from abc import ABC, abstractmethod
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from PIL import Image, ImageTk
import configs
#for debuging
import os
class Node(ABC):
    def __init__(self):
        self.parentNodes = []
        self.childNodes = []
        self.label = None

    @abstractmethod
    def addParentNode(self, node):
        pass

    @abstractmethod
    def removeParentNode(self, node):
        pass

    @abstractmethod
    def addChildNode(self, node):
        pass

    @abstractmethod
    def removeChildNode(self, node):
        pass

    @abstractmethod 
    def getChildren(self):
        pass




class EventNode(Node):

    def eventNodeClick(self, event):
        for parent in self.parentNodes:
            configs.plotter.canvas.create_line(parent.getXLocation(), parent.getYLocation(),self.startX,self.startY, width= 10, fill = configs.plotter.canvas.cget('bg'))
        for child in self.childNodes:
            configs.plotter.canvas.create_line(child.getXLocation(), child.getYLocation(),self.startX,self.startY, width= 10, fill = configs.plotter.canvas.cget('bg'))
        self.startX = self.getXLocation()
        self.startY = self.getYLocation()
        self.DragstartX = event.x
        self.DragstartY = event.y
        if configs.linking:
            if configs.currentSelectedNode not in self.parentNodes and configs.currentSelectedNode not in self.childNodes:
                self.addParentNode(configs.currentSelectedNode)
                configs.currentSelectedNode.addChildNode(self)
                configs.plotter.drawLinkingLine(configs.currentSelectedNode, self)
            configs.linking = False
        if configs.currentSelectedNode is not None:
            configs.currentSelectedNode.removeBoarder()
        configs.currentSelectedNode = self
        self.addBoarder()


    def addBoarder(self):
        self.label.config(borderwidth=5, relief="solid")

    def removeBoarder(self):
        self.label.config(borderwidth=0, relief="flat")

    def drag(self, event):
        x = self.getXLocation() - self.DragstartX + event.x -25
        y = self.getYLocation() - self.DragstartY + event.y -12.5
        self.label.place(x=  x, y= y)

        #print(f"Event X = {x}, Event y = {y}")
    
    def mouseUp(self,event):
        configs.plotter.canvas.delete('all')
        #readraw linking lines
        for parent in self.parentNodes:
            configs.plotter.canvas.create_line(parent.getXLocation(), parent.getYLocation(),self.getXLocation(),self.getYLocation(), width= 5)
        for child in self.childNodes:
            configs.plotter.canvas.create_line(child.getXLocation(), child.getYLocation(),self.getXLocation(),self.getYLocation(), width= 5)
        self.startX = self.getXLocation()
        self.startY = self.getYLocation()
        self.DragstartX = event.x
        self.DragstartY = event.y
        configs.plotter.organiseGraph()
        configs.plotter.window.update()
        


    def eventNodeRightClick(self,event):
        if configs.linking:
            configs.linking = False
        #clear hanging controls/menus
        configs.plotter.clearPlotter()
        #Change selected to clicked node
        configs.currentSelectedNode.removeBoarder()
        configs.currentSelectedNode = self
        self.addBoarder()
        #create menu
        frame = tk.Frame(self.window)
        frame.place(x = configs.plotter.canvas.winfo_pointerx() - configs.plotter.canvas.winfo_rootx(), y= configs.plotter.canvas.winfo_pointery() - configs.plotter.canvas.winfo_rooty())
        configs.menus.append(frame)
        if self.NodeType in ["Game Event", "Player Event", "Branch", "Property", "Nested"]:
            tk.Button(frame, text="Change Text", command= lambda:self.createTextBox(frame)).pack()
        if self.NodeType == "Operator":
            tk.Button(frame, text="Change Operator", command= lambda:self.changeOperatorMenu(frame)).pack()
        if self.NodeType == "Property":
            tk.Button(frame, text="Add Property", command= lambda:self.addProperty(frame)).pack()
            tk.Button(frame, text="Modify Property", command= lambda:self.modifyProperty(frame)).pack()
            if len(list(self.propertyDict.keys())) >=1:
                tk.Button(frame, text="Delete Property", command= lambda:self.deleteProperty(frame)).pack()
        tk.Button(frame, text="Change NodeType", command= lambda:self.createNodeTypeChangeList(frame)).pack()
        tk.Button(frame, text="Delete Node", command= lambda:self.removeNode()).pack()
        tk.Button(frame, text = "Join Nodes", command = self.startLink).pack()
        if(self.NodeType == "Nested"):
            tk.Button(frame,text="Embed Graph", command = self.embedGraph).pack()
            if(self.data.__contains__(".grph")):
                tk.Button(frame,text="Open Nested Graph", command = self.openNestedGraph).pack()

        #Create Menu
            #create frame
            #create buttons
            #flag them for removal on click?
        pass

    def removeNode(self):
        if (self in configs.plotter.nodes):
            configs.plotter.nodes.remove(self)
        configs.currentSelectedNode.removeBoarder()
        if len(self.parentNodes) >=1:
            configs.currentSelectedNode = self.parentNodes[0]
            configs.currentSelectedNode.addBoarder()
        elif len(self.childNodes) >=1:
            configs.currentSelectedNode = self.childNodes[0]
            configs.currentSelectedNode.addBoarder()            
        else:
            configs.currentSelectedNode = None
        for i in self.childNodes:
            configs.plotter.canvas.create_line(self.getXLocation(), self.getYLocation(),i.getXLocation(),i.getYLocation(), width= 5, fill = configs.plotter.canvas.cget('bg'))
            i.removeParentNode(self)
        for i in self.parentNodes:
            i.removeChildNode(self,i)

        self.label.destroy()
        configs.plotter.clearPlotter()

    
    #Defunct method not used any more but left here for reference
    def removeDependantChildren(self):
        #Can't remove nodes who have multiple parents but both parents are dependant on a previous node being deleted...
        #not sure how to fix algorithmically.
        toRemove = []
        for i in self.childNodes:
            if len(i.parentNodes) <=1:
                i.removeDependantChildren()
                toRemove.append(i)
        for i in toRemove:
            self.removeChildNode(i,self)

    def createTextBox(self, owner):
        entry = tk.Entry(owner)
        entry.bind("<Return>", lambda e :[self.updateNodeText(e,entry), configs.plotter.clearPlotter()])
        entry.focus()
        entry.pack()

    
    def updateNodeText(self, event, textbox):
        self.label.config(text=textbox.get())
        self.text = textbox.get()
        if(self.NodeType == "Event Node"):
            self.data = textbox.get()
        configs.plotter.clearPlotter()
        
    def createNodeTypeChangeList(self, owner):
        variable = tk.StringVar(owner)
        variable.set(self.NodeType)
        typePicker = tk.OptionMenu(owner,variable, "Game Event", "Player Event", "Branch", "Property", "Operator", "Nested","Pivot", command= lambda e :[self.updateNodeType(e,variable)])
        typePicker.pack()
        pass

    def changeOperatorMenu(self,owner):
        frame = tk.Frame(self.window)
        frame.place(x = configs.plotter.canvas.winfo_pointerx() - configs.plotter.canvas.winfo_rootx(), y= configs.plotter.canvas.winfo_pointery() - configs.plotter.canvas.winfo_rooty())
        configs.menus.append(frame)
        variable = tk.StringVar(owner)
        variable.set("Operator")
        typePicker = tk.OptionMenu(owner,variable, "+", "-", "/", "*", "Has", "in","completed", "is", "found",  "AND", "OR", "NOT", "Custom", command= lambda e :[self.changeOperatorType(e,variable,owner)])
        typePicker.pack()
    
    def changeOperatorType(self,event,variable, owner):
        opString = variable.get()
        if not (opString=="Custom"):
            self.label.config(text=opString)
            self.text = opString
        else:
            self.createTextBox(owner)

    def updateNodeType(self,event,variable):
        typeString = variable.get()
        self.changeNodeImage(typeString)
        self.NodeType = typeString
        if self.NodeType  == "Pivot":
            self.label.config(text="")
            self.text = ""
        configs.plotter.clearPlotter()
    
    def startLink(self):
        configs.linking = True
        configs.plotter.clearPlotter()
        pass

    def changeNodeImage(self, newType):
        self.label.config(fg="#000000")
        match newType:
            case "Player Event":
                #change img
                self.img = ImageTk.PhotoImage(Image.open("Images/PlayerEventNode.png").resize((100,50), Image.ANTIALIAS))
                self.label.configure(image=self.img)
                return
            case "Game Event":
                self.img = ImageTk.PhotoImage(Image.open("Images/GameEventNode.png").resize((100,50), Image.ANTIALIAS))
                self.label.configure(image=self.img)
                #change img
                return
            case "Branch":
                self.img = ImageTk.PhotoImage(Image.open("Images/BranchNode.png").resize((100,50), Image.ANTIALIAS))
                self.label.configure(image=self.img)
                #change img
                return
            case "Property":
                self.img = ImageTk.PhotoImage(Image.open("Images/PropertyNode.png").resize((100,50), Image.ANTIALIAS))
                self.label.configure(image=self.img)
                self.label.config(fg="#DDDDDD")
                #change img
                return
            case "Operator":
                #change img
                self.img = ImageTk.PhotoImage(Image.open("Images/OperatorNode.png").resize((100,50), Image.ANTIALIAS))
                self.label.configure(image=self.img)
                return
            case "Nested":
                self.img = ImageTk.PhotoImage(Image.open("Images/NestedNode.png").resize((100,50), Image.ANTIALIAS))
                self.label.configure(image=self.img)
            case "Pivot":
                self.img = ImageTk.PhotoImage(Image.open("Images/PivotNode.png").resize((15,15), Image.ANTIALIAS))
                self.label.configure(image=self.img)
                #change img
                return

    def embedGraph(self):
        filePath = filedialog.askopenfilename()
        self.data = filePath
        configs.plotter.clearPlotter()

    def openNestedGraph(self):
        configs.plotter.canvas.delete("all")
        toRemove = []
        for i in configs.plotter.window.children.values():
            if type(i) is tk.Label:
                toRemove.append(i)
        for i in range(len(toRemove)):
            toRemove[i].place_forget()
        configs.plotter.makeGraphFromJson(self.data)
        configs.plotter.clearPlotter()

    def addProperty(self, owner):
        window = tk.Toplevel(configs.plotter.window, takefocus=True)
        tk.Label(window,text="Property Name").pack()
        nameEntry = tk.Entry(window)
        nameEntry.focus()
        nameEntry.pack()
        tk.Label(window,text="Property Value").pack()
        valueEntry = tk.Entry(window)
        valueEntry.pack()
        okButton = tk.Button(window, text="OK", command= lambda:[self.addPropertyFromEntries(None, nameEntry,valueEntry), window.destroy()])
        okButton.bind("<Return>", lambda e :[self.addPropertyFromEntries(e , nameEntry,valueEntry), window.destroy()])
        okButton.pack()
        configs.plotter.clearPlotter()
        pass

    def addPropertyFromEntries(self,event ,nameEntry:tk.Entry,valueEntry:tk.Entry):
        name = nameEntry.get()
        value = valueEntry.get()
        self.propertyDict[nameEntry.get()] = valueEntry.get()
        self.reRenderPropertyNode()

    def modifyProperty(self, owner):
        if len(self.propertyDict.keys()) >=1:
            variable = tk.StringVar(owner)
            variable.set("Property")
            tk.OptionMenu(owner,variable, *list(self.propertyDict.keys()), command= lambda e :[self.clearWidget(owner), self.changeProperty(e,variable,owner)]).pack()
        else:
            ans = messagebox.askyesno("Property Alert", "No properties to modify, would you like to add a propery now?")
            if ans:
                self.addProperty(owner)
        pass

    def clearWidget(self,widget):
        for i in widget.winfo_children():
            i.destroy()

    def changeProperty(self, event ,variable, owner):
        toModify = variable.get()
        entry = tk.Entry(owner)
        entry.focus()
        entry.bind("<Return>", lambda e : [self.updateProperty(e ,entry,toModify)])
        entry.pack()
    
    def updateProperty(self, event, textbox, toModify):
        newProperty = textbox.get()
        self.propertyDict[toModify] = newProperty
        self.reRenderPropertyNode()        

    
    def reRenderPropertyNode(self):
        if not(self.NodeType == "Property"):
            return
        title = self.text.split("\n")[0]
        text = f"{title}\n"
        lines = 0
        for i in self.propertyDict.keys():
            text += f"{i}  :  {self.propertyDict[i]}\n"
            lines +=1
        self.img = ImageTk.PhotoImage(Image.open("Images/PropertyNode.png").resize((100,(50 + ((lines-1)*13))), Image.ANTIALIAS))
        self.label.config(text=text, image = self.img)
        self.text = text
        configs.plotter.clearPlotter()

    def deleteProperty(self, owner):
        variable = tk.StringVar(owner)
        variable.set("Property")
        tk.OptionMenu(owner,variable, *list(self.propertyDict.keys()), command= lambda e :[self.clearWidget(owner), self.removeProperty(e,variable,owner)]).pack()
        pass

    def removeProperty(self, event, variable, owner):
        toModify = variable.get()
        if toModify is not None:
            self.propertyDict.pop(toModify)


    def addParentNode(self, node):
        self.parentNodes.append(node)

    def removeParentNode(self, node):
        node.childNodes.remove(self)
        self.parentNodes.remove(node)

    def addChildNode(self, node):
        self.childNodes.append(node)

    def removeChildNode(self, node):
        self.childNodes.remove(node)
    
    def removeChildNode(self,node,parent):
        self.childNodes.remove(node)
        configs.plotter.canvas.create_line(parent.getXLocation(), parent.getYLocation(),node.getXLocation(),node.getYLocation(), width= 5, fill = configs.plotter.canvas.cget('bg'))
        node.label.destroy()
    
    def getXLocation(self):
        return self.label.winfo_x() + self.label.winfo_width()/2

    def getYLocation(self):
        return self.label.winfo_y() + self.label.winfo_depth()/2


    def getChildren(self, visited):
        data = []
        visited.append(self)
        if self.childNodes.__len__() >=1:
            for i in self.childNodes:
                if i not in visited:
                    data += i.getChildren(visited)
        return data + [self]

    def getSelfAsJson(self):
        data = {}
        data['xLocation'] = self.getXLocation()
        data['yLocation'] = self.getYLocation()
        data['TypeOfNode'] = self.NodeType
        if self.NodeType == "Property":
            data["Data"] = self.propertyDict
        else:
            data["Data"] = self.data
        data['Text'] = self.text
        return data
    """
    def __init__(self, window, xLocation, yLocation):
        self.window =window
        Node.__init__(self)
        self.NodeType = "Game Event"
        self.img = ImageTk.PhotoImage(Image.open("Images/GameEventNode.png").resize((100,50), Image.ANTIALIAS))
        self.label = tk.Label(image=self.img, text = "Event Node", compound=tk.CENTER)
        self.data = "Event Node"
        self.label.bind("<Button-1>", self.eventNodeClick)
        self.label.bind("<Button-3>", self.eventNodeRightClick)
        self.label.place(x = xLocation,y =yLocation)
    """

    def __init__(self, window, nodeType,Data,Text, xLocation, yLocation):
        self.window = window
        super().__init__()
        self.NodeType = nodeType
        self.data = Data
        self.text = Text
        self.textOut = None #Canvas to render text for propery node (made at time but declared here)
        self.propertyDict = {}
        if self.NodeType == "Property":
            self.propertyDict = self.data
        self.img = ImageTk.PhotoImage(Image.open("Images/GameEventNode.png").resize((100,50), Image.ANTIALIAS))
        self.label = tk.Label(image=self.img, text = self.text, compound=tk.CENTER, anchor="center")
        self.changeNodeImage(nodeType)
        self.label.bind("<Button-1>", self.eventNodeClick)
        self.label.bind("<Button-3>", self.eventNodeRightClick)
        self.label.bind("<B1-Motion>", self.drag)
        self.label.bind("<ButtonRelease-1>", self.mouseUp)
        self.startX = xLocation
        self.startY = yLocation
        self.label.place(x= xLocation, y=yLocation)
        
    
class GraphLabel():
    def __init__(self, window, text, xLocation,yLocation) -> None:
        self.window = window
        self.text = text
        self.label = tk.Label(text = self.text)
        self.xLocation = xLocation
        self.yLocation = yLocation
        self.DragstartX = xLocation
        self.DragstartY = yLocation
        self.label.place(x = xLocation,y = yLocation)
        self.label.bind("<Button-1>", self.labelClick)
        self.label.bind("<Button-3>", self.labelRightClick)
        self.label.bind("<B1-Motion>", self.drag)
        self.label.bind("<ButtonRelease-1>", self.mouseUp)
        pass


    def labelClick(self, event):       
        self.startX = self.getXLocation()
        self.startY = self.getYLocation()
        self.DragstartX = event.x
        self.DragstartY = event.y
    
        
    def getXLocation(self):
        return self.label.winfo_x() + self.label.winfo_width()/2

    def getYLocation(self):
        return self.label.winfo_y() + self.label.winfo_depth()/2


    def drag(self, event):
       x = self.getXLocation() - self.DragstartX + event.x
       y = self.getYLocation() - self.DragstartY + event.y
       self.label.place(x=  x, y= y)

    
    def mouseUp(self,event):
        self.startX = self.getXLocation()
        self.startY = self.getYLocation()
        self.DragstartX = event.x
        self.DragstartY = event.y

    
    def getSelfAsJson(self):
        data = {}
        data['xLocation'] = self.getXLocation()
        data['yLocation'] = self.getYLocation()
        data['Text'] = self.text
        return data
        
    
    def labelRightClick(self,event):
        #create menu
        frame = tk.Frame(self.window)
        frame.place(x = configs.plotter.canvas.winfo_pointerx() - configs.plotter.canvas.winfo_rootx(), y= configs.plotter.canvas.winfo_pointery() - configs.plotter.canvas.winfo_rooty())
        configs.menus.append(frame)
        tk.Button(frame, text="Change Text", command= lambda:self.createTextBox(frame)).pack()
        tk.Button(frame, text="Delete Label", command= lambda:self.removeLabel()).pack()

    def createTextBox(self, owner):
        entry = tk.Entry(owner)
        entry.focus()
        entry.bind("<Return>", lambda e :[self.updateLabelText(e,entry)])
        entry.pack()

    
    def updateLabelText(self, event, textbox):
        self.label.config(text=textbox.get())
        self.text = textbox.get()
        configs.plotter.clearPlotter()

    def removeLabel(self):
        self.label.destroy()
        configs.plotter.Labels.remove(self)
        configs.plotter.clearPlotter()
    


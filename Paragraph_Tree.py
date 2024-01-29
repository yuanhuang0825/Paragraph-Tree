from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer,LTTextLineHorizontal,LTAnno,LTChar
import numpy as np

class Node:
    def __init__(self,fontsize):
        self.text='' 
        self.father=None #father node
        self.nextParagraph=None #next same level node
        self.preParagraph=None #previous same level node
        self.subParagraph=[] #sub nodes
        self.fontsize=fontsize #font size

class ROOT(Node):
    def __init__(self, fontsize):
        super().__init__(fontsize)
        self.levelList=[self] #save every level firt node
        
    def sort(self): #sort by font size
        for i in range(len(self.levelList)-1,0,-1): #buble sort
            for j in range(i):
                if self.levelList[j].fontsize<self.levelList[j+1].fontsize:
                    temp=self.levelList[j]
                    self.levelList[j]=self.levelList[j+1]
                    self.levelList[j+1]=temp
                    
def findsameLevelnode(nodes,index,target):
    while(nodes[index].fontsize!=target): #find same font size node from previous nodes
        if index-1<0:
            return None
        else:
            index-=1
    return nodes[index]
    
def isalphabet(char):
    return True if (ord(char)>=65 and ord(char)<=90) or (ord(char)>=97 and ord(char)<=122) else False
            
            
class PT:
    """
    This is an algorithm that can convert the text of a PDF paper into structured data based on the font size. 
    
    The root:type is Node, a cover node, which considers the first page as the cover and forcibly makes it the root.
    
    Each paragraph is a Node, and the properties of the Node are as follows:
    
    subParagraph: type is a list, the paragraphs that belong to this node.
    text: type is string, the text of this paragraph.
    fontsize: type is float, the font size of the text.
    father: type is Node, the parent node of this node.
    nextParagraph: type is Node, the next node with the same font size.
    preParagraph: type is Node, the previous node with the same font size.
    """
    def __init__(self,file_path):
        self.pages=extract_pages(file_path)
        self.get_char()
        self.get_root()
        self.build_tree()
        self.root.sort()
        
    def get_root(self):
        self.root=ROOT(np.inf)
        for paragraph in self.first_page: #first page is root
                if isinstance(paragraph, LTTextContainer):
                    for line in paragraph:
                        if isinstance(line,LTTextLineHorizontal):
                            for char in line:
                                if isinstance(char,LTChar): 
                                    self.root.text+=char.get_text()
                                if isinstance(char,LTAnno): 
                                    self.root.text+='\n'
    
    def findfather(self,node,target): #find bigger font size from father nodes
        if node!=None:
            if node.fontsize<=target:
                return self.findfather(node.father,target)
            else:
                return node
        else:
            return self.root
                              
    def get_char(self):
        self.char=[]
        alphabet=False
        for i,page in enumerate(self.pages):
            if i!=0:
                for paragraph in page:
                    if isinstance(paragraph, LTTextContainer):
                        for line in paragraph:
                            if isinstance(line,LTTextLineHorizontal):
                                for char in line :
                                    if isinstance(char,LTChar) and (char.get_text()!=' ' or alphabet): # allow space char if it's behind to english char
                                        self.char.append({
                                            'type':'char',
                                            'size':round(char.size),
                                            'char':char.get_text()
                                        })
                                        alphabet=isalphabet(char.get_text())
                                    if isinstance(char,LTAnno):
                                        self.char.append({
                                            'type':'anno'
                                        })
            else:
                self.first_page=page #first page is root
    
    def build_tree(self):
        nodes=[self.root] #save every node orderly for finding same level node
        current_node=nodes[0] 
        index=0
        for char in self.char:
            if char['type']=='char':
                if current_node.fontsize>char['size']: #if this char's font size is smaller than prenode 
                    new_node=Node(char['size'])
                    prenode=findsameLevelnode(nodes,index,char['size']) #find same level node from previous nodes
                    
                    #link horizontally
                    new_node.preParagraph=prenode
                    if prenode!=None:
                        prenode.nextParagraph=new_node
                    else:
                        self.root.levelList.append(new_node)
                    #link vertically
                    new_node.father=current_node
                    current_node.subParagraph.append(new_node)
                    
                    current_node=new_node
                    current_node.text=char['char'] #save first char into this node
                    nodes.append(current_node) #append this node in list
                    index+=1
                    
                elif current_node.fontsize<char['size']:
                    new_node=Node(char['size'])
                    prenode=findsameLevelnode(nodes,index,char['size'])
                    
                    #link horizontally
                    new_node.preParagraph=prenode
                    if prenode!=None:
                        prenode.nextParagraph=new_node
                    else:
                        self.root.levelList.append(new_node)
                    #link vertically
                    father=self.findfather(current_node,char['size'])
                    new_node.father=father
                    father.subParagraph.append(new_node)
                    
                    current_node=new_node
                    current_node.text=char['char'] #save first char into this node
                    nodes.append(current_node) #append this node in list
                    index+=1
                else:
                    current_node.text+=char['char'] #if font size is same, than concat char into current node
            else:
                current_node.text+='\n' #concat \n
  
    def getLeveltext(self,level): #traversal same level nodes
        current_node=self.root.levelList[level]
        output=[]
        while(current_node!=None):
            output.append(current_node)
            current_node=current_node.nextParagraph
        return output
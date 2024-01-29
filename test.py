from Paragraph_Tree import PT, Node
import os

PATH='pdfs'
DST='paragraphs'
LEVEL=1

def inorder(node:Node): #In-order traversal 
    output=node.text
    for subnode in node.subParagraph:
        output+=inorder(subnode)
    return output

def main():
    for name in os.listdir(PATH):
        pdf=PT(os.path.join(PATH,name))
        nodes=pdf.getLeveltext(LEVEL)
        os.mkdir(os.path.join(DST,name[:-4]))
        for i,node in enumerate(nodes):
            with open(os.path.join(DST,name[:-4],str(i+1)),'w') as f:
                f.write(inorder(node))
    
if __name__=='__main__':
    main()
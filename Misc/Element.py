class Element():
    
    def __init__(self,text="",category="Unkown",source="Unkown",boundingBox=[0,0,0,0]):
        self.text = text
        self.category=category
        self.source = source
        self.boundingBox = boundingBox

    def return_metadata(self):
        return {
            "category": self.category,
            "source": self.source,
            "TopLeftX": self.boundingBox[0],
            "TopLeftY": self.boundingBox[1],
            "BottomRightX": self.boundingBox[2],
            "BottomRightY": self.boundingBox[3]
        }
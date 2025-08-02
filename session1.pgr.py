class distance:
     def __init__(self,km):
        self.km=km
        
     def __sub__(self,other):
         return distance(self.km-other.km)

     def display(self):
        print("the distance is:",self.km)
        

d1=distance(100)
d2=distance(60)

d3=d1-d2

d3.display()


import math

# Arrays example

numbers = [1, 10  , 0 -5 , -1000 ,  100 , 7]
maximum  = numbers [0]



for number in numbers:
    maximum = max(maximum, number)


print("The maximum value is ", maximum)






# Functions Example


def area (a, b ) :
    return a * b





def is_square (a , b):
    return a == b


print ("area(1 , 5 ) = ", area(1 , 5 ))
print ("area(1.5 , 2.3) = ", area(1.5, 2.3))


print ("is_square(1 ,5 ) = " , is_square(1 , 5))
print ("is_square(5 , 5) = " , is_square(5 ,5 ))




# Classes



class Passenger:
    def __init__(self, first_name, last_name):
        self.first_name = first_name
        self.last_name = last_name


    def display(self):
        print(f"Passenger: {self.first_name} {self.last_name}")


    @staticmethod
    def from_input():
        first_name = input("Enter first name: ")
        last_name = input("Enter last name: ")

        return Passenger(first_name, last_name)


if __name__ == "__main__":
        lisa = Passenger("Lisa" , "Has")
        user = Passenger.from_input()

        lisa.display()
        user.display()





class Shape:
    def area2(self):
        pass



class Circle (Shape):
    def __init__(self ,  radius ):
        self.radius = radius


    def area (self):
        return 3.14 * (math.pow(self.radius, 2))


class Square (Shape):
    def __init__(self, length):
        self.length = length

    def area (self):
        return self.length * self.length






shapes = [Circle(5) , Square(10)]
for shape in shapes:
    print(shape.area())
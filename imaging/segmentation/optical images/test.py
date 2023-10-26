import pickle

class MyClass:
    def __init__(self, attribute1, attribute2):
        self.attribute1 = attribute1
        self.attribute2 = attribute2

    def method1(self):
        return self.attribute1 * 2

    def method2(self):
        return self.attribute2 * 3

    def save_to_binary(self, filename):
        with open(filename, 'wb') as file:
            pickle.dump(self, file)

    @classmethod
    def load_from_binary(cls, filename):
        with open(filename, 'rb') as file:
            obj = pickle.load(file)
        return obj

# Create an instance of the class
my_instance = MyClass(10, 20)

# Save the object to binary
my_instance.save_to_binary("my_object.bin")

# Load the object from binary
loaded_instance = MyClass.load_from_binary("my_object.bin")

# Access and modify attributes
loaded_instance.attribute1 = 30
loaded_instance.attribute2 = 40

# Call methods, which reflect the changes in attributes
result1 = loaded_instance.method1()
result2 = loaded_instance.method2()

print("Attribute 1 after modification:", loaded_instance.attribute1)
print("Attribute 2 after modification:", loaded_instance.attribute2)
print("Result of method1:", result1)
print("Result of method2:", result2)

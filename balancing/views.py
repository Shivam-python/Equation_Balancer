from django.shortcuts import render
import re
from django.views import View
from sympy import Matrix,lcm


def Home(request):

    # 2 arrays to store List of elements and their numbers
    elementList = []
    elementMatrix = []

    def addToMatrix(element, index, count, side):
        # function for creating evaluation matrix
        if (index == len(elementMatrix)):
            elementMatrix.append([])
            for x in elementList:
                elementMatrix[index].append(0)
        
        if (element not in elementList):
            elementList.append(element)
            for i in range(len(elementMatrix)):
                elementMatrix[i].append(0)
        column = elementList.index(element)
        
        # updating element matrix values
        elementMatrix[index][column] += count * side

    def findElements(segment, index, multiplier, side):
        # finding elements
        elementsAndNumbers = re.split('([A-Z][a-z]?)', segment)
        i = 0
        while (i < len(elementsAndNumbers) - 1):  # last element always blank
            i += 1
            if (len(elementsAndNumbers[i]) > 0):
                if (elementsAndNumbers[i + 1].isdigit()):
                    count = int(elementsAndNumbers[i + 1]) * multiplier
                    addToMatrix(elementsAndNumbers[i], index, count, side)
                    i += 1
                else:
                    addToMatrix(elementsAndNumbers[i], index, multiplier, side)

    def compoundDecipher(compound, index, side):
        # splitting compounds
        segments = re.split('(\([A-Za-z0-9]*\)[0-9]*)', compound)
        for segment in segments:
            if segment.startswith("("):
                segment = re.split('\)([0-9]*)', segment)
                multiplier = int(segment[1])
                segment = segment[0][1:]
            else:
                multiplier = 1
            findElements(segment, index, multiplier, side)

    if request.method=="GET":
        # if method is GET, we'll render the page
        return render(request, 'home.html',)
    if request.method=="POST":
        # if request method is POST, we'll balance the equation
        # getting reactsants & products
        reactants = request.POST.get('reactants')
        products = request.POST.get('products')
        
        # replacing spaces & splitting from +
        reactants = reactants.replace(' ', '').split("+")
        products = products.replace(' ', '').split("+")
    
    # deciphering compounds & creating count matrix
    for i in range(len(reactants)):
        compoundDecipher(reactants[i], i, 1)
    for i in range(len(products)):
        compoundDecipher(products[i], i + len(reactants), -1)

    # balancing logic
    elementMatrix = Matrix(elementMatrix)
    elementMatrix = elementMatrix.transpose()
    solution = elementMatrix.nullspace()[0]
    multiple = lcm([val.q for val in solution])
    solution = multiple * solution
    coEffi = solution.tolist()
    output = ""
    # creating reactants side
    for i in range(len(reactants)):
        output += str(coEffi[i][0]) + reactants[i] if coEffi[i][0] >1 else reactants[i]
        if i < len(reactants) - 1:
            output += " + "
    
    # adding separator
    output += " -> "

    # adding product side
    for i in range(len(products)):
        output += str(coEffi[i + len(reactants)][0]) + products[i] if coEffi[i + len(reactants)][0]>1 else products[i]
        if i < len(products) - 1:
            output += " + "
    
    # rendering the output string
    return render(request,'home.html', {"output":output})

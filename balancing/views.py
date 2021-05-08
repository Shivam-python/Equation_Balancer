from django.shortcuts import render
import re
from django.views import View
from sympy import Matrix,lcm





def Home(request):
    elementList = []
    elementMatrix = []
    def addToMatrix(element, index, count, side):
        if (index == len(elementMatrix)):
            elementMatrix.append([])
            for x in elementList:
                elementMatrix[index].append(0)
        if (element not in elementList):
            elementList.append(element)
            for i in range(len(elementMatrix)):
                elementMatrix[i].append(0)
        column = elementList.index(element)
        elementMatrix[index][column] += count * side

    def findElements(segment, index, multiplier, side):
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
        return render(request, 'home.html',)
    if request.method=="POST":

        reactants = request.POST.get('reactants')
        products = request.POST.get('products')
        reactants = reactants.replace(' ', '').split("+")
        products = products.replace(' ', '').split("+")
    for i in range(len(reactants)):
        compoundDecipher(reactants[i], i, 1)
    for i in range(len(products)):
        compoundDecipher(products[i], i + len(reactants), -1)
    elementMatrix = Matrix(elementMatrix)
    elementMatrix = elementMatrix.transpose()
    solution = elementMatrix.nullspace()[0]
    multiple = lcm([val.q for val in solution])
    solution = multiple * solution
    coEffi = solution.tolist()
    output = ""
    for i in range(len(reactants)):
        output += str(coEffi[i][0]) + reactants[i] if coEffi[i][0] >1 else reactants[i]
        if i < len(reactants) - 1:
            output += " + "
    output += " -> "
    for i in range(len(products)):
        output += str(coEffi[i + len(reactants)][0]) + products[i] if coEffi[i + len(reactants)][0]>1 else products[i]
        if i < len(products) - 1:
            output += " + "
    return render(request,'home.html', {"output":output})

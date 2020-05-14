
def fixPosition(elementList):
    for innerIndex, s in enumerate(elementList):
        s.position = innerIndex
        s.save()

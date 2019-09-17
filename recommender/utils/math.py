
def take_closest(x, ls):
  '''Selects the element from the list that is closest to the given element.'''
  min(ls, key=lambda y:abs(x-y))

def take_smallest_closest(x, ls):
  '''Selects the closest element that is equal or smaller as the given element.'''
  return min(ls, key=lambda y:x-y if y<=x else x+1)

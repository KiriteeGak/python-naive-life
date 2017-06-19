def distance(point1, point2):
	return round(reduce(lambda a,b : a+b ,list(map(lambda x : x**2, list(point1-point2)))),3)
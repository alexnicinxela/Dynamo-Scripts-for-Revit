import clr
clr.AddReference("RevitAPI")
from Autodesk.Revit.DB import *

clr.AddReference("RevitNodes")

import Revit
clr.ImportExtensions(Revit.Elements)
from Revit.Elements import * 
clr.ImportExtensions(Revit.GeometryConversion)
clr.ImportExtensions(Revit.GeometryReferences)

clr.AddReference("RevitServices")
import RevitServices
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

doc = DocumentManager.Instance.CurrentDBDocument

elems = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Windows).WhereElementIsNotElementType().ToElements()
holes = []
for elem in elems:
	if elem.Name == "Отверстие_Стена":
		holes.append(elem)

count = 0
err = 0
err_hole = []
done_hole = []

TransactionManager.Instance.EnsureInTransaction(doc)	

for hole in holes:
	min_point = format((hole.Location.Point.Z * 304.8)/1000, '.3f')
	height_hole = hole.LookupParameter("Высота нижнего бруса").AsDouble()
	try: 
		hole.LookupParameter("Рзм.СмещениеОтУровня").Set(height_hole)
		hole.LookupParameter("FU_Отметка низа").Set("+{}".format(min_point))
		count += 1
		done_hole.append(hole)
	except: 
		err += 1
		err_hole.append(hole)
	
TransactionManager.Instance.TransactionTaskDone()

OUT = "Обработано окон: {}".format(count), done_hole, "Ошибок: {}".format(err), err_hole

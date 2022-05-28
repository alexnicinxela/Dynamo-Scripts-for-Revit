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

param = IN[1]
value = IN[2]
new_value = IN[3]
done = []
err = []
elems = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Doors).WhereElementIsNotElementType().ToElements()

TransactionManager.Instance.EnsureInTransaction(doc)	

for elem in elems:
	try: elem_param = elem.LookupParameter(param).AsString()
	except: continue
	
	if elem_param == value:
		try: 
			elem.LookupParameter(param).Set(new_value)
			done.append(elem)
		except:
			err.append(elem)
				
TransactionManager.Instance.TransactionTaskDone()

OUT = "Обработано {} дверей.".format(len(done)+len(err)),"\nУспешно:", done, "\nС ошибкой:", err




import clr
clr.AddReference("RevitAPI")
from Autodesk.Revit.DB import *
clr.AddReference("RevitServices")
import RevitServices
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

doc = DocumentManager.Instance.CurrentDBDocument

def create_type_names(elems):
	type_names = {}
	for elem in elems:
		type_name = elem.Name
		if type_name not in type_names:
			type_names[type_name] = []
	return type_names
	
doors = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Doors).WhereElementIsNotElementType().ToElements()
type_names = create_type_names(doors) #создание словаря типов
room_names = [] #список имен помещений, в которые ведут двери
errors = [] #список дверей, которые не удовлетворяют условиям

TransactionManager.Instance.EnsureInTransaction(doc)

for type_name in type_names: #сортировка дверей по типоразмеру
	for door in doors:
		if door.Name == type_name:
			type_names[type_name].append(door)
			try:
				phase_id = door.CreatedPhaseId # Получаем Id стадии в которой была создана дверь
				phase = doc.GetElement(phase_id) # получаем саму стадию
				to_room = door.ToRoom[phase] # помещение, в которое ведет дверь
				room_name = to_room.get_Parameter(BuiltInParameter.ROOM_NAME).AsString()
				if room_name not in room_names:
					room_names.append(room_name)
			except:
				errors.append(door)
	for door in type_names[type_name]:
		loc = door.LookupParameter('FU_Расположение')
		loc.Set(', '.join(room_names))
		
	room_names.Clear()

OUT = errors
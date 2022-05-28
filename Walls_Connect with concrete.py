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

#---------------------------------------------------------
"""
def GetSolids(elems):
	solid_repos = []
	for elem in elems:
		geom = elem.get_Geometry(Options())
		for g in geom:
			if g.ToString() == "Autodesk.Revit.DB.Solid" and g.Volume != 0:
				solid_repos.append(g)
			else:
				continue
	return solid_repos

def GetSolid(elem):
	geom = elem.get_Geometry(Options())
	for g in geom:
		if g.ToString() == "Autodesk.Revit.DB.Solid" and g.Volume != 0:
			solid = g
	return solid
"""

#---------------------------------------------------------
doc = DocumentManager.Instance.CurrentDBDocument
#---------------------------------------------------------

walls = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Walls).WhereElementIsNotElementType().ToElements()
brick_walls = []
concrete_walls = []
pgp_walls = []
other_walls = []

for wall in walls:
	material_ids = wall.GetMaterialIds(False)
	for material_id in material_ids:
		material = doc.GetElement(material_id)
		if 'Кладка_Кирпич' in material.Name:
			brick_walls.append(wall)
		elif 'Кладка_Плиты' in material.Name:
			pgp_walls.append(wall)
		elif 'Бетон' in material.Name:
			concrete_walls.append(wall)
		else:
			other_walls.append(wall)	
			
total_walls = brick_walls + pgp_walls
inter_walls = concrete_walls + pgp_walls

value_intsect = []
for t_wall in total_walls:
	tw_len = t_wall.get_Parameter(BuiltInParameter.CURVE_ELEM_LENGTH).AsDouble() * 304.8
	tw_high = t_wall.get_Parameter(BuiltInParameter.WALL_USER_HEIGHT_PARAM).AsDouble() * 304.8
	side = tw_high // 1000 + 1
	if side > 1: side = side
	else: side = 2
	top = tw_len // 1000 + 1
	if top > 1: top = top
	else: top = 2
		
	tw_geom = t_wall.get_Geometry(Options())
	for twg in tw_geom:
		if twg.ToString() == "Autodesk.Revit.DB.Solid" and twg.Volume != 0:
			tw_solid = twg
	tws_area = tw_solid.SurfaceArea
	count = 0
	
	for i_wall in inter_walls:
		iw_geom = i_wall.get_Geometry(Options())
		for iwg in iw_geom:
			if iwg.ToString() == "Autodesk.Revit.DB.Solid" and iwg.Volume != 0:
				iw_solid = iwg
		iws_area = iw_solid.SurfaceArea
		int_area = BooleanOperationsUtils.ExecuteBooleanOperation(tw_solid, iw_solid, BooleanOperationsType.Union).SurfaceArea
		if round(tws_area + iws_area, 5) > round(int_area, 5):
			if (t_wall in brick_walls and i_wall in concrete_walls) or (t_wall in pgp_walls and i_wall in concrete_walls) or (t_wall in pgp_walls and i_wall in pgp_walls):
				count += 1
			

	TransactionManager.Instance.EnsureInTransaction(doc)
	
	if t_wall in brick_walls:
		value_intsect.append(['Кирпич', t_wall, count])
		if count == 0:
			t_wall.LookupParameter('FU_Арм.стержни для крепления кладки_Количество').Set(top)
		elif count == 1 and t_wall.Width*304.8 < 130:
			t_wall.LookupParameter('FU_Арм.стержни для крепления кладки_Количество').Set(top + side)
		elif count > 1  and t_wall.Width*304.8 < 130:
			t_wall.LookupParameter('FU_Арм.стержни для крепления кладки_Количество').Set(top + side*2)
		elif count == 1 and t_wall.Width*304.8 >= 130:
			t_wall.LookupParameter('FU_Арм.стержни для крепления кладки_Количество').Set(top + side*2)
		elif count > 1 and t_wall.Width*304.8 >= 130:
			t_wall.LookupParameter('FU_Арм.стержни для крепления кладки_Количество').Set(top + side*4)
	
	if t_wall in pgp_walls:
		value_intsect.append(['ПГП', t_wall, count])
		t_wall.LookupParameter('FU_Монтажная лента для крепления кладки_Количество').Set(top)
		if count == 1 and t_wall.Width*304.8 < 130:
			t_wall.LookupParameter('FU_Арм.стержни для крепления кладки_Количество').Set(side)
		elif count > 1  and t_wall.Width*304.8 < 130:
			t_wall.LookupParameter('FU_Арм.стержни для крепления кладки_Количество').Set(side*2)
		elif count == 1 and t_wall.Width*304.8 >= 130:
			t_wall.LookupParameter('FU_Арм.стержни для крепления кладки_Количество').Set(side*2)
		elif count > 1  and t_wall.Width*304.8 >= 130:
			t_wall.LookupParameter('FU_Арм.стержни для крепления кладки_Количество').Set(side*4)
		
	TransactionManager.Instance.TransactionTaskDone()

OUT = value_intsect

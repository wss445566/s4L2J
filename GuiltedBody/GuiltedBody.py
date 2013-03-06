from com.l2jserver.gameserver.scripting.scriptengine.impl import L2Script
from com.l2jserver.gameserver.model import L2World
from com.l2jserver.gameserver.model.items.type import L2ArmorType

class Quest(L2Script):
	qn = "GuiltedBody"
	qDesc = "custom"

	def __init__(self, name = qn, descr = qDesc):
		self.qn, self.qDesc = name, descr
		L2Script.__init__(self, name, descr)
		self.addEquipmentNotify(None)
		print '%s loaded' % self.qn
		
	def onItemEquip(self, event):
		item = event.getItem()
		if item == None:
			return False
		playeroid = item.getOwnerId()
		if playeroid == None:
			return False
		player = L2World.getInstance().getPlayer(playeroid)
		if player == None:
			return False
		if event.isEquipped():
			aitem = item.getArmorItem()
			if aitem == None:
				return True
			if aitem.getItemType() in [L2ArmorType.HEAVY, L2ArmorType.MAGIC]:
				if player.getSkillLevel(462) != -1:
					return False
		return True
Quest()

from com.l2jserver.gameserver.model.conditions import Condition
from com.l2jserver.gameserver.model.stats import Env
from com.l2jserver.gameserver.datatables import ItemTable

class MyCondition(Condition):
	weapon_id = 3937
	require_item_id = 57
	require_item_count = 1
	
	def __init__(self, item_id, req_item_id, req_item_count):
		self.weapon_id, self.require_item_id, self.require_item_count = [item_id, req_item_id, req_item_count]
		item = ItemTable.getInstance().getTemplate(self.weapon_id)
		if item:
			item.attach(self)
		else:
			print "no item id " + str(self.weapon_id)
			return
		print "item id " + str(self.weapon_id) + " modified"

	def testImpl(self, env):
		inv = env.player.getInventory()
		if inv:
			for item in inv.getItems():
				if item.getItemId() == self.require_item_id and item.getCount() >= self.require_item_count:
					return True
		return False

for item_id, req_item_id, req_item_count in [[3937,57,1],[3938,5575,1]]:
	MyCondition(item_id, req_item_id, req_item_count)

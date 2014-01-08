import sys
from com.l2jserver.gameserver.model.quest		import State
from com.l2jserver.gameserver.model.quest		import QuestState
from com.l2jserver.gameserver.model.quest.jython	import QuestJython as JQuest

from com.l2jserver.gameserver.model.items.instance.L2ItemInstance import ItemLocation
from com.l2jserver.gameserver.datatables import ItemTable
from com.l2jserver.gameserver.network.serverpackets import SystemMessage
from com.l2jserver.gameserver.network import SystemMessageId
from com.l2jserver.gameserver.network.serverpackets import EnchantResult
from com.l2jserver.gameserver.network.serverpackets import StatusUpdate
from com.l2jserver.gameserver.network.serverpackets import ItemList
from com.l2jserver.util import Rnd

class MergeEnchance(JQuest):
	qID = -1				#quest id 預設值
	qn = "mergeEnchant"		#quest 名稱 預設值
	qDesc = "custom"		#quest 描述 預設值
	
	NPCID = 100				#觸發任務的 NPC
	
	htm_header = "<html><body><title>合拼強化</title>"
	htm_footer = "</body></html>"
	htm_select_part = """把要強化的物品裝備好, 選擇要強化的部位<BR>
	<a action="bypass -h Quest %(qn)s head">頭類</a><BR1>
	<a action="bypass -h Quest %(qn)s fullarmor">上下連身類</a><BR1>
	<a action="bypass -h Quest %(qn)s chest">上身類</a><BR1>
	<a action="bypass -h Quest %(qn)s legs">下身類</a><BR1>
	<a action="bypass -h Quest %(qn)s gloves">手套類</a><BR1>
	<a action="bypass -h Quest %(qn)s feet">鞋類</a><BR1>
	<a action="bypass -h Quest %(qn)s rhand">單手武器</a><BR1>
	<a action="bypass -h Quest %(qn)s lrhand">雙手武器</a><BR1>
	<a action="bypass -h Quest %(qn)s lhand">盾/符類</a><BR1>
	"""
	htm_show_2nd_item = """<a action="bypass -h Quest %(qn)s %(tmp)s">%(tmp2)s</a><BR>"""
	
	bodypart = {
		"head":ItemTable._slots.get("head")
		,"fullarmor":ItemTable._slots.get("fullarmor")
		,"chest":ItemTable._slots.get("chest")
		,"legs":ItemTable._slots.get("legs")
		,"gloves":ItemTable._slots.get("gloves")
		,"feet":ItemTable._slots.get("feet")
		,"lhand":ItemTable._slots.get("lhand")
		,"rhand":ItemTable._slots.get("rhand")
		,"lrhand":ItemTable._slots.get("lrhand")
	}

	def firstpage(self, **kv):
		return self.htm_header + self.htm_select_part + self.htm_footer

	def __init__(self, id = qID, name = qn, descr = qDesc):
		self.qID, self.qn, self.qDesc = id, name, descr
		JQuest.__init__(self, id, name, descr)
		self.addStartNpc(self.NPCID)
		self.addFirstTalkId(self.NPCID)
		self.addTalkId(self.NPCID)
		self.htm_select_part = self.htm_select_part % {"qn":self.qn}
		self.htm_show_2nd_item = self.htm_show_2nd_item % {"qn":self.qn, "tmp":"%d_%d", "tmp2":"%s"}
		print "Init:" + self.qn + " loaded"

	def getEquItem(self, player, bodypart):
		return [x for x in player.getInventory().getItems() if x.getLocation() == ItemLocation.PAPERDOLL and x.getItem().getBodyPart() == bodypart]
		
	def getInvItemById(self, player, item_id):
		return [x for x in player.getInventory().getItems() if x.getLocation() == ItemLocation.INVENTORY and x.getItemId() == item_id]
	
	def check(self, player, item1, item2):
		if not item1: return False
		if not item2: return False
		if item1.getOwnerId() != player.getObjectId():return False
		if item2.getOwnerId() != player.getObjectId():return False
		if not item1.isEnchantable(): return False
		return True
		
	def merge(self, player, item1, item2):
		inv = player.getInventory()
		item1 = inv.getItemByObjectId(int(item1))
		item2 = inv.getItemByObjectId(int(item2))
		if not self.check(player, item1, item2):
			return self.htm_header + "指定的道具出問題<BR>請確定道具能強化" + self.htm_footer
		enchant2 = item2.getEnchantLevel()
		inv.destroyItem(self.qn, item2, player, item2)
		item1.setEnchantLevel(item1.getEnchantLevel()+Rnd.get(enchant2+1))
		item1.updateDatabase()
		player.sendPacket(EnchantResult(0, 0, 0))
		sm = SystemMessage.getSystemMessage(SystemMessageId.C1_SUCCESSFULY_ENCHANTED_A_S2_S3);
		sm.addCharName(player)
		sm.addNumber(item1.getEnchantLevel())
		sm.addItemName(item1)
		player.sendPacket(sm)		
		su = StatusUpdate(player)
		su.addAttribute(StatusUpdate.CUR_LOAD, player.getCurrentLoad())
		player.sendPacket(su)
		player.sendPacket(ItemList(player, False));
		player.broadcastUserInfo()
		return self.htm_header + "恭喜! 合拼強化成功<BR>"+ self.htm_select_part + self.htm_footer
		
	def onAdvEvent(self, event, npc, player):
		if event in self.bodypart:
			frist_item = self.getEquItem(player, self.bodypart[event])
			if len(frist_item):
				r = "將要強化的道具:%s +%d<BR>" % (frist_item[0].getItemName(), frist_item[0].getEnchantLevel())
				items = self.getInvItemById(player, frist_item[0].getItemId())
				if len(items):
					r += "背包內有以下犧牲道具可作為合拼之用.<BR1>合拼後選擇的犧牲道具會消失<BR1>合拼後的強化等級 = 裝備道具強化等級 + 隨機值<BR1> 隨機值 = 0 至 (犧牲道具強化等級)<BR1>所以別拿 +0 的來合拼啊<BR>"
					for item in items:
						r += self.htm_show_2nd_item % (frist_item[0].getObjectId(), item.getObjectId(), "%s +%d" % (item.getItemName(), item.getEnchantLevel()))
				else:
					r += "背包內沒有相同的道具作為合拼強化之用"
				return self.htm_header + r + self.htm_footer
			return self.htm_header + "請先裝備要強化的道具" + self.htm_footer
		else:
			item1, item2 = event.split("_")
			return self.merge(player, item1, item2)
			
		
	def onFirstTalk(self, npc, player):
		return self.firstpage()
		
MergeEnchance()

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
from com.l2jserver.gameserver.model.itemcontainer import Inventory

class MergeEnchance(JQuest):
	qID = -1				#quest id 預設值
	qn = "mergeEnchant"		#quest 名稱 預設值
	qDesc = "custom"		#quest 描述 預設值
	
	NPCID = 100				#觸發任務的 NPC
	chance = 50			#強化成功機率 100 = 100% 必定成功
	requirements = [[57,1]]	#所需道具 [[道具ID, 數量],[道具ID, 數量],[道具ID, 數量]] 或 [] = 不用扣道具
	
	htm_header = "<html><body><title>合拼強化</title>"
	htm_footer = "</body></html>"
	htm_select_part = """把要強化的物品裝備好, 選擇要強化的部位<BR>
	<a action="bypass -h Quest %(qn)s head">頭盔</a><BR1>
	<a action="bypass -h Quest %(qn)s chest">胸甲</a><BR1>
	<a action="bypass -h Quest %(qn)s legs">脛甲</a><BR1>
	<a action="bypass -h Quest %(qn)s gloves">手套</a><BR1>
	<a action="bypass -h Quest %(qn)s feet">靴子</a><BR1>
	<a action="bypass -h Quest %(qn)s rhand">武器</a><BR1>
	<a action="bypass -h Quest %(qn)s lhand">盾牌/符印</a><BR1>
	<a action="bypass -h Quest %(qn)s lear">左耳</a><BR1>
	<a action="bypass -h Quest %(qn)s rear">右耳</a><BR1>
	<a action="bypass -h Quest %(qn)s neck">項鍊</a><BR1>
	<a action="bypass -h Quest %(qn)s lfinger">左戒</a><BR1>
	<a action="bypass -h Quest %(qn)s rfinger">右戒</a><BR1>
	<a action="bypass -h Quest %(qn)s underwear">襯衫</a><BR1>
	<a action="bypass -h Quest %(qn)s belt">腰帶</a><BR1>
	<a action="bypass -h Quest %(qn)s back">斗蓬</a><BR1>
	"""
	htm_show_2nd_item = """<a action="bypass -h Quest %(qn)s %(tmp)s">%(tmp2)s</a><BR>"""
	
	bodypart = {
		"head":Inventory.PAPERDOLL_HEAD
		,"chest":Inventory.PAPERDOLL_CHEST
		,"legs":Inventory.PAPERDOLL_LEGS
		,"gloves":Inventory.PAPERDOLL_GLOVES
		,"feet":Inventory.PAPERDOLL_FEET
		,"lhand":Inventory.PAPERDOLL_LHAND
		,"rhand":Inventory.PAPERDOLL_RHAND
		,"lear":Inventory.PAPERDOLL_LEAR
		,"rear":Inventory.PAPERDOLL_REAR
		,"neck":Inventory.PAPERDOLL_NECK
		,"lfinger":Inventory.PAPERDOLL_LFINGER
		,"rfinger":Inventory.PAPERDOLL_RFINGER
		,"belt":Inventory.PAPERDOLL_BELT
		,"back":Inventory.PAPERDOLL_CLOAK
		,"underwear":Inventory.PAPERDOLL_UNDER
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
		item = player.getInventory().getPaperdollItem(bodypart)
		if item:
			return[item]
		return []
		
	def getInvItemById(self, player, item_id):
		return [x for x in player.getInventory().getItems() if x.getLocation() == ItemLocation.INVENTORY and x.getItemId() == item_id]
	
	def check(self, player, item1, item2):
		if not item1: return False
		if not item2: return False
		if item1.getOwnerId() != player.getObjectId():return False
		if item2.getOwnerId() != player.getObjectId():return False
		if not item1.isEnchantable(): return False
		return True
	
	def removeRequirement(self, player):
		for itemid, count in self.requirements:
			if self.getQuestItemsCount(player, itemid) < count:
				return False
	
		for itemid, count in self.requirements:
			if not player.destroyItemByItemId(self.qn, itemid, count, None, True):
				return False
		return True

	def updatePlayerInfo(self, player):
		su = StatusUpdate(player)
		su.addAttribute(StatusUpdate.CUR_LOAD, player.getCurrentLoad())
		player.sendPacket(su)
		player.sendPacket(ItemList(player, False));
		player.broadcastUserInfo()
		
	def merge(self, player, item1OID, item2OID):
		inv = player.getInventory()
		item1 = inv.getItemByObjectId(int(item1OID))
		item2 = inv.getItemByObjectId(int(item2OID))
		if not self.check(player, item1, item2):
			return self.htm_header + "指定的道具出問題<BR>請確定道具能強化" + self.htm_footer
		if not self.removeRequirement(player):
			return self.htm_header + "需要金幣1個" + self.htm_footer
		item1enclvl = item1.getEnchantLevel()
		item2enclvl = item2.getEnchantLevel()
		enchant2 = item2.getEnchantLevel()
		inv.destroyItem(self.qn, item2, player, item2)
		if Rnd.get(100) > self.chance:
			self.updatePlayerInfo(player)
			return self.htm_header + "<font color=FF0000>合拼強化機率性失敗</font><BR>" + self.htm_select_part + self.htm_footer
		item1.setEnchantLevel(item1.getEnchantLevel()+Rnd.get(enchant2+1))
		item1.updateDatabase()
		player.sendPacket(EnchantResult(0, 0, 0))
		sm = SystemMessage.getSystemMessage(SystemMessageId.C1_SUCCESSFULY_ENCHANTED_A_S2_S3);
		sm.addCharName(player)
		sm.addNumber(item1.getEnchantLevel())
		sm.addItemName(item1)
		player.sendPacket(sm)
		self.updatePlayerInfo(player)
		return self.htm_header + "<font color=FFFF00>恭喜! 合拼強化成功 強化度由 +%d 變為 +%d</font><BR>" % (item1enclvl, item1.getEnchantLevel()) + self.htm_select_part + self.htm_footer
		
	def onAdvEvent(self, event, npc, player):
		if event in self.bodypart:
			frist_item = self.getEquItem(player, self.bodypart[event])
			if len(frist_item):
				r = "將要強化的道具:%s +%d<BR1>" % (frist_item[0].getItemName(), frist_item[0].getEnchantLevel())
				items = self.getInvItemById(player, frist_item[0].getItemId())
				r += "<font color=00FF00>將要收取金幣1個作為強化費用</font><BR>"
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

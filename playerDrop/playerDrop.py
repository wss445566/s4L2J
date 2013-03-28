from com.l2jserver.gameserver.model.quest.jython import QuestJython as JQuest
from com.l2jserver import Config
from com.l2jserver.gameserver.model.items.type import L2WeaponType
from com.l2jserver.gameserver.model.items.type import L2ArmorType
from com.l2jserver.gameserver.model.items.type import L2EtcItemType

class Quest(JQuest):
	qID = -1
	qn = "playerDrop"
	qDesc = "custom"
	
	#觸發 NPC ID
	NPCID = 100
	
	#白名單 名單內的物品 ID 不會掉落, 不會列出
	#預設 金幣 古代的金幣 慶典金幣 藍色伊娃 金色殷海薩 銀色席琳 血紅色帕格立歐 夢幻島代幣 金塊 活動-光彩紀念章
	whiteList = [57, 5575, 6673, 4355, 4356, 4357, 4358, 13067, 3470, 6393]
	#白名單 加入 D 至 R 級結晶
	whiteList += [1458, 1459, 1460, 1461, 1462, 17371]
	
	#允許 武器 列出/掉落/刪除
	isAllowWeaponDrop = True
	#允許 防具 列出/掉落/刪除
	isAllowArmorDrop = True
	#允許 強化卷 列出/掉落/刪除
	isAllowScrollEnchanceDrop = True
	#允許 含技能道具 列出/掉落/刪除
	isAllowHasSkillItemDrop = True
	
	
	#檢測物品可否掉落屬性
	checkDropable = True #False
	
	#一頁列出多少物品
	itemsPerPage = 10
	
	html_header = "<html><body><title>清空背包物品</title>"
	html_footer = "</body></html>"
	html_after_drop = "你有 15秒 優先權 撿回物品<br1>"
	html_disappear = "地上的物品將於 %d 秒後消失(部份物品除外)<br1>" % (Config.AUTODESTROY_ITEM_AFTER,)
	html_drop_all = """<a action="bypass -h Quest %(qn)s drop">點擊掉落背包內所有物品</a><br1>""" % {"qn":qn}
	html_drop_quest = """<a action="bypass -h Quest %(qn)s delQuestItems">點擊刪除所有任務道具</a><br1>""" % {"qn":qn}
	html_foreach_item = """<tr><td><a action="bypass -h Quest %(qn)s dropone %(itemid)d">掉落</a></td><td><a action="bypass -h Quest %(qn)s delone %(itemid)d">刪除</a></td><td>%(itemname)s</td></tr><br1>"""
	html_prev_page = """<a action="bypass -h Quest %s list %d">上一頁</a>"""
	html_next_page = """<a action="bypass -h Quest %s list %d">下一頁</a>"""
	html_drop_one_intro = "以下連結 點擊掉落<br1>"
	
	def __init__(self, id = qID, name = qn, descr = qDesc):
		self.qID, self.qn, self.qDesc = id, name, descr
		JQuest.__init__(self, id, name, descr)
		self.addStartNpc(self.NPCID)
		self.addFirstTalkId(self.NPCID)
		self.addTalkId(self.NPCID)
		print "Init:" + self.qn + " loaded"

	def onFirstTalk(self, npc, player):
		return self.html_header + self.html_drop_all + self.html_drop_quest + self.list(player) + self.html_footer

	def onAdvEvent(self, event, npc, player):
		if event == "delQuestItems":
			return self.delQuestItems(npc, player)
		if event == "drop":
			return self.drop(player)
		if event.startswith("dropone "):
			return self.dropone(npc, player, int(event[8:]))
		if event.startswith("delone "):
			return self.delone(npc, player, int(event[7:]))
		if event.startswith("list "):
			try:
				page = int(event[len("list "):])
			except:
				return
			return self.html_header + self.html_drop_all + self.html_drop_quest + self.list(player, page) + self.html_footer

	def dropone(self, npc, player, oid):
		item = player.getInventory().getItemByObjectId(oid)
		player.dropItem(self.qn, item, None, False, True)
		return self.onFirstTalk(npc, player)

	def delone(self, npc, player, oid):
		item = player.getInventory().getItemByObjectId(oid)
		player.destroyItem(self.qn, item, None, True)
		return self.onFirstTalk(npc, player)
		
	def check(self, item):
		if item.getItemId() in self.whiteList: return False
		if item.isEquipped(): return False
		if self.checkDropable and not item.isDropable(): return False
		if not self.isAllowWeaponDrop and item.isWeapon(): return False
		if not self.isAllowArmorDrop and item.isArmor(): return False
		if not self.isAllowScrollEnchanceDrop and item.getItemType() in [L2EtcItemType.SCRL_ENCHANT_WP, L2EtcItemType.SCRL_ENCHANT_AM, L2EtcItemType.BLESS_SCRL_ENCHANT_WP, L2EtcItemType.BLESS_SCRL_ENCHANT_AM, L2EtcItemType.SCRL_INC_ENCHANT_PROP_WP, L2EtcItemType.SCRL_INC_ENCHANT_PROP_AM, L2EtcItemType.ANCIENT_CRYSTAL_ENCHANT_WP, L2EtcItemType.ANCIENT_CRYSTAL_ENCHANT_AM]: return False
		if not self.isAllowHasSkillItemDrop and item.getItem().hasSkills(): return False
		return True
		
	def drop(self, player):
		r = ""
		for item in [x for x in player.getInventory().getItems() if self.check(x)]:
			player.dropItem(self.qn, item, None, False, True)
		if Config.DESTROY_DROPPED_PLAYER_ITEM and Config.AUTODESTROY_ITEM_AFTER > 0:
			r = r + self.html_disappear
		r = r + self.html_after_drop
		return self.html_header + r + self.html_footer
		
	def delQuestItems(self, npc, player):
		for item in [x for x in player.getInventory().getItems() if x.isQuestItem()]:
			player.destroyItem(self.qn, item, None, True)
		return self.onFirstTalk(npc, player)
		
		
	def list(self, player, page=1):
		r = self.html_drop_one_intro
		if page > 1:
			r += self.html_prev_page % (self.qn, page - 1)
		r += " 第 %d 頁 " % page
		r += self.html_next_page % (self.qn, page + 1)
		r = r + "<table>"
		index = 0
		startItemIndex = (page-1) * self.itemsPerPage
		for item in [x for x in player.getInventory().getItems() if self.check(x)]:
			if startItemIndex <= index < startItemIndex + self.itemsPerPage:
				r = r + self.html_foreach_item % {"qn":self.qn, "itemname":item.getName(), "itemid":item.getObjectId()}
			index = index + 1
		r = r + "</table>"
		return r
Quest()

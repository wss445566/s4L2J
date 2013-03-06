import sys
from com.l2jserver.gameserver.model.quest		import State
from com.l2jserver.gameserver.model.quest		import QuestState
from com.l2jserver.gameserver.model.quest.jython	import QuestJython as JQuest

import _codecs
try:
	from com.l2jserver.gameserver.datatables import EnchantItemTable
except:
	from com.l2jserver.gameserver.datatables import EnchantItemData as EnchantItemTable
from com.l2jserver.util import Rnd

from com.l2jserver.gameserver.network import SystemMessageId
from com.l2jserver.gameserver.network.serverpackets import InventoryUpdate
from com.l2jserver.gameserver.network.serverpackets import EnchantResult
from com.l2jserver.gameserver.util import Util
from com.l2jserver import Config
from com.l2jserver.gameserver.model import L2World
from com.l2jserver.gameserver.network.serverpackets import SystemMessage
from com.l2jserver.gameserver.network.serverpackets import StatusUpdate
from com.l2jserver.gameserver.network.serverpackets import ItemList
from com.l2jserver.gameserver.model.items import L2Item
from com.l2jserver.gameserver.datatables import SkillTable
from com.l2jserver.gameserver.network.serverpackets import MagicSkillUse

class ItemNameTable:
	itemNameTable = {}
	def __init__(self):
		f = open("data/scripts/custom/easyEnchant/itemname-tw.txt", "r")
		f.readline()
		for line in f:
			temp = line.split("\t")
			if temp[0].isdigit():
				self.itemNameTable[int(temp[0])] = [_codecs.utf_8_decode(temp[1])[0],_codecs.utf_8_decode(temp[2])[0]]
		f.close()

	def getTable(self):
		return self.itemNameTable
			
	def getName(self, id):
		assert type(id) == type(0)
		return self.itemNameTable[id][0]

	def getAddName(self, id):
		assert type(id) == type(0)
		return self.itemNameTable[id][1]

class EasyEnchance(JQuest):
	qID = -1
	qn = "easyEnchant"
	qDesc = "custom"
	
	maxWpEnchantLevel = 300 #武器強化上限
	maxAmEnchantLevel = 300 #防具強化上限
	maxRenEnchantLevel = 300 #飾品強化上限
	
	canEnchantZero = True #強化失敗 會否歸 0
	canDestory = True #強化失敗 會否變結晶
	
	isEnchantToSafe = True #是否自動強化至安定值
	
	enchant_lv_notify = [10,20,30,40,50] #強化成功後 指定等級才廣播文字訊息給其他玩家
	canFireWorks = True #廣播時是否放煙火

	# 武卷 D 955 C 951 B 947 A 729 S 959
	# 防卷 D 956 C 952 B 948 A 730 S 960
	# 祝武 D 6575 C 6573 B 6571 A 6569 S 6577
	# 祝防 D 6576 C 6574 B 6572 A 6570 S 6578
	custom_chance = {955:99, 951:98, 947:97, 729:96, 959:95, 956:99, 952:98, 948:97, 730:96, 960:95} # 可指定某一強化卷的機率, 沒有指定的使用系統預設{卷ID:機率, 卷ID:機率}
	isCustomChance = False #是否使用腳本自訂強化機率 True False
	
	command_split_char = "_#_"
	
	NPCID = [102] #觸發任務的 NPC 可修改.. 可以多 ID 例如 [100,102,103]
	htm_header = "<html><body><title>簡易強化</title>"
	htm_footer = "</body></html>"

	htm_menu_search = "<table><tr><td><edit var=\"value\" width=140 height=12></td><td><button value=\"搜尋\" width=50 height=20  action=\"bypass -h Quest %(qn)s list $value\"></td></tr></table>" % {"qn":qn}
	htm_menu_list_n = "<tr><td>普級</td><td><a action=\"bypass -h Quest %(qn)s list +gn +wp\">武器</a></td><td><a action=\"bypass -h Quest %(qn)s list +gn +am -ren\">防具</a></td><td><a action=\"bypass -h Quest %(qn)s list +gn +ren\">飾品</a></td><td><a action=\"bypass -h Quest %(qn)s list +gn\">全部</a></td></tr>" % {"qn":qn}
	htm_menu_list_d = "<tr><td>D級</td><td><a action=\"bypass -h Quest %(qn)s list +gd +wp\">武器</a></td><td><a action=\"bypass -h Quest %(qn)s list +gd +am -ren\">防具</a></td><td><a action=\"bypass -h Quest %(qn)s list +gd +ren\">飾品</a></td><td><a action=\"bypass -h Quest %(qn)s list +gd\">全部</a></td></tr>" % {"qn":qn}
	htm_menu_list_c = "<tr><td>C級</td><td><a action=\"bypass -h Quest %(qn)s list +gc +wp\">武器</a></td><td><a action=\"bypass -h Quest %(qn)s list +gc +am -ren\">防具</a></td><td><a action=\"bypass -h Quest %(qn)s list +gc +ren\">飾品</a></td><td><a action=\"bypass -h Quest %(qn)s list +gc\">全部</a></td></tr>" % {"qn":qn}
	htm_menu_list_b = "<tr><td>B級</td><td><a action=\"bypass -h Quest %(qn)s list +gb +wp\">武器</a></td><td><a action=\"bypass -h Quest %(qn)s list +gb +am -ren\">防具</a></td><td><a action=\"bypass -h Quest %(qn)s list +gb +ren\">飾品</a></td><td><a action=\"bypass -h Quest %(qn)s list +gb\">全部</a></td></tr>" % {"qn":qn}
	htm_menu_list_a = "<tr><td>A級</td><td><a action=\"bypass -h Quest %(qn)s list +ga +wp\">武器</a></td><td><a action=\"bypass -h Quest %(qn)s list +ga +am -ren\">防具</a></td><td><a action=\"bypass -h Quest %(qn)s list +ga +ren\">飾品</a></td><td><a action=\"bypass -h Quest %(qn)s list +ga\">全部</a></td></tr>" % {"qn":qn}
	htm_menu_list_s = "<tr><td>S級</td><td><a action=\"bypass -h Quest %(qn)s list +gs +wp\">武器</a></td><td><a action=\"bypass -h Quest %(qn)s list +gs +am -ren\">防具</a></td><td><a action=\"bypass -h Quest %(qn)s list +gs +ren\">飾品</a></td><td><a action=\"bypass -h Quest %(qn)s list +gs\">全部</a></td></tr>" % {"qn":qn}
	htm_menu_list_all = "<tr><td>不限級</td><td><a action=\"bypass -h Quest %(qn)s list +wp\">武器</a></td><td><a action=\"bypass -h Quest %(qn)s list +am -ren\">防具</a></td><td><a action=\"bypass -h Quest %(qn)s list +ren\">飾品</a></td><td><a action=\"bypass -h Quest %(qn)s list\">全部</a></td></tr>" % {"qn":qn}
	htm_menu = htm_menu_search + "列出角色身上可強化物品<BR><table cellspacing=5>" + htm_menu_list_n + htm_menu_list_d + htm_menu_list_c + htm_menu_list_b + htm_menu_list_a + htm_menu_list_s + htm_menu_list_all + "</table>"
	htm_intro = "簡介<BR>只會列出角色身上所有強化卷軸可強化之物品<BR1>卷軸下方數字為成功機率及剩餘卷軸數量<BR1>點擊直接強化<BR1>強化成功機率與失敗結果與手動強化相同<BR1>" + htm_menu
	
	def firstpage(self, **kv):
		return self.htm_header + self.htm_intro + self.htm_footer

	def getEnchantScroll(self, player):
		def isEnchantScroll(item):
			t = item.getItemType().toString()
			if t.endswith("enchant_wp") or t.endswith("enchant_am"): return True
			return False
		return [item for item in player.getInventory().getItems() if isEnchantScroll(item)]

	def getSafeEnchantLevel(self, item):
		if item.getItem().getBodyPart() == L2Item.SLOT_FULL_ARMOR:
			return Config.ENCHANT_SAFE_MAX_FULL
		else:
			return Config.ENCHANT_SAFE_MAX
		
	def getChance(self, scroll, item):
		if item.getEnchantLevel() < self.getSafeEnchantLevel(item):
			return 100
		if self.isCustomChance and scroll.getItemId() in self.custom_chance.keys():
			return self.custom_chance[scroll.getItemId()]
		tscroll = EnchantItemTable.getInstance().getEnchantScroll(scroll)
		if tscroll:
			return max(tscroll.getChance(item, None), 0)
		return 0
		
	def list_item(self, event, npc, player):
		def isValid(item):
			renPart = [L2Item.SLOT_NECK, L2Item.SLOT_R_EAR, L2Item.SLOT_L_EAR, L2Item.SLOT_LR_EAR, L2Item.SLOT_R_FINGER, L2Item.SLOT_L_FINGER, L2Item.SLOT_LR_FINGER]
			if not item.isEnchantable(): return False
			if not item.isEquipable(): return False
			ct = item.getItem().getCrystalType()
			for e in event:
				if e == "+wp" and not item.isWeapon(): return False
				if e == "+am" and not item.isArmor(): return False
				if e == "+ren":
					bp = item.getItem().getBodyPart()
					if not bp in renPart: return False
				if e == "-ren":
					bp = item.getItem().getBodyPart()
					if bp in renPart: return False
				if e == "+gn" and not ct == L2Item.CRYSTAL_NONE: return False
				if e == "+gd" and not ct == L2Item.CRYSTAL_D: return False
				if e == "+gc" and not ct == L2Item.CRYSTAL_C: return False
				if e == "+gb" and not ct == L2Item.CRYSTAL_B: return False
				if e == "+ga" and not ct == L2Item.CRYSTAL_A: return False
				if e == "+gs" and not ct in [L2Item.CRYSTAL_S,L2Item.CRYSTAL_S80,L2Item.CRYSTAL_S84]: return False
				if not e[0] in ["+", "-"] and not e in self.itemNameTable.getName(item.getItemId()): return False
			if item.isWeapon() and item.getEnchantLevel() >= self.maxWpEnchantLevel: return False
			if item.isArmor():
				if item.getItem().getBodyPart() in renPart:
					if item.getEnchantLevel() >= self.maxRenEnchantLevel: return False
				else:
					if item.getEnchantLevel() >= self.maxAmEnchantLevel: return False
			return True
			
		list_command = " ".join(["list"] + event)
		e_scroll = self.getEnchantScroll(player)
		r = ""
		for item in [x for x in player.getInventory().getItems() if isValid(x)]:
			eit = EnchantItemTable.getInstance()
			r3 = ""
			for e in [x for x in e_scroll]:
				tscroll = eit.getEnchantScroll(e)
				if tscroll == None or not tscroll.isValid(item, None): continue
				tempChance = self.getChance(e, item)
				if tempChance < 1: continue
				desc = "%d%%<BR1>(%d)" % (tempChance, e.getCount())
				r3 += "<td><img src=%(icon)s width=32 height=32><a action=\"bypass -h Quest %(qn)s enchant %(item)d %(scroll)d%(sepa)s%(list_command)s\">%(desc)s</a></td>" % {"qn":self.qn, "icon":e.getItem().getIcon(), "item":item.getObjectId(), "scroll":e.getObjectId(), "sepa":self.command_split_char, "desc":desc, "list_command":list_command}
			if len(r3) < 1:
				continue
			r2 = ""
			r2 += "<tr>"
			r2 += "<td height=34><img src=%(icon)s width=32 height=32></td>" % {"icon":item.getItem().getIcon()}
			enchance_string = ""
			enchantLevel = item.getEnchantLevel()
			if enchantLevel:
				enchance_string = "<font color=b09b79>+" + str(enchantLevel) + " </font>"
			addname = self.itemNameTable.getAddName(item.getItemId())
			if len(addname):
				addname = " <font color=ffd969>" + addname + " </font>"
			r2 += "<td>%(enchance)s%(name)s<br1>%(addname)s</td>" % {"name":self.itemNameTable.getName(item.getItemId()), "enchance":enchance_string, "addname":addname}
			r2 += r3
			r2 += "</tr>"
			r += r2
		if r == "":
			return self.htm_header + "沒有對應強化卷軸之物品" + self.htm_footer
		r = "<table>" + r + "</table>"
		if len(r) > 17249: #大約數
			r = "可強化列表過長 請減少身上可強化物品後再使用"
		return self.htm_header + r + self.htm_footer

	def process_enchant(self, event, npc, player):
		itemoid, scrolloid = event
		itemoid, scrolloid = int(itemoid), int(scrolloid)
		inv = player.getInventory()
		item = inv.getItemByObjectId(itemoid)
		scroll = inv.getItemByObjectId(scrolloid)
		if item == None or scroll == None: return
		escroll = EnchantItemTable.getInstance().getEnchantScroll(scroll)
		if escroll == None: return
		dscroll = inv.destroyItem(self.qn, scrolloid, 1, player, item)
		if not dscroll: return
		if not item.getOwnerId() == player.getObjectId(): return
		if not item.isEnchantable(): return
		chance = self.getChance(scroll, item)
		if Rnd.get(100) < chance:
			item.setEnchantLevel(item.getEnchantLevel() + 1)
			item.updateDatabase()
			player.sendPacket(EnchantResult(0, 0, 0))
			sm = SystemMessage.getSystemMessage(SystemMessageId.C1_SUCCESSFULY_ENCHANTED_A_S2_S3);
			sm.addCharName(player)
			sm.addNumber(item.getEnchantLevel())
			sm.addItemName(item)
			if item.getEnchantLevel() in self.enchant_lv_notify:
				player.broadcastPacket(sm)
				if self.canFireWorks:
					skill = SkillTable.FrequentSkill.FIREWORK.getSkill()
					if skill:
						player.broadcastPacket(MagicSkillUse(player, player, skill.getId(), skill.getLevel(), skill.getHitTime(), skill.getReuseDelay()))
			else:
				player.sendPacket(sm)
			if self.isEnchantToSafe:
				if item.getEnchantLevel() < self.getSafeEnchantLevel(item):
					self.process_enchant(event, npc, player)
					# self.startQuestTimer(" ".join(["enchant"] + event), 250, npc, player, False)
		else:
			if escroll.isSafe():
				player.sendPacket(SystemMessage.sendString("強化失敗 物品強化值不變"))
				# player.sendPacket(SystemMessageId.SAFE_ENCHANT_FAILED)
				player.sendPacket(EnchantResult(5, 0, 0))
			else:
				if item.isEquipped():
					if item.getEnchantLevel() > 0:
						sm = SystemMessage.getSystemMessage(SystemMessageId.EQUIPMENT_S1_S2_REMOVED)
						sm.addNumber(item.getEnchantLevel())
						sm.addItemName(item)
						player.sendPacket(sm)
					else:
						sm = SystemMessage.getSystemMessage(SystemMessageId.S1_DISARMED)
						sm.addItemName(item)
						player.sendPacket(sm)
					unequiped = inv.unEquipItemInSlotAndRecord(item.getLocationSlot())
					iu = InventoryUpdate()
					for itm in unequiped:
						iu.addModifiedItem(itm)
					player.sendPacket(iu)
					player.broadcastUserInfo()
				if escroll.isBlessed():
					player.sendPacket(SystemMessageId.BLESSED_ENCHANT_FAILED)
					if self.canEnchantZero:
						item.setEnchantLevel(0)
					item.updateDatabase()
					player.sendPacket(EnchantResult(3, 0, 0))
				else:
					if self.canDestory:
						crystalId = item.getItem().getCrystalItemId()
						count = item.getCrystalCount() - ((item.getItem().getCrystalCount() + 1) / 2)
						if count < 1:
							count = 1
						destroyItem = inv.destroyItem(self.qn, item, player, None)
						if not destroyItem:
							Util.handleIllegalPlayerAction(player, "Unable to delete item on enchant failure from player " + player.getName() + ", possible cheater !", Config.DEFAULT_PUNISH);
							player.sendPacket(EnchantResult(2, 0, 0))
						crystals = None
						if crystalId:
							crystals = inv.addItem(self.qn, crystalId, count, player, destroyItem)
							sm = SystemMessage.getSystemMessage(SystemMessageId.EARNED_S2_S1_S)
							sm.addItemName(crystals)
							sm.addItemNumber(count)
							player.sendPacket(sm)
						iu = InventoryUpdate()
						if destroyItem.getCount():
							iu.addModifiedItem(destroyItem)
						else:
							iu.addRemovedItem(destroyItem)
						if crystalId and crystals:
							iu.addItem(crystals)
						player.sendPacket(iu)
						L2World.getInstance().removeObject(destroyItem)
						if crystalId:
							player.sendPacket(EnchantResult(1, crystalId, count))
						else:
							player.sendPacket(EnchantResult(4, 0, 0))
					elif self.canEnchantZero:
						player.sendPacket(SystemMessage.sendString("強化失敗 物品強化值變為0"))
						item.setEnchantLevel(0)
						item.updateDatabase()
						player.sendPacket(EnchantResult(3, 0, 0))
					else:
						player.sendPacket(SystemMessage.sendString("強化失敗 物品強化值不變"))
						# player.sendPacket(SystemMessageId.SAFE_ENCHANT_FAILED)
						player.sendPacket(EnchantResult(5, 0, 0))
		su = StatusUpdate(player)
		su.addAttribute(StatusUpdate.CUR_LOAD, player.getCurrentLoad())
		player.sendPacket(su)
		
		player.sendPacket(ItemList(player, False));
		player.broadcastUserInfo()
		player.setActiveEnchantItem(None)
		
	htm_commands = {"list":list_item, "enchant":process_enchant}
	
	def __init__(self, id = qID, name = qn, descr = qDesc):
		JQuest.__init__(self, id, name, descr)
		for id in self.NPCID:
			self.addStartNpc(id)
			self.addFirstTalkId(id)
			self.addTalkId(id)
		self.itemNameTable = ItemNameTable()
		print "Init:" + self.qn + " loaded"

	def process_command(self, event, npc, player):
		t = event.split()
		if t and t[0] in self.htm_commands.keys():
			return self.htm_commands[t[0]](self, t[1:], npc, player)
		return self.firstpage()
	
	def onAdvEvent(self, event, npc, player):
		r = self.firstpage()
		for t in event.split(self.command_split_char):
			r = self.process_command(t, npc, player)
		return r
		
	def onFirstTalk(self, npc, player):
		st = player.getQuestState(self.qn)
		if not st:
			st = self.newQuestState(player)
			st.setState(State.STARTED)
		return self.firstpage()
		
EasyEnchance()

import sys
from com.l2jserver.gameserver.model.quest		import State
from com.l2jserver.gameserver.model.quest		import QuestState
from com.l2jserver.gameserver.model.quest.jython	import QuestJython as JQuest

from com.l2jserver.gameserver.datatables import SkillTable #技能中文名相關
from com.l2jserver.gameserver.datatables import SkillTreesData #學習技能相關
from com.l2jserver.gameserver.model import L2SkillLearn #學習技能相關
from com.l2jserver.gameserver.model.skills import L2Skill #技能相關
from com.l2jserver.gameserver.datatables import ItemTable

from java.util import Random

qID = -1
qn = "powerup"
qDesc = "custom"

class PowerUp(JQuest):
	NPCID = [102] #觸發任務的 NPC 可修改.. 可以多 ID 例如 [100,102,103]
	
	maxChoice = 5 #每次技能提升顯示,讓玩家可選擇項目的數量

	htm_header = "<html><title>能力提升系統</title><body>"
	htm_footer = "</body></html>"
	htm_first = "簡介<BR>......請 GM 自行修改..大約說明.. 玩家提升技能 會隨機抽出 預設 5個 技能 讓玩家選擇 直到技能提升過. 才會再次隨機抽出另外 5 個技能 供玩家選擇.....<BR><a action=\"bypass -h Quest " + qn + " listonly\">列出技能</a><BR><a action=\"bypass -h Quest " + qn + "\">提升技能</a>"
	htm_random = '<a action="bypass -h Quest %s random">再次隨機抽出技能 (需要 金幣 100億)</a>' % qn
	htm_not_meet_requirement = "<center>條件不符<BR>......<BR1>......<BR1></center>"

	random_require_item = [57,10000000000] #再次隨機所需花費
	
	#需求道具 可多個 [[需求道具ID,數量],[需求道具ID,數量]] 或沒有 []
	global_require_item = [[57,100000000]]
	#鍵值:[技能ID,最高多少級,[[需求道具ID,數量],[需求道具ID,數量]...],簡介]
	#這裡可以設定個別需求道具
	#技能等級 可以減少.. 如需增多 請自行修改 powerUp_skill.xml 佩合
	skill_data = {
		'MAX_HP':[5995, 20, [[57,10000],[13067,1]], 'HP 上限'],
		'MAX_MP':[5996, 10, [[57,1],[13067,1]], 'MP 上限'],
		'REGENERATE_MP_RATE':[5997, 20, [[57,1],[13067,1]], 'MP回復率'],
		'POWER_DEFENCE':[5998, 10, [[57,1],[13067,1]], '物防'],
		'MAGIC_DEFENCE':[5999, 10, [[57,1],[13067,1]], '魔防'],
		'POWER_ATTACK':[6000, 10, [[57,1],[13067,1]], '物攻'],
		'MAGIC_ATTACK':[6001, 10, [[57,1],[13067,1]], '魔攻'],
		'POWER_ATTACK_SPEED':[6002, 10, [[57,1],[13067,1]], '物攻速'],
		'MAGIC_ATTACK_SPEED':[6003, 10, [[57,1],[13067,1]], '魔攻速'],
		'MAGIC_REUSE_RATE':[6004, 10, [[57,1],[13067,1]], '魔技再用時間'],
		'CRITICAL_DAMAGE':[6005, 10, [[57,1],[13067,1]], '物爆擊傷害'],
		'MAGIC_CRIT_DMG':[6006, 10, [[57,1],[13067,1]], '魔爆擊傷害'],
		'EVASION_RATE':[6007, 10, [[57,1],[13067,1]], '回避率'],
		'SHIELD_RATE':[6008, 10, [[57,1],[13067,1]], '盾防率'],
		'CRITICAL_RATE':[6009, 10, [[57,1],[13067,1]], '物爆率'],
		'MCRITICAL_RATE':[6010, 10, [[57,1],[13067,1]], '魔爆率'],
		'EXPSP_RATE':[6011, 10, [[57,1],[13067,1]], '經驗,SP率'],
		'ACCURACY_COMBAT':[6012, 10, [[57,1],[13067,1]], '命中率'],
		'RUN_SPEED':[6013, 10, [[57,1],[13067,1]], '跑速'],
		'STAT_STR':[6014, 10, [[57,1],[13067,1]], '力量'],
		'STAT_CON':[6015, 10, [[57,1],[13067,1]], '體質'],
		'STAT_DEX':[6016, 10, [[57,1],[13067,1]], '敏捷'],
		'STAT_INT':[6017, 10, [[57,1],[13067,1]], '智力'],
		'STAT_WIT':[6018, 10, [[57,1],[13067,1]], '智慧'],
		'STAT_MEN':[6025, 10, [[57,1],[13067,1]], '精神'],
		'VITALITY_CONSUME_RATE':[6026, 10, [[57,1],[13067,1]], '活力消耗率'],
		'P_REUSE':[6027, 10, [[57,1],[13067,1]], '物技再用時間'],
	}

	def __init__(self, id, name, descr):
		JQuest.__init__(self, id, name, descr)
		for id in self.NPCID:
			self.addStartNpc(id)
			self.addFirstTalkId(id)
			self.addTalkId(id)
		print "Init:" + qn + " loaded"

	def powerup_list(self, player, listonly = False):
		def getRandomList(listSize):
			templist = []
			listSize = min(listSize, len(self.skill_data.keys()))
			while len(templist) < listSize:
				temp = self.skill_data.keys()[Random().nextInt(len(self.skill_data.keys()))]
				if temp not in templist:
					templist += [temp]
			return templist
			
		st = player.getQuestState(qn)
		if not st:
			st = self.newQuestState(player)
			st.setState(State.STARTED)
		choiceList = st.get('choiceList') or ""
		choiceList = choiceList.split(",")
		if len(choiceList) != self.maxChoice:
			choiceList = getRandomList(self.maxChoice)
			choiceList.sort()
			st.set('choiceList', ",".join(choiceList))
		r = ""
		if listonly:
			for key in self.skill_data.keys():
				skillid, skillmaxlv, requireitem, desc = self.skill_data[key]
				r += "" + desc + "&nbsp;" + str(max(0,player.getSkillLevel(skillid))) + "/" + str(skillmaxlv) + "<BR1>"
		else:
			for key in choiceList:
				skillid, skillmaxlv, requireitem, desc = self.skill_data[key]
				r += "<a action=\"bypass -h Quest " + qn + " show_requirement " + key + "\">" + desc + "&nbsp;" + str(max(0,player.getSkillLevel(skillid))) + "/" + str(skillmaxlv) + "</a><BR1>"
		return self.htm_header + r + self.htm_random + self.htm_footer
		
	def add_skill(self, player, skill_data_key):
		skill_id = self.skill_data[skill_data_key][0]
		new_skill_level = player.getSkillLevel(skill_id)
		new_skill_level = new_skill_level + 1 or 1
		player.addSkill(SkillTable.getInstance().getInfo(skill_id, new_skill_level), True)

	def take_items(self, player, skill_data_key):
		st = player.getQuestState(qn)	
		for itemid, count in self.global_require_item:
			st.takeItems(itemid, count)
		for itemid, count in self.skill_data[skill_data_key][2]:
			st.takeItems(itemid, count)

	def check_requirement(self, player, skill_data_key):
		skill_id = self.skill_data[skill_data_key][0]
		skill_max_level = self.skill_data[skill_data_key][1]
		if player.getSkillLevel(skill_id)+1 > skill_max_level:
			player.sendMessage("升級已達到上限")
			return False
		if not self.check_require_item(player, skill_data_key):
			#player.sendMessage("道具不足")
			return False
		return True
			
	def check_require_item(self, player, skill_data_key):
		st = player.getQuestState(qn)	
		for itemid, count in self.global_require_item:
			if st.getQuestItemsCount(itemid) < count:
				item_name = ItemTable.getInstance().getTemplate(itemid).getName()
				player.sendMessage("道具不足:" + item_name + " 需要 " + str(count))
				return False
		for itemid, count in self.skill_data[skill_data_key][2]:
			if st.getQuestItemsCount(itemid) < count:
				item_name = ItemTable.getInstance().getTemplate(itemid).getName()
				player.sendMessage("道具不足:" + item_name + " 需要 " + str(count))
				return False
		return True

	def show_requirement(self, player, skill_data_key):
		skillid, skillmaxlv, requireitem, desc = self.skill_data[skill_data_key]
		r = "<center>" + desc + "</center><BR>"
		r += "升級所需道具如下<BR>"
		for itemid, count in self.global_require_item:
			item_name = ItemTable.getInstance().getTemplate(itemid).getName()
			r += item_name + ":" + str(count) +"<br>"
		for itemid, count in requireitem:
			item_name = ItemTable.getInstance().getTemplate(itemid).getName()
			r += item_name + ":" + str(count) +"<br>"
		r += "<a action=\"bypass -h Quest " + qn + " confirm " + skill_data_key + "\">確認提升 " + desc + "&nbsp;" + str(max(0,player.getSkillLevel(skillid))) + "/" + str(skillmaxlv) + "</a><BR1>"
		return r
		
	def onAdvEvent(self, event, npc, player):
		st = player.getQuestState(qn)	
		if event.startswith("show_requirement "):
			event = event[17:]
			if event in self.skill_data.keys():
				return self.htm_header + self.show_requirement(player, event) + self.htm_footer
			
		if event.startswith("confirm "):
			event = event[8:]
			if event in self.skill_data.keys():
				if self.check_requirement(player, event):
					self.take_items(player, event)
					self.add_skill(player, event)
					st.unset('choiceList')
				else:
					return self.htm_header + self.htm_not_meet_requirement + self.htm_footer
					
		if event == "random":
			itemid, count = self.random_require_item
			if st.getQuestItemsCount(itemid) < count:
				item_name = ItemTable.getInstance().getTemplate(itemid).getName()
				player.sendMessage("道具不足:" + item_name + " 需要 " + str(count))
				return ""
			st.takeItems(itemid, count)
			st.unset('choiceList')

		if event == "listonly":
			return self.powerup_list(player, True)
		return self.powerup_list(player)
		
	def onFirstTalk(self, npc, player):
		st = player.getQuestState(qn)
		if not st:
			st = self.newQuestState(player)
			st.setState(State.STARTED)
		return self.htm_header + self.htm_first + self.htm_footer
		
PowerUp(qID, qn, qDesc)

'''
	MAX_HP("maxHp"),
	MAX_MP("maxMp"),
	MAX_CP("maxCp"),
	REGENERATE_HP_RATE("regHp"),
	REGENERATE_CP_RATE("regCp"),
	REGENERATE_MP_RATE("regMp"),
	RECHARGE_MP_RATE("gainMp"),
	HEAL_EFFECTIVNESS("gainHp"),
	HEAL_PROFICIENCY("giveHp"),
	HEAL_STATIC_BONUS("bonusHp"),
	
	// Atk & Def
	POWER_DEFENCE("pDef"),
	MAGIC_DEFENCE("mDef"),
	POWER_ATTACK("pAtk"),
	MAGIC_ATTACK("mAtk"),
	PHYSICAL_SKILL_POWER("physicalSkillPower"),
	POWER_ATTACK_SPEED("pAtkSpd"),
	MAGIC_ATTACK_SPEED("mAtkSpd"), // how fast a spell is casted (including animation)
	MAGIC_REUSE_RATE("mReuse"), // how fast spells becomes ready to reuse
	SHIELD_DEFENCE("sDef"),
	CRITICAL_DAMAGE("cAtk"),
	CRITICAL_DAMAGE_ADD("cAtkAdd"), // this is another type for special critical damage mods - vicious stance, crit power and crit damage SA
	// it was totally bad since now...
	MAGIC_CRIT_DMG("mCritPower"),
	
	PVP_PHYSICAL_DMG("pvpPhysDmg"),
	PVP_MAGICAL_DMG("pvpMagicalDmg"),
	PVP_PHYS_SKILL_DMG("pvpPhysSkillsDmg"),
	
	PVP_PHYSICAL_DEF("pvpPhysDef"),
	PVP_MAGICAL_DEF("pvpMagicalDef"),
	PVP_PHYS_SKILL_DEF("pvpPhysSkillsDef"),
	
	PVE_PHYSICAL_DMG("pvePhysDmg"),
	PVE_PHYS_SKILL_DMG("pvePhysSkillsDmg"),
	PVE_BOW_DMG("pveBowDmg"),
	PVE_BOW_SKILL_DMG("pveBowSkillsDmg"),
	PVE_MAGICAL_DMG("pveMagicalDmg"),
	
	// Atk & Def rates
	EVASION_RATE("rEvas"),
	P_SKILL_EVASION("pSkillEvas"),
	CRIT_DAMAGE_EVASION("critDamEvas"),
	SHIELD_RATE("rShld"),
	CRITICAL_RATE("rCrit"),
	BLOW_RATE("blowRate"),
	LETHAL_RATE("lethalRate"),
	MCRITICAL_RATE("mCritRate"),
	EXPSP_RATE("rExp"),
	ATTACK_CANCEL("cancel"),
	
	// Accuracy and range
	ACCURACY_COMBAT("accCombat"),
	POWER_ATTACK_RANGE("pAtkRange"),
	MAGIC_ATTACK_RANGE("mAtkRange"),
	POWER_ATTACK_ANGLE("pAtkAngle"),
	ATTACK_COUNT_MAX("atkCountMax"),
	// Run speed,
	// walk & escape speed are calculated proportionally,
	// magic speed is a buff
	RUN_SPEED("runSpd"),
	WALK_SPEED("walkSpd"),
	
	//
	// Player-only stats
	//
	STAT_STR("STR"),
	STAT_CON("CON"),
	STAT_DEX("DEX"),
	STAT_INT("INT"),
	STAT_WIT("WIT"),
	STAT_MEN("MEN"),
	
	//
	// Special stats, share one slot in Calculator
	//
	
	// stats of various abilities
	BREATH("breath"),
	FALL("fall"),
	LIMIT_HP("limitHp"), // non-displayed hp limit
	//
	AGGRESSION("aggression"), // locks a mob on tank caster
	BLEED("bleed"), // by daggers, like poison
	POISON("poison"), // by magic, hp dmg over time
	STUN("stun"), // disable move/ATTACK for a period of time
	ROOT("root"), // disable movement, but not ATTACK
	MOVEMENT("movement"), // slowdown movement, debuff
	CONFUSION("confusion"), // mob changes target, opposite to aggression/hate
	SLEEP("sleep"), // sleep (don't move/ATTACK) until attacked
	VALAKAS("valakas"),
	VALAKAS_RES("valakasRes"),
	//
	AGGRESSION_VULN("aggressionVuln"),
	BLEED_VULN("bleedVuln"),
	POISON_VULN("poisonVuln"),
	STUN_VULN("stunVuln"),
	PARALYZE_VULN("paralyzeVuln"),
	ROOT_VULN("rootVuln"),
	SLEEP_VULN("sleepVuln"),
	CONFUSION_VULN("confusionVuln"),
	MOVEMENT_VULN("movementVuln"),
	FIRE_RES("fireRes"),
	WIND_RES("windRes"),
	WATER_RES("waterRes"),
	EARTH_RES("earthRes"),
	HOLY_RES("holyRes"),
	DARK_RES("darkRes"),
	//Skills Power
	FIRE_POWER("firePower"),
	WATER_POWER("waterPower"),
	WIND_POWER("windPower"),
	EARTH_POWER("earthPower"),
	HOLY_POWER("holyPower"),
	DARK_POWER("darkPower"),
	CANCEL_VULN("cancelVuln"), // Resistance for cancel type skills
	DERANGEMENT_VULN("derangementVuln"),
	DEBUFF_VULN("debuffVuln"),
	BUFF_VULN("buffVuln"),
	CRIT_VULN("critVuln"), // Resistence to Crit DMG in percent.
	CRIT_ADD_VULN("critAddVuln"), // Resistence to Crit DMG in value (ex: +100 will be 100 more crit dmg, NOT 100% more).
	MAGIC_DAMAGE_VULN("magicDamVul"),
	MAGIC_SUCCESS_RES("magicSuccRes"),
	MAGIC_FAILURE_RATE("magicFailureRate"),
	
	AGGRESSION_PROF("aggressionProf"),
	BLEED_PROF("bleedProf"),
	POISON_PROF("poisonProf"),
	STUN_PROF("stunProf"),
	PARALYZE_PROF("paralyzeProf"),
	ROOT_PROF("rootProf"),
	SLEEP_PROF("sleepProf"),
	CONFUSION_PROF("confusionProf"),
	PROF("movementProf"),
	CANCEL_PROF("cancelProf"),
	DERANGEMENT_PROF("derangementProf"),
	DEBUFF_PROF("debuffProf"),
	CRIT_PROF("critProf"),
	
	NONE_WPN_VULN("noneWpnVuln"), // Shields!!!
	SWORD_WPN_VULN("swordWpnVuln"),
	BLUNT_WPN_VULN("bluntWpnVuln"),
	DAGGER_WPN_VULN("daggerWpnVuln"),
	BOW_WPN_VULN("bowWpnVuln"),
	CROSSBOW_WPN_VULN("crossbowWpnVuln"),
	POLE_WPN_VULN("poleWpnVuln"),
	ETC_WPN_VULN("etcWpnVuln"),
	FIST_WPN_VULN("fistWpnVuln"),
	DUAL_WPN_VULN("dualWpnVuln"),
	DUALFIST_WPN_VULN("dualFistWpnVuln"),
	BIGSWORD_WPN_VULN("bigSwordWpnVuln"),
	BIGBLUNT_WPN_VULN("bigBluntWpnVuln"),
	DUALDAGGER_WPN_VULN("dualDaggerWpnVuln"),
	RAPIER_WPN_VULN("rapierWpnVuln"),
	ANCIENT_WPN_VULN("ancientWpnVuln"),
	PET_WPN_VULN("petWpnVuln"),
	
	REFLECT_DAMAGE_PERCENT("reflectDam"),
	REFLECT_SKILL_MAGIC("reflectSkillMagic"),
	REFLECT_SKILL_PHYSIC("reflectSkillPhysic"),
	VENGEANCE_SKILL_MAGIC_DAMAGE("vengeanceMdam"),
	VENGEANCE_SKILL_PHYSICAL_DAMAGE("vengeancePdam"),
	ABSORB_DAMAGE_PERCENT("absorbDam"),
	TRANSFER_DAMAGE_PERCENT("transDam"),
	MANA_SHIELD_PERCENT("manaShield"),
	TRANSFER_DAMAGE_TO_PLAYER("transDamToPlayer"),
	ABSORB_MANA_DAMAGE_PERCENT("absorbDamMana"),
	
	MAX_LOAD("maxLoad"),
	WEIGHT_LIMIT("weightLimit"),
	
	PATK_PLANTS("pAtk-plants"),
	PATK_INSECTS("pAtk-insects"),
	PATK_ANIMALS("pAtk-animals"),
	PATK_MONSTERS("pAtk-monsters"),
	PATK_DRAGONS("pAtk-dragons"),
	PATK_GIANTS("pAtk-giants"),
	PATK_MCREATURES("pAtk-magicCreature"),
	
	PDEF_PLANTS("pDef-plants"),
	PDEF_INSECTS("pDef-insects"),
	PDEF_ANIMALS("pDef-animals"),
	PDEF_MONSTERS("pDef-monsters"),
	PDEF_DRAGONS("pDef-dragons"),
	PDEF_GIANTS("pDef-giants"),
	PDEF_MCREATURES("pDef-magicCreature"),
	
	ATK_REUSE("atkReuse"),
	P_REUSE("pReuse"),
	
	//ExSkill :)
	INV_LIM("inventoryLimit"),
	WH_LIM("whLimit"),
	FREIGHT_LIM("FreightLimit"),
	P_SELL_LIM("PrivateSellLimit"),
	P_BUY_LIM("PrivateBuyLimit"),
	REC_D_LIM("DwarfRecipeLimit"),
	REC_C_LIM("CommonRecipeLimit"),
	
	//C4 Stats
	PHYSICAL_MP_CONSUME_RATE("PhysicalMpConsumeRate"),
	MAGICAL_MP_CONSUME_RATE("MagicalMpConsumeRate"),
	DANCE_MP_CONSUME_RATE("DanceMpConsumeRate"),
	BOW_MP_CONSUME_RATE("BowMpConsumeRate"),
	HP_CONSUME_RATE("HpConsumeRate"),
	MP_CONSUME("MpConsume"),
	SOULSHOT_COUNT("soulShotCount"),
	
	//T1 stats
	transformId("transformId"),
	TALISMAN_SLOTS("talisman"),
	CLOAK_SLOT("cloak"),
	
	//Shield Stats
	SHIELD_DEFENCE_ANGLE("shieldDefAngle"),
	
	//Skill mastery
	SKILL_MASTERY			("skillMastery"),
	
	// vitality
	VITALITY_CONSUME_RATE("vitalityConsumeRate");
'''

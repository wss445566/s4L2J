import sys
from com.l2jserver.gameserver.model.quest		import State
from com.l2jserver.gameserver.model.quest		import QuestState
from com.l2jserver.gameserver.model.quest.jython	import QuestJython as JQuest

from com.l2jserver.util					import Rnd
from com.l2jserver.gameserver.datatables		import NpcTable
from com.l2jserver.gameserver.model			import L2DropData
from com.l2jserver.gameserver.ai			import CtrlIntention
from com.l2jserver.gameserver.model			import L2World
from com.l2jserver.gameserver.network.serverpackets	import NpcSay
from com.l2jserver.gameserver				import GameTimeController
from com.l2jserver.gameserver.datatables		import SkillTable
from com.l2jserver.gameserver				import Announcements
from com.l2jserver.gameserver.instancemanager		import TownManager

class NewYearEvent(JQuest):
	qID = -1
	qn = "NewYear_2011"
	qDesc = "custom"

	#掉落物品 ID, 類, 掉最少, 掉最多, 機率 1 * 10000 = 1%
	#itemID, category, minD, maxD, chance
	event_droplist = [
		[10304, 15, 1, 1, 5 * 10000],	#變身刻印書-劍齒虎
		[20876, 1, 1, 1, 5 * 10000],	#百年好合
		[20877, 2, 1, 1, 5 * 10000],	#年年有餘
		[20878, 3, 1, 1, 5 * 10000],	#圓滿如意
		[20879, 4, 1, 1, 5 * 10000],	#恭喜發財
		[20880, 5, 1, 1, 5 * 10000],	#金玉滿堂
		[20881, 6, 1, 1, 5 * 10000],	#花開富貴
		[20882, 7, 1, 1, 5 * 10000],	#佛跳牆
		[20870, 8, 1, 1, 1 * 10000],	#紅色鞭炮
		[20871, 9, 1, 1, 1 * 10000],	#金色鞭炮
		[20872, 10, 1, 1, 1 * 10000],	#藍色鞭炮
		[20873, 11, 1, 1, 1 * 10000],	#粉紅色鞭炮
		[20874, 12, 1, 1, 1 * 10000],	#白色鞭炮
		[20875, 13, 1, 1, 1 * 10000],	#銀色鞭炮
		[20788, 14, 1, 2, 50 * 10000]	#煙火箱
	]

	boss_droplist = event_droplist + [
		[57, 20, 100000, 1000000, 100 * 10000],	#掉錢 10-100萬 100%
		[57, 21, 100000, 1000000, 100 * 10000],	#掉錢 10-100萬 100%
		[57, 22, 100000, 1000000, 100 * 10000],	#掉錢 10-100萬 100%
		[57, 23, 100000, 1000000, 100 * 10000],	#掉錢 10-100萬 100%
		[57, 24, 100000, 1000000, 100 * 10000],	#掉錢 10-100萬 100%
		[57, 25, 100000, 1000000, 100 * 10000],	#掉錢 10-100萬 100%
	]

	npc_droplist = event_droplist + [
		[57, 0, 10000, 50000, 90 * 10000],	#掉錢 1-5萬 90%
		[20870, -1, 1, 1, 10 * 10000],	#紅色鞭炮 回收
		[20871, -1, 1, 1, 10 * 10000],	#金色鞭炮 回收
		[20872, -1, 1, 1, 10 * 10000],	#藍色鞭炮 回收
		[20873, -1, 1, 1, 10 * 10000],	#粉紅色鞭炮 回收
		[20874, -1, 1, 1, 10 * 10000],	#白色鞭炮 回收
		[20875, -1, 1, 1, 10 * 10000]	#銀色鞭炮 回收
	]

	Boss = [29118] #BOSS 巴烈斯
	#小怪清單
	NPCs = [22272, 22273, 22274, 22393, 22394, 22395, 22411, 22412, 22413, 22414, 22415, 22439, 22440, 22441, 22442, 18371, 18372, 18373, 18374, 18375, 18376, 18377, 18490, 27278]

	spawn_rate = 20 #沒變劍齒虎打 Boss 會生小怪的機率, 1 = 1%

	npc_town_spawn_time = 1000 * 60 * 1  # 1 分鐘 在城裡 找玩家 生一次
	npc_town_spawn_chance = 33	# 城裡生怪機率
	npc_town_spawn_min = 1		# 最少生多少隻怪
	npc_town_spawn_max = 5		# 最多生多少隻怪

	isGM_join_event = True	# 如果 False, GM 不受活動條件影響

	npc_spawn_say = [
		'%player_name% 受死吧',
		'年菜年菜 %player_name%有很多年菜 搶!',
		'恭喜發財 年菜拿來 %player_name% 給點年菜來吃',
		'很香很香 我嗅到了 是年菜的味道 就在 %player_name% 身上, 兄弟們 上啊!!',
		'%player_name% 不是劍齒虎, 殺..',
		'苦練十年 就是為了把 %player_name% 拿下',
		'%player_name% 放下年菜, 留你全屍',
		'聽聞 %player_name% 就在這個城裡, 找到你了'
	]

	#BOSS_spawn_info 的設定 會遊戲時間 1天 (現實 4小時) 重生一次
	# ID, [遊戲時間, BOSS ID, X, Y, Z, 面向, 位置隨機偏移, 現實時間存在多久] 0 = 不消失 (不建意 0 如果沒玩家去打 會累積很多隻)
	BOSS_spawn_info = dict([
		['boss1', ['00:00', 29118, 149494, 46727, -3413, 0, True, 59 * 60 * 1000]],	#預設現實時間 59分鐘後消失, 大圓型競技場中央 遊戲時間 0時0分
		['boss2', ['06:00', 29118, 7058, -23681, -3708, 0, True, 240 * 60 * 1000]],	#預設現實時間 4小時後消失, 原始之島
		['boss3', ['18:30', 29118, -11166, 254195, -3189, 0, True, 3300 * 1000]]	#預設 遊戲時間 330分鐘後消失 就是 遊戲時間 00:00 消失, 沙暴丘陵
	])

	ask_transform_zone = [
		300690,
		300691
	]

	main_town_id = [
		12,	#亞丁
		9,	#奇岩
		13,	#高達特
		17,	#修加特
		14,	#魯因
		15,	#水上都市海音斯
		5,	#古魯丁村
		7,	#古魯丁城
		8,	#狄恩
		16,	#芙羅蘭
		11,	#獵人村
		10,	#歐瑞
		2,	#說話之島
		6,	#矮人村
		3,	#精靈村
		4,	#半獸人村
		1,	#黑精村
		20,	#闇天使村
		22,	#夢幻島
		33	#聯合基地
	]
	
	# 1GameTime = 現實時間 10秒
	# 1GameTime = 遊戲時間 1分鐘
	# 60GameTime = 遊戲時間 1小時
	# 1440GameTime = 遊戲時間 1天
	def comming_game_time_to_real_sec(self, game_time):
		try:
			h, m = game_time.split(':')	#取出 小時, 分
			m = int(h) * 60 + int(m)	#統一用 分計算
			diff = m - GameTimeController.getInstance().getGameTime() % 1440	#計算時間差 --遊戲時間(分)
			if diff < 0: diff += 1440
			return diff * 10	#換為現實時間(秒)
		except:
			return -1	#錯誤時傳回 -1

	def addDrop(self, id, droplist):
		t = NpcTable.getInstance().getTemplate(id)
		for itemID, category, minD, maxD, chance in droplist:
			d = L2DropData()
			d.setItemId(itemID)
			d.setMinDrop(minD)
			d.setMaxDrop(maxD)
			d.setChance(chance) #100 * 10000 = 100%
			t.addDropData(d, category)

	def __init__(self, id = qID, name = qn, descr = qDesc):
		JQuest.__init__(self, id, name, descr)
		for id in self.Boss:
			self.addAttackId(id)
			self.addDrop(id, self.boss_droplist)
			self.addSkillSeeId(id)

		for id in self.NPCs:
			self.addDrop(id, self.npc_droplist)
			self.addSkillSeeId(id)

		for id in self.ask_transform_zone:
			self.addEnterZoneId(id)

		self.startQuestTimer('spawn_npc_in_town', self.npc_town_spawn_time, None, None, True)
		for timer_id in self.BOSS_spawn_info:
			t = self.comming_game_time_to_real_sec(self.BOSS_spawn_info[timer_id][0])
			if t >= 0:
				self.startQuestTimer(timer_id, t * 1000, None, None, False)
			else:
				print self.qn +':BPSS_spawn_info 的時間格式錯誤'
		
	def onEnterZone(self, character, zone):
		try:
			if character.getTransformationId(): return
			if not isGM_join_event and player.isGM(): return
		except:
			return
		skillId, skillLevel = [672, 1]
		skill = SkillTable.getInstance().getInfo(skillId, skillLevel)
		if skill:
			skill.getEffects(character, character)

	def onSkillSee(self, npc, caster, skill, targets, isPet):
		try:
			if not isGM_join_event and caster.isGM(): return
		except:
			pass
		npc.addDamageHate(caster, 0, len(targets)*1000)
		npc.getAI().setIntention(CtrlIntention.AI_INTENTION_ATTACK, caster)

	def onAttack(self, npc, player, damage, isPet, skill):
		try:
			if player and player.getTransformationId() != 5: # 劍齒虎變身 ID 5
				if Rnd.get(100) < spawn_rate:
					self.myAddSpawn(npc, player, damage)
		except:
			pass

	def myAddSpawn(self, npc, player, damage): # npc 用作召喚位置, player 被仇恨的玩家
		n = self.addSpawn(self.NPCs[Rnd.get(len(self.NPCs))], npc, False)
		n.addDamageHate(player, 0, damage * 1000 / (player.getLevel() + 7))
		n.getAI().setIntention(CtrlIntention.AI_INTENTION_ATTACK, player)
		npc.broadcastPacket(NpcSay(n.getObjectId(), 0, n.getNpcId(), self.npc_spawn_say[Rnd.get(len(self.npc_spawn_say))].replace('%player_name%', player.getName()) ))

	def canSpawn(self, player):
		if not player: return False
		if not self.isGM_join_event and player.isGM(): return False
		if player.isSilentMoving(): return False
		if player.getTransformationId() == 5: return False
		if player.getAI().getIntention() == CtrlIntention.AI_INTENTION_IDLE: return False
		if player.getAI().getIntention() == CtrlIntention.AI_INTENTION_REST: return False
		if not player.isInsideZone(player.ZONE_TOWN): return False
		if TownManager.getTown(player.getX(), player.getY(), player.getZ()).getTownId() not in self.main_town_id: return False
		if Rnd.get(100) > self.npc_town_spawn_chance: return False
		return True

	def onAdvEvent(self, event, npc, player):
		print event, npc, player
		if event == 'spawn_npc_in_town':
			for player in L2World.getInstance().getAllPlayers().values():
				print player
				if self.canSpawn(player):
					print "canspawn"
					c = Rnd.get(self.npc_town_spawn_max - self.npc_town_spawn_min) + self.npc_town_spawn_min
					for i in range(c):
						self.myAddSpawn(player, player, 1000)
		elif event in self.BOSS_spawn_info:
			t, boss_id, x, y, z, heading, random_offset, despawn_delay = self.BOSS_spawn_info[event]
			n = self.addSpawn(boss_id, x, y, z, heading, random_offset, despawn_delay)
			Announcements.getInstance().announceToAll('活動 BOSS 出現在「' + n.getCastle().getCName() + '」地區 ' + str(x) + ',' + str(y) + ',' + str(z))
			self.startQuestTimer(event, 14400*1000, None, None, False)	#遊戲時間一天後再重生

NewYearEvent()


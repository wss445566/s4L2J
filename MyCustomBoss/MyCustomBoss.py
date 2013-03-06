import math
from com.l2jserver.gameserver.model.quest import State
from com.l2jserver.gameserver.model.quest.jython import QuestJython as JQuest

from com.l2jserver.gameserver.instancemanager import InstanceManager
from com.l2jserver.gameserver.instancemanager.InstanceManager import InstanceWorld
from com.l2jserver.gameserver.ai import CtrlIntention
from com.l2jserver.gameserver.util import Util 
from com.l2jserver.gameserver.util import Broadcast
from com.l2jserver.gameserver.network.serverpackets import ExSendUIEvent
from com.l2jserver.gameserver.model import L2World
from com.l2jserver.gameserver.datatables import NpcTable
from com.l2jserver.gameserver.model import L2Spawn
from com.l2jserver.gameserver.datatables import SpawnTable
from com.l2jserver.gameserver.datatables import SkillTable
from com.l2jserver.util import Rnd
from com.l2jserver.gameserver.network.serverpackets import SystemMessage
from com.l2jserver.gameserver.model.actor.instance import L2PcInstance
from com.l2jserver.gameserver.model import L2Object
from java.lang import System
from com.l2jserver.gameserver.datatables import ItemTable
from com.l2jserver.gameserver.network.serverpackets import ExShowScreenMessage
from com.l2jserver.gameserver.model import L2CharPosition

class MyInstanceWorld(InstanceWorld):
	def __init__(self):
		InstanceWorld.__init__(self)
		self.stage = 0
		self.step = 0
		self.wave1killed = 0
		self.flagInstance = []
		self.bossInstance = None
		self.runningInstance = None
		self.runningIndex = 0

class Quest(JQuest):
	"""
	副本總時間 60分鐘
	進入後 有1分鐘時間 準備
	1分鐘過後 刷兔子.. 很多兔子
	刷出兔子後 1分鐘 兔子會主動打玩家
	殺 20隻兔子 會生出 兩隻 需要保護的怪物. 若保護怪物死亡 副本失敗結束
	刷出保護怪後 保護怪會打玩家.. 兔子會打保護怪
	若殺兔子多於 20隻.. 每殺一隻兔子 會在隨機點生出一隻強怪 打玩家.. 
	除了保護怪外 把所有怪 殺光.. BOSS 刷出來. 保護怪消失
	殺 BOSS 後 出現 離開 NPC
	中途離場 斷線 回城 可再次進入相同副本 繼續挑戰 不另收道具
	如果副本失敗 或 成功 不能再次進入相同副本
	"""
	qID = -1
	qn = "MyCustomBoss"
	qDesc = "custom"
	
	InstanceTemplateId = 99999
	InstanceReenterTime = 1000 * 60 * 15 #進場後開始計算多久 才可以再次挑戰新副本 (15分鐘後)
	
	NPCID = 100 #進入副本 NPC
	instanceTime = 1000 * 60 * 60 # 副本總時間, 單位 ms 暫定 60 分鐘
	timetos1s0 = 1000 * 60 * 1 # 進入副本後 有 1 分鐘準備時間
	timetos1s2 = 1000 * 60 * 1 # 生出兔子後多久 主動攻擊玩家 預設 1 分鐘
	#ejectLoc = [82698, 148638, -3468] #退出/回卷 位置 (奇岩)
	ejectLoc = [86655, -19739, -1944] #退出/回卷 位置 (山賊城寨外)
	entryLoc = (82995, -16210, -1750) #副本傳送後 位置 (山賊城寨)
	bossid = 29195 #BOSS ID
	wave1mobid = 157 #第一波 刷兔子
	killcounttos2s0 = 20 #殺多少隻兔子 進入下一階段
	killcountspawnstrongmob = 20 #殺多少隻兔子 後 每殺一隻兔子 生一隻強怪
	wave2flagid = 21182 #玩家保護怪物 ID 不能死亡
	wave2mobid = 23151 #第二波怪物 ID
	#第二波 刷怪隨機位置 可增加 減少
	wave2mobspawnloc = [
		[81499,-15130,-1830]
		,[83197,-15298,-1845]
		,[84638,-16244,-1830]
		,[84722,-17496,-1855]
		,[82931,-17144,-1842]
		,[81032,-16456,-1830]
		,[82507,-16214,-1893]
	]
	
	runningR = 800
	runningStep = 36
	
	require_item_id = 57 #進入所需道具 金幣 ID 57
	require_item_name = ItemTable.getInstance().getTemplate(require_item_id).getName()
	require_item_count = 100 #進入所需道具 數量 100
	
	htm_header = """<html><title>自訂副本</title><body>"""
	htm_footer = """</body></html>"""
	htm_go = """<a action="bypass -h Quest %s go">挑戰副本</a>""" % qn
	htm_reentry = """<a action="bypass -h Quest %s reentry">繼續挑戰副本</a>""" % qn
	htm_exit = """<a action="bypass -h Quest %s exit">離開副本</a>""" % qn
	htm_not_allow = """不能進入. <BR>必需隊長, 如有聯軍 必需聯軍長 點擊進入<br>所有隊員 必需在 2000單位範圍內"""
	htm_not_allow_member = """不能進入 以下成員未符合需求<br>"""
	
	def __init__(self, id = qID, name = qn, descr = qDesc):
		self.qID, self.qn, self.qDesc = id, name, descr
		JQuest.__init__(self, id, name, descr)
		self.addStartNpc(self.NPCID)
		self.addFirstTalkId(self.NPCID)
		self.addTalkId(self.NPCID)
		
		self.addKillId(self.wave1mobid)
		self.addKillId(self.wave2flagid)
		self.addKillId(self.bossid)
		print "%s loaded" % self.qn
		
	def onKill(self, npc, player, isPet):
		world = self.getWorld(npc)
		if not isinstance (world, MyInstanceWorld):
			return
		if npc.getNpcId() == self.wave1mobid:
			world.wave1killed += 1
			if world.wave1killed >= self.killcountspawnstrongmob:
				x, y, z = self.wave2mobspawnloc[Rnd.get(0,len(self.wave2mobspawnloc)-1)]
				x, y, z = self.getRandomXYZ(x, y, z, 100)
				n = self.spawnNpc(self.wave2mobid, x, y, z, 0, world.instanceId)
				p = self.getRandomPlayer(world)
				self.addHate(world, n, p)
		if npc.getNpcId() == self.bossid:
			self.broadcastMessage(world.instanceId, "%s 殺死了 %s 副本成功" % (player.getName(), npc.getName()))
			self.broadcastScreenMessage(world.instanceId, "副本成功")
			InstanceManager.getInstance().getInstance(world.instanceId).setDuration(1000*60*5)
			x, y, z = self.entryLoc
			self.spawnNpc(self.NPCID, x, y, z, 0, world.instanceId)
			world.stage, world.step = 4, 0
		
	def onAdvEvent(self, event, npc, player):
		def getWorldFromInstanceId():
			try:
				instanceid = int(event.split()[1])
			except:
				print "invaild instance id %s" % event
				return None
			world = self.getWorld(instanceId = instanceid)
			if not world:
				print "Instance disappear %d" % instanceid
				return None
			return world

		if event.startswith("flowControl "):
			try:
				instanceid = int(event.split()[1])
			except:
				print "flowControl error %s" % event
				return
			world = self.getWorld(instanceId = instanceid)
			if not world:
				self.cancelQuestTimer("flowControl %d" % instanceid, None, None)
				print "副本已消失 %d" % instanceid
				return
			i = InstanceManager.getInstance().getInstance(world.instanceId) 
			for pid in i.getPlayers().toArray():
				p = L2World.getInstance().getPlayer(pid)
				if p and p.getInstanceId() == world.instanceId:
					pass
				else:
					i.ejectPlayer(pid)
					i.removePlayer(pid)
			if i.getPlayers().isEmpty():
				print "副本沒有玩家 %d" % world.instanceId
				self.cancelQuestTimer("flowControl %d" % instanceid, None, None)
				return
			return self.flowControl(world)
			
		if event == 'reentry':
			st = player.getQuestState(self.qn)
			instanceId = st.getInt('instanceId')
			self.teleport(player, instanceId)
			self.startQuestTimer("flowControl %d" % instanceId, 1000, None, None, True)
			
		if event == 'go':
			members = [player]
			if player.getParty():
				if player.getParty().getCommandChannel():
					if player.getParty().getCommandChannel().getLeader().getObjectId() != player.getObjectId():
						return self.htm_header + self.htm_not_allow + self.htm_footer
					members = player.getParty().getCommandChannel().getMembers()
				else:
					if player.getParty().getLeader().getObjectId() != player.getObjectId():
						return self.htm_header + self.htm_not_allow + self.htm_footer
					members = player.getParty().getMembers()
			#檢測所有隊員進入需求
			r = ""
			for m in [x for x in members if not self.checkAllow(player, x)]:
				r += "%s<br1>" % m.getName()
			if len(r):
				return self.htm_header + self.htm_not_allow_member + r + self.htm_footer
			#創建副本
			im = InstanceManager.getInstance()
			instanceid = im.createDynamicInstance(None)
			if instanceid:
				instance = im.getInstance(instanceid)
				world = MyInstanceWorld()
				world.instanceId = instanceid
				im.addWorld(world)
				instance.setDuration(self.instanceTime)
				instance.setEmptyDestroyTime(1000 * 60 * 1)
				instance.setSpawnLoc(self.ejectLoc)
				instance.setName("%s %s" % (self.qn, player.getName()))
				for p in members:
					self.takeItems(p, self.require_item_id, self.require_item_count)
					pid = p.getObjectId()
					world.allowed.add(pid)
					InstanceManager.getInstance().setInstanceTime(pid, self.InstanceTemplateId, System.currentTimeMillis() + self.InstanceReenterTime)
					self.teleport(p, instanceid)
				self.broadcastScreenMessage(world.instanceId, "準備")
				world.stage, world.step = 0, 1
				#world.stage, world.step = 3, 0
				self.startQuestTimer("flowControl %d" % world.instanceId, 1000, None, None, True)
				self.broadcastTimer(world.instanceId, self.timetos1s0 / 1000, "準備時間")
				self.startQuestTimer("s1s0 %d" % world.instanceId, self.timetos1s0, None, None, False)
				print "%s 創建副本 ID %d" % (player.getName(), world.instanceId)
			else:
				print "%s Error:can not create dynamic instance" % self.qn
			return
			
		#刷兔子
		if event.startswith('s1s0 '):
			world = getWorldFromInstanceId()
			if not world:
				return
			if world.stage == 0 and world.step == 1:
				world.stage, world.step = 1, 0
				self.broadcastScreenMessage(world.instanceId, "第一階段")
				cx, cy, cz = self.entryLoc
				for r,s in [(500,10), (900,20), (1300,30)]:
					for x, y in self.plotCircle(cx, cy, r, s):
						npc = self.spawnNpc(self.wave1mobid, x, y, -1700, 0, world.instanceId)
				self.startQuestTimer("s1s2 %d" % world.instanceId, self.timetos1s2, None, None, False)
			return
			
		#兔子主動攻擊
		if event.startswith('s1s2 '):
			world = getWorldFromInstanceId()
			if not world:
				return
			if world.stage == 1 and world.step == 0:
				world.stage, world.step = 1, 2
				self.broadcastScreenMessage(world.instanceId, "兄弟們 上啊")
			return

		#刷保護怪
		#if event.startswith('s2s0 '):
		#	world = getWorldFromInstanceId()
		#	if not world:
		#		return
		#	if world.stage == 1 and world.step == 3:
		#		world.stage, world.step = 2, 0
		#		world.flagInstance += [self.spawnNpc(self.wave2flagid, 84516, -16753, -1829, 0, world.instanceId)]
		#		world.flagInstance += [self.spawnNpc(self.wave2flagid, 81651, -15373, -1832, 0, world.instanceId)]
		#	return
		if event == 'exit':
			world = self.getWorld(player)
			if world:
				self.playerExit(world.instanceId, player.getObjectId())
				
	def onFirstTalk(self, npc, player):
		st = player.getQuestState(self.qn)
		if not st:
			st = self.newQuestState(player)
			st.setState(State.STARTED)
		lastInstanceId = st.getInt('instanceId') or None
		world = self.getWorld(player)
		if world:
			return self.htm_header + self.htm_exit + self.htm_footer
		if lastInstanceId:
			world = InstanceManager.getInstance().getWorld(lastInstanceId)
			if world and world.stage in [0,1,2,3] and world.allowed.contains(player.getObjectId()):
				return self.htm_header + self.htm_reentry + self.htm_footer
		return self.htm_header + self.htm_go + self.htm_footer

	def checkAllow(self, player, target):
		message = ""
		if not Util.checkIfInRange(2000, player, target, False):
			message = "%s 不在隊長範圍 2000 單位內" % target.getName()
		if not target.getLevel() >= 80: 
			message = "%s 等級不足" % target.getName()
		if self.getQuestItemsCount(target, self.require_item_id) < self.require_item_count:
			message = "%s 所需道具不足 需要 %s %d 個" % (target.getName(), self.require_item_name, self.require_item_count)
		l, c = InstanceManager.getInstance().getInstanceTime(target.getObjectId(), self.InstanceTemplateId), System.currentTimeMillis()
		if l > c:
			message = "%s 副本時間限制 %d 秒後可用" % (target.getName(), (l - c)/1000)
		if len(message) > 0:
			player.sendMessage(message)
			if player.getObjectId() != target.getObjectId():
				target.sendMessage(message)
			return False
		return True
		
	def plotCircle(self, x, y, r, steps):
		ret = []
		anginc = math.pi * 2 / steps
		ang = 0
		for step in xrange(steps):
			ang += anginc
			xx = r * math.cos(ang)
			yy = r * math.sin(ang)
			ret += [(int(xx + x), int(yy + y))]
		return ret

	def getRandomXYZ(self, x, y, z, offset):
		return x+Rnd.get(-offset, offset), y+Rnd.get(-offset, offset), z
		
	def getRandomPlayer(self, world):
		allplayers = self.getAllInstancePlayers(world.instanceId)
		if len(allplayers):
			return allplayers[Rnd.get(0, len(allplayers)-1)]
		return None
		#return L2World.getInstance().getPlayer(world.allowed.get(Rnd.get(0, world.allowed.size()-1)))

	def getRandomFlag(self, world):
		return world.flagInstance[Rnd.get(0,len(world.flagInstance)-1)]

	def getWorld(self, player = None, instanceId = None):
		if player and isinstance(player, L2Object):
			return InstanceManager.getInstance().getWorld(player.getInstanceId())
			#return InstanceManager.getInstance().getPlayerWorld(player)
		if instanceId:
			return InstanceManager.getInstance().getWorld(instanceId)
		return None
	
	def teleport(self, player, instanceId):
		st = player.getQuestState(self.qn)
		if not st:
			st = self.newQuestState(player)
			st.setState(State.STARTED)
		st.set('instanceId', str(instanceId))
		player.getAI().setIntention(CtrlIntention.AI_INTENTION_IDLE)
		player.setInstanceId(instanceId);
		player.teleToLocation(*self.entryLoc);
		if player.getPet():
			self.teleport(player.getPet(), instanceId)

	def broadcastScreenMessage(self, instanceId, message, duration = 10000):
		Broadcast.toPlayersInInstance(ExShowScreenMessage(message, duration), instanceId)
			
	def showScreenMessage(self, player, message, duration = 10000):
		player.sendPacket(ExShowScreenMessage(message, duration))
			
	def broadcastMessage(self, instanceId, text):
		Broadcast.toPlayersInInstance(SystemMessage.sendString(text), instanceId)
	
	def broadcastTimer(self, instanceId, time, text):
		for objId in InstanceManager.getInstance().getWorld(instanceId).allowed:
			p = L2World.getInstance().getPlayer(objId)
			p.sendPacket(ExSendUIEvent(p, False, False, time, 0, text))
			#Broadcast.toPlayersInInstance(ExSendUIEvent(), instanceId)
			
	def spawnNpc(self, npcId, x, y, z, heading, instId):
		npcTemplate = NpcTable.getInstance().getTemplate(npcId)
		inst = InstanceManager.getInstance().getInstance(instId)
		try:
			npcSpawn = L2Spawn(npcTemplate)
			npcSpawn.setLocx(x)
			npcSpawn.setLocy(y)
			npcSpawn.setLocz(z)
			#npcSpawn.setHeading(heading)
			npcSpawn.setAmount(1)
			npcSpawn.setInstanceId(instId)
			SpawnTable.getInstance().addNewSpawn(npcSpawn, False)
			npc = npcSpawn.doSpawn()
			#npc.setOnKillDelay(0)
			#npc.setRunning()
			return npc
		except:
			print "spawnNPC error"
			
	def getAllVisibleNpcs(self, world):
		npcs = []
		if not isinstance (world, MyInstanceWorld):
			return npcs
		i = InstanceManager.getInstance().getInstance(world.instanceId)
		if not i:
			return npcs
		for n in i.getNpcs():
			if L2World.getInstance().findObject(n.getObjectId()):
				npcs += [n]
		return npcs
		
	def addHate(self, world, npc, target):
		try:
			if target and L2World.getInstance().findObject(target.getObjectId()):
				npc.setTarget(target)
				#npc.getKnownList().addKnownObject(target)
				npc.addDamageHate(target, 0, Rnd.get(100,999))
				npc.getAI().setIntention(CtrlIntention.AI_INTENTION_ATTACK)
		except:
			pass

	def getAllInstancePlayers(self, instanceId):
		p = []
		i = InstanceManager.getInstance().getInstance(instanceId) 
		if i:
			for pid in i.getPlayers().toArray():
				player = L2World.getInstance().getPlayer(pid)
				if player:
					p += [player]
		return p

	def playerExit(self, instanceId, playerId):
		i = InstanceManager.getInstance().getInstance(instanceId) 
		if i:
			i.ejectPlayer(playerId)
			i.removePlayer(playerId)
		
	def removeAllPlayers(self, instanceId):
		i = InstanceManager.getInstance().getInstance(instanceId) 
		if i:
			for pid in i.getPlayers().toArray():
				i.ejectPlayer(pid)
				i.removePlayer(pid)
					
	def flowControl(self, world):
		if not isinstance (world, MyInstanceWorld):
			return
		if world.stage == 1:
			if world.step == 2:
				allnpc = self.getAllVisibleNpcs(world)
				for n in allnpc:
					p = self.getRandomPlayer(world)
					self.addHate(world, n, p)
			if world.wave1killed >= self.killcounttos2s0:
				world.stage, world.step = 2, 0
				world.flagInstance += [self.spawnNpc(self.wave2flagid, 84516, -16753, -1829, 0, world.instanceId)]
				world.flagInstance += [self.spawnNpc(self.wave2flagid, 81651, -15373, -1832, 0, world.instanceId)]
				#self.startQuestTimer("s2s0 %d" % world.instanceId, 1000 * 5, None, None, False)
				self.broadcastScreenMessage(world.instanceId, "請保護 %s 不要被殺" % world.flagInstance[0].getName())

			return

		if world.stage == 2:
			if world.step == 0:
				allnpc = self.getAllVisibleNpcs(world)
				for n in allnpc:
					p = None
					if n.getNpcId() == self.wave1mobid:
						p = self.getRandomFlag(world)
					if n.getNpcId() in [self.wave2mobid, self.wave2flagid]:
						p = self.getRandomPlayer(world)
					if p:
						self.addHate(world, n, p)
				for n in world.flagInstance:
					if not L2World.getInstance().findObject(n.getObjectId()):
						self.broadcastMessage(world.instanceId, "%s 死亡 副本失敗" % n.getName())
						self.broadcastScreenMessage(world.instanceId, "%s 死亡 副本失敗" % n.getName())
						world.allowed.clear()
						self.removeAllPlayers(world.instanceId)
				if len(allnpc) == 2:
					world.stage, world.step = 3, 0
			return
		
		if world.stage == 3:
			if world.step == 0:
				for n in world.flagInstance:
					if n:
						i = InstanceManager.getInstance().getInstance(world.instanceId)
						if i:
							i.removeNpc(n)
							n.deleteMe()
				x, y, z = self.entryLoc
				world.bossInstance = self.spawnNpc(self.bossid, x, y, z, 0, world.instanceId)
				self.broadcastScreenMessage(world.instanceId, "最後階段")
				world.stage, world.step = 3, 1
			if world.step == 1:
				b = world.bossInstance
				if b.getCurrentHp() / b.getMaxHp() < 0.9:
					world.stage, world.step = 3, 2
					x, y, z = self.entryLoc
					world.runningInstance = self.spawnNpc(29191, x, y, z, 0, world.instanceId)
					world.runningInstance.setRunning()
					world.runningInstance.setIsInvul(True)
			if world.step == 2:
				x, y, z = world.bossInstance.getX(), world.bossInstance.getY(), world.bossInstance.getZ()
				r = self.plotCircle(x, y, self.runningR, self.runningStep)
				if r and len(r):
					world.runningIndex += 1
					if world.runningIndex >= self.runningStep:
						world.runningIndex = 0
					x, y = r[world.runningIndex]
					world.runningInstance.getAI().setIntention(CtrlIntention.AI_INTENTION_MOVE_TO, L2CharPosition(x, y, z, 0))

		if world.stage == 4:
			if world.step == 0:
				i = InstanceManager.getInstance().getInstance(world.instanceId)
				if i:
					i.removeNpc(world.runningInstance)
					world.runningInstance.deleteMe()
					
Quest()	


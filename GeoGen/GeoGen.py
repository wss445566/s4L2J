from java.net import Socket
from java.io import DataInputStream
from java.lang import Thread
import struct
from com.l2jserver.gameserver.model import L2World
from com.l2jserver import Config
from com.l2jserver.gameserver.network.serverpackets import FlyToLocation
from com.l2jserver.gameserver.model.quest.jython import QuestJython as JQuest
from com.l2jserver.gameserver.instancemanager import QuestManager
from com.l2jserver.gameserver.network.serverpackets.FlyToLocation import FlyType
from com.l2jserver.gameserver.geoeditorcon import GeoEditorListener
from com.l2jserver.gameserver.network.serverpackets import MoveToLocation
from com.l2jserver.gameserver.network.serverpackets import L2GameServerPacket
import time
from java.lang import Byte
from java.lang import String
from com.l2jserver.gameserver.geoeditorcon import VPListener

class MyMoveToLocation(L2GameServerPacket):
	def __init__(self, player, x, y, z, dx, dy, dz):
		L2GameServerPacket.__init__(self)
		self._charObjId = player.getObjectId()
		self._x, self._y, self._z = x, y, z
		self._xDst, self._yDst, self._zDst = dx, dy, dz
		
	def writeImpl(self):
		self.writeC(0x2f)
		self.writeD(self._charObjId)
		self.writeD(self._xDst)
		self.writeD(self._yDst)
		self.writeD(self._zDst)
		self.writeD(self._x)
		self.writeD(self._y)
		self.writeD(self._z)
		
	def getType(self):
		return "MyMoveToLocation"

class MyFlyToLocation(L2GameServerPacket):
	def __init__(self, player, x, y, z, dx, dy, dz):
		L2GameServerPacket.__init__(self)
		self._charObjId = player.getObjectId()
		self._x, self._y, self._z = x, y, z
		self._xDst, self._yDst, self._zDst = dx, dy, dz
		
	def writeImpl(self):
		self.writeC(0xd4)
		self.writeD(self._charObjId)
		self.writeD(self._xDst)
		self.writeD(self._yDst)
		self.writeD(self._zDst)
		self.writeD(self._x)
		self.writeD(self._y)
		self.writeD(self._z)
		self.writeD(2)
		
	def getType(self):
		return "MyFlyToLocation"
		
class MyValidatePosition(L2GameServerPacket):
	def __init__(self, player, x, y, z):
		L2GameServerPacket.__init__(self)
		self._charObjId = player.getObjectId()
		self._x, self._y, self._z = x, y, z
		
	def writeImpl(self):
		self.writeC(0x79)
		self.writeD(self._charObjId)
		self.writeD(self._x)
		self.writeD(self._y)
		self.writeD(self._z)
		self.writeD(0)
		
	def getType(self):
		return "MyValidatePosition"

class GeoUtil:
	def getRegionX(x):
		return (x >> 15) + 20
	def getRegionY(y):
		return (y >> 15) + 18
	def getRegionXY(x, y):
		return GeoUtil.getRegionX(x), GeoUtil.getRegionY(y)
	def getBlockX(x):
		return ((x - L2World.MAP_MIN_X) >> 7) % 256
	def getBlockY(y):
		return ((y - L2World.MAP_MIN_Y) >> 7) % 256
	def getBlockXY(x, y):
		return GeoUtil.getBlockX(x), GeoUtil.getBlockY(y)
	def getCellX(x):
		return ((x - L2World.MAP_MIN_X) >> 4) % 8
	def getCellY(y):
		return ((y - L2World.MAP_MIN_Y) >> 4) % 8
	def getCellXY(x, y):
		return GeoUtil.getCellX(x), GeoUtil.getCellY(y)
	def getX(rx, ry, bx, by, cx, cy):
		return ((rx - 20) << 15) + (bx << 7) + (cx << 4) + 8
	def getY(rx, ry, bx, by, cx, cy):
		return ((ry - 18) << 15) + (by << 7) + (cy << 4) + 8
	def getXY(rx, ry, bx, by, cx, cy):
		return GeoUtil.getX(rx, ry, bx, by, cx, cy), GeoUtil.getY(rx, ry, bx, by, cx, cy)
	getRegionX = staticmethod(getRegionX)
	getRegionY = staticmethod(getRegionY)
	getRegionXY = staticmethod(getRegionXY)
	getBlockX = staticmethod(getBlockX)
	getBlockY = staticmethod(getBlockY)
	getBlockXY = staticmethod(getBlockXY)
	getCellX = staticmethod(getCellX)
	getCellY = staticmethod(getCellY)
	getCellXY = staticmethod(getCellXY)
	getX = staticmethod(getX)
	getY = staticmethod(getY)
	getXY = staticmethod(getXY)

class gsgeConnect(Thread):
	def __init__(self):
		Thread.__init__(self)
		
	def setvpl(self, vpl):
		self.vpl = vpl
		
	def list2num(self, list):
		return sum([list[i] << (i*8) for i in xrange(len(list))])
	
	def run(self):
		print "connect to GS"
		sgs = Socket("127.0.0.1", 9011)
		i = DataInputStream(sgs.getInputStream())
		print "connect to GeoEditor"
		sge = Socket("127.0.0.1", 2109)
		#o = DataOutputStream(sge.getOutputStream())
		o = sge.getOutputStream()
		Thread.sleep(5000)
		GeoEditorListener.getInstance().getThread().addListener(self.vpl)
		print "gsge Ready"
		bufsize = 4096
		lastpos = 0
		buf = String("\0" * bufsize).getBytes()
		fc = 0
		while True:
			if not i.available():
				Thread.sleep(10)
				fc += 1
				if fc % 500 == 0:
					o.flush()
					fc = 0
				continue
			lastpos += i.read(buf, lastpos, bufsize-lastpos)
			while lastpos > 0 and lastpos > buf[0]:
				if buf[1] == 2:
					pass
				elif buf[1] == 1:
					x = self.list2num(buf[2:6])
					y = self.list2num(buf[6:10])
					z = self.list2num(buf[10:12])
					if z > -15000:
						rx, ry = GeoUtil.getRegionXY(x,y)
						if (rx, ry) == (22,22):
							bx, by = GeoUtil.getBlockXY(x, y)
							cx, cy = GeoUtil.getCellXY(x, y)
							o.write(struct.pack('>BBBBh', bx, by, cx, cy, z))
				newpos = buf[0]+1
				if len(buf) - newpos < bufsize:
					buf = buf[newpos:]+String("\0" * bufsize).getBytes()
				else:
					buf = buf[newpos:]
				lastpos -= newpos

				
class Runtask(Thread):
	def __init__(self):
		Thread.__init__(self)
		
	def setParam(self, q, freegm, bbx, bby):
		self.q = q
		self.freegm = freegm
		self.bbx = bbx
		self.bby = bby
		
	def run(self):
		gm = self.q.gm[self.freegm]['i']
		print "start %d %d" % (self.bbx, self.bby), self.freegm
		#GeoEditorListener.getInstance().getThread().addGM(gm)
		GeoEditorListener.getInstance().getThread().setMode(1)
		start = time.time()
		if self.q.fly256Block(self.freegm, self.bbx, self.bby):
			gm.sendMessage("finish %d %d %d sec" % (self.bbx, self.bby,  time.time() - start))
			gm.geoFree = True
		print "finish %d %d" % (self.bbx, self.bby), self.freegm, time.time() - start
		del self.q.gm[self.freegm]


class VPL(VPListener):
	def onVP(self, player, x, y, z):
		rx, ry = GeoUtil.getRegionXY(x, y)
		bx, by = GeoUtil.getBlockXY(x, y)
		cx, cy = GeoUtil.getCellXY(x, y)
		if (rx, ry) != (22,22):
			return
		self.q.setLastZ(bx, by, cx, cy, z)
	
	def setQuest(self, q):
		self.q = q
		
class Quest(JQuest):
	qID = -1
	qn = "GeoGen"
	qDesc = "custom"
	
	#doneBBlock = [0]*1
	doneBBlock = [0]*16*16
	doneBlock = [0]*256*256
	gm = {}
	lastZ = [20000]*(2048*2048)
	
	def __init__(self, id = qID, name = qn, descr = qDesc):
		self.qID, self.qn, self.qDesc = id, name, descr
		JQuest.__init__(self, id, name, descr)
		
		try:
			i = open('_lastZ.bin','rb')
			for z in xrange(2048*2048):
				self.lastZ[z] = struct.unpack('<h', i.read(2))[0]
			i.close()
		except:
			print "_lastZ.bin load error"
			
		self.vpl = VPL()
		self.vpl.setQuest(self)
		
		self.gsge = gsgeConnect()
		self.gsge.setvpl(self.vpl)
		self.gsge.start()
		
		self.startQuestTimer("onTime1", 200, None, None, True)
		print "Init:" + self.qn + " loaded"

	def fly(self, gg, x, y, z, dx, dy, dz):
		gg.sendPacket(MyFlyToLocation(gg, x, y, z, dx, dy, dz))
	def validate(self, gg, x, y, z):
		gg.sendPacket(MyValidatePosition(gg, x, y, z))

	def fly256Block(self, g, bbx, bby):
		self.gm[g]['s'] = 1
		gg = self.gm[g]['i']
		self.doneBBlock[bby*16+bbx] = 1
		x, y = GeoUtil.getXY(22, 22, bbx*16+7, bby*16+7, 0, 0)
		self.validate(gg, x, y ,20000)
		for by in xrange(bby*16, (bby+1)*16):
			for bx in xrange(bbx*16,(bbx+1)*16):
				if not self.flyOneBlock(gg, bx, by):
					print "fail bx by", bx, by
					self.doneBBlock[bby*16+bbx] = 0
					return False
		self.doneBBlock[bby*16+bbx] = 2
		return True
	
	def flyOneLine(self, gg, bx, by, cy):
		vpcount = gg.vpCount = 0
		for cx in xrange(8):
			x, y = GeoUtil.getXY(22, 22, bx, by, cx, cy)
			lastZ = self.getLastZ(bx, by, cx, cy) - 150
			self.setLastZ(bx, by, cx, cy, lastZ)
			if lastZ <= -15000:
				continue
		
			while vpcount > gg.vpCount+2:
				Thread.sleep(5)
				if not gg.isOnline():
					print "no gm"
					self.doneBlock[by*256+bx] = 0
					return False
				if not self.gsge.isAlive():
					print "gsge error"
					self.doneBlock[by*256+bx] = 0
					return False
				
			if gg.vpCount > vpcount:
				vpcount = gg.vpCount
			self.fly(gg, x, y, lastZ, x, y, lastZ - 16)
			vpcount += 1
		return True

	def flyOneBlock(self, gg, bx, by):
		if self.doneBlock[by*256+bx] in [2, 1]:
			return True
		self.doneBlock[by*256+bx] = 1
		#print "bx:%d by:%d working:%s" %(bx, by, gg.getName())
		
		for cy in xrange(8):
			if not self.flyOneLine(gg, bx, by, cy): return False
		self.doneBlock[by*256+bx] = 2
		return True
		
	def getFreeGM(self):
		return [x for x in self.gm if self.gm[x]['s'] == 0]

	def getNotDoneBBlock(self):
		#for x in xrange(len(self.doneBBlock)-1, -1, -1):
		for x in xrange(len(self.doneBBlock)):
			if self.doneBBlock[x] in [0,1]:
				return x
		return -1
	
	def getLastZIndex(self, bx, by, cx, cy):
		x = bx * 8 + cx
		y = by * 8 + cy
		return x + y * 2048
		
	def getLastZ(self, bx, by, cx, cy):
		return self.lastZ[self.getLastZIndex(bx, by, cx, cy)]
		
	def setLastZ(self, bx, by, cx, cy, z):
		index = self.getLastZIndex(bx, by, cx, cy)
		if z < self.lastZ[index]:
			self.lastZ[index] = z
	
	def checkOneBlock(self, bx, by):
		for y in xrange(8):
			for x in xrange(8):
				z = self.getLastZ(bx, by, x, y)
				if z > -15000: 
					#print bx, by, x, y, z
					return False
		return True
		
	def saveLastZ(self):
		o = open('_lastZ.bin','wb')
		for index in xrange(len(q.lastZ)):
			o.write(struct.pack('<h', q.lastZ[index]))
			#o.write("%d\n" % q.lastZ[line])
		o.close()

	def onAdvEvent(self, event, npc, player):
		#return
		if not self.gsge.isAlive():
			print "gsge not connect"
			self.cancelQuestTimers("onTime1")
			return
		if event == "onTime1":
			for gm in GeoEditorListener.getInstance().getThread()._gms.toArray():
			#for player in L2World.getInstance().getAllPlayersArray():
				name = gm.getName()
				if not name in self.gm:
					if gm.geoFree:
						gm.geoFree = False
						self.gm[name] = {'i':gm, 's':0}
			b = self.getNotDoneBBlock()
			if b > -1:
				freegm = self.getFreeGM()
				if len(freegm):
					freegm = freegm[0]
					rt = Runtask()
					rt.setParam(self, freegm, b % 16, b >> 4)
					rt.start()
			else:
				print "no job"
				self.saveLastZ()
				#self.doneBBlock = [0]*1
				self.doneBBlock = [0]*16*16
				doneCount = 0
				for by in xrange(256):
					for bx in xrange(256):
						if self.checkOneBlock(bx, by):
							self.doneBlock[by*256+bx] = 2
							#print "bx %d by %d done" % (bx, by)
							doneCount += 1
						else:
							self.doneBlock[by*256+bx] = 0
				print "Done %d, not done %d" % (doneCount, 256*256 - doneCount)
				#self.doneBlock = [0]*(256*256)
				#self.cancelQuestTimers("onTime1")
			return
Quest()

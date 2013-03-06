import sys
from com.l2jserver.gameserver.model.quest import State
from com.l2jserver.gameserver.model.quest import QuestState
from com.l2jserver.gameserver.model.quest.jython import QuestJython as JQuest

from com.l2jserver.gameserver.model import L2World

from javax.swing import *
from java.awt import *
from javax.imageio import ImageIO
from java.io import File
from java.awt.event import *
from java.lang import System
from java.awt.image import BufferedImage
from java.util import Date

class MyWindowListener(WindowListener):
	def windowActivated(self, event):
		pass
	def windowClosed(self, event):
		System.gc()
	def windowClosing(self, event):
		pass
	def windowDeactivated(self, event):
		pass
	def windowDeiconified(self, event):
		pass
	def windowIconified(self, event):
		pass
	def windowOpened(self, event):
		pass

class playerListPanel(JPanel):
	def __init__(self):
		JPanel.__init__(self)
		self.player_list = JList(["aaaaaaaaaaa","bbbbbbbbbbbbb","ccccccccc"])
		self.add(self.player_list)
		self.setPreferredSize(Dimension(100,100))
		
class mapPanel(JPanel, ActionListener, MouseListener):
	image1 = ImageIO.read(File("data/scripts/custom/mapGUI/l2map1.jpg"))
	image2 = ImageIO.read(File("data/scripts/custom/mapGUI/l2map2.jpg"))
	gameMinX = -259839
	gameMaxX = 228832
	gameMinY = -262143
	gameMaxY = 260000
	gameMapWidth = gameMaxX - gameMinX
	gameMapHeight = gameMaxY - gameMinY
	imageW = 2464
	imageH = 2623
	buff = BufferedImage(imageW, imageH, BufferedImage.TYPE_3BYTE_BGR)
	last_buff_update = 0
	buff_update_freq = 1000 * 10 #1000 = 1秒
	buff_update_timer = None
	
	gm_name_list = ["GM"]
	
	def __init__(self):
		JPanel.__init__(self)
		self.setPreferredSize(Dimension(self.imageW, self.imageH))
		self.updateBufferedImage()
		self.buff_update_timer = Timer(self.buff_update_freq, self)
		self.buff_update_timer.start()
		
	def mouseClicked(self, event):
		if event.getButton() == MouseEvent.BUTTON1:
			for player in L2World.getInstance().getAllPlayersArray():
				if player.getName() in self.gm_name_list:
					player.teleToLocation(self.mapToGameX(event.getX()), self.mapToGameY(event.getY()), 20000, 0, False)

	def mouseEntered(self, event):
		pass
	def mouseExited(self, event):
		pass
	def mousePressed(self, event):
		pass
	def mouseReleased(self, event):
		pass
		
	def actionPerformed(self, event):
		self.repaint()
	
	def updateBufferedImage(self):
		w = self.getWidth()
		h = self.getHeight()
		if w <= 0 or h <= 0: return
		g = self.buff.getGraphics()

		map1y = self.gameToMapY(108000)
		map2x = self.gameToMapX(-165000)

		g.clearRect(0,0,w,h)
		g.drawImage(self.image1, 0, map1y, map2x, h - map1y, self)
		g.drawImage(self.image2, map2x, 0, w - map2x, h, self)

		all_player = L2World.getInstance().getAllPlayersArray()
		for p in all_player:
			self.drawPlayer(g, p)
		self.last_buff_update = Date().getTime()
		
	def getScaleX(self):
		return self.gameMapWidth/self.getWidth()

	def getScaleY(self):
		return self.gameMapHeight/self.getHeight()
	
	def mapToGameX(self, x):
		return x * self.getScaleX() + self.gameMinX
		
	def mapToGameY(self, y):
		return y * self.getScaleY() + self.gameMinY

	def mapToGameXY(self, x, y):
		return self.mapToGameX(x), self.mapToGameY(y)
		
	def gameToMapX(self, x):
		return (x - self.gameMinX)/self.getScaleX()
		
	def gameToMapY(self, y):
		return (y - self.gameMinY)/self.getScaleY()
		
	def gameToMapXY(self, x, y):
		return self.gameToMapX(x), self.gameToMapY(y)
		
	def drawPlayer(self, g, p):
		fs = 10
		hs = fs/2
		x, y = self.gameToMapXY(p.getX(), p.getY())
		g.setColor(Color(0))
		g.fill3DRect(x - hs, y - hs, fs, fs, True)
		g.setColor(Color(p.getAppearance().getNameColor()))
		g.drawLine(x - hs, y - hs, x + hs, y + hs)
		g.drawLine(x + hs, y - hs, x - hs, y + hs)
		g.drawString(p.getName(), x, y)
		
	def paint(self, g):
		if self.last_buff_update + self.buff_update_freq <= Date().getTime():
			self.updateBufferedImage()
		g.drawImage(self.buff, 0, 0, self)

class Quest(JQuest):
	qID = -1
	qn = "mapGUI"
	qDesc = "custom"

	jmessage = None
        
	def __init__(self, id = qID, name = qn, desc = qDesc):
		JQuest.__init__(self, id, name, desc)
		self.buildGUI()
		print "Init:" + self.qn + " loaded"

	def buildGUI(self):
		self.jmap = mapPanel()
		self.jmap.addMouseListener(self.jmap)

		jsp = JScrollPane(self.jmap)
		jsp.setHorizontalScrollBarPolicy(JScrollPane.HORIZONTAL_SCROLLBAR_ALWAYS)
		jsp.setVerticalScrollBarPolicy(JScrollPane.VERTICAL_SCROLLBAR_ALWAYS)

		jp = JPanel()
		jp.add(playerListPanel())
		jp.add(jsp)
		jp.setSize(800, 600)
		
		frame = JFrame("玩家座標後台")
		container = frame.getContentPane()
		container.add(jp)
		
		frame.pack()
		frame.setVisible(True)
		frame.setSize(800, 600)
		frame.setDefaultCloseOperation(JFrame.DISPOSE_ON_CLOSE)
		#frame.setDefaultCloseOperation(JFrame.DO_NOTHING_ON_CLOSE)
		frame.addWindowListener(MyWindowListener())	

Quest()

from com.l2jserver.gameserver import Shutdown
Shutdown.getInstance().startTelnetShutdown("127.0.0.1", 60 * 60 * 24 * 7, True)
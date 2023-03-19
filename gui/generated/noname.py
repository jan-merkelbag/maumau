# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version 3.10.1-0-g8feb16b)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc

###########################################################################
## Class MainFrame
###########################################################################

class MainFrame ( wx.Frame ):

    def __init__( self, parent ):
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"Mau Mau", pos = wx.DefaultPosition, size = wx.Size( 500,300 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

        self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

        self.m_menubar = wx.MenuBar( 0 )
        self.m_menufile = wx.Menu()
        self.m_menuItem_newGame = wx.MenuItem( self.m_menufile, wx.ID_ANY, u"New Game"+ u"\t" + u"CTRL+n", wx.EmptyString, wx.ITEM_NORMAL )
        self.m_menufile.Append( self.m_menuItem_newGame )

        self.m_menuItem_close = wx.MenuItem( self.m_menufile, wx.ID_ANY, u"Close"+ u"\t" + u"ALT+F4", wx.EmptyString, wx.ITEM_NORMAL )
        self.m_menufile.Append( self.m_menuItem_close )

        self.m_menubar.Append( self.m_menufile, u"File" )

        self.SetMenuBar( self.m_menubar )

        gSizer = wx.GridSizer( 0, 2, 0, 0 )

        bSizer1 = wx.BoxSizer( wx.VERTICAL )

        self.m_staticText_labelPlayerList = wx.StaticText( self, wx.ID_ANY, u"Players:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText_labelPlayerList.Wrap( -1 )

        bSizer1.Add( self.m_staticText_labelPlayerList, 0, wx.ALL, 5 )

        m_listBox_playerListChoices = []
        self.m_listBox_playerList = wx.ListBox( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_listBox_playerListChoices, 0 )
        bSizer1.Add( self.m_listBox_playerList, 1, wx.ALL|wx.EXPAND, 5 )


        gSizer.Add( bSizer1, 1, wx.EXPAND, 5 )

        self.m_bitmap_lastCard = wx.StaticBitmap( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, 0 )
        gSizer.Add( self.m_bitmap_lastCard, 0, wx.ALL|wx.EXPAND, 5 )


        self.SetSizer( gSizer )
        self.Layout()

        self.Centre( wx.BOTH )

        # Connect Events
        self.Bind( wx.EVT_MENU, self.new_game, id = self.m_menuItem_newGame.GetId() )
        self.Bind( wx.EVT_MENU, self.close, id = self.m_menuItem_close.GetId() )

    def __del__( self ):
        pass


    # Virtual event handlers, override them in your derived class
    def new_game( self, event ):
        event.Skip()

    def close( self, event ):
        event.Skip()



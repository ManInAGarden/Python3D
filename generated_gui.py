# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version Oct 26 2018)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc

import gettext
_ = gettext.gettext

###########################################################################
## Class ViewerFrame
###########################################################################

class ViewerFrame ( wx.Frame ):

	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = _(u"Python3d Viewer"), pos = wx.DefaultPosition, size = wx.Size( 521,432 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL, name = u"ViewerMainFrame" )

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

		self.m_statusBar1 = self.CreateStatusBar( 1, wx.STB_SIZEGRIP, wx.ID_ANY )
		self.mainMenuBar = wx.MenuBar( 0 )
		self.fileManu = wx.Menu()
		self.quitMenuItem = wx.MenuItem( self.fileManu, wx.ID_ANY, _(u"Beenden")+ u"\t" + u"CTRL+Q", wx.EmptyString, wx.ITEM_NORMAL )
		self.fileManu.Append( self.quitMenuItem )

		self.mainMenuBar.Append( self.fileManu, _(u"Dateien") )

		self.SetMenuBar( self.mainMenuBar )

		bSizer1 = wx.BoxSizer( wx.VERTICAL )

		self.picTextSplitter = wx.SplitterWindow( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.SP_3D )
		self.picTextSplitter.Bind( wx.EVT_IDLE, self.picTextSplitterOnIdle )

		self.leftPanel = wx.Panel( self.picTextSplitter, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer3 = wx.BoxSizer( wx.VERTICAL )

		self.canvasScrolledWindow = wx.ScrolledWindow( self.leftPanel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.HSCROLL|wx.VSCROLL )
		self.canvasScrolledWindow.SetScrollRate( 5, 5 )
		bSizer3.Add( self.canvasScrolledWindow, 1, wx.EXPAND |wx.ALL, 5 )


		self.leftPanel.SetSizer( bSizer3 )
		self.leftPanel.Layout()
		bSizer3.Fit( self.leftPanel )
		self.rightPanel = wx.Panel( self.picTextSplitter, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer4 = wx.BoxSizer( wx.VERTICAL )

		self.sourceCodeTextBox = wx.TextCtrl( self.rightPanel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.HSCROLL|wx.TE_MULTILINE )
		self.sourceCodeTextBox.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "Courier New" ) )
		self.sourceCodeTextBox.SetMinSize( wx.Size( 200,300 ) )

		bSizer4.Add( self.sourceCodeTextBox, 0, wx.ALL|wx.EXPAND, 5 )

		bSizer41 = wx.BoxSizer( wx.HORIZONTAL )

		self.draw_button = wx.Button( self.rightPanel, wx.ID_ANY, _(u"Zeichnen"), wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer41.Add( self.draw_button, 0, wx.ALL, 5 )


		bSizer4.Add( bSizer41, 1, wx.EXPAND, 5 )


		self.rightPanel.SetSizer( bSizer4 )
		self.rightPanel.Layout()
		bSizer4.Fit( self.rightPanel )
		self.picTextSplitter.SplitVertically( self.leftPanel, self.rightPanel, 0 )
		bSizer1.Add( self.picTextSplitter, 1, wx.EXPAND, 5 )


		self.SetSizer( bSizer1 )
		self.Layout()

		self.Centre( wx.BOTH )

		# Connect Events
		self.Bind( wx.EVT_MENU, self.quit_viewer, id = self.quitMenuItem.GetId() )
		self.canvasScrolledWindow.Bind( wx.EVT_PAINT, self.paint_canvas )
		self.canvasScrolledWindow.Bind( wx.EVT_SIZE, self.resize_canvas )
		self.draw_button.Bind( wx.EVT_BUTTON, self.draw_btn_clicked )

	def __del__( self ):
		pass


	# Virtual event handlers, overide them in your derived class
	def quit_viewer( self, event ):
		event.Skip()

	def paint_canvas( self, event ):
		event.Skip()

	def resize_canvas( self, event ):
		event.Skip()

	def draw_btn_clicked( self, event ):
		event.Skip()

	def picTextSplitterOnIdle( self, event ):
		self.picTextSplitter.SetSashPosition( 0 )
		self.picTextSplitter.Unbind( wx.EVT_IDLE )



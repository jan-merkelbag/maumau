import wx

from gui.main_frame import MyMainFrame


def main():
    ex = wx.App()
    window = MyMainFrame(None)
    window.Show(True)
    ex.MainLoop()


if __name__ == '__main__':
    main()

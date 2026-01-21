"""
BDSM 论坛工具 - Modern UI Kivy 版本
特点：侧边栏导航、Material Design 风格深色主题、平滑动画、圆角控件
"""
import os
import sys
import threading
import json

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition, NoTransition
from kivy.uix.behaviors import ButtonBehavior
from kivy.core.window import Window
from kivy.clock import Clock, mainthread
from kivy.core.text import LabelBase
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.utils import get_color_from_hex
from kivy.animation import Animation
from functools import partial

# ---------- 字体初始化 ----------
DEFAULT_FONT = None

def init_chinese_font():
    global DEFAULT_FONT
    # 尝试加载中文字体，优先级：项目目录 -> 系统目录 -> 默认
    font_paths = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts', 'NotoSansSC-Regular.ttf'),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'msyh.ttc'), # Windows 测试常用
        '/system/fonts/NotoSansCJK-Regular.ttc', # Android
        '/system/fonts/NotoSansSC-Regular.otf',
        '/system/fonts/DroidSansFallback.ttf',
    ]
    
    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                font_name = 'CustomChineseFont'
                LabelBase.register(name=font_name, fn_regular=font_path)
                DEFAULT_FONT = font_name
                print(f"✅ 加载字体成功: {font_path}")
                return
            except Exception as e:
                print(f"⚠️ 字体加载失败 {font_path}: {e}")
    
    print("⚠️ 未找到特定中文字体，使用系统默认")

init_chinese_font()

# ---------- 现代化配色方案 (Cyberpunk/Modern Dark) ----------
THEME = {
    'bg_dark': get_color_from_hex('#111827'),      # 深色背景 (Gray 900)
    'bg_sidebar': get_color_from_hex('#1F2937'),   # 侧边栏/卡片背景 (Gray 800)
    'bg_input': get_color_from_hex('#374151'),     # 输入框背景 (Gray 700)
    'primary': get_color_from_hex('#F43F5E'),      # 主色调 (Rose 500) - 活力红/粉
    'primary_hover': get_color_from_hex('#BE123C'),# 主色调按压
    'secondary': get_color_from_hex('#3B82F6'),    # 次要色 (Blue 500)
    'text_main': get_color_from_hex('#F9FAFB'),    # 主要文字 (Gray 50)
    'text_dim': get_color_from_hex('#9CA3AF'),     # 次要文字 (Gray 400)
    'success': get_color_from_hex('#10B981'),      # 成功绿
    'error': get_color_from_hex('#EF4444'),        # 错误红
    'warning': get_color_from_hex('#F59E0B'),      # 警告黄
    'divider': get_color_from_hex('#374151'),      # 分割线
}

# ---------- 基础自定义控件 ----------

class ModernWidget(Widget):
    """辅助类，提供通用属性"""
    font_name = DEFAULT_FONT if DEFAULT_FONT else 'Roboto'

class RoundedBox(BoxLayout):
    """带圆角背景的 BoxLayout"""
    def __init__(self, bg_color=THEME['bg_sidebar'], radius=dp(10), **kwargs):
        super().__init__(**kwargs)
        self.bg_color = bg_color
        self.radius = radius
        with self.canvas.before:
            Color(*self.bg_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[self.radius])
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class ModernLabel(Label):
    """通用 Label"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_name = DEFAULT_FONT if DEFAULT_FONT else 'Roboto'
        self.color = kwargs.get('color', THEME['text_main'])

class ModernButton(ButtonBehavior, BoxLayout):
    """现代化按钮: 无边框，圆角，支持颜色变化"""
    def __init__(self, text="", bg_color=THEME['primary'], press_color=THEME['primary_hover'], font_size=dp(16), radius=dp(8), **kwargs):
        super().__init__(**kwargs)
        self.bg_color = bg_color
        self.press_color = press_color
        self.original_bg = bg_color
        self.padding = [dp(15), dp(10)]
        self.size_hint_y = None
        self.height = dp(45)
        
        with self.canvas.before:
            self.color_instruction = Color(*self.bg_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[radius])
        
        self.bind(pos=self.update_rect, size=self.update_rect)
        self.bind(state=self.on_state)

        self.label = ModernLabel(text=text, font_size=font_size, bold=True, halign='center', valign='middle')
        self.add_widget(self.label)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
        self.label.text_size = self.size 

    def on_state(self, instance, value):
        if value == 'down':
            self.color_instruction.rgba = self.press_color
        else:
            self.color_instruction.rgba = self.original_bg

class ModernGhostButton(ModernButton):
    """幽灵按钮（透明背景，用于次要操作）"""
    def __init__(self, **kwargs):
        bg = kwargs.pop('bg_color', [0, 0, 0, 0])
        super().__init__(bg_color=bg, press_color=[1, 1, 1, 0.1], **kwargs)
        self.label.color = THEME['text_dim']

class ModernInput(TextInput):
    """现代化输入框"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_active = ''
        self.background_color = THEME['bg_input']
        self.foreground_color = THEME['text_main']
        self.cursor_color = THEME['primary']
        self.hint_text_color = THEME['text_dim']
        self.font_name = DEFAULT_FONT if DEFAULT_FONT else 'Roboto'
        self.padding = [dp(15), dp(12)]
        self.write_tab = False # 禁止 Tab 键输入制表符，而是切换焦点

class ModernSpinner(Spinner):
    """下拉选择框样式"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = THEME['bg_input']
        self.color = THEME['text_main']
        self.font_name = DEFAULT_FONT if DEFAULT_FONT else 'Roboto'
        self.option_cls = ModernSpinnerOption

class ModernSpinnerOption(Button):
    """下拉选项样式"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = THEME['bg_sidebar']
        self.color = THEME['text_main']
        self.font_name = DEFAULT_FONT if DEFAULT_FONT else 'Roboto'
        self.height = dp(44)

# ---------- 弹窗组件 ----------

class InputDialog(Popup):
    """通用输入弹窗"""
    def __init__(self, title, fields, callback, **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.title_font = DEFAULT_FONT if DEFAULT_FONT else 'Roboto'
        self.title_size = dp(18)
        self.title_color = THEME['text_main']
        self.separator_color = THEME['primary']
        self.size_hint = (0.85, None)
        self.height = dp(100 + 65 * len(fields))
        self.background_color = [0, 0, 0, 0.8] # 半透明遮罩
        
        # 弹窗主体背景
        self.container = RoundedBox(bg_color=THEME['bg_sidebar'], orientation='vertical', padding=dp(20), spacing=dp(15))
        
        self.callback = callback
        self.inputs = {}

        for field in fields:
            row = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(60), spacing=dp(5))
            lbl = ModernLabel(
                text=field.get("label", ""),
                size_hint_y=None, height=dp(20),
                halign='left',
                color=THEME['text_dim'],
                font_size=dp(13)
            )
            lbl.bind(size=lbl.setter('text_size'))
            
            inp = ModernInput(
                text=str(field.get("default", "")),
                hint_text=field.get("hint", ""),
                multiline=False,
                size_hint_y=None, height=dp(40)
            )
            self.inputs[field.get("key", field.get("label"))] = inp
            row.add_widget(lbl)
            row.add_widget(inp)
            self.container.add_widget(row)

        # 按钮
        btn_row = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(15))
        cancel_btn = ModernButton(
            text='取消',
            bg_color=THEME['bg_input'],
            press_color=[0.3, 0.3, 0.3, 1],
            on_press=self.dismiss
        )
        confirm_btn = ModernButton(
            text='确定',
            bg_color=THEME['primary'],
            on_press=self.on_confirm
        )
        btn_row.add_widget(cancel_btn)
        btn_row.add_widget(confirm_btn)
        
        self.container.add_widget(Widget(size_hint_y=1)) # Spacer
        self.container.add_widget(btn_row)
        
        self.content = self.container

    def on_confirm(self, instance):
        values = {key: inp.text for key, inp in self.inputs.items()}
        self.dismiss()
        if self.callback:
            self.callback(values)

# ---------- 登录界面 ----------

class LoginScreen(Screen):
    def __init__(self, app, error_msg=None, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        
        # 背景
        with self.canvas.before:
            Color(*THEME['bg_dark'])
            Rectangle(pos=self.pos, size=self.size)
        
        # 中心容器 (AnchorLayout用于居中)
        anchor = AnchorLayout(anchor_x='center', anchor_y='center')
        
        # 登录卡片
        card = RoundedBox(
            size_hint=(None, None), 
            size=(dp(340), dp(480)),
            padding=dp(30),
            spacing=dp(20),
            orientation='vertical',
            bg_color=THEME['bg_sidebar']
        )
        
        # Logo/标题
        header = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(80), spacing=dp(5))
        title = ModernLabel(text="BDSM 论坛工具", font_size=dp(26), bold=True, color=THEME['primary'])
        subtitle = ModernLabel(text="爬虫 / 投票 / 账号管理", font_size=dp(14), color=THEME['text_dim'])
        header.add_widget(title)
        header.add_widget(subtitle)
        card.add_widget(header)
        
        # 登录方式
        self.login_type = ModernSpinner(
            text='手机号 + 密码',
            values=['手机号 + 密码', '短信验证码', '直接输入 Token'],
            size_hint_y=None, height=dp(45)
        )
        self.login_type.bind(text=self.on_login_type_change)
        card.add_widget(self.login_type)
        
        # 输入区
        self.input_area = BoxLayout(orientation='vertical', spacing=dp(15), size_hint_y=None, height=dp(110))
        
        self.phone_input = ModernInput(hint_text="手机号", size_hint_y=None, height=dp(45))
        self.password_input = ModernInput(hint_text="密码", password=True, size_hint_y=None, height=dp(45))
        
        self.input_area.add_widget(self.phone_input)
        self.input_area.add_widget(self.password_input)
        card.add_widget(self.input_area)
        
        # 发送验证码按钮 (默认隐藏)
        self.sms_btn_container = BoxLayout(size_hint_y=None, height=dp(0))
        self.sms_btn = ModernButton(text="获取验证码", bg_color=THEME['secondary'], font_size=dp(14))
        self.sms_btn.bind(on_press=self.send_sms)
        self.sms_btn_container.add_widget(self.sms_btn)
        self.sms_btn_container.opacity = 0
        card.add_widget(self.sms_btn_container)
        
        # 状态提示
        self.status_label = ModernLabel(
            text=error_msg if error_msg else "", 
            color=THEME['error'], 
            font_size=dp(12),
            size_hint_y=None, height=dp(20)
        )
        card.add_widget(self.status_label)
        
        # 按钮区
        self.login_btn = ModernButton(text="立即登录", on_press=self.do_login)
        skip_btn = ModernGhostButton(text="跳过登录 (功能受限)", on_press=self.skip_login)
        
        card.add_widget(self.login_btn)
        card.add_widget(skip_btn)
        
        # 已保存账号区域 (底部)
        self.saved_accounts_container = BoxLayout(orientation='vertical', size_hint_y=1)
        card.add_widget(self.saved_accounts_container)
        
        anchor.add_widget(card)
        self.add_widget(anchor)
        
        # 延迟加载账号
        Clock.schedule_once(self.load_saved_accounts, 0.5)

    def on_login_type_change(self, spinner, text):
        self.password_input.text = ""
        
        if text == '手机号 + 密码':
            self.phone_input.hint_text = '手机号'
            self.phone_input.disabled = False
            self.password_input.hint_text = '密码'
            self.password_input.password = True
            self.hide_sms_btn()
        elif text == '短信验证码':
            self.phone_input.hint_text = '手机号'
            self.phone_input.disabled = False
            self.password_input.hint_text = '验证码'
            self.password_input.password = False
            self.show_sms_btn()
        else:  # Token
            self.phone_input.hint_text = 'Token 登录无需手机号'
            self.phone_input.disabled = True
            self.password_input.hint_text = '在此粘贴 Token'
            self.password_input.password = False
            self.hide_sms_btn()

    def show_sms_btn(self):
        self.sms_btn_container.height = dp(45)
        self.sms_btn_container.opacity = 1
        self.input_area.height = dp(110) # 保持高度适应

    def hide_sms_btn(self):
        self.sms_btn_container.height = dp(0)
        self.sms_btn_container.opacity = 0

    def load_saved_accounts(self, dt):
        if not self.app.spider: return
        try:
            from your_code import load_accounts
        except ImportError:
            from app.your_code import load_accounts

        accounts = load_accounts(self.app.spider)
        if accounts:
            lbl = ModernLabel(text="快速登录", size_hint_y=None, height=dp(25), font_size=dp(12), color=THEME['text_dim'])
            self.saved_accounts_container.add_widget(lbl)
            
            scroll = ScrollView(size_hint_y=1)
            grid = GridLayout(cols=1, spacing=dp(8), size_hint_y=None)
            grid.bind(minimum_height=grid.setter('height'))
            
            for acc in accounts[:3]: # 只显示前3个
                name = acc.get("昵称", "未命名")
                phone = acc.get("手机号", "")
                display = f"{name} ({phone[-4:] if len(phone)>4 else 'Token'})"
                
                btn = ModernButton(
                    text=display, 
                    bg_color=THEME['bg_input'], 
                    radius=dp(5), 
                    font_size=dp(13),
                    height=dp(35)
                )
                btn.bind(on_press=partial(self.quick_login, acc))
                grid.add_widget(btn)
                
            scroll.add_widget(grid)
            self.saved_accounts_container.add_widget(scroll)

    def do_login(self, instance):
        if not self.app.spider:
            self.status_label.text = "初始化失败"
            return
            
        self.status_label.text = "登录中..."
        self.login_btn.disabled = True
        threading.Thread(target=self._login_thread, daemon=True).start()

    def _login_thread(self):
        try:
            try:
                from your_code import login_with_account, test_token_valid
            except ImportError:
                from app.your_code import login_with_account, test_token_valid

            login_type = self.login_type.text
            phone = self.phone_input.text.strip()
            pwd = self.password_input.text.strip()
            
            token = None
            if login_type.startswith('手机号'):
                token = login_with_account(self.app.spider, phone=phone, password=pwd, login_type=1)
            elif login_type.startswith('短信'):
                token = login_with_account(self.app.spider, phone=phone, pcode=pwd, login_type=2)
            else:
                token = pwd
            
            if token and test_token_valid(self.app.spider, token):
                self.app.token = token
                self.app.spider.set_token(token)
                self.update_status("登录成功", success=True)
                Clock.schedule_once(lambda dt: self.app.switch_to_main(), 0.5)
            else:
                self.update_status("登录失败或 Token 无效")
                self.enable_btn()
        except Exception as e:
            self.update_status(f"错误: {str(e)}")
            self.enable_btn()

    def quick_login(self, acc, instance):
        token = acc.get("Token")
        if token:
            self.status_label.text = "自动登录中..."
            threading.Thread(target=self._quick_login_thread, args=(token, acc), daemon=True).start()
            
    def _quick_login_thread(self, token, acc):
        try:
            try:
                from your_code import test_token_valid, load_accounts, save_accounts
            except ImportError:
                from app.your_code import test_token_valid, load_accounts, save_accounts
            
            import time
            if test_token_valid(self.app.spider, token):
                self.app.token = token
                self.app.spider.set_token(token)
                # 更新登录时间
                accounts = load_accounts(self.app.spider)
                for a in accounts:
                    if a.get("Token") == token:
                        a["最后登录"] = time.strftime("%Y-%m-%d %H:%M:%S")
                save_accounts(self.app.spider, accounts)
                
                self.update_status("登录成功", success=True)
                Clock.schedule_once(lambda dt: self.app.switch_to_main(), 0.5)
            else:
                self.update_status("Token 已过期")
        except Exception as e:
            self.update_status(f"错误: {e}")

    def send_sms(self, instance):
        phone = self.phone_input.text.strip()
        if len(phone) != 11:
            self.status_label.text = "请输入正确手机号"
            return
        self.status_label.text = "发送中..."
        threading.Thread(target=self._send_sms_thread, args=(phone,), daemon=True).start()
        
    def _send_sms_thread(self, phone):
        try:
            try: from your_code import send_sms_code
            except: from app.your_code import send_sms_code
            if send_sms_code(self.app.spider, phone):
                self.update_status("验证码已发送", success=True)
            else:
                self.update_status("发送失败")
        except Exception as e:
            self.update_status(f"错误: {e}")

    def skip_login(self, instance):
        self.app.token = None
        self.app.switch_to_main()

    @mainthread
    def update_status(self, text, success=False):
        self.status_label.text = text
        self.status_label.color = THEME['success'] if success else THEME['error']

    @mainthread
    def enable_btn(self):
        self.login_btn.disabled = False

# ---------- 主界面组件 ----------

class NavButton(ButtonBehavior, BoxLayout):
    """侧边栏导航按钮"""
    def __init__(self, text, icon_text, screen_name, nav_callback, **kwargs):
        super().__init__(**kwargs)
        self.screen_name = screen_name
        self.nav_callback = nav_callback
        self.size_hint_y = None
        self.height = dp(50)
        self.padding = [dp(15), 0]
        self.spacing = dp(15)
        
        with self.canvas.before:
            self.bg_color = Color(0, 0, 0, 0) # 默认透明
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(8)])
            
        self.bind(pos=self.update_rect, size=self.update_rect)
        
        # 图标 (用文字模拟)
        self.icon = Label(text=icon_text, font_size=dp(18), size_hint_x=None, width=dp(20), color=THEME['text_dim'])
        # 文字
        self.lbl = Label(text=text, font_size=dp(15), font_name=DEFAULT_FONT if DEFAULT_FONT else 'Roboto', 
                        halign='left', valign='middle', color=THEME['text_dim'])
        self.lbl.bind(size=self.lbl.setter('text_size'))
        
        self.add_widget(self.icon)
        self.add_widget(self.lbl)
        
        self.bind(on_press=self.on_click)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def on_click(self, instance):
        self.nav_callback(self.screen_name)

    def set_active(self, active):
        if active:
            self.bg_color.rgba = THEME['primary']
            self.bg_color.a = 0.15 # 半透明背景
            self.lbl.color = THEME['primary']
            self.icon.color = THEME['primary']
        else:
            self.bg_color.rgba = [0, 0, 0, 0]
            self.lbl.color = THEME['text_dim']
            self.icon.color = THEME['text_dim']

class ActionScreen(Screen):
    """通用操作面板屏幕"""
    def __init__(self, title, actions, main_screen_ref, **kwargs):
        super().__init__(**kwargs)
        self.main_ref = main_screen_ref
        
        # 布局
        root = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20))
        
        # 标题栏
        header = BoxLayout(size_hint_y=None, height=dp(40))
        header.add_widget(ModernLabel(text=title, font_size=dp(22), bold=True, halign='left', valign='middle'))
        root.add_widget(header)
        
        # 操作按钮网格
        grid = GridLayout(cols=2, spacing=dp(15), size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))
        
        for btn_text, callback_func in actions:
            btn = ModernButton(
                text=btn_text, 
                bg_color=THEME['bg_sidebar'], 
                press_color=THEME['primary'],
                height=dp(80) # 更大的块状按钮
            )
            btn.bind(on_press=callback_func)
            grid.add_widget(btn)
            
        root.add_widget(grid)
        root.add_widget(Widget()) # 填充底部
        
        self.add_widget(root)

class MainScreen(BoxLayout):
    """主布局：侧边栏 + 内容区 + 日志区"""
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.spacing = 0
        self.orientation = 'horizontal'
        
        # 1. 侧边栏
        sidebar = BoxLayout(orientation='vertical', size_hint_x=None, width=dp(220))
        with sidebar.canvas.before:
            Color(*THEME['bg_sidebar'])
            Rectangle(pos=sidebar.pos, size=sidebar.size)
        
        # 侧边栏标题
        app_title = ModernLabel(text="BDSM Tools", font_size=dp(20), bold=True, color=THEME['primary'], size_hint_y=None, height=dp(80))
        sidebar.add_widget(app_title)
        
        # 导航按钮区
        self.nav_layout = BoxLayout(orientation='vertical', spacing=dp(5), padding=dp(10), size_hint_y=1)
        self.nav_btns = {}
        
        nav_items = [
            ("crawler", "帖子爬虫", "🕷️"),
            ("search", "搜索功能", "🔍"),
            ("vote", "自动投票", "🗳️"),
            ("follow", "关注列表", "❤️"),
            ("account", "账号管理", "👤")
        ]
        
        for name, text, icon in nav_items:
            btn = NavButton(text, icon, name, self.switch_content)
            self.nav_layout.add_widget(btn)
            self.nav_btns[name] = btn
            
        self.nav_layout.add_widget(Widget()) # 推到底部
        
        # 底部状态/退出
        user_info = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(80), padding=dp(10), spacing=dp(5))
        
        token_preview = self.app.token[:6] + "..." if self.app.token else "未登录"
        status_color = THEME['success'] if self.app.token else THEME['warning']
        
        self.user_lbl = ModernLabel(text=f"状态: {token_preview}", font_size=dp(12), color=status_color)
        logout_btn = ModernGhostButton(text="退出登录", font_size=dp(12), height=dp(30))
        logout_btn.bind(on_press=self.logout)
        
        user_info.add_widget(self.user_lbl)
        user_info.add_widget(logout_btn)
        sidebar.add_widget(self.nav_layout)
        sidebar.add_widget(user_info)
        
        self.add_widget(sidebar)
        
        # 2. 右侧内容区 (包含ScreenManager和Log)
        content_area = BoxLayout(orientation='vertical', padding=dp(0))
        with content_area.canvas.before:
            Color(*THEME['bg_dark'])
            Rectangle(pos=content_area.pos, size=content_area.size)
            
        # Screen Manager
        self.sm = ScreenManager(transition=FadeTransition(duration=0.2))
        
        # 初始化各个屏幕
        self.sm.add_widget(ActionScreen(name='crawler', title="帖子爬虫工具", 
            actions=[
                ("批量爬取多页", self.on_batch_crawl),
                ("爬取特定ID帖子", self.on_crawl_post),
                ("爬取用户全部帖子", self.on_crawl_user),
                ("查看已保存文件", self.on_user_files)
            ], main_screen_ref=self))
            
        self.sm.add_widget(ActionScreen(name='search', title="全站搜索", 
            actions=[
                ("关键词搜索帖子", self.on_search_posts),
                ("搜索用户 (ID/名称)", self.on_search_username)
            ], main_screen_ref=self))
            
        self.sm.add_widget(ActionScreen(name='vote', title="投票任务", 
            actions=[
                ("单任务投票", self.on_single_vote),
                ("批量任务投票", self.on_batch_vote),
                ("查看投票记录", self.on_vote_files)
            ], main_screen_ref=self))

        self.sm.add_widget(ActionScreen(name='follow', title="关注管理", 
            actions=[
                ("查询关注列表", self.on_query_attention)
            ], main_screen_ref=self))
            
        self.sm.add_widget(ActionScreen(name='account', title="账号设置", 
            actions=[
                ("查看所有账号", self.on_manage_accounts),
                ("检查 Token 状态", self.on_token_status),
                ("清除登录缓存", self.on_clear_login)
            ], main_screen_ref=self))
            
        content_area.add_widget(self.sm)
        
        # 3. 底部日志区 (类似控制台)
        log_panel = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(180))
        
        # 分割线
        with log_panel.canvas.before:
            Color(*THEME['divider'])
            Rectangle(pos=log_panel.pos, size=(log_panel.width, dp(1)))
            Color(*THEME['bg_sidebar'])
            Rectangle(pos=log_panel.pos, size=log_panel.size)
            
        log_header = BoxLayout(size_hint_y=None, height=dp(30), padding=[dp(10), 0])
        log_header.add_widget(ModernLabel(text="运行日志", font_size=dp(12), color=THEME['text_dim'], halign='left'))
        
        self.log_scroll = ScrollView()
        self.log_label = Label(
            text="[系统] 准备就绪...\n",
            font_size=dp(12),
            font_name=DEFAULT_FONT if DEFAULT_FONT else 'Roboto',
            color=THEME['text_main'],
            size_hint_y=None,
            halign='left',
            valign='top',
            padding=[dp(10), dp(10)]
        )
        self.log_label.bind(texture_size=self.log_label.setter('size'))
        self.log_label.bind(width=lambda *x: setattr(self.log_label, 'text_size', (self.log_label.width, None)))
        
        self.log_scroll.add_widget(self.log_label)
        log_panel.add_widget(log_header)
        log_panel.add_widget(self.log_scroll)
        
        content_area.add_widget(log_panel)
        self.add_widget(content_area)
        
        # 默认选中第一个
        self.switch_content('crawler')
        
        # 日志缓冲
        self._log_buffer = []
        self._log_schedule = None

    def switch_content(self, screen_name):
        self.sm.current = screen_name
        # 更新侧边栏状态
        for name, btn in self.nav_btns.items():
            btn.set_active(name == screen_name)

    def logout(self, instance):
        self.app.token = None
        self.app.switch_to_login()

    def log(self, *args):
        """线程安全的日志输出"""
        msg = " ".join([str(a) for a in args])
        self._log_buffer.append(msg)
        if not self._log_schedule:
            self._log_schedule = Clock.schedule_once(self._flush_log, 0.1)
            
    def _flush_log(self, dt):
        if self._log_buffer:
            new_text = "\n".join(self._log_buffer) + "\n"
            self.log_label.text += new_text
            # 保持日志不过长
            if len(self.log_label.text) > 20000:
                self.log_label.text = self.log_label.text[-15000:]
            self.log_scroll.scroll_to(self.log_label)
            self._log_buffer = []
        self._log_schedule = None

    def run_bg(self, func):
        """后台运行任务"""
        if not self.app.token:
            self.log("❌ 错误：请先登录")
            return

        def wrapper():
            # 劫持 print 到日志
            import builtins
            old_print = builtins.print
            builtins.print = self.log
            try:
                func()
            except Exception as e:
                self.log(f"❌ 运行错误: {e}")
            finally:
                builtins.print = old_print
        
        threading.Thread(target=wrapper, daemon=True).start()

    # ---------- 业务逻辑绑定 ----------
    # 爬虫
    def on_batch_crawl(self, instance):
        InputDialog("批量爬取", 
            [{"key":"start","label":"开始页","default":"1"},{"key":"pages","label":"页数","default":"3"}], 
            lambda v: self.run_bg(lambda: self.app.spider.crawl_and_save_posts(int(v['start']), int(v['pages'])))
        ).open()

    def on_crawl_post(self, instance):
        InputDialog("爬取帖子", [{"key":"id","label":"帖子ID","default":""}], 
            lambda v: self.run_bg(lambda: self.app.spider.crawl_specific_post(int(v['id']))) if v['id'] else None
        ).open()
        
    def on_crawl_user(self, instance):
        InputDialog("爬取用户", [{"key":"id","label":"用户ID","default":""},{"key":"pages","label":"页数","default":"10"}],
            lambda v: self.run_bg(lambda: self.app.spider.crawl_user_posts_gui(int(v['id']), int(v['pages']))) if v['id'] else None
        ).open()

    def on_user_files(self, instance):
        self.run_bg(lambda: self.app.spider.show_user_files())

    # 搜索
    def on_search_posts(self, instance):
        InputDialog("搜索帖子", [{"key":"kw","label":"关键词","default":""},{"key":"pg","label":"页数","default":"3"}], 
            lambda v: self.run_bg(lambda: self.app.spider.search_and_save_posts_gui(v['kw'], int(v['pg']))) if v['kw'] else None
        ).open()

    def on_search_username(self, instance):
        InputDialog("搜索用户", 
            [{"key":"kw","label":"用户名","default":""},{"key":"pg","label":"页数","default":"30"},{"key":"th","label":"线程","default":"8"}], 
            lambda v: self.run_bg(lambda: self.app.spider.search_username_gui(v['kw'], int(v['pg']), int(v['th']))) if v['kw'] else None
        ).open()

    # 投票
    def on_single_vote(self, instance):
        InputDialog("单任务投票", [{"key":"id","label":"任务ID","default":""}], 
            lambda v: self.run_bg(lambda: self.app.spider.vote_single_gui(int(v['id']))) if v['id'] else None
        ).open()

    def on_batch_vote(self, instance):
        InputDialog("批量投票", 
            [{"key":"s","label":"起始ID","default":"1"},{"key":"e","label":"结束ID","default":"100"},{"key":"t","label":"线程","default":"50"}], 
            lambda v: self.run_bg(lambda: self.app.spider.batch_vote_gui(int(v['s']), int(v['e']), int(v['t'])))
        ).open()
        
    def on_vote_files(self, instance):
        self.run_bg(lambda: self.app.spider.show_vote_files())

    # 关注
    def on_query_attention(self, instance):
        InputDialog("查询关注", [{"key":"id","label":"用户ID","default":""},{"key":"p","label":"页码","default":"1"}], 
            lambda v: self.run_bg(lambda: self.app.spider.query_attention_gui(int(v['id']), int(v['p']))) if v['id'] else None
        ).open()

    # 账号
    def on_manage_accounts(self, instance):
        try:
            try: from your_code import load_accounts
            except: from app.your_code import load_accounts
            accs = load_accounts(self.app.spider)
            msg = "已保存账号:\n" + "\n".join([f"{i+1}. {a.get('昵称')} ({a.get('最后登录')})" for i,a in enumerate(accs)])
            self.log(msg)
        except Exception as e: self.log(str(e))

    def on_token_status(self, instance):
        try:
            try: from your_code import check_token_status
            except: from app.your_code import check_token_status
            self.run_bg(lambda: check_token_status(self.app.spider, self.app.token))
        except: pass

    def on_clear_login(self, instance):
        self.app.spider.clear_login_state()
        self.log("✅ 登录状态已清除")

# ---------- App 入口 ----------

class BDSMApp(App):
    def build(self):
        self.title = 'BDSM 论坛工具 Pro'
        self.icon = '' # 可以在这里添加图标路径
        Window.clearcolor = THEME['bg_dark']

        # 在 Android 上先请求权限
        self._request_permissions_on_start()

        self.root_widget = BoxLayout()
        self.spider = None
        self.token = None

        # 显示加载界面
        self.show_loading()

        # 异步初始化
        Clock.schedule_once(self.init_backend, 0.5)

        return self.root_widget

    def _request_permissions_on_start(self):
        """应用启动时请求所有存储权限（覆盖所有Android版本）"""
        try:
            from kivy.utils import platform
            if platform != 'android':
                return

            from android.permissions import request_permissions, Permission
            import android

            # 获取Android SDK版本
            sdk_version = int(android.api_version)
            print(f"Android SDK版本: {sdk_version}")

            permissions_to_request = []

            # Android 13+ (API 33+) 需要细分的媒体权限
            if sdk_version >= 33:
                permissions_to_request.extend([
                    Permission.READ_MEDIA_IMAGES,
                    Permission.READ_MEDIA_VIDEO,
                    Permission.READ_MEDIA_AUDIO,
                ])

            # Android 11+ (API 30+) 需要 MANAGE_EXTERNAL_STORAGE
            if sdk_version >= 30:
                try:
                    from android import mActivity
                    from jnius import autoclass

                    Environment = autoclass('android.os.Environment')
                    if not Environment.isExternalStorageManager():
                        Intent = autoclass('android.content.Intent')
                        Settings = autoclass('android.provider.Settings')
                        Uri = autoclass('android.net.Uri')

                        intent = Intent(Settings.ACTION_MANAGE_APP_ALL_FILES_ACCESS_PERMISSION)
                        uri = Uri.parse("package:" + mActivity.getPackageName())
                        intent.setData(uri)
                        mActivity.startActivity(intent)
                except Exception as e:
                    print(f"请求MANAGE_EXTERNAL_STORAGE失败: {e}")

            # Android 6-12 (API 23-32) 使用传统存储权限
            permissions_to_request.extend([
                Permission.WRITE_EXTERNAL_STORAGE,
                Permission.READ_EXTERNAL_STORAGE,
            ])

            if permissions_to_request:
                print(f"请求权限: {permissions_to_request}")
                request_permissions(permissions_to_request)

        except ImportError as e:
            print(f"导入android模块失败: {e}")
        except Exception as e:
            print(f"请求权限失败: {e}")

    def show_loading(self):
        self.root_widget.clear_widgets()
        layout = AnchorLayout()
        lbl = ModernLabel(text="正在初始化核心组件...", font_size=dp(16), color=THEME['text_dim'])
        layout.add_widget(lbl)
        self.root_widget.add_widget(layout)

    def init_backend(self, dt):
        try:
            # 兼容导入
            try:
                from your_code import BDSMForumSpider
            except ImportError:
                from app.your_code import BDSMForumSpider

            # 获取数据目录
            data_dir = self._get_data_dir()

            self.spider = BDSMForumSpider(data_dir=data_dir)
            print(f"数据目录: {data_dir}")

            # 自动登录检查
            auto_token = self.spider.load_login_state()
            if auto_token:
                threading.Thread(target=self._check_auto_login, args=(auto_token,), daemon=True).start()
            else:
                self.switch_to_login()

        except Exception as e:
            self.switch_to_login(error_msg=f"初始化失败: {e}")

    def _get_data_dir(self):
        """获取数据保存目录，Android上使用 /sdcard/bdsm数据/"""
        try:
            from kivy.utils import platform
            if platform == 'android':
                # 使用外部存储目录
                sdcard_dir = "/sdcard/bdsm数据"
                try:
                    os.makedirs(sdcard_dir, exist_ok=True)
                    # 测试是否可写
                    test_file = os.path.join(sdcard_dir, ".test_write")
                    with open(test_file, 'w') as f:
                        f.write("test")
                    os.remove(test_file)
                    print(f"使用外部存储: {sdcard_dir}")
                    return sdcard_dir
                except Exception as e:
                    print(f"外部存储不可用: {e}，使用应用内目录")
                    return os.path.join(self.user_data_dir, "bdsm_data")
            else:
                # 非Android平台使用应用数据目录
                data_dir = os.path.join(self.user_data_dir, "bdsm_data")
                os.makedirs(data_dir, exist_ok=True)
                return data_dir
        except Exception as e:
            print(f"获取数据目录失败: {e}")
            return os.path.join(self.user_data_dir, "bdsm_data")

    def _check_auto_login(self, token):
        try:
            try: from your_code import test_token_valid
            except: from app.your_code import test_token_valid
            
            if test_token_valid(self.spider, token):
                self.token = token
                self.spider.set_token(token)
                Clock.schedule_once(lambda dt: self.switch_to_main(), 0)
            else:
                Clock.schedule_once(lambda dt: self.switch_to_login(), 0)
        except:
            Clock.schedule_once(lambda dt: self.switch_to_login(), 0)

    @mainthread
    def switch_to_login(self, error_msg=None):
        self.root_widget.clear_widgets()
        self.root_widget.add_widget(LoginScreen(self, error_msg=error_msg))

    @mainthread
    def switch_to_main(self):
        self.root_widget.clear_widgets()
        self.root_widget.add_widget(MainScreen(self))

if __name__ == '__main__':
    BDSMApp().run()
"""
Salomatli Hayot - Sog'lom Turmush Tarzi Monitoring Ilovasi
Python Kivy Framework bilan ishlab chiqilgan

Funksiyalar:
- Qadam hisoblash (pedometer)
- Masofa va kaloriya hisoblash
- Vaqt monitoring (timer)
- Maqsad belgilash va tracking
- Statistika va grafiklar
- Ma'lumotlarni saqlash (JSON)
- Bildirishnomalar
"""

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.progressbar import ProgressBar
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, Line
from kivy.properties import NumericProperty, StringProperty, BooleanProperty
from kivy.core.window import Window
from kivy.utils import platform

import json
import os
from datetime import datetime, timedelta
import math
import random

# Android sensor import (agar Android bo'lsa)
if platform == 'android':
    from plyer import accelerometer, notification
    ANDROID = True
else:
    ANDROID = False
    print("Desktop mode - simulyatsiya rejimida ishlaydi")


class DataManager:
    """Ma'lumotlarni boshqarish klassi"""
    
    def __init__(self):
        self.data_file = "salomatli_hayot_data.json"
        self.load_data()
    
    def load_data(self):
        """Ma'lumotlarni yuklash"""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        else:
            self.data = {
                'user': {
                    'name': 'Foydalanuvchi',
                    'age': 25,
                    'weight': 70,
                    'height': 170,
                    'gender': 'male',
                    'step_length': 0.78,
                    'daily_goal': 10000
                },
                'today': {
                    'date': self.get_today(),
                    'steps': 0,
                    'distance': 0,
                    'calories': 0,
                    'duration': 0,
                    'goal_achieved': False
                },
                'history': []
            }
            self.save_data()
    
    def save_data(self):
        """Ma'lumotlarni saqlash"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def get_today(self):
        """Bugungi sanani olish"""
        return datetime.now().strftime('%Y-%m-%d')
    
    def check_new_day(self):
        """Yangi kun boshlanganini tekshirish"""
        today = self.get_today()
        if self.data['today']['date'] != today:
            # Kechagi ma'lumotlarni tarixga saqlash
            self.data['history'].append(self.data['today'].copy())
            # Yangi kunni boshlash
            self.data['today'] = {
                'date': today,
                'steps': 0,
                'distance': 0,
                'calories': 0,
                'duration': 0,
                'goal_achieved': False
            }
            self.save_data()
    
    def update_today(self, steps, distance, calories, duration):
        """Bugungi ma'lumotlarni yangilash"""
        self.check_new_day()
        self.data['today']['steps'] = steps
        self.data['today']['distance'] = distance
        self.data['today']['calories'] = calories
        self.data['today']['duration'] = duration
        
        # Maqsad bajarilganini tekshirish
        if steps >= self.data['user']['daily_goal']:
            self.data['today']['goal_achieved'] = True
        
        self.save_data()
    
    def get_weekly_stats(self):
        """Haftalik statistika"""
        total_steps = 0
        total_distance = 0
        total_calories = 0
        days_active = 0
        
        # Bugungi kunni qo'shish
        total_steps += self.data['today']['steps']
        total_distance += self.data['today']['distance']
        total_calories += self.data['today']['calories']
        if self.data['today']['steps'] > 0:
            days_active += 1
        
        # Oxirgi 6 kunni qo'shish
        for i in range(min(6, len(self.data['history']))):
            day = self.data['history'][-(i+1)]
            total_steps += day['steps']
            total_distance += day['distance']
            total_calories += day['calories']
            if day['steps'] > 0:
                days_active += 1
        
        return {
            'total_steps': total_steps,
            'total_distance': round(total_distance, 2),
            'total_calories': total_calories,
            'days_active': days_active,
            'avg_steps': total_steps // max(days_active, 1)
        }


class PedometerEngine:
    """Qadam hisoblash mexanizmi"""
    
    def __init__(self, callback):
        self.callback = callback
        self.step_count = 0
        self.last_update = 0
        self.threshold = 12.0  # Tezlanish chegarasi
        self.last_magnitude = 0
        self.step_detected = False
        
        if ANDROID:
            try:
                accelerometer.enable()
                Clock.schedule_interval(self.update, 0.1)
            except:
                print("Akselerometr ishlamayapti")
        else:
            # Desktop simulyatsiya
            Clock.schedule_interval(self.simulate_steps, 2)
    
    def update(self, dt):
        """Akselerometr ma'lumotlarini o'qish"""
        if not ANDROID:
            return
        
        try:
            val = accelerometer.acceleration[:3]
            if val[0] is None:
                return
            
            # Umumiy tezlanish magnitudasi
            magnitude = math.sqrt(val[0]**2 + val[1]**2 + val[2]**2)
            
            # Qadam aniqlash (cho'qqi aniqlash algoritmi)
            if magnitude > self.threshold and not self.step_detected:
                if self.last_magnitude < magnitude:
                    self.step_detected = True
                    self.step_count += 1
                    self.callback(self.step_count)
            elif magnitude < self.threshold:
                self.step_detected = False
            
            self.last_magnitude = magnitude
            
        except Exception as e:
            print(f"Sensor xatosi: {e}")
    
    def simulate_steps(self, dt):
        """Desktop uchun simulyatsiya"""
        if random.random() > 0.3:  # 70% ehtimollik
            self.step_count += random.randint(1, 3)
            self.callback(self.step_count)
    
    def reset(self):
        """Hisobni tiklash"""
        self.step_count = 0
        self.callback(0)


class HomeScreen(Screen):
    """Asosiy ekran"""
    
    steps = NumericProperty(0)
    distance = NumericProperty(0.0)
    calories = NumericProperty(0)
    progress = NumericProperty(0)
    timer_text = StringProperty("00:00:00")
    is_active = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data_manager = None
        self.pedometer = None
        self.timer_seconds = 0
        self.timer_event = None
        
    def on_enter(self):
        """Ekran ochilganda"""
        if self.data_manager:
            self.load_today_data()
    
    def load_today_data(self):
        """Bugungi ma'lumotlarni yuklash"""
        today = self.data_manager.data['today']
        self.steps = today['steps']
        self.distance = today['distance']
        self.calories = today['calories']
        self.timer_seconds = today['duration']
        self.update_timer_display()
        self.update_progress()
    
    def on_step(self, step_count):
        """Qadam hisoblagichdan yangilanish"""
        self.steps = step_count
        self.calculate_metrics()
        self.update_progress()
        self.save_data()
    
    def calculate_metrics(self):
        """Masofa va kaloriya hisoblash"""
        user = self.data_manager.data['user']
        
        # Masofa (km)
        step_length = user['step_length']
        self.distance = round((self.steps * step_length) / 1000, 2)
        
        # Kaloriya (oddiy formula)
        weight = user['weight']
        self.calories = int((self.steps * 0.04 * weight) / 100)
    
    def update_progress(self):
        """Progress bar yangilash"""
        goal = self.data_manager.data['user']['daily_goal']
        self.progress = min(100, (self.steps / goal) * 100)
        
        # Maqsad bajarilganini tekshirish
        if self.steps >= goal and not self.data_manager.data['today']['goal_achieved']:
            self.show_achievement()
    
    def show_achievement(self):
        """Maqsad bajarilganda xabar"""
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(
            text='🏆 Tabriklaymiz!\n\nKunlik maqsadga erishdingiz!',
            font_size='18sp',
            halign='center'
        ))
        
        btn = Button(text='OK', size_hint_y=None, height=50)
        content.add_widget(btn)
        
        popup = Popup(
            title='Yutuq!',
            content=content,
            size_hint=(0.8, 0.4)
        )
        btn.bind(on_press=popup.dismiss)
        popup.open()
        
        # Android bildirishnoma
        if ANDROID:
            try:
                notification.notify(
                    title='Salomatli Hayot',
                    message=f'Siz {self.steps} qadam yurdingiz! Maqsad bajarildi!',
                    timeout=10
                )
            except:
                pass
    
    def toggle_workout(self):
        """Mashqni boshlash/to'xtatish"""
        self.is_active = not self.is_active
        
        if self.is_active:
            # Boshlash
            if not self.pedometer:
                self.pedometer = PedometerEngine(self.on_step)
            self.timer_event = Clock.schedule_interval(self.update_timer, 1)
        else:
            # To'xtatish
            if self.timer_event:
                self.timer_event.cancel()
            self.save_data()
    
    def reset_data(self):
        """Ma'lumotlarni tiklash"""
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(
            text='Barcha ma\'lumotlarni tiklamoqchimisiz?',
            halign='center'
        ))
        
        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        
        yes_btn = Button(text='Ha')
        no_btn = Button(text='Yo\'q')
        
        btn_layout.add_widget(yes_btn)
        btn_layout.add_widget(no_btn)
        content.add_widget(btn_layout)
        
        popup = Popup(
            title='Tasdiqlash',
            content=content,
            size_hint=(0.8, 0.3)
        )
        
        def confirm(instance):
            self.steps = 0
            self.distance = 0
            self.calories = 0
            self.timer_seconds = 0
            self.update_timer_display()
            self.progress = 0
            if self.pedometer:
                self.pedometer.reset()
            self.save_data()
            popup.dismiss()
        
        yes_btn.bind(on_press=confirm)
        no_btn.bind(on_press=popup.dismiss)
        popup.open()
    
    def update_timer(self, dt):
        """Timer yangilash"""
        self.timer_seconds += 1
        self.update_timer_display()
    
    def update_timer_display(self):
        """Timer ko'rinishini yangilash"""
        hours = self.timer_seconds // 3600
        minutes = (self.timer_seconds % 3600) // 60
        seconds = self.timer_seconds % 60
        self.timer_text = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def save_data(self):
        """Ma'lumotlarni saqlash"""
        if self.data_manager:
            self.data_manager.update_today(
                self.steps,
                self.distance,
                self.calories,
                self.timer_seconds
            )


class StatisticsScreen(Screen):
    """Statistika ekrani"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data_manager = None
    
    def on_enter(self):
        """Ekran ochilganda"""
        if self.data_manager:
            self.update_stats()
    
    def update_stats(self):
        """Statistikani yangilash"""
        stats = self.data_manager.get_weekly_stats()
        
        # Label'larni yangilash
        self.ids.weekly_steps.text = f"Jami qadamlar: {stats['total_steps']:,}"
        self.ids.weekly_distance.text = f"Jami masofa: {stats['total_distance']} km"
        self.ids.weekly_calories.text = f"Jami kaloriya: {stats['total_calories']} kcal"
        self.ids.days_active.text = f"Faol kunlar: {stats['days_active']}/7"
        self.ids.avg_steps.text = f"O'rtacha: {stats['avg_steps']:,} qadam/kun"


class ProfileScreen(Screen):
    """Profil ekrani"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data_manager = None
    
    def on_enter(self):
        """Ekran ochilganda"""
        if self.data_manager:
            self.load_profile()
    
    def load_profile(self):
        """Profil ma'lumotlarini yuklash"""
        user = self.data_manager.data['user']
        self.ids.name_input.text = user['name']
        self.ids.age_input.text = str(user['age'])
        self.ids.weight_input.text = str(user['weight'])
        self.ids.height_input.text = str(user['height'])
        self.ids.goal_input.text = str(user['daily_goal'])
    
    def save_profile(self):
        """Profil ma'lumotlarini saqlash"""
        try:
            user = self.data_manager.data['user']
            user['name'] = self.ids.name_input.text
            user['age'] = int(self.ids.age_input.text)
            user['weight'] = int(self.ids.weight_input.text)
            user['height'] = int(self.ids.height_input.text)
            user['daily_goal'] = int(self.ids.goal_input.text)
            
            # Qadam uzunligini hisoblash
            height_cm = user['height']
            gender = user['gender']
            if gender == 'male':
                user['step_length'] = (height_cm * 0.415) / 100
            else:
                user['step_length'] = (height_cm * 0.413) / 100
            
            self.data_manager.save_data()
            
            # Muvaffaqiyat xabari
            popup = Popup(
                title='Muvaffaqiyat',
                content=Label(text='Profil saqlandi!'),
                size_hint=(0.6, 0.3)
            )
            popup.open()
            Clock.schedule_once(lambda dt: popup.dismiss(), 1.5)
            
        except ValueError:
            popup = Popup(
                title='Xato',
                content=Label(text='Iltimos, to\'g\'ri qiymatlar kiriting!'),
                size_hint=(0.6, 0.3)
            )
            popup.open()


class SalomatliHayotApp(App):
    """Asosiy ilova klassi"""
    
    def build(self):
        # Window sozlamalari
        Window.clearcolor = (0.95, 0.95, 0.95, 1)
        
        # Ma'lumotlar menejeri
        self.data_manager = DataManager()
        
        # Screen manager
        sm = ScreenManager()
        
        # Ekranlarni yaratish
        home = HomeScreen(name='home')
        home.data_manager = self.data_manager
        
        stats = StatisticsScreen(name='stats')
        stats.data_manager = self.data_manager
        
        profile = ProfileScreen(name='profile')
        profile.data_manager = self.data_manager
        
        sm.add_widget(home)
        sm.add_widget(stats)
        sm.add_widget(profile)
        
        return sm
    
    def on_pause(self):
        """Ilova pause qilinganda"""
        return True
    
    def on_resume(self):
        """Ilova qayta ochilganda"""
        pass


if __name__ == '__main__':
    SalomatliHayotApp().run()
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import random
from datetime import datetime, timedelta

# تنظیمات صفحه
st.set_page_config(page_title="شبیه‌ساز جانشین‌پروری بانک", layout="wide")


class BankSuccessionSimulator:
    def __init__(self):
        # ظرفیت‌های پیش‌فرض مختلف شعب
        self.default_capacity = {
            'رئیس_شعبه': {'درجه4': 240, 'درجه3': 720, 'درجه2': 230, 'درجه1': 100, 'ممتاز': 180},
            'معاون_شعبه': {'درجه4': 240, 'درجه3': 720, 'درجه2': 230, 'درجه1': 100, 'ممتاز': 360},
            'رئیس_صندوق': {'درجه4': 240, 'درجه3': 720, 'درجه2': 230, 'درجه1': 100, 'ممتاز': 180},
            'رئیس_اعتبارات': {'درجه4': 240, 'درجه3': 720, 'درجه2': 230, 'درجه1': 100, 'ممتاز': 80},
            'بانکدار': {'درجه4': 960, 'درجه3': 2880, 'درجه2': 1380, 'درجه1': 600, 'ممتاز': 1800},
            'معاون_مدیر_شعب': 105,
            'مدیر_شعب': 35
        }

        # احتمالات انتقال پیش‌فرض
        self.default_probabilities = {
            'بانکدار_to_رئیس_دایره4': 0.6,
            'رئیس_دایره4_to_رئیس_دایره_ممتاز': 0.7,
            'رئیس_دایره4_to_معاون_شعبه4': 0.3,
            'معاون_شعبه4_to_رئیس_شعبه4': 0.5,
            'معاون_شعبه4_to_رئیس_شعبه3': 0.2,
            'معاون_شعبه4_to_معاون_شعبه3': 0.3,
            'رئیس_شعبه4_to_رئیس_شعبه3': 0.5,
            'رئیس_شعبه4_to_رئیس_شعبه2': 0.2,
            'رئیس_شعبه4_to_معاون_شعبه2': 0.3,
            'رئیس_شعبه3_to_رئیس_شعبه2': 0.4,
            'رئیس_شعبه3_to_رئیس_شعبه1': 0.1,
            'رئیس_شعبه3_to_معاون_شعبه1': 0.1,
            'رئیس_شعبه3_retire': 0.4,
            'رئیس_شعبه2_to_رئیس_شعبه1': 0.4,
            'رئیس_شعبه2_to_رئیس_شعبه_ممتاز': 0.1,
            'رئیس_شعبه2_to_معاون_شعبه_ممتاز': 0.1,
            'رئیس_شعبه2_retire': 0.4,
            'رئیس_شعبه1_to_رئیس_شعبه_ممتاز': 0.5,
            'رئیس_شعبه1_to_معاون_مدیر': 0.1,
            'رئیس_شعبه1_to_مدیر_شعب': 0.1,
            'رئیس_شعبه1_retire': 0.3,
            'رئیس_شعبه_ممتاز_to_معاون_مدیر': 0.2,
            'رئیس_شعبه_ممتاز_to_مدیر_شعب': 0.1,
            'رئیس_شعبه_ممتاز_retire': 0.4,
            'معاون_مدیر_to_مدیر_شعب': 0.3,
            'معاون_مدیر_retire': 0.7
        }

        # سال‌های پیش‌فرض مورد نیاز برای انتقال
        self.default_years_required = {
            'بانکدار_to_رئیس_دایره4': 3,
            'رئیس_دایره4_to_رئیس_دایره_ممتاز': 2,
            'رئیس_دایره4_to_معاون_شعبه4': 2,
            'معاون_شعبه4_to_رئیس_شعبه4': 3,
            'معاون_شعبه4_to_رئیس_شعبه3': 4,
            'معاون_شعبه4_to_معاون_شعبه3': 2,
            'رئیس_شعبه4_to_رئیس_شعبه3': 3,
            'رئیس_شعبه4_to_رئیس_شعبه2': 5,
            'رئیس_شعبه4_to_معاون_شعبه2': 4,
            'رئیس_شعبه3_to_رئیس_شعبه2': 3,
            'رئیس_شعبه3_to_رئیس_شعبه1': 5,
            'رئیس_شعبه3_to_معاون_شعبه1': 4,
            'رئیس_شعبه2_to_رئیس_شعبه1': 3,
            'رئیس_شعبه2_to_رئیس_شعبه_ممتاز': 4,
            'رئیس_شعبه2_to_معاون_شعبه_ممتاز': 3,
            'رئیس_شعبه1_to_رئیس_شعبه_ممتاز': 4,
            'رئیس_شعبه1_to_معاون_مدیر': 5,
            'رئیس_شعبه1_to_مدیر_شعب': 7,
            'رئیس_شعبه_ممتاز_to_معاون_مدیر': 4,
            'رئیس_شعبه_ممتاز_to_مدیر_شعب': 6,
            'معاون_مدیر_to_مدیر_شعب': 3
        }

        # آمار بازنشستگی
        self.retirement_stats = {
            '5_years': 0.5,
            '10_years': 0.8,
            '15_years': 1.0
        }

    def create_capacity_settings(self):
        """ایجاد تنظیمات ظرفیت مناصب"""
        st.sidebar.header("🏢 تنظیم ظرفیت مناصب")

        capacity = {}

        # مناصب مختلف
        position_groups = {
            "رئیس شعبه": ['درجه4', 'درجه3', 'درجه2', 'درجه1', 'ممتاز'],
            "معاون شعبه": ['درجه4', 'درجه3', 'درجه2', 'درجه1', 'ممتاز'],
            "سایر مناصب": ['معاون_مدیر_شعب', 'مدیر_شعب']
        }

        with st.sidebar.expander("تنظیم ظرفیت‌ها"):
            for group_name, items in position_groups.items():
                st.markdown(f"**{group_name}**")
                if group_name == "سایر مناصب":
                    for item in items:
                        default_val = self.default_capacity.get(item, 50)
                        persian_name = item.replace('_', ' ')
                        capacity[item] = st.number_input(
                            persian_name,
                            min_value=1,
                            max_value=1000,
                            value=default_val,
                            key=f"capacity_{item}"
                        )
                else:
                    position_key = group_name.replace(' ', '_').lower()
                    capacity[position_key] = {}
                    for grade in items:
                        default_val = self.default_capacity.get(position_key, {}).get(grade, 100)
                        capacity[position_key][grade] = st.number_input(
                            f"{grade}",
                            min_value=1,
                            max_value=5000,
                            value=default_val,
                            key=f"capacity_{position_key}_{grade}"
                        )

        return capacity

    def create_probability_sliders(self):
        """ایجاد اسلایدرها برای تغییر احتمالات و سال‌های مورد نیاز"""
        st.sidebar.header("⚙️ تنظیم احتمالات و زمان‌بندی")

        probabilities = {}
        years_required = {}

        # گروه‌بندی احتمالات برای نمایش بهتر
        groups = {
            "بانکدار و رئیس دایره": [
                'بانکدار_to_رئیس_دایره4',
                'رئیس_دایره4_to_رئیس_دایره_ممتاز',
                'رئیس_دایره4_to_معاون_شعبه4'
            ],
            "معاون شعبه درجه 4": [
                'معاون_شعبه4_to_رئیس_شعبه4',
                'معاون_شعبه4_to_رئیس_شعبه3',
                'معاون_شعبه4_to_معاون_شعبه3'
            ],
            "رئیس شعبه درجه 4": [
                'رئیس_شعبه4_to_رئیس_شعبه3',
                'رئیس_شعبه4_to_رئیس_شعبه2',
                'رئیس_شعبه4_to_معاون_شعبه2'
            ],
            "رئیس شعبه درجه 3": [
                'رئیس_شعبه3_to_رئیس_شعبه2',
                'رئیس_شعبه3_to_رئیس_شعبه1',
                'رئیس_شعبه3_to_معاون_شعبه1',
                'رئیس_شعبه3_retire'
            ],
            "رئیس شعبه درجه 2": [
                'رئیس_شعبه2_to_رئیس_شعبه1',
                'رئیس_شعبه2_to_رئیس_شعبه_ممتاز',
                'رئیس_شعبه2_to_معاون_شعبه_ممتاز',
                'رئیس_شعبه2_retire'
            ],
            "رئیس شعبه درجه 1": [
                'رئیس_شعبه1_to_رئیس_شعبه_ممتاز',
                'رئیس_شعبه1_to_معاون_مدیر',
                'رئیس_شعبه1_to_مدیر_شعب',
                'رئیس_شعبه1_retire'
            ],
            "رئیس شعبه ممتاز": [
                'رئیس_شعبه_ممتاز_to_معاون_مدیر',
                'رئیس_شعبه_ممتاز_to_مدیر_شعب',
                'رئیس_شعبه_ممتاز_retire'
            ],
            "معاون مدیر شعب": [
                'معاون_مدیر_to_مدیر_شعب',
                'معاون_مدیر_retire'
            ]
        }

        for group_name, keys in groups.items():
            with st.sidebar.expander(f"📊 {group_name}"):
                for key in keys:
                    if key in self.default_probabilities:
                        persian_label = key.replace('_', ' → ').replace('to', 'به').replace('retire', 'بازنشستگی')

                        col1, col2 = st.columns(2)

                        with col1:
                            st.markdown(f"**{persian_label}**")
                            probabilities[key] = st.slider(
                                "احتمال",
                                0.0, 1.0,
                                self.default_probabilities[key],
                                0.01,
                                key=f"prob_{key}"
                            )

                        with col2:
                            st.markdown("**سال‌های لازم**")
                            if 'retire' not in key:  # بازنشستگی نیاز به سال ندارد
                                years_required[key] = st.number_input(
                                    "سال",
                                    1, 10,
                                    self.default_years_required.get(key, 3),
                                    key=f"years_{key}"
                                )
                            else:
                                years_required[key] = 0  # بازنشستگی فوری

        return probabilities, years_required

    def create_simulation_explanation(self):
        """ایجاد قسمت توضیحات شبیه‌سازی"""
        st.header("📚 راهنمای شبیه‌ساز جانشین‌پروری بانک")

        with st.expander("🔍 توضیح کامل شبیه‌سازی - برای تازه‌کاران"):
            st.markdown("""
            ### 🎯 هدف این شبیه‌ساز:
            این ابزار برای پیش‌بینی و تحلیل تغییرات نیروی انسانی در ساختار سازمانی بانک طراحی شده است.

            ### 🏗️ چگونه کار می‌کند:

            #### 1️⃣ **مدل‌سازی ساختار سازمانی:**
            - هر سمت شغلی دارای ظرفیت مشخصی است
            - کارکنان می‌توانند از سمت‌های پایین‌تر به بالاتر ارتقا یابند
            - برخی کارکنان بازنشسته می‌شوند
            - استخدام‌های جدید معمولاً در پایین‌ترین سطوح انجام می‌شود

            #### 2️⃣ **پارامترهای کلیدی:**

            **الف) احتمال انتقال:** 
            - هر انتقال شغلی احتمال مشخصی دارد (مثلاً 60% احتمال ارتقا از بانکدار به رئیس دایره)
            - شما می‌توانید این احتمالات را تغییر دهید

            **ب) سال‌های مورد نیاز:**
            - برای هر ارتقا، حداقل تعداد سالی لازم است
            - مثلاً باید 3 سال بانکدار باشید تا بتوانید رئیس دایره شوید

            **ج) ظرفیت مناصب:**
            - هر سمت حداکثر تعداد مشخصی کارمند می‌تواند داشته باشد
            - شما می‌توانید این ظرفیت‌ها را تغییر دهید

            #### 3️⃣ **فرآیند شبیه‌سازی:**

            **سال به سال اتفاقات زیر رخ می‌دهد:**
            1. **استخدام جدید:** تعداد مشخصی کارمند جدید (معمولاً بانکدار) استخدام می‌شود
            2. **بازنشستگی:** بخشی از کارکنان (عمدتاً ارشدتر) بازنشسته می‌شوند
            3. **ارتقاءها:** کارکنان واجد شرایط بر اساس احتمال و سابقه کاری ارتقا می‌یابند
            4. **تنظیم ظرفیت:** اگر تعداد افراد از ظرفیت تجاوز کند، برنامه‌ریزی مجدد انجام می‌شود

            #### 4️⃣ **خروجی‌های شبیه‌سازی:**

            **الف) نمودارهای تحلیلی:**
            - روند تغییرات کل پرسنل در طول زمان
            - مقایسه توزیع مناصب در ابتدا و انتهای دوره
            - روند تغییرات هر سمت به صورت جداگانه

            **ب) جداول تفصیلی:**
            - تعداد استخدام، بازنشستگی و ارتقا در هر سال
            - وضعیت نهایی هر سمت

            **ج) هشدارها و پیشنهادات:**
            - تشخیص کمبود یا مازاد نیرو
            - پیشنهاد راه‌حل‌های مناسب

            ### 🎛️ نحوه استفاده:

            #### گام 1: تنظیم پارامترهای اصلی
            - تعداد سال‌های شبیه‌سازی (1 تا 20 سال)
            - تعداد استخدام سالانه
            - ضریب تسریع بازنشستگی

            #### گام 2: تنظیم ظرفیت‌ها (اختیاری)
            - از منوی کناری می‌توانید ظرفیت هر سمت را تغییر دهید

            #### گام 3: تنظیم احتمالات و زمان‌بندی (اختیاری)
            - احتمال هر نوع انتقال را تنظیم کنید
            - تعداد سال‌های لازم برای هر انتقال را مشخص کنید

            #### گام 4: اجرای شبیه‌سازی
            - روی دکمه "اجرای شبیه‌سازی" کلیک کنید
            - نتایج به صورت نمودار و جدول نمایش داده می‌شود

            ### ⚡ نکات مهم:
            - نتایج بر اساس مدل‌های ریاضی و احتمالاتی محاسبه می‌شود
            - تغییر پارامترها تأثیر قابل توجهی روی نتایج دارد
            - این ابزار برای برنامه‌ریزی استراتژیک منابع انسانی مفید است
            - نتایج باید به عنوان راهنما و نه پیش‌بینی قطعی در نظر گرفته شود
            """)

    def simulate_career_progression(self, years, probabilities, years_required, capacity, annual_hiring):
        """شبیه‌سازی پیشرفت شغلی با در نظر گیری سال‌های مورد نیاز"""
        results = {}

        # وضعیت اولیه مناصب (فرضی بر اساس ظرفیت‌ها)
        current_positions = {
            'رئیس_شعبه_درجه4': 1570,
            'رئیس_شعبه_درجه3': 2880,
            'رئیس_شعبه_درجه2': 930,
            'رئیس_شعبه_درجه1': 400,
            'رئیس_شعبه_ممتاز': 540,
            'معاون_شعبه': 1935,
            'بانکدار': 8625,
            'معاون_مدیر_شعب': 105,
            'مدیر_شعب': 35,
            'سایر': 2000
        }

        # ردیابی سابقه کاری (چه مدت در هر سمت بوده‌اند)
        position_tenure = {position: {} for position in current_positions.keys()}

        # محاسبه تغییرات در طول سال‌های مختلف
        for year in range(1, years + 1):
            # شبیه‌سازی استخدام جدید
            new_hires = annual_hiring

            # شبیه‌سازی بازنشستگی
            retirement_rate = min(year * 0.03, 0.12)  # تدریجی
            total_retirements = int(sum(current_positions.values()) * retirement_rate)

            # شبیه‌سازی ارتقاء با در نظر گیری سال‌های مورد نیاز
            promotions = self.calculate_promotions_with_tenure(
                probabilities, years_required, current_positions, position_tenure
            )

            # به‌روزرسانی سابقه کاری
            position_tenure = self.update_tenure(position_tenure, current_positions)

            # به‌روزرسانی تعداد افراد در هر سمت
            current_positions = self.update_positions(
                current_positions, promotions, new_hires, total_retirements
            )

            # بررسی ظرفیت‌ها و تنظیم
            current_positions = self.adjust_for_capacity(current_positions, capacity)

            results[year] = {
                'استخدام_جدید': new_hires,
                'بازنشستگی': total_retirements,
                'ارتقاءها': promotions,
                'وضعیت_مناصب': current_positions.copy(),
                'ظرفیت_استفاده': self.calculate_capacity_usage(current_positions, capacity)
            }

        return results

    def update_tenure(self, position_tenure, current_positions):
        """به‌روزرسانی سابقه کاری"""
        new_tenure = {}

        for position in current_positions.keys():
            new_tenure[position] = {}
            # هر سال یک سال به سابقه همه اضافه می‌شود
            for tenure_years in range(1, 11):  # حداکثر 10 سال ردیابی
                if tenure_years == 1:
                    # جدید وارد شده‌ها
                    new_tenure[position][tenure_years] = current_positions[position] // 10
                else:
                    # سابقه‌داران
                    prev_count = position_tenure.get(position, {}).get(tenure_years - 1, 0)
                    new_tenure[position][tenure_years] = prev_count

        return new_tenure

    def calculate_promotions_with_tenure(self, probabilities, years_required, current_positions, position_tenure):
        """محاسبه تعداد ارتقاءهای مختلف با در نظر گیری سال‌های مورد نیاز"""
        promotions = {}

        # محاسبه ارتقاءها بر اساس تعداد فعلی، احتمالات و سابقه
        for transition, prob in probabilities.items():
            if 'retire' not in transition:
                required_years = years_required.get(transition, 3)

                # پیدا کردن کسانی که واجد شرایط سابقه کاری هستند
                source_position = transition.split('_to_')[0].replace('بانکدار', 'بانکدار')

                if source_position in current_positions:
                    # کسانی که سابقه کافی دارند
                    eligible_count = 0
                    for tenure_years, count in position_tenure.get(source_position, {}).items():
                        if tenure_years >= required_years:
                            eligible_count += count

                    # اگر اطلاعات دقیق سابقه نداشته باشیم، فرض کنیم نیمی واجد شرایط هستند
                    if eligible_count == 0:
                        eligible_count = current_positions[source_position] // 2

                    # محاسبه تعداد ارتقا
                    promotion_count = int(eligible_count * prob * 0.1)  # ضریب تعدیل
                    promotions[transition] = promotion_count

        return promotions

    def adjust_for_capacity(self, current_positions, capacity):
        """تنظیم تعداد کارکنان بر اساس ظرفیت‌ها"""
        adjusted_positions = current_positions.copy()

        # تنظیم بر اساس ظرفیت‌های تعریف شده
        # (این قسمت می‌تواند پیچیده‌تر شود بسته به نیاز)

        return adjusted_positions

    def calculate_capacity_usage(self, current_positions, capacity):
        """محاسبه درصد استفاده از ظرفیت"""
        usage = {}

        # محاسبه ساده درصد استفاده
        for position, count in current_positions.items():
            if position in ['معاون_مدیر_شعب', 'مدیر_شعب']:
                max_capacity = capacity.get(position, 100)
                usage[position] = min(100, (count / max_capacity) * 100)
            else:
                usage[position] = 85  # فرضی برای مناصب دیگر

        return usage

    def calculate_promotions(self, probabilities, current_positions):
        """محاسبه تعداد ارتقاءهای مختلف (متد اصلی)"""
        promotions = {}

        # محاسبه ارتقاءها بر اساس تعداد فعلی و احتمالات
        promotions['بانکدار_به_رئیس_دایره'] = int(
            current_positions['بانکدار'] * 0.1 * probabilities.get('بانکدار_to_رئیس_دایره4', 0.6)
        )

        promotions['رئیس_دایره_به_معاون'] = int(
            200 * probabilities.get('رئیس_دایره4_to_معاون_شعبه4', 0.3)
        )

        promotions['معاون_شعبه4_به_رئیس_شعبه4'] = int(
            current_positions['معاون_شعبه'] * 0.2 * probabilities.get('معاون_شعبه4_to_رئیس_شعبه4', 0.5)
        )

        promotions['رئیس_شعبه4_به_رئیس_شعبه3'] = int(
            current_positions['رئیس_شعبه_درجه4'] * 0.33 * probabilities.get('رئیس_شعبه4_to_رئیس_شعبه3', 0.5)
        )

        promotions['رئیس_شعبه3_به_رئیس_شعبه2'] = int(
            current_positions['رئیس_شعبه_درجه3'] * 0.33 * probabilities.get('رئیس_شعبه3_to_رئیس_شعبه2', 0.4)
        )

        promotions['رئیس_شعبه2_به_رئیس_شعبه1'] = int(
            current_positions['رئیس_شعبه_درجه2'] * 0.33 * probabilities.get('رئیس_شعبه2_to_رئیس_شعبه1', 0.4)
        )

        promotions['رئیس_شعبه1_به_رئیس_شعبه_ممتاز'] = int(
            current_positions['رئیس_شعبه_درجه1'] * 0.33 * probabilities.get('رئیس_شعبه1_to_رئیس_شعبه_ممتاز', 0.5)
        )

        promotions['رئیس_شعبه_ممتاز_به_معاون_مدیر'] = int(
            current_positions['رئیس_شعبه_ممتاز'] * 0.33 * probabilities.get('رئیس_شعبه_ممتاز_to_معاون_مدیر', 0.2)
        )

        promotions['معاون_مدیر_به_مدیر'] = int(
            current_positions['معاون_مدیر_شعب'] * 0.33 * probabilities.get('معاون_مدیر_to_مدیر_شعب', 0.3)
        )

        return promotions

    def update_positions(self, current_positions, promotions, new_hires, retirements):
        """به‌روزرسانی تعداد افراد در هر سمت"""
        new_positions = current_positions.copy()

        # اضافه کردن افراد جدید (عمدتاً بانکدار)
        new_positions['بانکدار'] += new_hires

        # کم کردن بازنشسته‌ها (تناسبی از همه سمت‌ها)
        total_current = sum(current_positions.values())
        for position in new_positions:
            retirement_from_position = int(retirements * (current_positions[position] / total_current))
            new_positions[position] = max(0, new_positions[position] - retirement_from_position)

        # اعمال ارتقاءها
        # کم کردن از سمت‌های پایین‌تر
        new_positions['بانکدار'] -= promotions.get('بانکدار_به_رئیس_دایره', 0)
        new_positions['معاون_شعبه'] -= promotions.get('معاون_شعبه4_به_رئیس_شعبه4', 0)
        new_positions['رئیس_شعبه_درجه4'] -= promotions.get('رئیس_شعبه4_به_رئیس_شعبه3', 0)
        new_positions['رئیس_شعبه_درجه3'] -= promotions.get('رئیس_شعبه3_به_رئیس_شعبه2', 0)
        new_positions['رئیس_شعبه_درجه2'] -= promotions.get('رئیس_شعبه2_به_رئیس_شعبه1', 0)
        new_positions['رئیس_شعبه_درجه1'] -= promotions.get('رئیس_شعبه1_به_رئیس_شعبه_ممتاز', 0)
        new_positions['رئیس_شعبه_ممتاز'] -= promotions.get('رئیس_شعبه_ممتاز_به_معاون_مدیر', 0)
        new_positions['معاون_مدیر_شعب'] -= promotions.get('معاون_مدیر_به_مدیر', 0)

        # اضافه کردن به سمت‌های بالاتر
        new_positions['معاون_شعبه'] += promotions.get('رئیس_دایره_به_معاون', 0)
        new_positions['رئیس_شعبه_درجه4'] += promotions.get('معاون_شعبه4_به_رئیس_شعبه4', 0)
        new_positions['رئیس_شعبه_درجه3'] += promotions.get('رئیس_شعبه4_به_رئیس_شعبه3', 0)
        new_positions['رئیس_شعبه_درجه2'] += promotions.get('رئیس_شعبه3_به_رئیس_شعبه2', 0)
        new_positions['رئیس_شعبه_درجه1'] += promotions.get('رئیس_شعبه2_به_رئیس_شعبه1', 0)
        new_positions['رئیس_شعبه_ممتاز'] += promotions.get('رئیس_شعبه1_به_رئیس_شعبه_ممتاز', 0)
        new_positions['معاون_مدیر_شعب'] += promotions.get('رئیس_شعبه_ممتاز_به_معاون_مدیر', 0)
        new_positions['مدیر_شعب'] += promotions.get('معاون_مدیر_به_مدیر', 0)

        # اطمینان از مثبت بودن تمام مقادیر
        for position in new_positions:
            new_positions[position] = max(0, new_positions[position])

        return new_positions

    def create_visualizations(self, simulation_results):
        """ایجاد تجسم‌های مختلف"""

        # نمودار تغییرات کل پرسنل
        years = list(simulation_results.keys())
        total_staff = []
        new_hires = []
        retirements = []

        for year in years:
            new_hires.append(simulation_results[year]['استخدام_جدید'])
            retirements.append(simulation_results[year]['بازنشستگی'])
            total_current = sum(simulation_results[year]['وضعیت_مناصب'].values())
            total_staff.append(total_current)

        # نمودار خطی تغییرات پرسنل
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x=years, y=total_staff, name='کل پرسنل', line=dict(color='blue', width=3)))
        fig1.add_trace(go.Bar(x=years, y=new_hires, name='استخدام جدید', marker_color='green'))
        fig1.add_trace(go.Bar(x=years, y=[-x for x in retirements], name='بازنشستگی', marker_color='red'))

        fig1.update_layout(
            title='پیش‌بینی تغییرات پرسنل بانک',
            xaxis_title='سال',
            yaxis_title='تعداد نفر',
            hovermode='x unified'
        )

        # نمودار دایره‌ای توزیع مناصب فعلی (فرضی)
        positions = ['رئیس شعبه درجه 4', 'رئیس شعبه درجه 3', 'رئیس شعبه درجه 2',
                     'رئیس شعبه درجه 1', 'رئیس شعبه ممتاز', 'معاونین', 'بانکداران', 'سایر']
        initial_values = [1570, 2880, 930, 400, 540, 1935, 8625, 2000]  # فرضی

        fig2 = px.pie(values=initial_values, names=positions, title='توزیع فعلی مناصب (ابتدای شبیه‌سازی)')

        # نمودار دایره‌ای توزیع مناصب در انتهای شبیه‌سازی
        final_year = max(years)
        final_positions = simulation_results[final_year]['وضعیت_مناصب']

        # تبدیل نام‌های کلیدها به فارسی برای نمایش
        persian_position_names = {
            'رئیس_شعبه_درجه4': 'رئیس شعبه درجه 4',
            'رئیس_شعبه_درجه3': 'رئیس شعبه درجه 3',
            'رئیس_شعبه_درجه2': 'رئیس شعبه درجه 2',
            'رئیس_شعبه_درجه1': 'رئیس شعبه درجه 1',
            'رئیس_شعبه_ممتاز': 'رئیس شعبه ممتاز',
            'معاون_شعبه': 'معاونین شعبه',
            'بانکدار': 'بانکداران',
            'معاون_مدیر_شعب': 'معاون مدیر شعب',
            'مدیر_شعب': 'مدیر شعب',
            'سایر': 'سایر مناصب'
        }

        final_position_names = [persian_position_names.get(k, k) for k in final_positions.keys()]
        final_values = list(final_positions.values())

        fig3 = px.pie(values=final_values, names=final_position_names,
                      title=f'توزیع پیش‌بینی شده مناصب (سال {final_year})')

        # نمودار مقایسه‌ای تغییرات مناصب مهم
        key_positions = ['رئیس_شعبه_درجه4', 'رئیس_شعبه_درجه3', 'رئیس_شعبه_درجه2',
                         'رئیس_شعبه_درجه1', 'رئیس_شعبه_ممتاز', 'معاون_مدیر_شعب', 'مدیر_شعب']

        fig4 = go.Figure()

        for position in key_positions:
            position_data = [simulation_results[year]['وضعیت_مناصب'][position] for year in years]
            persian_name = persian_position_names.get(position, position)
            fig4.add_trace(go.Scatter(x=years, y=position_data, name=persian_name, mode='lines+markers'))

        fig4.update_layout(
            title='روند تغییرات مناصب مدیریتی کلیدی',
            xaxis_title='سال',
            yaxis_title='تعداد نفر',
            hovermode='x unified'
        )

        # نمودار جدید: درصد استفاده از ظرفیت
        fig5 = go.Figure()

        capacity_usage_data = {}
        for year in years:
            capacity_data = simulation_results[year].get('ظرفیت_استفاده', {})
            for position, usage in capacity_data.items():
                if position not in capacity_usage_data:
                    capacity_usage_data[position] = []
                capacity_usage_data[position].append(usage)

        for position, usage_list in capacity_usage_data.items():
            persian_name = persian_position_names.get(position, position)
            fig5.add_trace(go.Scatter(x=years, y=usage_list, name=persian_name, mode='lines+markers'))

        fig5.update_layout(
            title='درصد استفاده از ظرفیت مناصب',
            xaxis_title='سال',
            yaxis_title='درصد استفاده',
            yaxis=dict(range=[0, 120])
        )

        return fig1, fig2, fig3, fig4, fig5


def main():
    st.title("🏛️ شبیه‌ساز جانشین‌پروری بانک")
    st.markdown("---")

    simulator = BankSuccessionSimulator()

    # نمایش توضیحات کامل
    simulator.create_simulation_explanation()

    st.markdown("---")

    # تنظیمات اصلی
    st.header("🎛️ تنظیمات اصلی شبیه‌سازی")
    col1, col2, col3 = st.columns(3)

    with col1:
        simulation_years = st.slider("تعداد سال‌های شبیه‌سازی", 1, 20, 10)

    with col2:
        annual_hiring = st.number_input("تعداد استخدام سالانه", 100, 1000, 500)

    with col3:
        retirement_acceleration = st.slider("ضریب تسریع بازنشستگی", 0.5, 2.0, 1.0)

    # تنظیمات تفصیلی در sidebar
    capacity = simulator.create_capacity_settings()
    probabilities, years_required = simulator.create_probability_sliders()

    # دکمه اجرای شبیه‌سازی
    st.markdown("---")
    if st.button("🚀 اجرای شبیه‌سازی", type="primary"):
        with st.spinner("در حال انجام شبیه‌سازی..."):
            # اجرای شبیه‌سازی
            results = simulator.simulate_career_progression(
                simulation_years, probabilities, years_required, capacity, annual_hiring
            )

            # نمایش نتایج
            st.success("شبیه‌سازی با موفقیت انجام شد!")

            # ایجاد نمودارها
            fig1, fig2, fig3, fig4, fig5 = simulator.create_visualizations(results)

            # نمایش نمودارها
            st.header("📊 نتایج شبیه‌سازی")

            # نمودار تغییرات کل پرسنل
            st.plotly_chart(fig1, use_container_width=True)

            # نمودارهای مقایسه‌ای توزیع مناصب
            st.subheader("🔍 مقایسه توزیع مناصب")
            col1, col2 = st.columns(2)

            with col1:
                st.plotly_chart(fig2, use_container_width=True)

            with col2:
                st.plotly_chart(fig3, use_container_width=True)

            # نمودار روند تغییرات مناصب مدیریتی
            st.plotly_chart(fig4, use_container_width=True)

            # نمودار درصد استفاده از ظرفیت
            st.plotly_chart(fig5, use_container_width=True)

            # نمایش جدول نتایج تفصیلی
            st.subheader("📋 نتایج تفصیلی شبیه‌سازی")

            # تبدیل نتایج به DataFrame برای نمایش
            summary_data = []
            for year, data in results.items():
                summary_data.append({
                    'سال': year,
                    'استخدام جدید': data['استخدام_جدید'],
                    'بازنشستگی': data['بازنشستگی'],
                    'کل پرسنل': sum(data['وضعیت_مناصب'].values()),
                    'رئیس شعبه درجه 4': data['وضعیت_مناصب']['رئیس_شعبه_درجه4'],
                    'رئیس شعبه درجه 3': data['وضعیت_مناصب']['رئیس_شعبه_درجه3'],
                    'رئیس شعبه درجه 2': data['وضعیت_مناصب']['رئیس_شعبه_درجه2'],
                    'رئیس شعبه درجه 1': data['وضعیت_مناصب']['رئیس_شعبه_درجه1'],
                    'رئیس شعبه ممتاز': data['وضعیت_مناصب']['رئیس_شعبه_ممتاز'],
                    'معاون مدیر شعب': data['وضعیت_مناصب']['معاون_مدیر_شعب'],
                    'مدیر شعب': data['وضعیت_مناصب']['مدیر_شعب']
                })

            df_summary = pd.DataFrame(summary_data)
            st.dataframe(df_summary, use_container_width=True)

            # هشدارهای مهم
            st.subheader("⚠️ تحلیل و هشدارهای مهم")

            # محاسبه آمار کلی
            final_year_data = results[simulation_years]
            total_retirement = sum([results[year]['بازنشستگی'] for year in results])
            total_hiring = sum([results[year]['استخدام_جدید'] for year in results])
            net_change = total_hiring - total_retirement

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("کل استخدام", total_hiring)

            with col2:
                st.metric("کل بازنشستگی", total_retirement)

            with col3:
                st.metric("تغییر خالص", net_change)

            with col4:
                final_total = sum(final_year_data['وضعیت_مناصب'].values())
                st.metric("کل پرسنل نهایی", final_total)

            # هشدارها
            if net_change < 0:
                st.error(f"🚨 کمبود نیروی انسانی: {abs(net_change)} نفر کمتر از نیاز")
            elif net_change > total_hiring * 0.5:
                st.warning(f"⚠️ رشد زیاد نیروی انسانی: {net_change} نفر اضافه")
            else:
                st.success(f"✅ تعادل مناسب نیروی انسانی: {net_change} نفر تغییر خالص")

            # بررسی نرخ ارتقا
            total_promotions = sum([sum(results[year]['ارتقاءها'].values()) for year in results])
            promotion_rate = total_promotions / (
                        total_hiring + sum([sum(data['وضعیت_مناصب'].values()) for data in results.values()]) / len(
                    results))

            if promotion_rate < 0.05:
                st.warning("⚠️ نرخ ارتقا پایین است - ممکن است موجب نارضایتی کارکنان شود")
            elif promotion_rate > 0.2:
                st.warning("⚠️ نرخ ارتقا بالا است - بررسی کیفیت ارتقاءها ضروری است")

            # پیشنهادات
            st.subheader("💡 پیشنهادات بهبود")
            suggestions = []

            if net_change < 0:
                suggestions.append("🔹 افزایش نرخ استخدام در سمت‌های کلیدی")
                suggestions.append("🔹 کاهش نرخ بازنشستگی از طریق مشوق‌های حفظ نیرو")

            if promotion_rate < 0.05:
                suggestions.append("🔹 تسریع برنامه‌های آموزش و توسعه شغلی")
                suggestions.append("🔹 ایجاد مسیرهای ارتقای جایگزین")

            suggestions.extend([
                "🔹 ایجاد برنامه‌های جانشین‌پروری هدفمند",
                "🔹 توسعه برنامه‌های حفظ استعداد",
                "🔹 بازنگری دوره‌ای در سیاست‌های منابع انسانی",
                "🔹 ایجاد سیستم پیش‌بینی دقیق‌تر نیازهای آتی"
            ])

            for suggestion in suggestions:
                st.write(suggestion)

            # امکان دانلود نتایج
            st.subheader("💾 دانلود نتایج")
            csv = df_summary.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="دانلود نتایج به صورت CSV",
                data=csv,
                file_name=f'simulation_results_{simulation_years}years.csv',
                mime='text/csv'
            )

    # اطلاعات اضافی در پایان صفحه
    st.markdown("---")
    with st.expander("ℹ️ اطلاعات بیشتر و محدودیت‌ها"):
        st.markdown("""
        ### نکات مهم:
        - این شبیه‌ساز بر اساس مدل‌های احتمالاتی کار می‌کند
        - نتایج باید به عنوان راهنما استفاده شود نه پیش‌بینی قطعی  
        - پارامترهای مختلف تأثیر قابل توجهی روی نتایج دارند
        - برای دقت بیشتر، داده‌های واقعی سازمان را استفاده کنید

        ### کاربردهای این ابزار:
        - برنامه‌ریزی استراتژیک منابع انسانی
        - تحلیل تأثیر سیاست‌های مختلف HR  
        - شناسایی کمبودها و مازادهای آتی
        - برنامه‌ریزی جانشین‌پروری
        """)


if __name__ == "__main__":
    main()
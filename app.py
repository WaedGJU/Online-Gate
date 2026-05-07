import streamlit as st
import pandas as pd
import os
import plotly.express as px

# 1. إعدادات الصفحة
# --- جدار الحماية (كلمة المرور) ---
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if not st.session_state["password_correct"]:
        st.warning("🔒 Please enter the password to proceed. For access authorization, contact Eng. Waed Alswaeer at waed.alswaer@gju.edu.jo.TEST")
        pwd = st.text_input("Password:", type="password")
        if pwd == st.secrets["APP_PASSWORD"]: # يمكنك تغيير كلمة المرور من هنا
            st.session_state["password_correct"] = True
            st.rerun()
        elif pwd:
            st.error("❌ Incorrect Password")
        return False
    return True

if not check_password():
    st.stop() # يوقف قراءة باقي الكود وجلب البيانات حتى يتم إدخال الباسورد
st.set_page_config(page_title="Online Gate Project Dashboard- 1st Semester", layout="wide")

# كود CSS لتنسيق الصورة والعنوان
st.markdown("""
    <style>
           [data-testid="stImage"] {
                margin-top: -60px; 
            }
           .block-container {
                padding-top: 4rem;
            }
    </style>
    """, unsafe_allow_html=True)

# 2. تحديد المسار والروابط
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

URL_ACT = f"https://docs.google.com/spreadsheets/d/e/2PACX-1vR5JN5Bdu51RK2ldTDtMU5IBvSN4kkJxv06zbN7oyPFe41YgX6kZFvRrlFU89Pw8BS4WxA2NSq5C-OL/pub?gid=163756926&single=true&output=csv"
URL_CONT = f"https://docs.google.com/spreadsheets/d/e/2PACX-1vR5JN5Bdu51RK2ldTDtMU5IBvSN4kkJxv06zbN7oyPFe41YgX6kZFvRrlFU89Pw8BS4WxA2NSq5C-OL/pub?gid=1390356673&single=true&output=csv"
URL_INFO = f"https://docs.google.com/spreadsheets/d/e/2PACX-1vR5JN5Bdu51RK2ldTDtMU5IBvSN4kkJxv06zbN7oyPFe41YgX6kZFvRrlFU89Pw8BS4WxA2NSq5C-OL/pub?gid=1113105367&single=true&output=csv"
URL_DEAD = f"https://docs.google.com/spreadsheets/d/e/2PACX-1vR5JN5Bdu51RK2ldTDtMU5IBvSN4kkJxv06zbN7oyPFe41YgX6kZFvRrlFU89Pw8BS4WxA2NSq5C-OL/pub?gid=574481000&single=true&output=csv"

# 3. دالة تحميل البيانات
@st.cache_data(ttl=30)
def load_data():
    df_act = pd.read_csv(URL_ACT)
    df_cont = pd.read_csv(URL_CONT)
    df_info = pd.read_csv(URL_INFO)
    df_dead = pd.read_csv(URL_DEAD)
    
    df_dead['start'] = pd.to_datetime(df_dead['start'])
    df_dead['End'] = pd.to_datetime(df_dead['End'])
    df_dead['unit'] = df_dead['unit'].astype(str)
    df_act['Unit'] = df_act['Unit'].astype(str)
    df_cont['Unit'] = df_cont['Unit'].astype(str)
    
    df_act['Progress_Num'] = df_act['Done'].apply(lambda x: 1 if str(x).strip().lower() == 'done' else 0)
    df_cont['Progress_Num'] = df_cont['Done'].apply(lambda x: 1 if str(x).strip().lower() == 'done' else 0)
    
    return df_act, df_cont, df_info, df_dead

try:
    df_act, df_cont, df_info, df_dead = load_data()
except Exception as e:
    st.error("يرجى التأكد من روابط Google Sheets وصلاحيات المشاركة.")
    st.stop()

# 4. المعالجة الزمنية
today = pd.to_datetime('today').normalize()
project_deadline = pd.to_datetime('2026-06-20')
days_to_project_end = (project_deadline - today).days

active_unit_row = df_dead[(df_dead['start'] <= today) & (df_dead['End'] >= today)]

if not active_unit_row.empty:
    active_unit = active_unit_row['unit'].iloc[0]
    active_end_date = active_unit_row['End'].iloc[0]
    days_remaining = (active_end_date - today).days
    
    active_idx = active_unit_row.index[0]
    next_unit = df_dead.iloc[active_idx + 1]['unit'] if active_idx + 1 < len(df_dead) else "None"
else:
    active_unit, next_unit, days_remaining = "None", "None", 0

# --- دالة تلوين الحالات ---
def highlight_status(val):
    colors = {'Delayed': '#ff4b4b', 'At Risk': '#ffa500', 'Completed': '#00cc96'}
    return f"color: {colors.get(val, '#1f77b4')}; font-weight: bold"

# --- 5. حساب المؤشرات ---
overall_progress = df_act['Progress_Num'].mean() * 100
course_progress = df_act.groupby('Course Name')['Progress_Num'].mean() * 100
active_unit_progress = (df_act[df_act['Unit'] == active_unit]['Progress_Num'].mean() * 100) if active_unit != "None" else 0

# حالة المساقات (Course Status)
df_act_merged = df_act.merge(df_dead, left_on='Unit', right_on='unit', how='left')
delayed_courses = df_act_merged[(df_act_merged['Progress_Num'] == 0) & (df_act_merged['End'] < today)]['Course Name'].unique()
course_active_prog = df_act[df_act['Unit'] == active_unit].groupby('Course Name')['Progress_Num'].mean() * 100

def get_course_status(course, prog):
    if course in delayed_courses: return 'Delayed'
    if course in course_active_prog.index and course_active_prog[course] < 70 and 0 <= days_remaining <= 3: return 'At Risk'
    return 'Completed' if prog == 100 else 'In progress'

course_status_df = pd.DataFrame({
    'Course Name': course_progress.index,
    'Overall Progress (%)': [f"{val:.2f}%" for val in course_progress.values],
    'Status': [get_course_status(c, p) for c, p in zip(course_progress.index, course_progress.values)]
})

# --- 6. واجهة الهيدر ---
header_col1, header_col2 = st.columns([1, 4])
with header_col1:
    logo_path = os.path.join(CURRENT_DIR, "1.png")
    if os.path.exists(logo_path): st.image(logo_path, width=500)
with header_col2:
    st.markdown("<h1 style='margin-top: 6rem; margin-bottom: -10px; padding-top: 0rem; color: #706f6f;'>Online Gate project Dashboard-1st Semester </h1>", unsafe_allow_html=True)

st.markdown("<hr style='margin-top: -90px; margin-bottom: 15px;'>", unsafe_allow_html=True)

# --- 7. قسم الـ Metrics ---
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("🎯 Total Progress", f"{overall_progress:.2f}%")
m2.metric("📍 Active Unit", f"Unit {active_unit}", f"{days_remaining} Days Left", delta_color="off")
m3.metric("🚀 Unit Progress", f"{active_unit_progress:.2f}%")
m4.metric("⏭️ Next Unit", f"Unit {next_unit}")
m5.metric("📅 Project Deadline", "20/06/2026", f"{days_to_project_end} Days Left", delta_color="normal")

st.markdown("---")

# --- 8. الجداول والرسومات ---
col_a, col_b = st.columns(2)
with col_a:
    st.subheader("📚 Course Progress & Status")
    st.dataframe(course_status_df.style.map(highlight_status, subset=['Status']), use_container_width=True, hide_index=True)

with col_b:
    st.subheader("📊 Units Overall Progress")
    valid_units = df_dead['unit'].dropna().astype(str).str.strip().drop_duplicates()
    valid_units = valid_units[(valid_units.str.lower() != 'nan') & (valid_units != '')]
    unit_prog = df_act.groupby('Unit')['Progress_Num'].mean() * 100
    chart_df = pd.DataFrame({'Unit': valid_units})
    chart_df['Completed (%)'] = chart_df['Unit'].map(unit_prog).fillna(0)
    chart_df['Remaining (%)'] = 100 - chart_df['Completed (%)']
    
    fig = px.bar(chart_df, x='Unit', y=['Completed (%)', 'Remaining (%)'],
                 color_discrete_map={'Completed (%)': '#0d86c8', 'Remaining (%)': '#e6e9ef'})
    fig.update_xaxes(type='category', categoryorder='array', categoryarray=chart_df['Unit'])
    fig.update_yaxes(range=[0, 100])
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), legend_title=None)
    st.plotly_chart(fig, use_container_width=True)

# --- 8.5. إنجاز الوحدة الفعالة لكل مساق (الرسم الجديد) ---
st.markdown("---")
st.subheader(f"📊 Active Unit ({active_unit}) Progress per Course")

if active_unit != "None" and not course_active_prog.empty:
    active_chart_df = pd.DataFrame({'Course Name': course_active_prog.index})
    active_chart_df['Completed (%)'] = course_active_prog.values
    active_chart_df['Remaining (%)'] = 100 - active_chart_df['Completed (%)']
    
    fig_active = px.bar(
        active_chart_df, 
        x='Course Name', 
        y=['Completed (%)', 'Remaining (%)'],
        color_discrete_map={'Completed (%)': '#0d86c8', 'Remaining (%)': '#e6e9ef'},
        labels={'value': 'Progress %', 'variable': 'Status'}
    )
    fig_active.update_yaxes(range=[0, 100])
    fig_active.update_layout(margin=dict(l=0, r=0, t=0, b=0), legend_title=None)
    st.plotly_chart(fig_active, use_container_width=True)
else:
    st.info("لا توجد بيانات متاحة للوحدة الفعالة حالياً.")

st.markdown("---")

# --- 9. Content Readiness ---
st.subheader("📄 Content Readiness (Instructor's Responsibility)")
c1, c2 = st.columns(2)

def get_cont_status(prog, days):
    if prog == 100: return 'Completed'
    return 'Delayed' if days < 0 else ('At Risk' if prog < 70 and 0 <= days <= 3 else 'In Progress')

# حساب تواريخ الاستحقاق (أسبوع قبل نهاية الوحدة)
active_deadline_dt = (active_end_date - pd.Timedelta(days=7)).strftime('%d/%m/%Y') if active_unit != "None" else "N/A"

if not active_unit_row.empty and active_idx + 1 < len(df_dead):
    next_end_date = df_dead.iloc[active_idx + 1]['End']
    next_deadline_dt = (next_end_date - pd.Timedelta(days=7)).strftime('%d/%m/%Y')
else:
    next_deadline_dt = "N/A"

for col, unit_val, label, days_val, deadline_date in zip(
    [c1, c2], 
    [active_unit, next_unit], 
    ["Current", "Next"], 
    [days_remaining - 7, days_remaining],
    [active_deadline_dt, next_deadline_dt]
):
    with col:
        # كود HTML لترتيب العنوان والتاريخ على نفس السطر (العنوان يسار، التاريخ يمين)
        header_html = f"""
        <div style="display: flex; justify-content: space-between; align-items: center; padding-bottom: 10px;">
            <span style="font-size: 16px; font-weight: bold;">{label} Unit: {unit_val}</span>
            <span style="font-size: 14px; font-weight: bold; color: #706f6f; background-color: #f0f2f6; padding: 4px 10px; border-radius: 5px;">
                📅 Deadline: {deadline_date}
            </span>
        </div>
        """
        st.markdown(header_html, unsafe_allow_html=True)
        
        df_c = df_cont[df_cont['Unit'] == unit_val].groupby(['Instructor', 'Course Name'])['Progress_Num'].mean().reset_index()
        if not df_c.empty:
            df_c['Readiness %'] = df_c['Progress_Num'] * 100
            df_c['Status'] = df_c['Readiness %'].apply(lambda x: get_cont_status(x, days_val))
            df_c['Readiness %'] = df_c['Readiness %'].apply(lambda x: f"{x:.2f}%")
            st.dataframe(df_c[['Instructor', 'Course Name', 'Readiness %', 'Status']].style.map(highlight_status, subset=['Status']), use_container_width=True, hide_index=True)
        else:
            st.info(f"No content data for Unit {unit_val}")
# --- 10. Footer ---
footer_html = """
<div style="background-color: #706f6f; padding: 15px; border-radius: 8px; text-align: center; color: white; margin-top: 20px;">
    <p style="margin: 0; font-size: 18px; font-weight: bold;">Designed & Developed by: Eng. Waed Alswaeer</p>
    <p style="margin: 5px 0 0 0; font-size: 14px;">✉️ Email: <a href="mailto:Waed.alswaer@gju.edu.jo" style="color: white; text-decoration: none;">Waed.alswaer@gju.edu.jo</a> | 📞 Phone: +962795948223</p>
</div>"""
st.markdown(footer_html, unsafe_allow_html=True)

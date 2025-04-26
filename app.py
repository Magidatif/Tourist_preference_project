import streamlit as st
import pandas as pd
import joblib
import os

# إعداد صفحة Streamlit
st.set_page_config(
    page_title="نظام تفضيلات السياح في عسير",
    page_icon="🏔️",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_resource
def load_model():
    try:
        model = joblib.load('tourist_model.joblib')
        columns = joblib.load('model_columns.joblib')
        return model, columns
    except Exception as e:
        st.error(f"خطأ في تحميل النموذج: {str(e)}")
        return None, None

model, model_columns = load_model()

if model is None:
    st.stop()

# القاموس الكامل للوجهات السياحية في عسير
DESTINATIONS = {
    'Mountain Trips': {
        "title": "الرحلات الجبلية",
        "places": [
            {"name": "منتزه السودة", "desc": "أعلى قمة في السعودية (3015م) مع منصات مشاهدة ومسارات مشي", "type": "جبل"},
            {"name": "جبل فروش", "desc": "إطلالات بانورامية وطبيعة خلابة", "type": "جبل"},
            {"name": "جبل المجاز", "desc": "طرق متعرجة ومشاهد ساحرة", "type": "جبل"},
            {"name": "قرية المفتاحة", "desc": "قرية فنية على قمة جبل", "type": "قرية جبلية"},
            {"name": "مرتفعات تنومة", "desc": "تشتهر بمناخها المعتدل والضباب الكثيف", "type": "منطقة جبلية"}
        ]
    },
    'Heritage Tourism': {
        "title": "السياحة التراثية",
        "places": [
            {"name": "قرية رجال ألمع", "desc": "قرية حجرية مسجلة في اليونسكو", "type": "موقع تراثي"},
            {"name": "قصر شدا", "desc": "تحفة معمارية تعود للقرن الـ19", "type": "قصر تاريخي"},
            {"name": "سوق الثلاثاء", "desc": "أحد أقدم الأسواق الشعبية في المنطقة", "type": "سوق تراثي"},
            {"name": "بلدة النماص", "desc": "تشتهر بالعمارة التقليدية", "type": "بلدة تراثية"}
        ]
    },
    'Shopping': {
        "title": "التسوق",
        "places": [
            {"name": "العثيم مول", "desc": "أكبر المجمعات التجارية في المنطقة", "type": "مركز تجاري"},
            {"name": "سوق الحرف اليدوية", "desc": "لشراء المنتجات التراثية", "type": "سوق شعبي"},
            {"name": "سوق الفنون", "desc": "للأعمال الفنية والحرفية", "type": "سوق فني"}
        ]
    },
    'Nature Exploration': {
        "title": "استكشاف الطبيعة",
        "places": [
            {"name": "وادي المحالة", "desc": "وادي العسل بشلالاته وغاباته الكثيفة", "type": "وادي"},
            {"name": "غابة رغدان", "desc": "أشجار العرعر الكثيفة", "type": "غابة"},
            {"name": "شلالات أبو خيال", "desc": "شلالات طبيعية خلابة", "type": "شلالات"}
        ]
    },
    'Events': {
        "title": "الفعاليات",
        "places": [
            {"name": "مهرجان صيف عسير", "desc": "أكبر الفعاليات الصيفية", "type": "مهرجان"},
            {"name": "سوق عكاظ", "desc": "فعاليات ثقافية وتراثية", "type": "فعالية تراثية"},
            {"name": "مهرجان الزهور", "desc": "في فصل الربيع", "type": "مهرجان موسمي"}
        ]
    }
}

# واجهة المستخدم
st.title('🏔️   البرامج السياحيه في منطقة عسير')
st.markdown("""
<style>
.arabic-font {
    font-family: 'Arial', sans-serif;
    direction: rtl;
    text-align: right;
}
</style>
""", unsafe_allow_html=True)

# حقول الإدخال
with st.form("tourist_form"):
    st.subheader("الخصائص الديموغرافية")
    col1, col2 = st.columns(2)
    
    with col1:
        age = st.slider('العمر', 18, 70, 30)
        gender = st.radio('الجنس', ['ذكر', 'أنثى'])
        nationality = st.selectbox('الجنسية', ['خليجي', 'أوروبي', 'آسيوي', 'شرق أوسطي', 'أفريقي'])
        
    with col2:
        family_status = st.selectbox('نوع الزيارة', ['فردي', 'عائلي', 'مجموعة'])
        season = st.selectbox('الموسم', ['الصيف', 'الشتاء', 'الربيع', 'الخريف'])
    
    st.subheader("تفضيلات الإقامة")
    col3, col4 = st.columns(2)
    
    with col3:
        purpose = st.selectbox('الغرض من الزيارة', ['ترفيه', 'عمل', 'تراث', 'تسوق', 'زيارة أقارب', 'أخرى'])
        
    with col4:
        accommodation = st.selectbox('نوع الإقامة', ['فندق', 'شقة', 'سكن خاص'])
    
    st.subheader("المعلومات المالية")
    spending = st.slider('الميزانية (بالريال السعودي)', 1000, 5000, 2000, step=500)
    stay_length = st.slider('مدة الإقامة (أيام)', 1, 14, 5)
    
    submitted = st.form_submit_button("توصية بالوجهات المناسبة")

if submitted:
    try:
        # تحويل المدخلات إلى الإنجليزية للنموذج
        gender_map = {'ذكر': 'Male', 'أنثى': 'Female'}
        nationality_map = {
            'خليجي': 'GCC',
            'أوروبي': 'Europe',
            'آسيوي': 'Asia',
            'شرق أوسطي': 'Middle East',
            'أفريقي': 'Africa'
        }
        family_map = {'فردي': 'Individual', 'عائلي': 'Family', 'مجموعة': 'Group'}
        season_map = {'الصيف': 'Summer', 'الشتاء': 'Winter', 'الربيع': 'Spring', 'الخريف': 'Fall'}
        purpose_map = {
            'ترفيه': 'Leisure',
            'عمل': 'Business',
            'تراث': 'Heritage',
            'تسوق': 'Shopping',
            'زيارة أقارب': 'Visiting Friends & Relatives',
            'أخرى': 'Other'
        }
        accommodation_map = {'فندق': 'Hotel', 'شقة': 'Apartment', 'سكن خاص': 'Private'}
        
        # إنشاء بيانات الإدخال للنموذج
        input_data = {
            'Age': [age],
            'Spending_per_Trip': [spending],
            'Length_of_Stay': [stay_length]
        }
        
        # إضافة جميع الأعمدة الفئوية
        for col in model_columns:
            if col not in input_data:
                # تحديد قيمة العمود
                value = 0
                
                if col.startswith('Gender_'):
                    value = 1 if col == f"Gender_{gender_map[gender]}" else 0
                elif col.startswith('Nationality_'):
                    value = 1 if col == f"Nationality_{nationality_map[nationality]}" else 0
                elif col.startswith('Family_Status_'):
                    value = 1 if col == f"Family_Status_{family_map[family_status]}" else 0
                elif col.startswith('Season_'):
                    value = 1 if col == f"Season_{season_map[season]}" else 0
                elif col.startswith('Purpose_'):
                    cleaned_purpose = purpose_map[purpose].replace(' & ', '_')
                    value = 1 if col == f"Purpose_{cleaned_purpose}" else 0
                elif col.startswith('Accommodation_'):
                    value = 1 if col == f"Accommodation_{accommodation_map[accommodation]}" else 0
                
                input_data[col] = [value]
        
        input_df = pd.DataFrame(input_data)
        input_df = input_df[model_columns]  # ترتيب الأعمدة كما في التدريب
        
        # التنبؤ
        prediction = model.predict(input_df)[0]
        activity_info = DESTINATIONS[prediction]
        
        # عرض النتائج
        st.success(f"## التوصية: {activity_info['title']}")
        
        # عرض الوجهات المقترحة
        st.subheader("الوجهات السياحية المقترحة:")
        
        for place in activity_info['places']:
            with st.expander(f"{place['name']} ({place['type']})"):
                st.markdown(f"""
                **الوصف:** {place['desc']}
                
                **أهم الأنشطة:**
                - استكشاف المنطقة
                - التصوير الفوتوغرافي
                - الاستمتاع بالمناظر الطبيعية
                
                **مدة الزيارة المقترحة:** 2-3 ساعات
                """)
        
        # خريطة توضح مواقع الوجهات (يمكن إضافتها لاحقاً)
        # st.subheader("خريطة الوجهات المقترحة")
        # st.map(...)
        
    except Exception as e:
        st.error(f"حدث خطأ أثناء معالجة طلبك: {str(e)}")

# معلومات إضافية في الشريط الجانبي
with st.sidebar:
    st.header("معلومات عن منطقة عسير")
    st.markdown("""
    - **الموقع:** جنوب غرب السعودية
    - **المساحة:** 81,000 كم²
    - **المناخ:** معتدل صيفاً بارد شتاءً
    - **أشهر المعالم:** السودة، رجال ألمع، أبها
    """)
    
    st.header("نصائح للسائح")
    st.markdown("""
    1. احمل ملابس دافئة للمساء
    2. استخدم خريطة جوجل للتنقل
    3. احجز الفنادق مسبقاً في المواسم
    4. جرب المأكولات المحلية
    """)

# تذييل الصفحة
st.markdown("---")
st.markdown("""
""", unsafe_allow_html=True)
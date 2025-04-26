import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib
import sys
import io

# إصلاح مشكلة الترميز
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def build_model():
    try:
        # تحميل البيانات
        data_path = r"C:\Users\Magid\Downloads\المشروع\tourist_dataset_final.csv"
        data = pd.read_csv(data_path)
        
        # تنظيف البيانات - إزالة الصف الأخير إذا كان يحتوي على "Total"
        data = data[data['Tourist_ID'].notna()]
        
        # معالجة البيانات
        data_encoded = pd.get_dummies(data, columns=[
            'Gender', 'Nationality', 'Family_Status', 
            'Season', 'Purpose', 'Accommodation'
        ])
        
        # تحديد الميزات والهدف
        X = data_encoded.drop(['Tourist_ID', 'Preferred_Activity', 'Year'], axis=1, errors='ignore')
        y = data['Preferred_Activity']
        
        # تقسيم البيانات
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # بناء النموذج
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        # تقييم النموذج
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        # طباعة النتائج
        print(f"نموذج التدريب اكتمل بدقة: {accuracy:.2f}")
        print("تم حفظ النموذج بنجاح في tourist_model.joblib")
        
        # حفظ النموذج
        joblib.dump(model, 'tourist_model.joblib')
        joblib.dump(list(X.columns), 'model_columns.joblib')  # حفظ أسماء الأعمدة
        
    except Exception as e:
        print(f"حدث خطأ: {str(e)}")

if __name__ == "__main__":
    build_model()
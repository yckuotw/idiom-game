import streamlit as st
import pandas as pd
import json
from pathlib import Path

# 預設題庫（作為備用）
DEFAULT_IDIOMS_DATA = {
    "categories": [
        {
            "name": "預見類",
            "questions": [
                {
                    "id": "1",
                    "idiom": "一葉知秋",
                    "meaning": "從小徵兆可以預見未來的發展",
                    "options": ["月暈而風", "揮霍無度", "無懈可擊", "撥雲見日", "見微知著", "如魚得水"],
                    "answers": ["月暈而風", "見微知著"],
                    "explanation": "「月暈而風」預示天氣變化,「見微知著」是從小察覺大事,都有預見未來之意"
                }
            ]
        }
    ]
}

def load_idioms_from_csv():
    """從 CSV 載入題庫"""
    try:
        df = pd.read_csv('idioms.csv')
        categories = {}
        
        for _, row in df.iterrows():
            category = row['category']
            if category not in categories:
                categories[category] = []
                
            # 將字串形式的列表轉換為實際的列表
            options = eval(row['options'])
            answers = eval(row['answers'])
            
            question = {
                'id': str(row['id']),
                'idiom': row['idiom'],
                'meaning': row['meaning'],
                'options': options,
                'answers': answers,
                'explanation': row['explanation']
            }
            categories[category].append(question)
        
        return {'categories': [
            {'name': k, 'questions': v} for k, v in categories.items()
        ]}
    except Exception as e:
        st.error(f"載入題庫時發生錯誤: {str(e)}")
        return DEFAULT_IDIOMS_DATA

def init_session_state():
    """初始化 session state"""
    if 'category_index' not in st.session_state:
        st.session_state.category_index = 0
    if 'question_index' not in st.session_state:
        st.session_state.question_index = 0
    if 'selected' not in st.session_state:
        st.session_state.selected = []
    if 'score' not in st.session_state:
        st.session_state.score = 0
    if 'show_result' not in st.session_state:
        st.session_state.show_result = False
    if 'total_questions' not in st.session_state:
        st.session_state.total_questions = 0

def reset_game():
    """重置遊戲"""
    st.session_state.category_index = 0
    st.session_state.question_index = 0
    st.session_state.selected = []
    st.session_state.score = 0
    st.session_state.show_result = False
    st.session_state.total_questions = 0

def main():
    st.title('成語配對遊戲')
    
    # 載入題庫
    idioms_data = load_idioms_from_csv()
    
    # 初始化遊戲狀態
    init_session_state()
    
    # 側邊欄顯示類別選擇
    categories = [cat['name'] for cat in idioms_data['categories']]
    selected_category = st.sidebar.selectbox(
        '選擇類別',
        categories,
        index=st.session_state.category_index
    )
    
    # 更新類別索引
    st.session_state.category_index = categories.index(selected_category)
    
    # 取得當前類別的題目
    current_category = idioms_data['categories'][st.session_state.category_index]
    current_questions = current_category['questions']
    
    # 如果切換類別，重置問題索引
    if st.session_state.question_index >= len(current_questions):
        st.session_state.question_index = 0
    
    current_question = current_questions[st.session_state.question_index]
    
    # 顯示題目資訊
    st.header(current_question['idiom'])
    st.write(current_question['meaning'])
    
    # 選項區域
    col1, col2 = st.columns(2)
    
    for i, option in enumerate(current_question['options']):
        if i % 2 == 0:
            if col1.button(
                option,
                key=f'opt_{i}',
                type='primary' if option in st.session_state.selected else 'secondary'
            ):
                if option in st.session_state.selected:
                    st.session_state.selected.remove(option)
                elif len(st.session_state.selected) < 2:
                    st.session_state.selected.append(option)
        else:
            if col2.button(
                option,
                key=f'opt_{i}',
                type='primary' if option in st.session_state.selected else 'secondary'
            ):
                if option in st.session_state.selected:
                    st.session_state.selected.remove(option)
                elif len(st.session_state.selected) < 2:
                    st.session_state.selected.append(option)
    
    # 確認答案按鈕
    if not st.session_state.show_result:
        if st.button('確認答案', disabled=len(st.session_state.selected) != 2):
            st.session_state.show_result = True
            is_correct = all(ans in current_question['answers'] 
                           for ans in st.session_state.selected)
            if is_correct:
                st.session_state.score += 1
            st.session_state.total_questions += 1
    
    # 顯示結果
    if st.session_state.show_result:
        is_correct = all(ans in current_question['answers'] 
                        for ans in st.session_state.selected)
        
        if is_correct:
            st.success('答對了！')
        else:
            st.error('答錯了！')
            st.write(f"正確答案是：{', '.join(current_question['answers'])}")
        
        st.info(current_question['explanation'])
        
        if st.button('下一題'):
            st.session_state.selected = []
            st.session_state.show_result = False
            
            if st.session_state.question_index < len(current_questions) - 1:
                st.session_state.question_index += 1
            else:
                st.success(f'本類別完成！\n總得分：{st.session_state.score}/{st.session_state.total_questions}')
                if st.button('重新開始'):
                    reset_game()
    
    # 顯示得分和進度
    st.sidebar.write(f'當前得分：{st.session_state.score}/{st.session_state.total_questions}')
    st.sidebar.write(f'當前進度：{st.session_state.question_index + 1}/{len(current_questions)}')
    
    # 重新開始按鈕
    if st.sidebar.button('重新開始遊戲'):
        reset_game()

if __name__ == '__main__':
    main()

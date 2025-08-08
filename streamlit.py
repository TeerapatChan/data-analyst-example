import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================
# PAGE CONFIG (การตั้งค่าหน้าเพจ)
# ==========================
st.set_page_config(
    page_title="Olympic Athlete Data Analysis",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================
# LOAD DATA (โหลดข้อมูล)
# ==========================
@st.cache_data
def load_data():
    """
    โหลดข้อมูลจากไฟล์ CSV และทำความสะอาดข้อมูลเบื้องต้น
    - เปลี่ยนชื่อคอลัมน์เพื่อความสะดวกในการใช้งาน
    - สร้างคอลัมน์ BMI
    - แปลงข้อมูลปีเป็นประเภทตัวเลข
    """
    df = pd.read_csv("athlete_events.csv")
    df.rename(columns={'NOC': 'Country', 'Team': 'Team Name'}, inplace=True)

    # Calculate BMI
    df['BMI'] = df['Weight'] / ((df['Height'] / 100) ** 2)

    return df

df = load_data()

# ==========================
# SIDEBAR FILTERS (แถบตัวกรองด้านข้าง)
# ==========================
st.sidebar.header("Filters (ตัวกรอง)")
year_list = sorted(df['Year'].unique())
selected_year = st.sidebar.selectbox("Select Year (เลือกปี)", ["All"] + year_list)

sport_list = sorted(df['Sport'].dropna().unique())
selected_sport = st.sidebar.selectbox("Select Sport (เลือกประเภทกีฬา)", ["All"] + sport_list)

country_list = sorted(df['Country'].dropna().unique())
selected_country = st.sidebar.selectbox("Select Country (NOC) (เลือกประเทศ)", ["All"] + country_list)

# Apply filters (ใช้ตัวกรอง)
filtered_df = df.copy()
if selected_year != "All":
    filtered_df = filtered_df[filtered_df['Year'] == selected_year]
if selected_sport != "All":
    filtered_df = filtered_df[filtered_df['Sport'] == selected_sport]
if selected_country != "All":
    filtered_df = filtered_df[filtered_df['Country'] == selected_country]

# ==========================
# MAIN TITLE AND OVERVIEW (หัวข้อหลักและภาพรวม)
# ==========================
st.title("🏅 Olympic Athlete Data Analysis Dashboard")
st.markdown("### Dashboard Overview")

# Use columns for key metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Athletes (นักกีฬาทั้งหมด)", f"{filtered_df['ID'].nunique():,}")
col2.metric("Total Events (รายการแข่งขันทั้งหมด)", f"{filtered_df['Event'].nunique():,}")
col3.metric("Total Countries (ประเทศทั้งหมด)", f"{filtered_df['Country'].nunique():,}")
col4.metric("Total Medals (เหรียญรางวัลทั้งหมด)", f"{len(filtered_df.dropna(subset=['Medal'])):,}")

st.markdown("---")
st.markdown("### Dataset Overview (ภาพรวมข้อมูล)")
st.dataframe(filtered_df.head())

st.markdown("---")
st.header("Key Distributions (การกระจายข้อมูลที่สำคัญ)")
col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Age Distribution of Athletes (การกระจายอายุ)")
    fig_age = px.histogram(
        filtered_df.dropna(subset=['Age']),
        x='Age',
        color='Sex',
        marginal="box",
        hover_data=filtered_df.columns,
        title='Age Distribution by Gender'
    )
    st.plotly_chart(fig_age, use_container_width=True)

with col2:
    st.subheader("2. Gender Distribution (การกระจายเพศ)")
    gender_counts = filtered_df['Sex'].value_counts()
    fig_gender = px.pie(
        values=gender_counts.values,
        names=gender_counts.index,
        title='Gender Proportion'
    )
    st.plotly_chart(fig_gender, use_container_width=True)

st.markdown("---")
st.header("Physical Attributes (ข้อมูลทางกายภาพ)")
col3, col4 = st.columns(2)

with col3:
    st.subheader("3. Height vs Weight (ส่วนสูงกับน้ำหนัก)")
    fig_hw = px.scatter(
        filtered_df.dropna(subset=['Height', 'Weight', 'Sex']),
        x='Height',
        y='Weight',
        color='Sex',
        hover_data=['Name', 'Sport', 'Country'],
        title='Height vs Weight of Athletes'
    )
    st.plotly_chart(fig_hw, use_container_width=True)

with col4:
    st.subheader("4. BMI Distribution (การกระจายค่า BMI)")
    fig_bmi = px.histogram(
        filtered_df.dropna(subset=['BMI']),
        x='BMI',
        color='Sex',
        marginal="box",
        hover_data=filtered_df.columns,
        title='BMI Distribution by Gender'
    )
    st.plotly_chart(fig_bmi, use_container_width=True)

st.markdown("---")
st.header("Event and Medal Analysis (การวิเคราะห์การแข่งขันและเหรียญรางวัล)")
col5, col6 = st.columns(2)

with col5:
    st.subheader("5. Top 10 Sports by Medals (10 อันดับกีฬายอดนิยม)")
    medal_counts = filtered_df.dropna(subset=['Medal'])['Sport'].value_counts().head(10)
    fig_top_sport_medals = px.bar(
        medal_counts,
        x=medal_counts.index,
        y=medal_counts.values,
        title='Top 10 Sports by Number of Medals',
        labels={'x': 'Sport', 'y': 'Number of Medals'}
    )
    st.plotly_chart(fig_top_sport_medals, use_container_width=True)

with col6:
    st.subheader("6. Medals Over the Years by Type (เหรียญรางวัลตามปีและประเภท)")
    medal_year_type = df.dropna(subset=['Medal']).groupby(['Year', 'Medal'])['ID'].count().unstack(fill_value=0)
    fig_medals_over_years = px.line(
        medal_year_type,
        x=medal_year_type.index,
        y=medal_year_type.columns,
        title='Number of Medals Over the Years by Type',
        markers=True
    )
    st.plotly_chart(fig_medals_over_years, use_container_width=True)

st.markdown("---")
st.header("Country and Athlete Performance (ประสิทธิภาพของประเทศและนักกีฬา)")

st.subheader("7. Top Athletes by Medals (10 อันดับนักกีฬาที่ได้เหรียญมากที่สุด)")
top_athletes = filtered_df.dropna(subset=['Medal']).groupby('Name')['Medal'].count().sort_values(ascending=False).head(10)
fig_top_athletes = px.bar(
    top_athletes,
    x=top_athletes.index,
    y=top_athletes.values,
    title='Top 10 Athletes with Most Medals',
    labels={'x': 'Athlete Name', 'y': 'Number of Medals'}
)
st.plotly_chart(fig_top_athletes, use_container_width=True)

st.subheader("8. Medal Count for Selected Country (จำนวนเหรียญรางวัลของประเทศที่เลือก)")
if selected_country != "All":
    country_medals_over_years = df[df['Country'] == selected_country].dropna(subset=['Medal']).groupby('Year')['Medal'].count()
    fig_country_medals = px.line(
        country_medals_over_years,
        x=country_medals_over_years.index,
        y=country_medals_over_years.values,
        title=f"Medal Count for {selected_country} Over the Years",
        markers=True
    )
    st.plotly_chart(fig_country_medals, use_container_width=True)
else:
    st.info("Please select a country from the sidebar to see its medal count over the years.")


st.subheader("9. Athletes Over the Years (จำนวนนักกีฬาในแต่ละปี)")
athlete_counts_overall = df.groupby('Year')['ID'].nunique()
fig_athletes_overall = px.line(
    athlete_counts_overall,
    x=athlete_counts_overall.index,
    y=athlete_counts_overall.values,
    title='Number of Unique Athletes Over the Years',
    labels={'x': 'Year', 'y': 'Number of Athletes'},
    markers=True
)
st.plotly_chart(fig_athletes_overall, use_container_width=True)


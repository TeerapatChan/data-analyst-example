import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================
# PAGE CONFIG
# ==========================
st.set_page_config(
    page_title="Olympic Athlete Data Analysis",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================
# LOAD DATA
# ==========================
@st.cache_data
def load_data():
    """
    Load and prepare dataset.
    - Rename columns for clarity
    - Calculate BMI
    """
    df = pd.read_csv("athlete_events.csv")
    df.rename(columns={'NOC': 'Country', 'Team': 'Team Name'}, inplace=True)
    df['BMI'] = df['Weight'] / ((df['Height'] / 100) ** 2)
    return df

df = load_data()

# ==========================
# SIDEBAR FILTERS
# ==========================
st.sidebar.header("Filters (ตัวกรอง)")

# Year range slider
year_list = sorted(df['Year'].unique())
min_year, max_year = min(year_list), max(year_list)
selected_year_range = st.sidebar.slider(
    "Select Year Range (เลือกช่วงปี)",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year),
    step=1
)

# Sport filter
sport_list = sorted(df['Sport'].dropna().unique())
selected_sport = st.sidebar.selectbox("Select Sport (เลือกประเภทกีฬา)", ["All"] + sport_list)

# Country multiselect
country_list = sorted(df['Country'].dropna().unique())
selected_countries = st.sidebar.multiselect(
    "Select Country (เลือกประเทศ)",
    country_list
)

# Apply filters
filtered_df = df.copy()
filtered_df = filtered_df[
    (filtered_df['Year'] >= selected_year_range[0]) &
    (filtered_df['Year'] <= selected_year_range[1])
]
if selected_sport != "All":
    filtered_df = filtered_df[filtered_df['Sport'] == selected_sport]
if selected_countries:
    filtered_df = filtered_df[filtered_df['Country'].isin(selected_countries)]

# ==========================
# MAIN TITLE & METRICS
# ==========================
st.title("🏅 Olympic Athlete Data Analysis Dashboard")
st.markdown("### Dashboard Overview")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Athletes", f"{filtered_df['ID'].nunique():,}")
col2.metric("Total Events", f"{filtered_df['Event'].nunique():,}")
col3.metric("Total Countries", f"{filtered_df['Country'].nunique():,}")
col4.metric("Total Medals", f"{len(filtered_df.dropna(subset=['Medal'])):,}")

st.markdown("---")
st.markdown("### Dataset Overview")
st.dataframe(filtered_df.head())

# ==========================
# AGE & GENDER DISTRIBUTIONS
# ==========================
st.markdown("---")
st.header("Key Distributions")

col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Age Distribution by Gender")
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
    st.subheader("2. Gender Proportion")
    gender_counts = filtered_df['Sex'].value_counts()
    fig_gender = px.pie(
        values=gender_counts.values,
        names=gender_counts.index,
        title='Gender Distribution'
    )
    st.plotly_chart(fig_gender, use_container_width=True)

# ==========================
# PHYSICAL ATTRIBUTES
# ==========================
st.markdown("---")
st.header("Physical Attributes")

col3, col4 = st.columns(2)

with col3:
    st.subheader("3. Height vs Weight")
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
    st.subheader("4. BMI Distribution")
    fig_bmi = px.histogram(
        filtered_df.dropna(subset=['BMI']),
        x='BMI',
        color='Sex',
        marginal="box",
        hover_data=filtered_df.columns,
        title='BMI Distribution by Gender'
    )
    st.plotly_chart(fig_bmi, use_container_width=True)

# ==========================
# EVENT & MEDAL ANALYSIS
# ==========================
st.markdown("---")
st.header("Event and Medal Analysis")

col5, col6 = st.columns(2)

with col5:
    st.subheader("5. Top 10 Sports by Medals")
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
    st.subheader("6. Medals Over the Years by Type")
    medal_year_type = filtered_df.dropna(subset=['Medal']).groupby(['Year', 'Medal'])['ID'].count().unstack(fill_value=0)
    fig_medals_over_years = px.line(
        medal_year_type,
        x=medal_year_type.index,
        y=medal_year_type.columns,
        title='Number of Medals Over the Years by Type',
        markers=True
    )
    st.plotly_chart(fig_medals_over_years, use_container_width=True)

# ==========================
# COUNTRY & ATHLETE PERFORMANCE
# ==========================
st.markdown("---")
st.header("Country and Athlete Performance")

st.subheader("7. Top 10 Athletes with Most Medals")
top_athletes = filtered_df.dropna(subset=['Medal']).groupby('Name')['Medal'].count().sort_values(ascending=False).head(10)
fig_top_athletes = px.bar(
    top_athletes,
    x=top_athletes.index,
    y=top_athletes.values,
    title='Top 10 Athletes with Most Medals',
    labels={'x': 'Athlete Name', 'y': 'Number of Medals'}
)
st.plotly_chart(fig_top_athletes, use_container_width=True)

st.subheader("8. Medal Count for Selected Countries")
if selected_countries:
    country_medals_over_years = (
        filtered_df[filtered_df['Country'].isin(selected_countries)]
        .dropna(subset=['Medal'])
        .groupby(['Year', 'Country'])['Medal']
        .count()
        .reset_index()
    )
    fig_country_medals = px.line(
        country_medals_over_years,
        x='Year',
        y='Medal',
        color='Country',
        title="Medal Count Over the Years (Selected Countries)",
        markers=True
    )
    st.plotly_chart(fig_country_medals, use_container_width=True)
else:
    st.info("Please select one or more countries from the sidebar to see their medal counts.")

st.subheader("9. Athletes Over the Years")
athlete_counts_overall = filtered_df.groupby('Year')['ID'].nunique()
fig_athletes_overall = px.line(
    athlete_counts_overall,
    x=athlete_counts_overall.index,
    y=athlete_counts_overall.values,
    title='Number of Unique Athletes Over the Years',
    labels={'x': 'Year', 'y': 'Number of Athletes'},
    markers=True
)
st.plotly_chart(fig_athletes_overall, use_container_width=True)
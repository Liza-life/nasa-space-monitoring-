"""
NASA Space Monitoring Dashboard
Interactive Streamlit dashboard for visualizing space data
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add src directory to path
sys.path.append(str(Path(__file__).parent.parent))

# Page configuration
st.set_page_config(
    page_title="NASA Space Monitoring",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        padding: 1rem 0;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .alert-box {
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .alert-danger {
        background-color: #fee;
        border-left: 4px solid #f44;
    }
    .alert-warning {
        background-color: #ffeaa7;
        border-left: 4px solid #fdcb6e;
    }
    .alert-info {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
</style>
""", unsafe_allow_html=True)


def load_sample_data():
    """Load sample asteroid data for demonstration"""
    # Generate sample data
    dates = pd.date_range(start=datetime.now(), periods=30, freq='D')
    
    data = {
        'asteroid_id': [f'2024{i:03d}' for i in range(1, 31)],
        'name': [f'Asteroid {chr(65+i%26)}{i}' for i in range(1, 31)],
        'close_approach_date': dates,
        'miss_distance_km': [400000 + i*50000 for i in range(30)],
        'miss_distance_lunar': [(400000 + i*50000)/384400 for i in range(30)],
        'diameter_min_km': [0.1 + i*0.05 for i in range(30)],
        'diameter_max_km': [0.3 + i*0.08 for i in range(30)],
        'relative_velocity_kms': [10 + i*0.5 for i in range(30)],
        'is_potentially_hazardous': [i % 5 == 0 for i in range(30)]
    }
    
    return pd.DataFrame(data)


def create_header():
    """Create dashboard header"""
    st.markdown('<h1 class="main-header">🚀 NASA Space Monitoring Platform</h1>', unsafe_allow_html=True)
    st.markdown("---")


def create_sidebar():
    """Create sidebar with filters and controls"""
    with st.sidebar:
        st.image("https://www.nasa.gov/wp-content/themes/nasa/assets/images/nasa-logo.svg", width=200)
        st.title("⚙️ Controls")
        
        st.markdown("### 📅 Date Range")
        date_range = st.date_input(
            "Select date range",
            value=(datetime.now(), datetime.now() + timedelta(days=7)),
            key="date_range"
        )
        
        st.markdown("### 🎯 Filters")
        show_hazardous_only = st.checkbox("Show only potentially hazardous", value=False)
        
        min_distance = st.slider(
            "Maximum distance (Lunar distances)",
            min_value=0.0,
            max_value=10.0,
            value=10.0,
            step=0.5
        )
        
        st.markdown("### 🔄 Data Refresh")
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
        
        st.markdown("---")
        st.markdown("### ℹ️ About")
        st.info("""
        This dashboard monitors Near-Earth Objects (NEOs) using NASA's API.
        
        **Data Sources:**
        - NeoWs API
        - APOD
        - Mars Rover Photos
        - DONKI Space Weather
        """)
        
        return {
            'date_range': date_range,
            'show_hazardous_only': show_hazardous_only,
            'min_distance': min_distance
        }


def display_kpis(df):
    """Display key performance indicators"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_asteroids = df['asteroid_id'].nunique()
        st.metric(
            label="🌑 Total Asteroids Monitored",
            value=total_asteroids,
            delta=f"+{int(total_asteroids * 0.1)} this week"
        )
    
    with col2:
        hazardous_count = df['is_potentially_hazardous'].sum()
        st.metric(
            label="⚠️ Potentially Hazardous",
            value=hazardous_count,
            delta=f"{(hazardous_count/len(df)*100):.1f}% of total",
            delta_color="inverse"
        )
    
    with col3:
        closest_approach = df['miss_distance_lunar'].min()
        st.metric(
            label="🎯 Closest Approach",
            value=f"{closest_approach:.2f} LD",
            delta="Lunar Distances"
        )
    
    with col4:
        avg_velocity = df['relative_velocity_kms'].mean()
        st.metric(
            label="⚡ Avg Velocity",
            value=f"{avg_velocity:.1f} km/s",
            delta=f"{avg_velocity*3600:.0f} km/h"
        )


def create_timeline_chart(df):
    """Create timeline of asteroid approaches"""
    st.markdown("### 📅 Upcoming Close Approaches Timeline")
    
    # Sort by date
    df_sorted = df.sort_values('close_approach_date')
    
    # Create figure
    fig = go.Figure()
    
    # Add scatter plot
    fig.add_trace(go.Scatter(
        x=df_sorted['close_approach_date'],
        y=df_sorted['miss_distance_lunar'],
        mode='markers',
        marker=dict(
            size=df_sorted['diameter_max_km'] * 20,
            color=df_sorted['is_potentially_hazardous'].map({True: 'red', False: 'blue'}),
            line=dict(width=1, color='white'),
            opacity=0.7
        ),
        text=df_sorted['name'],
        hovertemplate='<b>%{text}</b><br>' +
                      'Date: %{x}<br>' +
                      'Distance: %{y:.2f} LD<br>' +
                      '<extra></extra>'
    ))
    
    # Add Moon distance reference line
    fig.add_hline(
        y=1.0,
        line_dash="dash",
        line_color="gray",
        annotation_text="Moon Distance (1 LD)",
        annotation_position="right"
    )
    
    fig.update_layout(
        title="Asteroid Close Approaches Over Time",
        xaxis_title="Date",
        yaxis_title="Distance (Lunar Distances)",
        hovermode='closest',
        height=400,
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)


def create_distance_distribution(df):
    """Create distribution of approach distances"""
    st.markdown("### 📊 Distance Distribution")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Histogram
        fig = px.histogram(
            df,
            x='miss_distance_lunar',
            nbins=20,
            color='is_potentially_hazardous',
            color_discrete_map={True: '#ff4444', False: '#4444ff'},
            labels={'miss_distance_lunar': 'Distance (Lunar Distances)', 'count': 'Number of Asteroids'},
            title='Distribution by Distance'
        )
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Size distribution
        fig = px.box(
            df,
            y='diameter_max_km',
            color='is_potentially_hazardous',
            color_discrete_map={True: '#ff4444', False: '#4444ff'},
            labels={'diameter_max_km': 'Diameter (km)'},
            title='Size Distribution'
        )
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)


def create_velocity_analysis(df):
    """Create velocity analysis charts"""
    st.markdown("### ⚡ Velocity Analysis")
    
    # Scatter plot: Distance vs Velocity
    fig = px.scatter(
        df,
        x='miss_distance_lunar',
        y='relative_velocity_kms',
        size='diameter_max_km',
        color='is_potentially_hazardous',
        color_discrete_map={True: '#ff4444', False: '#4444ff'},
        hover_data=['name', 'close_approach_date'],
        labels={
            'miss_distance_lunar': 'Distance (Lunar Distances)',
            'relative_velocity_kms': 'Velocity (km/s)',
            'diameter_max_km': 'Size (km)'
        },
        title='Distance vs Velocity (size = diameter)'
    )
    
    fig.update_layout(height=450)
    st.plotly_chart(fig, use_container_width=True)


def display_alerts(df):
    """Display alerts for close approaches"""
    st.markdown("### 🚨 Alerts & Warnings")
    
    # Filter for close approaches (< 2 LD)
    close_approaches = df[df['miss_distance_lunar'] < 2.0].sort_values('miss_distance_lunar')
    
    if len(close_approaches) > 0:
        for _, asteroid in close_approaches.head(5).iterrows():
            alert_class = "alert-danger" if asteroid['is_potentially_hazardous'] else "alert-warning"
            
            st.markdown(f"""
            <div class="alert-box {alert_class}">
                <strong>{'⚠️ POTENTIALLY HAZARDOUS' if asteroid['is_potentially_hazardous'] else '⚡ CLOSE APPROACH'}</strong><br>
                <strong>Asteroid:</strong> {asteroid['name']}<br>
                <strong>Date:</strong> {asteroid['close_approach_date'].strftime('%Y-%m-%d')}<br>
                <strong>Distance:</strong> {asteroid['miss_distance_lunar']:.2f} LD ({asteroid['miss_distance_km']:,.0f} km)<br>
                <strong>Velocity:</strong> {asteroid['relative_velocity_kms']:.1f} km/s<br>
                <strong>Diameter:</strong> {asteroid['diameter_min_km']:.2f} - {asteroid['diameter_max_km']:.2f} km
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="alert-box alert-info">
            <strong>✅ All Clear</strong><br>
            No asteroids within 2 Lunar Distances in the selected period.
        </div>
        """, unsafe_allow_html=True)


def display_data_table(df):
    """Display detailed data table"""
    st.markdown("### 📋 Detailed Asteroid Data")
    
    # Select columns to display
    display_cols = [
        'name',
        'close_approach_date',
        'miss_distance_lunar',
        'miss_distance_km',
        'relative_velocity_kms',
        'diameter_max_km',
        'is_potentially_hazardous'
    ]
    
    # Format the dataframe
    df_display = df[display_cols].copy()
    df_display['close_approach_date'] = df_display['close_approach_date'].dt.strftime('%Y-%m-%d')
    df_display['miss_distance_km'] = df_display['miss_distance_km'].apply(lambda x: f"{x:,.0f}")
    df_display = df_display.rename(columns={
        'name': 'Asteroid Name',
        'close_approach_date': 'Approach Date',
        'miss_distance_lunar': 'Distance (LD)',
        'miss_distance_km': 'Distance (km)',
        'relative_velocity_kms': 'Velocity (km/s)',
        'diameter_max_km': 'Max Diameter (km)',
        'is_potentially_hazardous': 'Hazardous'
    })
    
    st.dataframe(
        df_display,
        use_container_width=True,
        hide_index=True
    )
    
    # Download button
    csv = df.to_csv(index=False)
    st.download_button(
        label="📥 Download Full Data (CSV)",
        data=csv,
        file_name=f"asteroid_data_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )


def main():
    """Main dashboard function"""
    # Create header
    create_header()
    
    # Create sidebar and get filters
    filters = create_sidebar()
    
    # Load data
    df = load_sample_data()
    
    # Apply filters
    if filters['show_hazardous_only']:
        df = df[df['is_potentially_hazardous'] == True]
    
    df = df[df['miss_distance_lunar'] <= filters['min_distance']]
    
    # Display KPIs
    display_kpis(df)
    
    st.markdown("---")
    
    # Display alerts
    display_alerts(df)
    
    st.markdown("---")
    
    # Create visualizations
    create_timeline_chart(df)
    
    st.markdown("---")
    
    create_distance_distribution(df)
    
    st.markdown("---")
    
    create_velocity_analysis(df)
    
    st.markdown("---")
    
    # Display data table
    display_data_table(df)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>Data source: NASA's Near Earth Object Web Service (NeoWs)</p>
        <p>🚀 Built with Streamlit & Python | Last updated: {}</p>
    </div>
    """.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')), unsafe_allow_html=True)


if __name__ == "__main__":
    main()

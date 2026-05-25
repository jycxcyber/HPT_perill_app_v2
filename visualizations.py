import plotly.graph_objects as go
import plotly.express as px
from fpdf import FPDF
import tempfile
import os

CATHAY_TEAL = '#006564'
CATHAY_SAND = '#C6A27A'

def create_radar_chart(scores_df, compare_df=None):
    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=scores_df['Adjusted Score'],
        theta=scores_df['Pillar'],
        fill='toself',
        name='Selected Group',
        line_color=CATHAY_TEAL
    ))
    
    if compare_df is not None:
        fig.add_trace(go.Scatterpolar(
            r=compare_df['Adjusted Score'],
            theta=compare_df['Pillar'],
            fill='toself',
            name='Comparison Group',
            line_color=CATHAY_SAND
        ))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
        showlegend=True,
        title="Perill Pillar Alignment (Adjusted Scores)"
    )
    return fig

def create_heatmap(df):
    # Exclude Timestamp and Department
    q_cols = [c for c in df.columns if "Question" in c]
    avg_df = df.groupby('Department')[q_cols].mean().T
    
    fig = px.imshow(
        avg_df, 
        color_continuous_scale=[[0, 'red'], [0.5, 'yellow'], [1, CATHAY_TEAL]],
        zmin=1, zmax=10,
        aspect="auto",
        title="Question Heatmap by Department"
    )
    fig.update_layout(xaxis_title="Department", yaxis_title="Questions")
    return fig

def export_to_pdf(radar_fig, heatmap_fig, insights_text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=16, style='B')
    pdf.cell(200, 10, txt="Perill Team Diagnostic Report", ln=True, align='C')
    
    # Save plots as temp images
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as radar_file:
        radar_fig.write_image(radar_file.name)
        pdf.image(radar_file.name, x=10, y=30, w=190)
        
    pdf.add_page()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as heat_file:
        heatmap_fig.write_image(heat_file.name)
        pdf.image(heat_file.name, x=10, y=10, w=190)
        
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt=insights_text.replace('*', ''))
    
    # Cleanup temp files
    os.unlink(radar_file.name)
    os.unlink(heat_file.name)
    
    return pdf.output(dest='S').encode('latin1')
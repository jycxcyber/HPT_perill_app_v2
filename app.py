import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns
from fpdf import FPDF
import io
import excel_handler as eh

# Page Configuration Setup
st.set_page_config(page_title="Perill Team Diagnostic App", layout="wide", page_icon="🛡️")

# Custom Cathay Pacific Palette CSS Injection
st.markdown("""
    <style>
    .stButton>button {background-color: #006564; color: white; border-radius: 4px;}
    .stButton>button:hover {background-color: #004d4c; color: white;}
    .stAlert {border-left-color: #006564;}
    h3 {color: #333333;}
    </style>
    """, unsafe_allow_html=True)

# Run explicit setup and load mappings
eh.initialize_excel()
departments, questions_map = eh.load_config()

# The strict 6 Pillars structure
perill_order = [
    "Purpose & Motivation", 
    "External-facing systems & processes", 
    "Relationships", 
    "Internal-facing systems & processes", 
    "Learning", 
    "Leadership"
]

def classify_tier(score, sd_val):
    if score < 4.4 or sd_val > 3.0:
        return "Permanent Dysfunction", "🟥", "Critical operational risk or severe internal team fragmentation requiring structural realignment."
    elif score < 6.5:
        return "Needs Support", "🟧", "Clear systemic vulnerabilities needing targeted intervention and development."
    elif score < 8.5:
        return "Performing, Balanced", "🟨", "Solid baseline performance with minor operational optimizations required."
    else:
        return "High Performing", "🟩", "This pillar shows world-class execution, strong alignment, and high internal consistency."

# Contextual insights mapping used to generate dynamic subtexts based on real-time scores
PILLAR_ANALYTICS_CONTEXT = {
    "Purpose & Motivation": {
        "polarized": "Team members have highly conflicting views on what success looks like, indicating a fragmented understanding of macro strategic goals.",
        "weak": "Low baseline scores point to a collective drift where daily tasks feel disconnected from a meaningful or inspiring vision.",
        "strong": "Excellent strategic alignment. The team operates with high pride, shared accountability, and clear operational milestones."
    },
    "External-facing systems & processes": {
        "polarized": "Certain team factions feel well-resourced while others experience acute bottleneck friction from external partners and stakeholder requests.",
        "weak": "The team is currently isolated or constantly defensive against external scope creep, lacking formal conduits or intake protocols.",
        "strong": "Superb stakeholder management framework. The team successfully protects its perimeter while adapting seamlessly to enterprise shifts."
    },
    "Relationships": {
        "polarized": "A dangerous split in psychological safety exists. A sub-cohort feels safe while others are silencing dissenting opinions due to fear of friction.",
        "weak": "Interpersonal trust metrics have degraded. Destructive conflicts or micro-frictions are being left unvoiced and unaddressed.",
        "strong": "Outstanding workplace climate. High psychological safety allows the team to engage in healthy, constructive dissent and collaborative support."
    },
    "Internal-facing systems & processes": {
        "polarized": "Operational workflows are highly asymmetrical. Some members have clear execution paths while others are drowning in meeting duplication.",
        "weak": "Internal structures are broken or unmapped. Roles are ambiguous, meetings are unproductive, and digital collaboration tools are underutilized.",
        "strong": "Highly optimized internal workflows. Roles are crystalline, meetings are action-oriented, and documentation avoids duplicate effort."
    },
    "Learning": {
        "polarized": "Lessons learned and growth metrics are siloed. Part of the team is experimenting while others are penalized or stuck in rigid legacy loops.",
        "weak": "The group lacks a framework for post-mortems or continuous growth, turning repeated mistakes into standard operating friction.",
        "strong": "An exemplary blameless learning culture. Mistakes are rapidly treated as process enhancements and R&D time is strictly insulated."
    },
    "Leadership": {
        "polarized": "A profound divide exists regarding management efficacy. Leadership may be empowering a select few while micromanaging others.",
        "weak": "The current management archetype is creating a bottleneck, failing to remove roadblocks, communicate macro strategy early, or balance delivery with care.",
        "strong": "World-class leadership modeling. Managers act as true strategic enablers, balancing firm execution guidelines with deep psychological care."
    }
}

ACTIONABLE_SUGGESTIONS = {
    "Purpose & Motivation": [
        "Facilitate a structured vision workshop to re-align team outcomes with enterprise goals.",
        "Implement explicit, measurable OKRs (Objectives & Key Results) that explicitly map to individual contributions."
    ],
    "External-facing systems & processes": [
        "Establish formal Service Level Agreements (SLAs) and communication conduits with interface teams.",
        "Appoint a stakeholder liaison to manage intake protocols and decouple the core team from scope creep."
    ],
    "Relationships": [
        "Introduce facilitated psychological safety retrospectives to address unvoiced team concerns.",
        "Organize deliberate trust-building cadences focused on understanding individual communication profiles."
    ],
    "Internal-facing systems & processes": [
        "Conduct a comprehensive audit of existing meetings to prune unstructured or unproductive syncs.",
        "Formally document operational standard operating procedures (SOPs) within a centralized knowledge base."
    ],
    "Learning": [
        "Incorporate a blameless post-mortem framework for all key project cycles to emphasize structural over personal accountability.",
        "Dedicate structured sprint allocations or budgets exclusively to engineering/process R&D and cross-training."
    ],
    "Leadership": [
        "Transition management checkpoints toward an empowerment-coaching archetype to alleviate micromanagement friction.",
        "Implement transparent leadership stand-ups explaining macro-organizational strategy and shifts."
    ]
}

# PDF Generator Function
def generate_pdf_report(scope, metrics, polarized_list):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 18)
    
    # Header
    pdf.set_text_color(0, 101, 100) # Cathay Teal
    pdf.cell(0, 10, "Perill Team Effectiveness Diagnostic Report", ln=True, align="C")
    pdf.set_font("Arial", "", 12)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(0, 10, f"Target Profile Scope: {scope}", ln=True, align="C")
    pdf.ln(10)
    
    # Executive Summary Table Header
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Executive Performance Summary Table", ln=True)
    pdf.set_font("Arial", "B", 10)
    
    # Table Grid Layout
    pdf.cell(65, 8, "Strategic Pillar", border=1)
    pdf.cell(30, 8, "Raw Mean", border=1)
    pdf.cell(30, 8, "Volatility (sd)", border=1)
    pdf.cell(30, 8, "Adjusted Score", border=1)
    pdf.cell(35, 8, "Tier Status", border=1, ln=True)
    
    pdf.set_font("Arial", "", 10)
    for p in perill_order:
        d = metrics[p]
        pdf.cell(65, 8, str(p), border=1)
        pdf.cell(30, 8, f"{d['mean']:.2f}", border=1)
        pdf.cell(30, 8, f"{d['sd']:.2f}", border=1)
        pdf.cell(30, 8, f"{d['adj']:.2f}", border=1)
        pdf.cell(35, 8, str(d['tier']), border=1, ln=True)
        
    pdf.ln(10)
    
    # Tailored Action Items Section
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Tailored Actionable Interventions", ln=True)
    pdf.set_font("Arial", "", 10)
    
    rendered = 0
    for p in perill_order:
        if metrics[p]["adj"] < 6.5:
            rendered += 1
            pdf.set_font("Arial", "B", 11)
            pdf.cell(0, 8, f"Pillar Crisis: {p} (Score: {metrics[p]['adj']:.2f})", ln=True)
            pdf.set_font("Arial", "", 10)
            for rec in ACTIONABLE_SUGGESTIONS.get(p, []):
                pdf.multi_cell(0, 6, f"- {rec}")
            pdf.ln(2)
            
    if rendered == 0:
        pdf.cell(0, 10, "All pillars are functioning effectively. No critical interventions required.", ln=True)
        
    return pdf.output(dest="S").encode("latin1")

st.title("🛡️ Perill Team Effectiveness Diagnostic Suite")
st.markdown("---")

view_mode = st.sidebar.radio("Navigation Hub", ["📋 Team Assessment Survey", "📊 Administrator Dashboard"])

# ==========================================
# VIEW 1: TEAM ASSESSMENT SURVEY
# ==========================================
if view_mode == "📋 Team Assessment Survey":
    st.header("Team Diagnostic Questionnaire")
    st.write("Please answer the following questions honestly. Submissions are compiled anonymously.")
    
    with st.form("survey_form"):
        selected_dept = st.selectbox("Select Your Current Department/Group:", ["-- Select Department --"] + departments)
        st.markdown("---")
        
        pillars_grouped = {}
        for q, p in questions_map.items():
            pillars_grouped.setdefault(p, []).append(q)
            
        form_answers = {}
        
        for pillar in perill_order:
            if pillar in pillars_grouped:
                queries = pillars_grouped[pillar]
                st.subheader(f"🔷 Pillar: {pillar}")
      
                for q_text in queries:
                    form_answers[q_text] = st.select_slider(
                        q_text,
                        options=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                        value=5,
                        format_func=lambda x: {1: "1 - Disagree", 5: "5 - Neutral", 10: "10 - Agree"}.get(x, str(x))
                    )
                st.markdown("---")
            
        submit_btn = st.form_submit_button("Submit Confidential Evaluation")
        if submit_btn:
            if selected_dept == "-- Select Department --":
                st.error("Submission blocked: You must specify a valid Department selection.")
            else:
                eh.save_submission(selected_dept, form_answers)
                st.success(f"Thank you! Your diagnostics have been securely saved to the database for {selected_dept}.")

# ==========================================
# VIEW 2: ADMINISTRATOR DASHBOARD
# ==========================================
elif view_mode == "📊 Administrator Dashboard":
    st.header("Admin Analytics & Diagnostics Engine")
    admin_password = st.sidebar.text_input("Enter Administrator Access Key:", type="password")
    
    if admin_password != "Cathay2026":
        if admin_password:
            st.error("Access Denied: Invalid Administrative Credentials.")
        else:
            st.info("Please input your admin verification password in the sidebar panel to unlock enterprise metrics.")
    else:
        df_res = eh.load_responses()
        
        # UPLOAD DATA FILE
        st.sidebar.markdown("---")
        st.sidebar.subheader("📥 Database Operations")
        uploaded_file = st.sidebar.file_uploader("Import External Survey Data (Excel)", type=["xlsx"])
        if uploaded_file is not None:
            try:
                success = eh.import_external_data(uploaded_file)
                if success:
                    st.sidebar.success("External records merged successfully!")
                    st.rerun()
                else:
                    st.sidebar.error("Schema mismatch. Upload file headers must exactly match standard database rows.")
            except Exception as e:
                st.sidebar.error(f"Error parsing file: {e}")

        if df_res.empty or len(df_res) == 0:
            st.info("The application database contains no responses yet.")
        else:
            st.sidebar.subheader("Filter Configurations")
            all_depts = sorted(df_res["Department"].dropna().unique().tolist())
            
            filter_type = st.sidebar.radio("Scope Selection Method", ["All Departments", "Specific Filters"])
            if filter_type == "All Departments":
                filtered_df = df_res
                scope_title = "All Enterprise Departments"
            else:
                selected_depts = st.sidebar.multiselect("Select Targeted Department(s):", all_depts, default=all_depts[:1] if all_depts else [])
                filtered_df = df_res[df_res["Department"].isin(selected_depts)]
                scope_title = ", ".join(selected_depts) if selected_depts else "No cohorts selected"
                
            st.subheader(f"Analyzing Target Profile: `{scope_title}` ({len(filtered_df)} responses compiled)")
            
            if filtered_df.empty:
                st.warning("No metrics match the selected department filters.")
            else:
                active_questions = [q for q in questions_map.keys() if q in filtered_df.columns]
                for col in active_questions:
                    filtered_df[col] = pd.to_numeric(filtered_df[col], errors='coerce')
                
                def calculate_pillar_metrics(target_dataframe):
                    metrics = {}
                    for pillar in perill_order:
                        pillar_cols = [col for col in active_questions if questions_map[col] == pillar]
                        if not pillar_cols or target_dataframe.empty:
                            metrics[pillar] = {"mean": 0.0, "sd": 0.0, "adj": 0.0, "tier": "No Data", "color": "⬜", "desc": ""}
                            continue
                        
                        scores_vector = target_dataframe[pillar_cols].values.flatten()
                        scores_vector = scores_vector[~np.isnan(scores_vector)]
                        if len(scores_vector) == 0:
                            metrics[pillar] = {"mean": 0.0, "sd": 0.0, "adj": 0.0, "tier": "No Data", "color": "⬜", "desc": ""}
                            continue
                            
                        m = np.mean(scores_vector)
                        sd = np.std(scores_vector, ddof=1) if len(scores_vector) > 1 else 0.0
                        
                        # Apply Volatility Penalty Model
                        adj = m - (0.5 * sd) if sd >= 2.0 else m
                        
                        tier, icon, description = classify_tier(adj, sd)
                        metrics[pillar] = {"mean": m, "sd": sd, "adj": adj, "tier": tier, "color": icon, "desc": description}
                    return metrics

                primary_metrics = calculate_pillar_metrics(filtered_df)
                
                st.sidebar.markdown("---")
                overlay_company_baseline = st.sidebar.checkbox("Overlay Company-wide Average", value=False)
                company_metrics = calculate_pillar_metrics(df_res) if overlay_company_baseline else None
                
                # DOWNLOAD REPORT AS PDF
                polarized_pillars = [p for p in perill_order if primary_metrics[p]["sd"] >= 2.0]
                pdf_data = generate_pdf_report(scope_title, primary_metrics, polarized_pillars)
                st.sidebar.download_button(
                    label="📥 Download Executive PDF Report",
                    data=pdf_data,
                    file_name=f"Perill_Diagnostic_{scope_title.replace(' ', '_')}.pdf",
                    mime="application/pdf"
                )
                
                # Radar Graph Setup
                categories_closed = perill_order + [perill_order[0]]
                primary_values = [primary_metrics[p]["adj"] for p in perill_order]
                primary_values_closed = primary_values + [primary_values[0]]
                
                fig = go.Figure()
                fig.add_trace(go.Scatterpolar(
                    r=primary_values_closed, theta=categories_closed, fill='toself',
                    name=f"Selected Profile ({scope_title})",
                    fillcolor='rgba(0, 101, 100, 0.20)', line=dict(color='#006564', width=3.5)
                ))
                
                if overlay_company_baseline:
                    comp_values = [company_metrics[p]["adj"] for p in perill_order]
                    comp_values_closed = comp_values + [comp_values[0]]
                    fig.add_trace(go.Scatterpolar(
                        r=comp_values_closed, theta=categories_closed, fill='toself',
                        name="Global Company Average",
                        fillcolor='rgba(198, 162, 122, 0.15)', line=dict(color='#C6A27A', width=2.5, dash='dash')
                    ))
                
                fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[1.0, 10.0])), showlegend=overlay_company_baseline, height=400)
                
                col1, col2 = st.columns([1, 1.2], gap="medium")
                with col1:
                    st.markdown("### 🕸️ Strategic Vector Performance")
                    st.plotly_chart(fig, use_container_width=True)
                with col2:
                    st.markdown("### 📋 Executive Summary Table")
                    grid_rows = []
                    for pillar in perill_order:
                        p_data = primary_metrics[pillar]
                        grid_rows.append({
                            "Perill Strategic Pillar": pillar,
                            "Raw Mean Score": f"{p_data['mean']:.2f} / 10.00",
                            "Volatility (σ)": f"{p_data['sd']:.2f}",
                            "Adjusted Score": f"{p_data['adj']:.2f} / 10.00",
                            "Status Classification": f"{p_data['color']} {p_data['tier']}"
                        })
                    st.table(pd.DataFrame(grid_rows))
                
                # THE SEABORN PILLAR HEATMAP
                st.markdown("---")
                st.subheader("📊 Strategic Pillar Inter-Correlation Heatmap")
                st.write("This correlation analysis tracks how closely performance changes in one Perill pillar match shifts in other elements.")
                
                heatmap_df = pd.DataFrame()
                for pillar in perill_order:
                    pillar_cols = [col for col in active_questions if questions_map[col] == pillar]
                    if pillar_cols:
                        heatmap_df[pillar] = filtered_df[pillar_cols].mean(axis=1)
                
                if len(filtered_df) > 1 and not heatmap_df.empty:
                    corr_matrix = heatmap_df.corr().fillna(0)
                    plt.figure(figsize=(7, 4.5))
                    sns.heatmap(corr_matrix, annot=True, cmap="YlGnBu", vmin=-1, vmax=1, fmt=".2f", cbar=True, annot_kws={"size": 9})
                    plt.xticks(rotation=25, ha='right', fontsize=8)
                    plt.yticks(fontsize=8)
                    plt.tight_layout()
                    
                    buf = io.BytesIO()
                    plt.savefig(buf, format="png", dpi=180)
                    st.image(buf)
                    plt.close()
                else:
                    st.info("Additional entry records are required to map transactional correlation coefficients.")

                # ====================================================
                # REWRITTEN: DYNAMIC CONTEXTUAL POLARIZATION ANALYSIS
                # ====================================================
                st.markdown("---")
                st.subheader("🔍 Polarization & Variance Analysis")
                
                if polarized_pillars:
                    st.error("⚠️ **Internal Subgroup Fragmentation & Alignment Disagreement Detected!**")
                    st.markdown(
                        "The evaluation indicates that respondents inside this cohort have **differing operational experiences**. "
                        "A high variance means your team is splitting into separate subgroups, "
                        "which means a simple average alone does not accurately reflect the whole picture. "
                    )
                    
                    for p_name in polarized_pillars:
                        v_val = primary_metrics[p_name]["sd"]
                        context_txt = PILLAR_ANALYTICS_CONTEXT[p_name]["polarized"]
                        
                        if v_val > 3.0:
                            st.markdown(f"* 🚨 **{p_name}** (`σ = {v_val:.2f}`) → **Extreme Internal Split:** {context_txt} This high disagreement introduces severe operational risk, triggering an automatic reduction to the *Dysfunctional* tier.")
                        else:
                            st.markdown(f"* ⚠️ **{p_name}** (`σ = {v_val:.2f}`) → **Moderate Polarization:** {context_txt} A volatility penalty has been applied to adjust the baseline average score downwards for safety.")
                else:
                    st.success("✅ **High Internal Consensus Verified:** Team perspectives are tightly aligned across all measured facets, reflecting a shared, consistent workplace experience.")
                
                # ====================================================
                # REWRITTEN: DYNAMIC AUTOMATED INSIGHTS SUMMARY
                # ====================================================
                st.markdown("---")
                st.subheader("💡 Automated Insights Summary")
                sorted_pillars = sorted(primary_metrics.items(), key=lambda item: item[1]["adj"], reverse=True)
                max_score = sorted_pillars[0][1]["adj"]
                min_score = sorted_pillars[-1][1]["adj"]
                
                c1, c2 = st.columns(2)
                with c1:
                    st.success("#### 💪 Identified Strategic Strengths")
                    for s, d in sorted_pillars:
                        if d["adj"] == max_score or (max_score - d["adj"]) < 0.2:
                            st.markdown(f"**{s}** (`{d['adj']:.2f}` → {d['tier']})")
                            # DYNAMIC SUBTEXT: Extracts unique pillar strength context
                            st.caption(f"🧠 **Insight:** {PILLAR_ANALYTICS_CONTEXT[s]['strong']} (Internal variation remains low at σ = {d['sd']:.2f})")
                with c2:
                    st.error("#### ⚠️ Primary Optimization Opportunities")
                    for g, d in sorted_pillars:
                        if d["adj"] == min_score or (d["adj"] - min_score) < 0.2:
                            st.markdown(f"**{g}** (`{d['adj']:.2f}` → {d['tier']})")
                            # DYNAMIC SUBTEXT: Checks if the problem is flat low-scores or polarization confusion
                            if d["sd"] >= 2.0:
                                problem_txt = f"This is primarily driven by internal friction and sub-cohort polarization (σ = {d['sd']:.2f}). " + PILLAR_ANALYTICS_CONTEXT[g]['polarized']
                            else:
                                problem_txt = f"This is driven by uniform low sentiment across the cohort. " + PILLAR_ANALYTICS_CONTEXT[g]['weak']
                            st.caption(f"🎯 **Insight:** {problem_txt}")
                
                # RECOMMENDATIONS
                st.markdown("---")
                st.subheader("🚀 Tailored Actionable Recommendations")
                action_items_rendered = 0
                for p_name in perill_order:
                    p_data = primary_metrics[p_name]
                    if p_data["adj"] < 6.5:
                        action_items_rendered += 1
                        st.markdown(f"#### {p_data['color']} Due to performance drop or polarization in **{p_name}** ({p_data['adj']:.2f}):")
                        for rec in ACTIONABLE_SUGGESTIONS.get(p_name, []):
                            st.markdown(f"* 📍 {rec}")
                if action_items_rendered == 0:
                    st.info("🌟 **All pillars are currently tracking within target thresholds!**")
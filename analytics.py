import pandas as pd
import numpy as np

def calculate_pillar_scores(df):
    if df.empty:
        return None
    
    results = []
    
    # Extract pillars from question strings
    pillars = ["Purpose & Motivation", "External-facing systems", "Relationships", 
               "Internal-facing systems", "Learning", "Leadership"]
    
    for pillar in pillars:
        # Get columns that belong to this pillar
        pillar_cols = [col for col in df.columns if f"[{pillar}]" in col]
        
        # Flatten all responses for this pillar into a single array
        all_scores = df[pillar_cols].values.flatten()
        all_scores = all_scores[~np.isnan(all_scores)] # Remove NaNs
        
        if len(all_scores) == 0:
            continue
            
        mean_val = np.mean(all_scores)
        std_val = np.std(all_scores, ddof=1) if len(all_scores) > 1 else 0
        
        # Apply Volatility Penalty
        if std_val >= 2.0:
            adjusted_score = mean_val - (0.5 * std_val)
        else:
            adjusted_score = mean_val
            
        # Determine Tier
        if adjusted_score < 4.5 or std_val > 3.0:
            tier = "Dysfunctional"
        elif adjusted_score >= 8.5:
            tier = "High Performing"
        elif adjusted_score >= 6.5:
            tier = "Performing, Balance"
        else:
            tier = "Needs Support"
            
        results.append({
            "Pillar": pillar,
            "Raw Mean": round(mean_val, 2),
            "SD": round(std_val, 2),
            "Adjusted Score": round(adjusted_score, 2),
            "Tier": tier
        })
        
    return pd.DataFrame(results)

def generate_insights(scores_df):
    if scores_df is None or scores_df.empty:
        return "Not enough data to generate insights."
    
    highest = scores_df.loc[scores_df['Adjusted Score'].idxmax()]
    lowest = scores_df.loc[scores_df['Adjusted Score'].idxmin()]
    
    dysfunctional = scores_df[scores_df['Tier'] == 'Dysfunctional']['Pillar'].tolist()
    
    insight = f"**Greatest Strength:** {highest['Pillar']} ({highest['Adjusted Score']}/10). Keep leveraging this.\n\n"
    insight += f"**Primary Opportunity:** {lowest['Pillar']} ({lowest['Adjusted Score']}/10). This requires immediate attention.\n\n"
    
    if dysfunctional:
        insight += f"**Critical Warning:** The following areas are highly polarized or scoring critically low, indicating dysfunction: {', '.join(dysfunctional)}."
        
    return insight
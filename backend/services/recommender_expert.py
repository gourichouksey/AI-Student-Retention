def generate_expert_recommendations(data, risk_score, shap_explanation):
    recs = []
    
    # Extract feature impacts from your SHAP service
    impacts = {item['name']: item['impact'] for item in shap_explanation['top_features']}
    
    # 1. Academic Intervention based on SHAP impact
    if impacts.get('remainder__backlogs', 0) > 0.1:
        recs.append("Academic Priority: SHAP analysis identifies 'Backlogs' as your primary risk factor. Priority remedial classes assigned.")

    # 2. Financial Intervention
    if impacts.get('remainder__family_income', 0) > 0.1:
        recs.append("Financial Priority: Income level is impacting retention probability. Reviewing specialized scholarship matches.")

    # 3. Standard Risk Threshold
    if risk_score > 0.8:
        recs.append("CRITICAL: Immediate counselor meeting required regardless of specific factors.")
        
    return recs
import pandas as pd


def get_panel_final_accuracy(final_marks_df):
    """
    Calculate the Spearman correlation for a single dance in the final
    Return a Series with the correlation values, sorted in descending order
    """
    final_result = final_marks_df['place'].astype(float)

    judge_cols = [c for c in final_marks_df.columns if len(c) == 1 and c.isalpha()]
    
    correlations = final_marks_df[judge_cols].apply(lambda x: x.corr(final_result, method='spearman')).round(2)
    
    return correlations.sort_values(ascending=False)


def get_overall_panel_final_accuracy(final_marks):
    """
    Aggregates judge accuracy across all dances and produces a report.
    
    Returns:
        DataFrame sorted by 'overall_accuracy' (descending).
        Columns: [overall_accuracy, C, S, R, P, J...]
    """
    scores_per_dance = {}
    
    for dance_name, df in final_marks.items():
        scores_per_dance[dance_name] = get_panel_final_accuracy(df)
        
    # Combine into one Matrix
    report = pd.DataFrame(scores_per_dance)
    
    # Calculate Aggregate Metrics
    report['overall_accuracy'] = report.mean(axis=1).round(2)
    
    # Formatting
    cols = ['overall_accuracy'] + [c for c in report.columns if c != 'overall_accuracy']
    report = report[cols]
    
    # Sort
    return report.sort_values(by='overall_accuracy', ascending=False)


def get_panel_final_bias(final_marks_df):
    """
    Calculates bias for a single dance in a final
    Returns a 'melted' DataFrame: [couple, judge, bias_value]
    """
    judge_cols = [c for c in final_marks_df.columns if len(c) == 1 and c.isalpha()]
    
    # Vectorized Calculation (Bias = Judge - Place)
    judges_df = final_marks_df[judge_cols].astype(float)
    final_place = final_marks_df['place'].astype(float)
    
    # Calculate difference aligned by index
    bias_matrix = judges_df.sub(final_place, axis=0)
    
    # 3. Melt for simplified merging
    bias_long = bias_matrix.stack().reset_index()
    bias_long.columns = ['couple', 'judge', 'bias_value']
    
    return bias_long

def get_overall_panel_final_bias(final_marks):
    """
    Aggregates bias across all dances into a comprehensive report
        
    Returns:
        DataFrame columns: [judge, couple, overall_bias, W, T, V, F, Q...]
    """
    all_records = []
    
    for dance_name, df in final_marks.items():
        dance_bias = get_panel_final_bias(df)
        
        dance_bias = dance_bias.rename(columns={'bias_value': dance_name})
        
        # Set MultiIndex for merging: (judge, couple) are the unique keys
        dance_bias = dance_bias.set_index(['judge', 'couple'])
        all_records.append(dance_bias)
    
    if not all_records:
        return pd.DataFrame()

    # Merge All Dances
    full_report = pd.concat(all_records, axis=1)
    
    # Calculate Overall Bias
    full_report['overall_bias'] = full_report.mean(axis=1).round(2)
    
    # Final Formatting
    full_report = full_report.reset_index()

    # Sort
    full_report['severity'] = full_report['overall_bias'].abs()
    full_report = full_report.sort_values('severity', ascending=False).drop(columns=['severity'])
    
    # Reorder columns: Judge, Couple, Overall, then the specific dances
    dance_cols = list(final_marks.keys())
    cols = ['judge', 'couple', 'overall_bias'] + dance_cols
    
    return full_report[cols]
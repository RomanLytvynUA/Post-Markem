import pandas as pd


def get_panel_final_accuracy(df):
    """
    Calculate the Spearman correlation between each judge's scores and the final placements.
    Return a Series with the correlation values, sorted in descending order.
    """
    final_result = df['place'].astype(float)

    judge_cols = [c for c in df.columns if len(c) == 1 and c.isalpha()]
    
    correlations = df[judge_cols].apply(lambda x: x.corr(final_result, method='spearman'))
    
    return correlations.sort_values(ascending=False)


def get_overall_panel_final_accuracy(final_marks):
    """
    Aggregates judge accuracy across all dances and produces a report.
    
    Returns:
        DataFrame sorted by 'overall_accuracy' (descending).
        Columns: [overall_accuracy, C, S, R, P, J...]
    """
    # Collect accuracy scores for each dance
    scores_per_dance = {}
    
    for dance_name, df in final_marks.items():
        scores_per_dance[dance_name] = get_panel_final_accuracy(df)
        
    # Combine into one Matrix
    report = pd.DataFrame(scores_per_dance)
    
    # Calculate Aggregate Metrics
    report['overall_accuracy'] = report.mean(axis=1)
    
    # Formatting & Sorting
    cols = ['overall_accuracy'] + [c for c in report.columns if c != 'overall_accuracy']
    report = report[cols]
    
    # Sort: Best judges first
    return report.sort_values(by='overall_accuracy', ascending=False)
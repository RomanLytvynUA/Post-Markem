import pandas as pd
import numpy as np


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


def get_correlation_pairs(df):
    """
    Calculates pairwise correlation for one dance.
    Returns: DataFrame [judge_1, judge_2, correlation]
    """
    judge_cols = [c for c in df.columns if len(c) == 1 and c.isalpha()]
    
    if len(judge_cols) < 2:
        return pd.DataFrame(columns=['judge_1', 'judge_2', 'correlation'])

    corr_matrix = df[judge_cols].astype(float).corr(method='spearman')
    
    # 3. Mask Lower Triangle & Diagonal (Keep Upper Triangle only)
    # k=1 excludes the diagonal (self-correlation)
    mask = np.triu(np.ones(corr_matrix.shape), k=1).astype(bool)
    
    # 4. Flatten to List
    # .where(mask) sets lower triangle to NaN
    # .stack() drops NaNs, keeping only unique A-B pairs
    pairs = corr_matrix.where(mask).stack().reset_index()
    pairs.columns = ['judge_1', 'judge_2', 'correlation']
    
    unique_pairs = pairs[pairs['judge_1'] < pairs['judge_2']].copy()

    return unique_pairs

def get_coalition_report(dances):
    """
    Aggregates correlation pairs across all dances.
    Returns: [judge_1, judge_2, overall_score, W, T, V...]
    """
    all_dance_pairs = []
    
    for dance_name, df in dances.items():
        # Get pairs for this dance
        dance_pairs = get_correlation_pairs(df)
        
        if dance_pairs.empty:
            continue
            
        # Rename 'correlation' to the specific dance name
        dance_pairs = dance_pairs.rename(columns={'correlation': dance_name})
        
        # Set Index for merging
        dance_pairs = dance_pairs.set_index(['judge_1', 'judge_2'])
        all_dance_pairs.append(dance_pairs)
            
    if not all_dance_pairs:
        return pd.DataFrame(columns=['judge_1', 'judge_2', 'overall_score'])

    # Merge all dances (Outer Join aligns A-B correctly across dances)
    full_report = pd.concat(all_dance_pairs, axis=1)
    
    # Calculate Overall Score (Mean)
    full_report['overall_score'] = full_report.mean(axis=1)
    
    # Cleanup & Sort
    full_report = full_report.reset_index()
    full_report = full_report.sort_values(by='overall_score', ascending=False)
    
    # Reorder
    dance_cols = [c for c in full_report.columns if c not in ['judge_1', 'judge_2', 'overall_score']]
    final_cols = ['judge_1', 'judge_2', 'overall_score'] + dance_cols
    
    return full_report[final_cols]


def find_voting_blocs(report, threshold = 0.85):
    """
    Identifies groups of judges who consistently agree with each other
    """
    pairs = report[report['overall_score'] >= threshold].copy()
    
    blocs = []
    
    for _, row in pairs.iterrows():
        j1, j2 = row['judge_1'], row['judge_2']
        
        # Search for existing blocs containing these judges
        bloc_j1 = next((b for b in blocs if j1 in b), None)
        bloc_j2 = next((b for b in blocs if j2 in b), None)

        if bloc_j1 and bloc_j2 and bloc_j1 is not bloc_j2:
            bloc_j1.update(bloc_j2)
            blocs.remove(bloc_j2)
        elif bloc_j1:
            bloc_j1.add(j2)
        elif bloc_j2:
            bloc_j2.add(j1)
        elif not bloc_j1 and not bloc_j2:
            blocs.append({j1, j2})
            
    formatted_blocs = [sorted(list(b)) for b in blocs]
    formatted_blocs.sort(key=len, reverse=True)
    
    return formatted_blocs
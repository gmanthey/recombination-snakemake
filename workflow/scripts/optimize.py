from snakemake.script import snakemake, shell
import pandas as pd

def ranks_per_col(data: pd.DataFrame, sense: list):
    ranks = pd.DataFrame(index=data.index, columns=data.columns, dtype=int)
    for col, s in zip(data, sense):
        if s == 'min':
            d = data[col]
        elif s == 'max':
            d = -data[col]
        else:
            print(f'Error: {s} not an acceptable value for sense!')
        
        ranks[col] = d.argsort()
        
    return ranks

def get_hyperparam(hyperparam_file):
    hyperparam = pd.read_csv(hyperparam_file, sep='\t')
    
    ranks = ranks_per_col(hyperparam[['Pearson_Corr_1bp', 'Pearson_Corr_10kb',
       'Pearson_Corr_100kb', 'Log_Pearson_Corr_1bp', 'Log_Pearson_Corr_10kb',
       'Log_Pearson_Corr_100kb', 'Spearman_Corr_1bp', 'Spearman_Corr_10kb',
       'Spearman_Corr_100kb', 'L2', 'Log_L2']], ['max', 'max',
       'max', 'max', 'max',
       'max', 'max', 'max',
       'max', 'min', 'min']).sum(axis=1)
    
    best_index = ranks.argmin()
    
    bp, ws = hyperparam.loc[best_index, ['Block_Penalty', 'Window_Size']]
    
    bp = int(bp)
    ws = int(ws)
    
    return bp, ws

bp, ws = get_hyperparam(snakemake.input[1])

shell(f"pyrho optimize --vcffile {snakemake.input[0]} --windowsize {ws} --blockpenalty {bp} --tablefile {snakemake.input[2]} --ploidy 2 --outfile {snakemake.output[0]} --numthreads {snakemake.threads} > {snakemake.log} 2>&1")
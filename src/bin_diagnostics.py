"""Empirical runway-integrand projection diagnostic; not a full vector-field certificate."""
from pathlib import Path
import json
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'data/processed/audited_listed_firm_liquidity.csv'
OUT=ROOT/'data/processed/bin_diagnostics'
OUT.mkdir(parents=True,exist_ok=True)

def main():
    d=pd.read_csv(SRC)
    d=d[(d.frecuencia=='annual') & (~d.es_sector_financiero.astype(bool))].copy()
    d=d[d.runway_liquidez_dias.gt(0)&d.runway_liquidez_dias.le(3650)]
    d=d.sort_values('fecha_cierre').groupby('ticker',as_index=False).tail(1)
    # Use months as the normalized runway unit; epsilon=.25 months matches the reduced model's scale.
    R=d.runway_liquidez_dias.to_numpy(float)/30.4375
    eps=.25; alpha=1.0
    exact_u=float(np.mean(1/(R+eps)))
    exact_q=float(np.mean((eps/(R+eps))**alpha))
    rows=[]
    for scheme in ('uniform','quantile'):
        for K in (4,8,16,32,64,128):
            if scheme=='uniform':
                edges=np.linspace(0,float(R.max())+1e-12,K+1)
            else:
                edges=np.quantile(R,np.linspace(0,1,K+1))
                edges[0]=min(0.0,float(edges[0])); edges[-1]=float(R.max())+1e-10
                edges=np.unique(edges)
                if len(edges)<2: continue
            ids=np.clip(np.digitize(R,edges[1:-1],right=False),0,len(edges)-2)
            mids=(edges[:-1]+edges[1:])/2
            approx_u=float(np.mean(1/(mids[ids]+eps)))
            approx_q=float(np.mean((eps/(mids[ids]+eps))**alpha))
            delta=float(np.max(np.diff(edges)))
            rows.append({'scheme':scheme,'requested_K':K,'actual_bins':len(edges)-1,'max_bin_width_months':delta,
                         'mean_urgency_exact':exact_u,'mean_urgency_binned':approx_u,'abs_error_urgency':abs(approx_u-exact_u),
                         'mean_distress_exact':exact_q,'mean_distress_binned':approx_q,'abs_error_distress':abs(approx_q-exact_q),
                         'uniform_bound_urgency':delta/(2*eps**2),'uniform_bound_distress':delta/(2*eps)})
    result=pd.DataFrame(rows)
    result.to_csv(OUT/'bin_diagnostics.csv',index=False)
    report={'n_firms':int(len(R)),'runway_unit':'months (days / 30.4375)','epsilon_months':eps,'alpha':alpha,
            'exact_sample_mean_urgency':exact_u,'exact_sample_mean_distress':exact_q,
            'interpretation':'This checks only projection of two nonlinear integrands over the observed listed-firm runway sample. It does not bound transition, trajectory, root or bifurcation errors of the finite-dimensional vector field.',
            'results':result.to_dict(orient='records')}
    (OUT/'bin_diagnostics.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(result.to_string(index=False))

if __name__=='__main__': main()

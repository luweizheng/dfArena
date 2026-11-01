"""Reproduce DAB descriptive figures from the frozen, adjudicated analysis inputs.

Run: python make_figures.py
Does not alter scores, annotations, experiments, or human review records.
"""
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import math

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager, colors
from matplotlib.patches import Patch
from matplotlib.ticker import MultipleLocator

OUT = Path(__file__).resolve().parent
BASE = OUT.parent
CLASSES = ['I1', 'I2', 'I3', 'I4', 'I5', 'I6', 'II1', 'II3', 'II4']
MODELS = ['gpt55', 'astra', 'kimi', 'glm53']
MODES = ['direct', 'clarified', 'interact']
MODEL_NAMES = {'gpt55': 'GPT-5.5', 'astra': 'GPT-6', 'kimi': 'Kimi K3', 'glm53': 'GLM-5.3'}
SHORT = {
 'I1': 'Task interpretation & analysis planning',
 'I2': 'Data selection & interpretation',
 'I3': 'Data processing & algorithm implementation',
 'I4': 'API, execution & repair failures',
 'I5': 'Instruction following & result delivery',
 'I6': 'Problem-solving workflow failure',
 'II1': 'Missing / ambiguous task requirements',
 'II3': 'Missing output conventions',
 'II4': 'Inadequate / erroneous clarification',
}
ZH = {
 'I1': '任务理解与分析方案错误', 'I2': '数据选择与解释错误',
 'I3': '数据处理与算法实现错误', 'I4': 'API、执行与修复失败',
 'I5': '指令落实与结果交付错误', 'I6': '求解流程失效',
 'II1': '任务口径与必要信息缺失或歧义', 'II3': '输出约定缺失',
 'II4': '澄清信息不充分、错误或矛盾',
}
DATASET_NAMES = {
 'DEPS_DEV_V1': 'Deps.dev', 'GITHUB_REPOS': 'GitHub Repos',
 'PANCANCER_ATLAS': 'PanCancer Atlas', 'PATENTS': 'Patents',
 'agnews': 'AG News', 'bookreview': 'Book Review',
 'civic_unstructured': 'Civic Unstructured', 'crmarenapro': 'CRMArena-Pro',
 'cve': 'CVE', 'googlelocal': 'Google Local', 'imdb': 'IMDb',
 'krama': 'Krama', 'music_brainz_20k': 'MusicBrainz',
 'stockindex': 'Stock Index', 'stockmarket': 'Stock Market',
 'usaspending': 'USAspending', 'yelp': 'Yelp',
}
# Semantics, not arbitrary per-figure colors. Heatmaps use an independent
# sequential scale because color there encodes a rate rather than a class.
PALETTE = {'I': '#326A8A', 'II': '#DB9154', 'gain': '#277C73',
           'loss': '#C66C3A', 'same': '#BCC3CB', 'changed': '#786D9C'}
FONT = 'Arial'
font_manager.findfont(FONT, fallback_to_default=False)
plt.rcParams.update({
 'font.family': FONT, 'font.size': 8.5, 'axes.labelsize': 8.5,
 'axes.titlesize': 10, 'axes.titleweight': 'normal', 'axes.linewidth': 0.65,
 'xtick.labelsize': 8, 'ytick.labelsize': 8.5, 'xtick.major.width': 0.6,
 'ytick.major.width': 0.6, 'text.color': '#222222', 'axes.labelcolor': '#222222',
 'xtick.color': '#444444', 'ytick.color': '#444444',
 'pdf.fonttype': 42, 'ps.fonttype': 42, 'svg.fonttype': 'none',
 'savefig.facecolor': 'white', 'figure.facecolor': 'white',
 'savefig.dpi': 400, 'axes.unicode_minus': False,
})
HEAT = colors.LinearSegmentedColormap.from_list('dab_blue', ['#F6F8FA', '#CCE0EB', '#73A6C2', '#245B7B'])
EXPECTED = {
 'annotations': 'ef5efa9d56a825eb9fd5822d2af9d58542e51144f8ab3810b95a63bf4f048a86',
 'effective_index': '6058b7d4e6772e0f743aa4bf8910e58fa1f44ac72fd7883182a2b9bd8bf97a55',
 'taxonomy': '0568bcf9788ba0d1cdf900ad8205456c4bbb3dacac29832917ce9402cd67eed7',
}

def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def write(name, obj):
    (OUT / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def clean(ax):
    for side in ['top', 'right', 'left']:
        ax.spines[side].set_visible(False)
    ax.tick_params(axis='y', length=0)
    ax.set_axisbelow(True)

def save(fig, name):
    # No tight crop: dimensions and typography remain invariant across exports.
    fig.canvas.draw()
    for ext in ['pdf', 'svg', 'png']:
        fig.savefig(OUT / f'{name}.{ext}')
    plt.close(fig)

def matrix_cells(ax, matrix, vmax, rowlabels, fontsize=8, gaps=()):
    image = ax.imshow(matrix, cmap=HEAT, vmin=0, vmax=vmax, aspect='auto', interpolation='nearest')
    ax.set_xticks(range(9), CLASSES)
    ax.set_yticks(range(len(rowlabels)), rowlabels)
    ax.tick_params(length=0, pad=5)
    ax.set_xticks(np.arange(-.5, 9, 1), minor=True)
    ax.set_yticks(np.arange(-.5, len(rowlabels), 1), minor=True)
    ax.grid(which='minor', color='white', linewidth=.65)
    ax.tick_params(which='minor', length=0)
    for s in ax.spines.values(): s.set_visible(False)
    for y in gaps: ax.axhline(y, color='white', linewidth=3)
    ax.axvline(5.5, color='white', linewidth=3)
    for (i,j), v in np.ndenumerate(matrix):
        ax.text(j,i, f'{v:.1f}' if v else '0', ha='center', va='center',
                fontsize=fontsize, color='white' if v > .66*vmax else '#23323D')
    return image

def main():
    inputs = read(BASE / 'current-analysis-input.json')
    paths = {'effective_index': inputs['effective_run_index'],
             'annotations': inputs['current_root_annotations'], 'taxonomy': inputs['classification_spec']}
    hashes = {k:sha(p) for k,p in paths.items()}
    assert hashes == EXPECTED, ('Frozen input changed; inspect before regenerating', hashes)
    original = read(paths['effective_index'])['records']
    annotations = read(paths['annotations'])['records']
    annotation_map = {r['sample_id']:r for r in annotations}
    assert len(annotation_map) == len(annotations) == 1803
    assert len(original) == len({r['sample_id'] for r in original}) == 4992
    records = []
    for r in original:
        x = {k:r[k] for k in ['sample_id','model','mode','dataset','task','backend','passed',
                              'result_path','result_sha256','actual_generation_timeout_seconds','effective_source_kind']}
        x['subclass'] = None
        if not r['passed']:
            a = annotation_map[r['sample_id']]
            for k in ['model','mode','dataset','task','backend','result_path','result_sha256']:
                assert r[k] == a[k], (r['sample_id'],k)
            x['subclass'] = a['subclass']
            assert x['subclass'] in CLASSES
        records.append(x)
    fail = [x for x in records if not x['passed']]
    counts = Counter(r['subclass'] for r in fail)
    assert len(fail)==1801 and counts == dict(zip(CLASSES,[96,146,695,9,26,213,593,12,11]))
    tasks = {(r['dataset'],r['task']) for r in records}
    assert len(tasks)==104
    for m in MODELS:
        for mode in MODES:
            for backend in ['pandas','polars','ibis','pyspark']:
                sub = [r for r in records if (r['model'],r['mode'],r['backend'])==(m,mode,backend)]
                assert len(sub)==104 and {(r['dataset'],r['task']) for r in sub}==tasks

    # This compact copy is a sufficient reproduction input, with provenance.
    write('plot-input-records.json', {'schema_version':1, 'sources':paths, 'source_sha256':hashes,
                                   'blind_review_labels_overrode_primary_annotations':False, 'records':records})
    stats = {'total_runs':4992,'pass':3191,'fail':1801,'tasks':104,
             'classes':CLASSES,'class_names':ZH,'counts':dict(counts),
             'model_mode':[], 'paired':[], 'dataset':[], 'sensitivity':[]}

    # Fig. 1: failure composition (the only main figure with failure denominator).
    fig = plt.figure(figsize=(7.2,3.7))
    ax=fig.add_axes([.405,.23,.46,.62])
    y=np.arange(9)
    ax.barh(y,[counts[c] for c in CLASSES],height=.66,
            color=[PALETTE['II' if c.startswith('II') else 'I'] for c in CLASSES])
    ax.set_yticks(y,[f'{c}  {SHORT[c]}' for c in CLASSES],fontsize=8.2)
    ax.invert_yaxis(); ax.set_xlim(0,840); ax.set_xticks([0,200,400,600,800])
    ax.set_xlabel('Number of failed runs'); ax.grid(axis='x',color='#E3E6E9',linewidth=.6);clean(ax)
    ax.axhline(5.5,color='#D5DADD',linewidth=.7)
    for i,c in enumerate(CLASSES):
        ax.text(counts[c]+12,i,f'{counts[c]} ({100*counts[c]/1801:.1f}%)',va='center',fontsize=8.3)
    fig.text(.04,.94,'Failure composition',fontsize=11,weight='bold')
    fig.text(.04,.885,'1,801 failed runs; one primary category per failure',fontsize=8.5,color='#555555')
    fig.legend(handles=[Patch(color=PALETTE['I'],label='I: Agent-side'),Patch(color=PALETTE['II'],label='II: Task / information-side')],
               loc='lower center',bbox_to_anchor=(.52,.012),ncol=2,frameon=False,fontsize=8)
    save(fig,'fig1_error_distribution')

    # Fig. 2: all-run rates, with pass rates kept on a different scale.
    heat=[]; passed=[]; labels=[]
    for m in MODELS:
        for mode in MODES:
            sub=[r for r in records if r['model']==m and r['mode']==mode]
            cc=Counter(r['subclass'] for r in sub if not r['passed']); pp=sum(r['passed'] for r in sub)
            assert len(sub)==416 and pp+sum(cc.values())==416
            heat.append([100*cc[c]/416 for c in CLASSES]); passed.append(100*pp/416)
            labels.append(f'{MODEL_NAMES[m]}  {mode.capitalize()}')
            stats['model_mode'].append({'model':m,'mode':mode,'n':416,'pass':pp,'counts':dict(cc)})
    heat=np.array(heat); vmax=60  # Shared rate-to-color mapping across both heatmaps.
    fig=plt.figure(figsize=(7.2,5.2))
    ax=fig.add_axes([.235,.20,.61,.68]); im=matrix_cells(ax,heat,vmax,labels,gaps=[2.5,5.5,8.5])
    pa=fig.add_axes([.875,.20,.075,.68]); pa.imshow(np.array(passed)[:,None],cmap='Greens',vmin=0,vmax=100,aspect='auto')
    pa.set_xticks([0],['Pass']);pa.set_yticks([]);pa.tick_params(length=0,pad=5)
    for s in pa.spines.values():s.set_visible(False)
    for i,p in enumerate(passed):pa.text(0,i,f'{p:.1f}',ha='center',va='center',fontsize=8,color='white' if p>60 else '#222222')
    for yline in [2.5,5.5,8.5]:pa.axhline(yline,color='white',linewidth=3)
    fig.text(.235,.955,'Error incidence by model and mode',fontsize=11,weight='bold')
    fig.text(.235,.91,'Cell = category failures / 416 runs (%)',fontsize=8.5,color='#555555')
    ca=fig.add_axes([.235,.085,.61,.025]);cb=fig.colorbar(im,cax=ca,orientation='horizontal');cb.set_label('Category failure rate (%)',labelpad=2);cb.outline.set_visible(False)
    fig.text(.915,.115,'Pass rate (%)\n0-100 scale',ha='center',fontsize=7,color='#555555')
    save(fig,'fig2_model_mode_heatmap')

    # Full paired states include Pass plus every failure class.
    by_key={(r['model'],r['mode'],r['dataset'],r['task'],r['backend']):r for r in records}
    states=['Pass']+CLASSES
    for target in ['clarified','interact']:
        for m in MODELS:
            transitions=Counter(); modeset=[r for r in records if r['model']==m and r['mode']=='direct']
            for r in modeset:
                z=by_key[(m,target,r['dataset'],r['task'],r['backend'])]
                a='Pass' if r['passed'] else r['subclass']; b='Pass' if z['passed'] else z['subclass']
                transitions[(a,b)]+=1
            gain=sum(n for (a,b),n in transitions.items() if a!='Pass' and b=='Pass')
            loss=sum(n for (a,b),n in transitions.items() if a=='Pass' and b!='Pass')
            same=sum(n for (a,b),n in transitions.items() if a==b and a!='Pass')
            changed=sum(n for (a,b),n in transitions.items() if a!=b and a!='Pass' and b!='Pass')
            pp=transitions[('Pass','Pass')]
            assert gain+loss+same+changed+pp==416
            stats['paired'].append({'model':m,'target':target,'n':416,'fail_to_pass':gain,'pass_to_fail':loss,
                'net_pass_change':gain-loss,'fail_same_class':same,'fail_changed_class':changed,'pass_to_pass':pp,
                'state_order':states,'transition_counts':[[transitions[(a,b)] for b in states] for a in states]})
    fig=plt.figure(figsize=(7.2,5.7))
    for row,target in enumerate(['clarified','interact']):
        bottom=.55 if row==0 else .145
        left=fig.add_axes([.14,bottom,.42,.245]); right=fig.add_axes([.67,bottom,.26,.245])
        group=[p for p in stats['paired'] if p['target']==target]
        gain=np.array([p['fail_to_pass'] for p in group]);loss=np.array([p['pass_to_fail'] for p in group])
        same=np.array([p['fail_same_class'] for p in group]);changed=np.array([p['fail_changed_class'] for p in group])
        yy=np.arange(4)
        left.barh(yy,gain,height=.61,color=PALETTE['gain']);left.barh(yy,-loss,height=.61,color=PALETTE['loss'])
        left.set_yticks(yy,[MODEL_NAMES[m] for m in MODELS]);left.set_xlim(-62,120);left.set_ylim(3.65,-.65)
        left.set_xticks([-50,0,50,100],['50','0','50','100']);left.axvline(0,color='#555555',linewidth=.7)
        clean(left);left.grid(axis='x',color='#E5E8EB',linewidth=.55)
        left.set_title(f'({"a" if row==0 else "c"}) Direct to {target.capitalize()}',loc='left',pad=13)
        for i,p in enumerate(group):
            left.text(-loss[i]-3,i,str(loss[i]),ha='right',va='center',fontsize=8)
            left.text(gain[i]+3,i,str(gain[i]),ha='left',va='center',fontsize=8)
            left.text(117,i,f'{p["net_pass_change"]:+d}',ha='right',va='center',fontsize=8,weight='bold')
        left.text(.98,1.025,'Net',transform=left.transAxes,ha='right',fontsize=7.8)
        left.set_xlabel('Regressions  |  Improvements (paired runs)',labelpad=4)
        right.barh(yy,same,height=.61,color=PALETTE['same']);right.barh(yy,changed,left=same,height=.61,color=PALETTE['changed'])
        right.set_yticks([]);right.set_ylim(3.65,-.65);right.set_xlim(0,165);right.set_xticks([0,50,100,150]);clean(right)
        right.grid(axis='x',color='#E5E8EB',linewidth=.55)
        right.set_title(f'({"b" if row==0 else "d"}) Failed in both modes',loc='left',pad=13)
        for i,p in enumerate(group):
            if same[i]:right.text(same[i]/2,i,str(same[i]),ha='center',va='center',fontsize=8)
            if changed[i]:right.text(same[i]+changed[i]/2,i,str(changed[i]),ha='center',va='center',fontsize=8,color='white')
        right.set_xlabel('Same / changed primary category',labelpad=4)
    fig.text(.04,.965,'Paired outcome changes',fontsize=11,weight='bold')
    fig.text(.04,.925,'416 matched task-backend pairs per model and comparison',fontsize=8.5,color='#555555')
    handles=[Patch(color=PALETTE[k],label=lab) for k,lab in [('loss','Pass to fail'),('gain','Fail to pass'),('same','Fail: same class'),('changed','Fail: changed class')]]
    fig.legend(handles=handles,loc='lower center',bbox_to_anchor=(.51,.018),ncol=4,frameon=False,fontsize=7.8,columnspacing=1.5)
    save(fig,'fig3_paired_transitions')

    # Fig. 4: dataset denominators are tasks * 48, not fixed across datasets.
    ds_order=sorted({r['dataset'] for r in records},key=lambda x:DATASET_NAMES[x].lower())
    matrix=[]; dslabels=[]
    for ds in ds_order:
        sub=[r for r in records if r['dataset']==ds];nt=len({r['task'] for r in sub});N=len(sub)
        assert N==48*nt
        cc=Counter(r['subclass'] for r in sub if not r['passed'])
        matrix.append([100*cc[c]/N for c in CLASSES])
        dslabels.append(f'{DATASET_NAMES[ds]}  ({nt}; {N})')
        stats['dataset'].append({'dataset':ds,'tasks':nt,'n':N,'pass':sum(r['passed'] for r in sub),'counts':dict(cc)})
    matrix=np.array(matrix);vmax=60
    fig=plt.figure(figsize=(7.2,6.35))
    ax=fig.add_axes([.30,.17,.65,.715]);im=matrix_cells(ax,matrix,vmax,dslabels,fontsize=8)
    fig.text(.04,.96,'Error incidence by dataset',fontsize=11,weight='bold')
    fig.text(.04,.92,'Row labels: dataset (tasks; runs). Cell = category failures / all dataset runs (%)',fontsize=8.2,color='#555555')
    ca=fig.add_axes([.30,.075,.65,.022]);cb=fig.colorbar(im,cax=ca,orientation='horizontal');cb.set_label('Category failure rate (%)',labelpad=2);cb.outline.set_visible(False)
    save(fig,'fig4_dataset_heatmap')

    # Sensitivity: descriptive weights only, not confidence intervals.
    def summarize_weighted(name, chosen, equal_dataset=False):
        if equal_dataset:
            dslist=sorted({r['dataset'] for r in chosen});cw={c:0. for c in CLASSES};pw=0.
            for ds in dslist:
                sub=[r for r in chosen if r['dataset']==ds];co=Counter(r['subclass'] for r in sub if not r['passed'])
                for c in CLASSES:cw[c]+=co[c]/len(sub)/len(dslist)
                pw+=sum(r['passed'] for r in sub)/len(sub)/len(dslist)
        else:
            co=Counter(r['subclass'] for r in chosen if not r['passed']);cw={c:co[c]/len(chosen) for c in CLASSES}
            pw=sum(r['passed'] for r in chosen)/len(chosen)
        assert abs(pw+sum(cw.values())-1)<1e-12
        return {'name':name,'runs':len(chosen),'datasets':len({r['dataset'] for r in chosen}),
                'tasks':len({(r['dataset'],r['task']) for r in chosen}), 'pass_rate_pct':100*pw,
                'category_incidence_pct':{c:100*cw[c] for c in CLASSES},
                'composition_among_failures_pct':{c:100*cw[c]/(1-pw) for c in CLASSES}}
    stats['sensitivity'].append(summarize_weighted('All runs (also task-equal: 48 runs/task)',records))
    stats['sensitivity'].append(summarize_weighted('Dataset-equal',records,True))
    for exclude in [{'cve'},{'civic_unstructured'},{'cve','civic_unstructured'}]:
        chosen=[r for r in records if r['dataset'] not in exclude]
        stats['sensitivity'].append(summarize_weighted('Exclude '+', '.join(sorted(exclude)),chosen))
    stats['concentration']={'I6_cve':counts['I6'] and sum(r['subclass']=='I6' and r['dataset']=='cve' for r in fail),
                            'II1_civic_unstructured':sum(r['subclass']=='II1' and r['dataset']=='civic_unstructured' for r in fail)}
    write('figure-data.json',stats)
    write('validation.json', {'created_at':datetime.now(timezone.utc).isoformat(),'all_checks_passed':True,
           'source_sha256':hashes,'source_hashes_unchanged_after_render':hashes=={k:sha(p) for k,p in paths.items()},
           'unique_effective_runs':4992,'unique_tasks':104,'datasets':17,'effective_failures':1801,
           'annotation_records':1803,'excluded_historical_passes':2,'label_join_mismatches':0,
           'matched_pairs_per_model_and_comparison':416,'blind_review_labels_overrode_primary_annotations':False,
           'actual_budget_seconds':dict(Counter(str(r['actual_generation_timeout_seconds']) for r in records)),
           'source_kinds':dict(Counter(r['effective_source_kind'] for r in records)),
           'font':FONT,'font_path':font_manager.findfont(FONT,fallback_to_default=False),
           'png_dpi':400,'pdf_embedded_font_type':42,'svg_text_editable':True,
           'inference':'Descriptive census only; no independence assumption or significance claims',
           'script_sha256':sha(__file__),'matplotlib_version':matplotlib.__version__})
    print(json.dumps({'outputs':4,'runs':4992,'failures':1801,'source_hashes_unchanged':True,'out':str(OUT)}))

if __name__=='__main__': main()

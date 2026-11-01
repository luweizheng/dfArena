"""Run from anywhere: python make_publication_figures.py --bundle /path/to/bundle."""
import argparse,json,collections
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

ap=argparse.ArgumentParser();ap.add_argument('--bundle',type=Path,required=True);args=ap.parse_args()
B=args.bundle;F=B/'02_figures';F.mkdir(exist_ok=True)
D=json.loads((B/'01_data/figure-data.json').read_text(encoding='utf-8'))
R=D['records'];H=D['annotations']
MODELS=['gpt6','kimi','glm'];NAMES=['GPT-6','Kimi','GLM'];MODES=['direct','clarified','interact'];MN=['Direct','Clarified','Interact']
CODES=['I1','I2','I3','I4','I5','I6','II1','II3','II4']
CN=['Task interpretation / planning','Data selection / interpretation','Data processing / algorithms','API / execution / repair','Instruction / delivery','Unfinished solution process','Missing / ambiguous task rules','Missing output conventions','Unreliable clarification']
COL=['#0072B2','#D55E00','#009E73'];CLASSCOL=['#0072B2','#D55E00']
plt.rcParams.update({'font.family':'Arial','font.size':9,'axes.titlesize':10,'axes.labelsize':9,'xtick.labelsize':9,'ytick.labelsize':9,'legend.fontsize':9,'axes.linewidth':.65,'lines.linewidth':1.2,'pdf.fonttype':42,'ps.fonttype':42,'svg.fonttype':'none','savefig.facecolor':'white','axes.spines.top':False,'axes.spines.right':False})
def save(fig,name):
 for ext in ['pdf','svg','png']:fig.savefig(F/(name+'.'+ext),dpi=600 if ext=='png' else 150)
 plt.close(fig)
def rows(model,mode):return [r for r in R if r['model']==model and r['mode']==mode]
def title(ax,letter,text):ax.set_title(text,loc='left',pad=12);ax.text(-.13,1.06,letter,transform=ax.transAxes,fontweight='bold',fontsize=11)
aggregates={}

# Figure 1. Complete benchmark success rates, common zero-baseline axes.
fig,axs=plt.subplots(1,3,figsize=(7.2,3.25));fig.subplots_adjust(left=.085,right=.98,bottom=.23,top=.85,wspace=.27)
for j,(model,name,ax) in enumerate(zip(MODELS,NAMES,axs)):
 ns=[sum(r['passed'] is True for r in rows(model,m)) for m in MODES];ys=np.array(ns)/1180*100
 ax.plot(range(3),ys,color='#777777',zorder=1)
 for i,(y,n) in enumerate(zip(ys,ns)):
  ax.scatter(i,y,s=38,c=COL[i],marker=['o','s','^'][i],zorder=3)
  ax.annotate(f'{y:.1f}%',(i,y),xytext=(0,10 if y<90 else -20),textcoords='offset points',ha='center',fontsize=9)
 ax.set(xlim=(-.35,2.35),ylim=(0,105),xticks=range(3),xticklabels=MN,yticks=[0,25,50,75,100]);ax.tick_params(axis='x',rotation=25)
 if j==0:ax.set_ylabel('Pass rate (%)')
 title(ax,chr(97+j),name);aggregates[model]={'pass_counts':dict(zip(MODES,ns))}
fig.text(.085,.025,'295 tasks × 4 backends per model–mode; complete benchmark counts.',fontsize=9)
save(fig,'fig1_success_rates')

# Figure 2. Population taxonomy, and within-failure broad-class composition.
counts=collections.Counter(r['subclass'] for r in R if not r['passed'])
order=sorted(range(9),key=lambda i:(-counts[CODES[i]],i))
fig=plt.figure(figsize=(7.2,4.75));gs=fig.add_gridspec(1,2,width_ratios=[1.5,1],left=.06,right=.97,top=.86,bottom=.18,wspace=.56)
a=fig.add_subplot(gs[0]);b=fig.add_subplot(gs[1])
y=np.arange(9)
a.barh(y,[counts[CODES[i]] for i in order],height=.65,color=[CLASSCOL[int(CODES[i].startswith('II'))] for i in order])
a.set(yticks=y,yticklabels=[CODES[i] for i in order],xlim=(0,1800),xticks=[0,500,1000,1500]);a.invert_yaxis();a.set_xlabel('Failed runs (count)')
for yy,i in enumerate(order):a.text(counts[CODES[i]]+22,yy,f'{counts[CODES[i]]:,}  ({counts[CODES[i]]/3424*100:.1f}%)',va='center',fontsize=9)
title(a,'a','Failure categories (N = 3,424)')
group_labels=[];totals=[]
for model,name in zip(MODELS,NAMES):
 for mode,mn in zip(MODES,MN):
  rr=[r for r in rows(model,mode) if not r['passed']];n=len(rr);k=sum(not r['subclass'].startswith('II') for r in rr);yy=len(totals)
  b.barh(yy,k/n*100,color=CLASSCOL[0],height=.65);b.barh(yy,100-k/n*100,left=k/n*100,color=CLASSCOL[1],height=.65)
  b.text(103,yy,str(n),va='center',fontsize=9);group_labels.append(name+' '+mn[0]);totals.append(n)
b.set(yticks=range(9),yticklabels=group_labels,xlim=(0,123),xticks=[0,50,100]);b.invert_yaxis();b.set_xlabel('Share within failures (%)');b.text(103,-.85,'n',fontsize=9)
title(b,'b','Broad classes by condition')
fig.legend(handles=[Patch(color=CLASSCOL[0],label='I · Capability / execution'),Patch(color=CLASSCOL[1],label='II · Information / clarification')],loc='lower center',bbox_to_anchor=(.5,.045),ncol=2,frameon=False)
fig.text(.06,.015,'D / C / I = Direct / Clarified / Interact. All nine categories are retained.',fontsize=9)
save(fig,'fig2_failure_taxonomy')

# Figure 3. Exact paired transitions, without treating backends as independent replicates.
fig,axs=plt.subplots(1,2,figsize=(7.2,3.15));fig.subplots_adjust(left=.1,right=.90,top=.77,bottom=.28,wspace=.65)
paired=[]
for j,(mode,ax) in enumerate(zip(MODES[1:],axs)):
 for y,(model,name) in enumerate(zip(MODELS,NAMES)):
  direct={(r['case'],r['backend']):r['passed'] is True for r in rows(model,'direct')};other={(r['case'],r['backend']):r['passed'] is True for r in rows(model,mode)};assert direct.keys()==other.keys()
  gain=sum(not direct[k] and other[k] for k in direct);loss=sum(direct[k] and not other[k] for k in direct)
  ax.barh(y,gain,color=COL[2],height=.5);ax.barh(y,-loss,color=COL[1],height=.5)
  ax.text(gain+8,y,str(gain),va='center');ax.text(-loss/2,y+.38,str(loss),ha='center',va='center')
  ax.text(1.10,y,f'+{gain-loss}',va='center',ha='center',transform=ax.get_yaxis_transform())
  paired.append({'model':model,'comparison':mode+' - direct','n':1180,'fail_to_pass':gain,'pass_to_fail':loss,'net':gain-loss,'both_pass':sum(direct[k] and other[k] for k in direct),'both_fail':sum(not direct[k] and not other[k] for k in direct)})
 ax.axvline(0,color='#333333',linewidth=.6);ax.set(xlim=(-110,650),xticks=[0,200,400,600],yticks=range(3),yticklabels=NAMES,ylim=(2.6,-.7));ax.set_xlabel('Paired runs (count)');ax.text(1.10,-.7,'Net',ha='center',transform=ax.get_yaxis_transform())
 title(ax,chr(97+j),MN[j+1]+' versus Direct')
fig.legend(handles=[Patch(color=COL[2],label='Fail → pass'),Patch(color=COL[1],label='Pass → fail')],loc='lower center',bbox_to_anchor=(.5,.10),ncol=2,frameon=False)
fig.text(.1,.025,'Same task and backend; 1,180 pairs per comparison. Net = gains − losses.',fontsize=9)
save(fig,'fig3_paired_changes')

# Supplementary 1. All four backend rates.
backs=['pandas','polars','ibis','pyspark'];row_names=[];vals=[];nums=[]
for model,name in zip(MODELS,NAMES):
 for mode,mn in zip(MODES,MN):
  rr=rows(model,mode);nn=[sum(r['passed'] is True for r in rr if r['backend']==b) for b in backs]
  assert all(sum(r['backend']==b for r in rr)==295 for b in backs)
  nums.append(nn);vals.append(np.array(nn)/295*100);row_names.append(name+' / '+mn)
fig,ax=plt.subplots(figsize=(7.2,4.8));fig.subplots_adjust(left=.25,right=.85,bottom=.13,top=.91)
im=ax.pcolormesh(np.arange(5)-.5,np.arange(10)-.5,vals,vmin=0,vmax=100,cmap='Blues',shading='flat',rasterized=False);ax.set_ylim(8.5,-.5)
for y in range(9):
 for x in range(4):ax.text(x,y,f'{vals[y][x]:.1f}%\n{nums[y][x]}/295',ha='center',va='center',color='white' if vals[y][x]>65 else '#111111',fontsize=9)
ax.set(xticks=range(4),xticklabels=['pandas','Polars','Ibis','PySpark'],yticks=range(9),yticklabels=row_names)
ax.set_title('Pass rates across computational backends',loc='left',pad=14)
for yy in [2.5,5.5]:ax.axhline(yy,color='white',lw=2)
cax=fig.add_axes([.89,.2,.018,.62]);cb=fig.colorbar(im,cax=cax,label='Pass rate (%)');cb.solids.set_rasterized(False);save(fig,'figS1_backend_rates')

# Supplementary 2. Category incidence out of ALL runs, common denominator.
arr=[]
for model in MODELS:
 for mode in MODES:
  c=collections.Counter(r['subclass'] for r in rows(model,mode));arr.append([c[k]/1180*100 for k in CODES])
arr=np.array(arr);fig,ax=plt.subplots(figsize=(7.2,4.6));fig.subplots_adjust(left=.25,right=.88,bottom=.17,top=.9)
im=ax.pcolormesh(np.arange(10)-.5,np.arange(10)-.5,arr,vmin=0,vmax=35,cmap='Blues',shading='flat',rasterized=False);ax.set_ylim(8.5,-.5)
for y in range(9):
 for x in range(9):
  if arr[y,x]>0:ax.text(x,y,f'{arr[y,x]:.1f}',ha='center',va='center',color='white' if arr[y,x]>22 else '#111111',fontsize=9)
ax.set(xticks=range(9),xticklabels=CODES,yticks=range(9),yticklabels=row_names);ax.set_title('Failure-category incidence among all runs',loc='left',pad=14)
for yy in [2.5,5.5]:ax.axhline(yy,color='white',lw=2)
cax=fig.add_axes([.91,.22,.015,.6]);cb=fig.colorbar(im,cax=cax,label='Incidence (%)');cb.solids.set_rasterized(False)
fig.text(.25,.035,'Each row: n = 1,180. Blank cells = 0; I6 is observed zero.',fontsize=9);save(fig,'figS2_category_incidence')

# Supplementary 3. Descriptive confusion tables on the original 100-item sample.
fig,axs=plt.subplots(1,2,figsize=(7.2,3.8));fig.subplots_adjust(left=.09,right=.98,top=.78,bottom=.23,wspace=.26)
human_matrices={}
for j,(who,ax) in enumerate(zip(['user','teacher'],axs)):
 mat=np.zeros((9,9),dtype=int)
 for r in H:mat[CODES.index(r['ai']),CODES.index(r[who])]+=1
 human_matrices[who]=mat.tolist();assert mat.sum()==100
 ax.pcolormesh(np.arange(10)-.5,np.arange(10)-.5,mat,cmap='Blues',vmin=0,vmax=31,shading='flat',rasterized=False);ax.set_ylim(8.5,-.5);ax.set_aspect('equal')
 for y in range(9):
  for x in range(9):
   if mat[y,x]:ax.text(x,y,str(mat[y,x]),ha='center',va='center',fontsize=9,color='white' if mat[y,x]>20 else '#111111')
 ax.set(xticks=range(9),xticklabels=CODES,yticks=range(9),yticklabels=CODES,xlabel='Human label');ax.tick_params(axis='both',length=2,pad=3)
 if j==0:ax.set_ylabel('Frozen AI label')
 title(ax,chr(97+j),('User' if j==0 else 'Teacher')+f' vs AI: {np.trace(mat)}/100')
fig.text(.09,.08,'Original stratified sample; latest reported repeat annotations. Counts, not population estimates.',fontsize=9)
fig.text(.09,.03,'Blank cells = 0. Prior review history is retained in the accompanying method record.',fontsize=9)
save(fig,'figS3_annotation_agreement')
(B/'01_data/derived-figure-statistics.json').write_text(json.dumps({'model_mode':aggregates,'paired':paired,'category_counts':dict(counts),'backend_counts':nums,'category_incidence_percent':arr.tolist(),'human_matrices':human_matrices},ensure_ascii=False,indent=2),encoding='utf-8')
print('Exported 6 figures in PDF, editable-text SVG and 600 dpi PNG.')

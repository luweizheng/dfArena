"""Create the Chinese reading copy with the six original vector figures."""
import argparse, json
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pypdf import PdfReader,PdfWriter,Transformation

ap=argparse.ArgumentParser();ap.add_argument('--bundle',type=Path,required=True);ap.add_argument('--cjk-font',default='C:/Windows/Fonts/simsun.ttc');args=ap.parse_args()
B=args.bundle;D=json.loads((B/'01_data/figure-data.json').read_text(encoding='utf-8'));S=json.loads((B/'01_data/derived-figure-statistics.json').read_text(encoding='utf-8'))
pdfmetrics.registerFont(TTFont('Chinese',args.cjk_font,subfontIndex=0))
W,H=A4;M=40;CW=W-2*M
style=ParagraphStyle('body',fontName='Chinese',fontSize=10.5,leading=16,textColor=colors.HexColor('#20252b'),wordWrap='CJK')
en=ParagraphStyle('caption',fontName='Helvetica',fontSize=9,leading=12,textColor=colors.HexColor('#333333'))
temp=B/'07_validation/reading-layout.pdf';c=canvas.Canvas(str(temp),pagesize=A4);c.setTitle('PrepBench - Final results and error analysis');c.setAuthor('PrepBench analysis')
placements=[];page=0
def para(text,y,english=False):
 p=Paragraph(text,en if english else style);w,h=p.wrap(CW,700);p.drawOn(c,M,y-h);return y-h-10
def start(title,sub=''):
 global page
 page+=1;c.setFillColor(colors.HexColor('#1d3557'));c.setFont('Chinese',18);c.drawString(M,H-52,title)
 c.setFillColor(colors.HexColor('#333333'))
 if sub:c.setFont('Helvetica',9);c.drawString(M,H-70,sub)
 c.setStrokeColor(colors.HexColor('#b7c4d2'));c.line(M,H-83,W-M,H-83)
 c.setFont('Helvetica',8);c.drawString(M,25,'PrepBench | Final analysis | 01 November 2026');c.drawRightString(W-M,25,str(page))
 return H-102
def table(data,y,widths=None):
 t=Table([[Paragraph(str(v),style) for v in row] for row in data],colWidths=widths or [CW/len(data[0])]*len(data[0]))
 t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'MIDDLE'),('BACKGROUND',(0,0),(-1,0),colors.HexColor('#edf2f7')),('LINEBELOW',(0,0),(-1,0),.7,colors.HexColor('#243b53')),('LINEBELOW',(0,-1),(-1,-1),.5,colors.HexColor('#8a99aa')),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]))
 w,h=t.wrap(CW,700);t.drawOn(c,M,y-h);return y-h-15
def fig(name,y):
 p=PdfReader(B/'02_figures'/(name+'.pdf')).pages[0];w=float(p.mediabox.width);h=float(p.mediabox.height);scale=CW/w
 placements.append((page-1,name,M,y-h*scale,scale));return y-h*scale-8

y=start('PrepBench 最终结果与错误分析','10,620 evaluated conditions · 3 models · 3 modes · 4 backends')
y=para('完成范围：295题 × 3个模型 × 3种模式 × 4个后端，共10,620条有效结果。评分修正和7条服务满载补跑已纳入最终索引；全部3,424条未通过结果均有一个AI主因类别。',y)
y=table([['指标','最终结果'],['通过','7,196 / 10,620（67.76%）'],['未通过及已归类','3,424 / 10,620（32.24%）'],['未解决环境排除 / 待分类','0 / 0'],['原100条样本：用户 / 老师与AI相同','96 / 100；92 / 100']],y,[CW*.52,CW*.48])
tab=[['模型','Direct','Clarified','Interact']]
for model,name in [('gpt6','GPT-6'),('kimi','Kimi'),('glm','GLM')]:
 ns=S['model_mode'][model]['pass_counts'];tab.append([name]+[f'{ns[m]:,}/1,180<br/>{ns[m]/1180*100:.2f}%' for m in ['direct','clarified','interact']])
y=table(tab,y)
y=para('主要观察：三个模型均为Clarified通过率最高、Interact其次、Direct最低。GPT-6在三种模式中均领先。信息与澄清相关主因占失败的65.13%；能力或执行主因占34.87%。这些是本次固定基准上的描述，不是随机重复运行的估计，也不说明所有失败只有一个可能解释。',y)
y=para('阅读顺序：图1总体表现；图2错误分类；图3配对变化；图S1后端差异；图S2类别发生率；图S3人工标注对照。所有英文图可单独用于论文排版，中文说明和方法记录随包提供。',y)
c.showPage()

y=start('图1 · 三种模式下的通过率','Main figure 1 | Success rates')
y=fig('fig1_success_rates',y)
y=para('Figure 1. Success rates over 295 tasks and four backends for each model-mode condition (n = 1,180). The three panels share the same zero-baseline percentage scale. Points are connected only to aid comparison across modes.',y,True)
y=para('统计口径：每个点包含1,180条运行，使用补跑和评分修正后的有效结果。Direct使用原题；Clarified使用补全要求；Interact允许通过既定模拟用户澄清。模式顺序不表示时间序列或剂量关系。',y)
y=para('结果：GPT-6从Direct的54.83%提高至Clarified的96.02%和Interact的94.92%；Kimi为38.90%、81.95%、68.64%；GLM为35.68%、81.10%、57.80%。总体差异还需结合图3的逐条配对结果理解。',y)
y=para('这是全量基准描述，因此未绘制把四个后端误当独立重复实验的误差线，也未添加显著性星号。未通过包括未成功交付等有效失败；不将这些记录当作缺失数据删除。',y)
c.showPage()

y=start('图2 · 错误类别与两大类构成','Main figure 2 | Failure taxonomy')
y=fig('fig2_failure_taxonomy',y)
y=para('Figure 2. (a) Counts and shares of the nine AI-assigned primary categories among 3,424 failed runs, sorted by frequency. (b) Broad-class composition conditional on failure within each model-mode condition; n gives that condition\'s failure count.',y,True)
y=para('I类：I1任务理解与方案（29）；I2数据选择与解释（63）；I3数据处理与算法（911）；I4接口、执行与修复（5）；I5指令落实与交付（186）；I6求解流程失效（0）。',y)
y=para('II类：II1任务口径与必要信息缺失或歧义（1,270）；II3输出约定缺失（937）；II4澄清信息不充分、错误或矛盾（23）。II2已并入II1，保留原编号。',y)
y=para('图2b的分母是各条件的失败数，而非全部运行。它描述失败内部构成，不能单独解释为某类错误的总体发生风险；图S2给出统一按全部运行计算的发生率。',y)
c.showPage()

y=start('图3 · 同题同后端的改善与退化','Main figure 3 | Paired changes from Direct')
y=fig('fig3_paired_changes',y)
y=para('Figure 3. Matched pass/fail transitions from Direct to Clarified or Interact, pairing on task and backend (1,180 pairs per model and comparison). Positive bars count fail-to-pass changes; negative bars count pass-to-fail changes. The separate Net column reports gains minus losses.',y,True)
tab=[['模型 / 对照','失败→通过','通过→失败','净变化']]
for x in S['paired']:tab.append([x['model'].upper()+' / '+x['comparison'].split(' - ')[0],x['fail_to_pass'],x['pass_to_fail'],f'+{x["net"]}'])
y=table(tab,y,[CW*.43,CW*.19,CW*.19,CW*.19])
y=para('未改变状态的配对也包含在1,180的分母中，完整四种配对计数保存在derived-figure-statistics.json。净变化以运行条数计，不是百分点；没有因总体改善而隐去退化记录。',y)
c.showPage()

y=start('图S1 · 四个计算后端的完整结果','Supplementary figure S1 | Backend breakdown')
y=fig('figS1_backend_rates',y)
y=para('Figure S1. Pass rate and pass count for every model-mode-backend condition. Each cell contains the same 295 tasks; all cells use a shared 0-100% color scale. Backend differences are descriptive and do not establish a backend-specific causal effect.',y,True)
y=para('pandas、Polars、Ibis和PySpark分别展示，避免仅汇总四后端而掩盖实现差异。每格均有百分比与精确通过数，所有格子的分母都是295。',y)
c.showPage()

y=start('图S2 · 九类错误在全部运行中的发生率','Supplementary figure S2 | Unconditional category incidence')
y=fig('figS2_category_incidence',y)
y=para('Figure S2. Percentage of all 1,180 runs in each model-mode condition assigned to each primary failure category. Cells use a shared 0-35% scale. Blank cells denote observed zero, not missing observations; I6 is retained despite having no cases.',y,True)
y=para('每行九类发生率之和等于该条件的未通过率，而不是100%。因此可以跨模型、跨模式直接比较某一类错误的实际发生频率；不要把本图与图2b的条件比例混为一谈。',y)
y=para('类别为AI基于实际题面、允许数据、程序、输出差异与相关真实澄清所作的最可能主因判断。每条失败只计一个主因；竞争机制和证据局限仍保留在完整分类记录中。',y)
c.showPage()

y=start('图S3 · 原100条样本的人工标注对照','Supplementary figure S3 | Annotation agreement')
y=fig('figS3_annotation_agreement',y)
y=para('Figure S3. Confusion matrices comparing the frozen AI labels with the latest reported user and teacher repeat annotations on the original 100-item sample. Rows are AI labels, columns are human labels. Numbers are counts; both panels use the same 0-31 color scale, and blank cells are zero.',y,True)
y=table([['对照','九小类相同','两大类相同'],['用户 vs AI','96 / 100','97 / 100'],['老师 vs AI','92 / 100','97 / 100'],['用户 vs 老师','88 / 100','94 / 100']],y,[CW*.44,CW*.28,CW*.28])
y=para('抽样与来源：100条来自补跑前3,422条已分类失败，按AI小类分层抽样，各层纳入概率不同。这里是未加权的样本一致率，不是全体3,424条标签的准确率；补跑新增两条不进入原100条。',y)
y=para('本图采用用户报告的最后一轮盲标复做结果；此前比较与修改历史随包保留。复做条件未被独立核验，不能将其描述为经验证从未接触AI判定的全新样本。未用人工答案回写AI类别，也未计算Kappa。',y)
c.showPage()

y=start('方法、修正与交付说明','Methods, provenance and reproducibility')
for text in [
'有效范围：全部10,620条正式结果，不包含另一个对话的50题GPT-6/OpenCode harness对照。原始运行、评分与修正链均保留。七条容量异常只替换对应有效选择，没有因普通答错重跑。',
'评分修正：168题允许的ISO UTC时间格式已纳入评分器，指定失败项重新评分后通过。174题完成参考答案修正及重新评分，最终通过与失败数量未变化。详见05_corrections。',
'容量补跑：7条有效补跑获得5条通过、2条失败；270题为II1（未明确Incomplete的快照日期），297题为II3（Couple数字脚注清理约定未明确）。第一次本地Python启动失败发生在模型调用前，单独留档。',
'证据与冻结：01_data包含完整有效索引、3,424条AI归类、绘图数据与汇总；06_evidence按内容哈希保存证据，source-map.json记录原路径与包内路径。04_annotations保留原3,422条冻结AI表、原盲标题包、两份人工答案、抽样概率和过程记录。',
'复现：03_reproducibility提供绘图与阅读版脚本。绘图只读取包内figure-data.json，不调用模型或服务；数据与归类仍以保存的有效索引为准。PDF是矢量图，SVG保留文字，PNG为600 dpi预览。使用双栏宽度；单栏投稿应重新排版，不能简单缩小至难以阅读。',
'图形设计依据：参照Nature的矢量文字、可读性与无障碍配色原则，并采用JMLR图中文字至少9 pt的可读性要求。不同刊物尺寸、字号要求不同；本包是可调整的论文图源，不声称同一版式满足所有期刊。',
]:y=para(text,y)
y=para('Nature Research Figure Guide: <link href="https://research-figure-guide.nature.com/figures/preparing-figures-our-specifications/">Preparing figures - our specifications</link><br/>JMLR: <link href="https://jmlr.org/format/format.html">Instructions for Formatting JMLR Articles, Figures and Tables</link><br/>Guidelines accessed 1 November 2026.',y,True)
c.showPage();c.save()
reader=PdfReader(temp);writer=PdfWriter()
for p in reader.pages:writer.add_page(p)
for ix,name,x,y,s in placements:
 fp=PdfReader(B/'02_figures'/(name+'.pdf')).pages[0];writer.pages[ix].merge_transformed_page(fp,Transformation().scale(s).translate(x,y))
writer.add_metadata({'/Title':'PrepBench final results and error analysis','/Author':'PrepBench analysis'})
with (B/'PrepBench_final_reading_copy.pdf').open('wb') as f:writer.write(f)
print('Built 8-page vector reading copy.')

PrepBench 最终交付包 | 2026-11-01

建议先打开 START_HERE.html 或 PrepBench_final_reading_copy.pdf。
本包为老师复核和论文图表使用的最终分析交付，包含已揭示的AI与人工标签，不是新的空白盲标测试。

最终结果
10,620条有效结果：7,196通过（67.76%），3,424未通过（32.24%）。
全部3,424失败均有AI主因分类，无剩余容量异常排除或待分类。
I类1,194（34.87%）；II类2,230（65.13%）。
用户与AI：96/100；老师与AI：92/100；用户与老师：88/100。
人工结果采用用户报告的最后一轮盲标复做，来源和此前过程分别留存，不修改冻结AI标签。

目录
01_data：10,620条完整有效索引、3,424条归类、绘图数据、分类边界。
02_figures：3张主图与3张补充图；每张PDF（矢量）、SVG（可编辑文字）、PNG（600 dpi）。
03_reproducibility：绘图、阅读版脚本与依赖说明。
04_annotations：原100条样本与老师20条题包、两人标签、原冻结AI、抽样概率及标注来源。
05_corrections：168/174评分修正、重新评分报告和七条容量补跑的审核记录。
06_evidence：全部分类所引用的证据、失败候选输出和有效结果/评分证据；文件按内容哈希去重。
07_validation：数量核对、原始证据哈希核对、绘图统计复算与PDF检查记录。
MANIFEST.sha256：包内文件的SHA256。外部zip的校验值另存。

图形说明
fig1_success_rates：三个模型×三种模式的通过率，统一0-100%坐标。
fig2_failure_taxonomy：九类频数/失败内占比，以及各条件两大类构成。
fig3_paired_changes：同题同后端的失败→通过、通过→失败和净变化。
figS1_backend_rates：9×4后端通过率矩阵，每格295题。
figS2_category_incidence：9×9类别发生率矩阵，每行以全部1,180运行计。
figS3_annotation_agreement：原100条样本的AI-人工混淆矩阵，共用0-31颜色尺度。

统计口径
全量范围是295题×3模型×3模式×4后端，不包含另一个对话的50题harness对照。
只有passed=true算通过；无有效答案等有效未通过记录仍计失败。
一条失败只计一个AI主因。I6=0也保留；II2已并入II1。
图2使用失败分母；图S2使用全部运行分母。不同分母不可混用。
配对键是case+backend，模型内比较；所有1,180对均保留，不仅统计变化对。
无随机重复运行，图表不添加误差线、显著性星号或因果声明。
原100条分层抽自3,422条旧冻结失败，各层纳入概率不同；96%/92%为样本内未加权一致率，不是总体分类准确率。
后续补跑新增两条只加入最终分析分母3,424，不进入旧100条，不重抽、不改人工结果。

证据使用
从START_HERE.html按题号、模型、类别检索；每条有题面、程序、评分等链接。
ai-classification-3424.json中evidence.path与candidate_outputs.path均相对包根目录。
effective-results-10620.json的result/evaluation证据路径已便携化；其他历史绝对路径是来源元数据，不能直接在异机运行。
source-map.json记录每份证据的原路径、包内路径和SHA256，原生内容不修改。
04_annotations内原题包zip保持原样，若要查看原离线界面可另行解压；已完成标注结果在旁边独立JSON中。
不包含订阅认证文件、环境密钥或模型运行环境；本包支持结果复核和绘图复现，不用于直接重跑模型。

设计与导出依据（2026-11-01查阅）
Nature research figure guide: https://research-figure-guide.nature.com/figures/preparing-figures-our-specifications/
JMLR formatting guide: https://jmlr.org/format/format.html
采用Arial、矢量图/可编辑文字、色觉友好配色与9 pt主要标注；主图宽7.2英寸。
不同刊物字号和版芯要求不同；Nature常用更小字号，JMLR要求图中文字至少9 pt。投稿时需按目标模板适配，不能简单缩到单栏。
600 dpi PNG仅为备用；正式排版优先PDF或SVG。

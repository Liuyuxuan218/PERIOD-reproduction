"""Scientific figure and review draft from the audited nine-program dataset."""
import html
import json
import math
from pathlib import Path
import shutil
from reportlab.graphics.shapes import Drawing, String, Line, Circle
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics import renderPDF, renderSVG
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, PageBreak
from pypdf import PdfReader

BASE = Path(__file__).resolve().parents[2]
OUT = BASE / 'outputs/rq3-expanded-20261121'
data = json.loads((OUT / 'results.json').read_text())
dataset = json.loads((OUT / 'workbook-data.json').read_text())
stats = {(s['case'],s['method']):s for s in data['statistics']}
cases,methods = data['cases'],data['methods']
palette = ['#8794A3','#167C80','#386CB0','#A46528','#8C5BA6']
labels = ['CS3','CS4','CS5','CS10','qsort_mt','WSQ','IWSQ','IWSQWS','safestack']

def figure():
    drawing = Drawing(940,420)
    drawing.add(String(65,396,'Runtime slowdown across nine selected programs',fontName='Helvetica-Bold',fontSize=17,fillColor=colors.HexColor('#18232D')))
    drawing.add(String(65,375,'Mean +/- sample SD of 3 paired repetitions; 10 actual launches per method per repetition',fontName='Helvetica',fontSize=11))
    chart = LinePlot(); chart.x=65; chart.y=83; chart.width=835; chart.height=244
    offsets = [-.24,-.12,0,.12,.24]
    chart.data = [[(i+1+offsets[mi],math.log10(stats[case,method]['slowdown_mean'])) for i,case in enumerate(cases)] for mi,method in enumerate(methods)]
    chart.joinedLines=0
    chart.xValueAxis.valueMin=.5;chart.xValueAxis.valueMax=9.5;chart.xValueAxis.valueSteps=list(range(1,10))
    chart.xValueAxis.labelTextFormat=lambda x:labels[int(x)-1]
    chart.yValueAxis.valueMin=-.08;chart.yValueAxis.valueMax=3.08;chart.yValueAxis.valueSteps=[0,1,2,3]
    chart.yValueAxis.labelTextFormat=lambda v:'%gx' % (10**v)
    for axis in (chart.xValueAxis,chart.yValueAxis):
        axis.labels.fontName='Helvetica';axis.labels.fontSize=10;axis.strokeWidth=.6;axis.strokeColor=colors.HexColor('#63717E')
    chart.yValueAxis.visibleGrid=True;chart.yValueAxis.gridStrokeColor=colors.HexColor('#DFE5EA');chart.yValueAxis.gridStrokeWidth=.6
    for mi in range(5): chart.lines[mi].strokeColor=colors.HexColor(palette[mi])
    drawing.add(chart)
    def xy(x,y):return chart.x+(x-.5)/9*chart.width,chart.y+(y+.08)/3.16*chart.height
    for mi,method in enumerate(methods):
        color=colors.HexColor(palette[mi])
        for i,case in enumerate(cases):
            stat=stats[case,method];mean=stat['slowdown_mean'];sd=stat['slowdown_sample_sd']
            assert mean-sd>0 and mean+sd < 10**3.08
            x,y=xy(i+1+offsets[mi],math.log10(mean))
            _,low=xy(i+1+offsets[mi],math.log10(mean-sd));_,high=xy(i+1+offsets[mi],math.log10(mean+sd))
            drawing.add(Line(x,low,x,high,strokeColor=color,strokeWidth=1))
            for yy in (low,high): drawing.add(Line(x-2.8,yy,x+2.8,yy,strokeColor=color,strokeWidth=1))
            drawing.add(Circle(x,y,3.3,fillColor=color,strokeColor=color))
        x=230+mi*108
        drawing.add(Circle(x,349,3.3,fillColor=color,strokeColor=color))
        drawing.add(String(x+10,345.5,method,fontName='Helvetica',fontSize=11))
    for first,last,label in [(1,4,'CS'),(5,5,'Inspect'),(6,8,'Chess'),(9,9,'Misc')]:
        x1,_=xy(first-.35,0);x2,_=xy(last+.35,0)
        drawing.add(Line(x1,53,x2,53,strokeColor=colors.HexColor('#A5AFB9'),strokeWidth=.8))
        drawing.add(String((x1+x2)/2,39,label,textAnchor='middle',fontName='Helvetica',fontSize=10))
    drawing.add(String(65,20,'Logarithmic y-axis. Lower is better. Startup-inclusive child lifetime. Native = 1. No line implies a trend across unrelated programs.',fontName='Helvetica',fontSize=9))
    drawing.add(String(65,7,'1,350 adopted measurements; 4/7 SCTBench families; 57 source-matched assertion outcomes retained. Error bars are SD, not confidence intervals.',fontName='Helvetica',fontSize=9,fillColor=colors.HexColor('#4D5D6B')))
    renderPDF.drawToFile(drawing,str(OUT / 'rq3-nine-programs.pdf'))
    renderSVG.drawToFile(drawing,str(OUT / 'rq3-nine-programs.svg'))
    return drawing

def main():
    drawing=figure()
    fmt=lambda c,m:'%.2f +/- %.2f' % (stats[c,m]['slowdown_mean'],stats[c,m]['slowdown_sample_sd'])
    table=[['Program','PERIOD','IPB','IDB','PCT']]+[[c]+[fmt(c,m) for m in methods[1:]] for c in cases]
    pstats=[s for s in data['statistics'] if s['method']=='PERIOD']
    bstats=[s for s in data['statistics'] if s['method'] in methods[2:]]
    pmin=min(s['slowdown_mean'] for s in pstats);pmax=max(s['slowdown_mean'] for s in pstats)
    bmin=min(s['slowdown_mean'] for s in bstats);bmax=max(s['slowdown_mean'] for s in bstats)
    maximum=max(bstats,key=lambda s:s['slowdown_mean'])
    passed=all(stats[c,'PERIOD']['slowdown_mean']<min(stats[c,m]['slowdown_mean'] for m in methods[2:]) for c in cases)
    assert passed
    scope=('We partially reproduce PERIOD Section 4.4 / Figure 7 using nine SCTBench programs from four families: CS (four reorder variants), Inspect (qsort_mt), Chess (WSQ, IWSQ and IWSQWS), and Misc (safestack). Each program receives Native, PERIOD, IPB, IDB and PCT with ten actual measured launches in each of three repeated sessions. The adopted dataset contains 1,350 children, 135 groups and 27 complete five-method paired blocks. This covers 9/36 SCTBench programs and 4/7 families. No CVE runtime measurements are included.')
    metric=('For each program and session, we average the ten measured child lifetimes and divide each method mean by the Native mean from the same session and batch. We then calculate the arithmetic mean and sample SD of the three paired ratios. The statistical repetition unit is the session, not each child. The three sessions reset profiling/search databases and rotate method order, but share one VM and predetermined PCT seeds. Timing is CLOCK_MONOTONIC child lifetime, including sudo, tool/target startup, target execution, debug output and pipe collection. Compilation, static analysis, profiling, PERIOD discovery, driver startup, schedule generation and driver-side DB parsing are excluded. This is a startup-inclusive metric, not pure steady-state scheduling overhead.')
    finding=('PERIOD has the lowest measured mean among the four CCT methods on all nine selected programs. Its mean slowdowns range from %.2fx to %.2fx Native; IPB/IDB/PCT means range from %.2fx to %.2fx. These descriptive results support the lower-overhead claim within the selected workload and measurement boundary. They do not establish statistical significance, broad benchmark coverage or the paper\'s explanation of the performance difference.' % (pmin,pmax,bmin,bmax))
    assertion=('Fifty-seven source-file/line-matched assertion outcomes remain in the fixed ten-launch groups: eight PERIOD outcomes from the CS batch and 49 outcomes from the added WSQ/IWSQ measurements. Abnormal exits are accepted only under the predefined target-assertion rules; tool errors, unknown abnormal exits and timeouts are rejected. Assertions may shorten executions and methods explore different schedules, so these runtime averages do not establish bug-finding superiority. success-only-sensitivity.csv is descriptive only and must not replace the fixed-budget primary result.')
    repair=('The original five-program run completed 71/75 groups. In IWSQWS session 3, a PERIOD automatic retest consumed the tenth actual launch after nine schedule rounds; the observer rejected the next request. Ten completed child logs were valid, but the driver group was incomplete under the old rule. Before rerunning, the protocol was amended to stop PERIOD normally before an eleventh measured child, only when exactly ten valid children have completed, including retests. A distinct completion reason, unique rounds and retest count are retained. Budget exhaustion is not search-space exhaustion. The rerun replaces all five methods of that paired block with 50 new measurements. The original Native 10 and incomplete PERIOD 10 remain diagnostic evidence and are excluded from the adopted 1,350. The other 14 full blocks from the original batch are unchanged. The replacement PERIOD group returned normally after ten measured rounds with zero retests; its saved completion reason is driver_returned.')
    comparison=('The paper states PERIOD 2-30x and IPB/IDB/PCT 10-500x Native across its evaluated programs. Our PERIOD means lie within that contextual range. Our largest baseline mean is %s on %s: %.2fx, %.2fx (%.2f%%) above the paper\'s 500x upper bound. This is a comparison with an aggregate range endpoint, not a matched per-program discrepancy. Exact Figure 7 per-case values and a fully matched timing boundary were not recovered, so per-case absolute and relative gaps are unavailable. Startup, tool configuration and virtualization are plausible influences but have not been separated by controlled measurements and are not established causes.' % (maximum['method'],maximum['case'],bmax,bmax-500,(bmax/500-1)*100))
    limitations=('The sample is four of seven SCTBench families, with small fixed inputs and only three sessions on one virtualized host. Family diversity is broader than the original four CS cases but is not representative of all programs or bug classes. IWSQWS session 3 is a full replacement sampled later; programs were run in separate batches. Native pairing controls only within the same program/session, and raw seconds must not be pooled across different workloads as equivalent work. No consistent thread-count trend is established by the four CS points. The coarse host-minus-child timing screen found no flags in 135 adopted groups; it cannot establish fine-grained timing precision or exclude host scheduling noise.')
    remaining=('The reduced RQ3 measurement and plotting stage is complete for these nine programs. The group assignment is not complete: the teacher requires a controlled one-factor extension, evidence-based discrepancy analysis and a paper-versus-ours comparison under matched settings. A possible next experiment is budget 5 versus 10 on the same workloads with three new sessions, fixed PCT settings and fresh profiling/search DBs. It has not been run and must not be presented as completed. SWSQ and boundedBuffer remain deferred after their initial execution issues. The team must also confirm author contribution statements, integrate other RQs, prepare portable clean-environment setup/run instructions and review any repository additions. No teammate files, README, commit or push were changed by this analysis.')
    environment_rows=[['Program','Arguments','Workers / total','PCT n / k / d']]+[[e['case'],e['arguments'],str(e['worker_threads'])+' / '+str(e['total_threads']), '%d / %d / %d'%(e['pct_n'],e['pct_k'],e['pct_d'])] for e in dataset['environments']]
    deviations=[['Item','Paper setting','Our setting / reason'],
      ['Scope','SCTBench programs with varied thread counts and all CVE programs for RQ3','Nine selected SCTBench programs, four families; reduced scale.'],
      ['Hardware / system','Intel Xeon Silver 4214 workstation; Ubuntu 18.04','Windows host, VirtualBox 7.2/NEM, 2 vCPU, 2 GB; Ubuntu 14.04 outer VM, Ubuntu 18.04.5 chroot; Linux 3.16.0-77 for legacy PIN and PERIOD compatibility.'],
      ['Compiler / tools','GCC 7.5, LLVM 10.0; compared CCT implementations','Clang 10, -g -O0, non-PIE; PERIOD commit b6f72a7b06d01ffa7114b640312873ec2578a5ea; Maple/PIN 2.12 and protobuf 2.5. Same input bitcode for native and separately instrumented PERIOD.'],
      ['Repetitions / budget','Section 4.1 describes 10 invocations and up to 10,000 schedules; exact Figure 7 timing boundary unspecified','Three sessions, ten actual measured launches including retests; fixed small budget, not exhaustive coverage.'],
      ['Inputs / parameters','Exact matching Figure 7 input/parameter mapping not fully recovered','Explicit small inputs in Table 4. PCT d=3, n includes main. CS k=8*(workers+1)+16; added programs k is next power of two >=max(256,8*smoke steps). Bounds 0-3 for IPB/IDB.'],
      ['Affinity / clock','Fine-grained timing/affinity details not fully matched','kvm-clock and CLOCK_MONOTONIC. Maple fork disables affinity/FIFO calls; passing cpu=0 does not prove CPU pinning.'],
      ['Completion / assertions','Matching Figure 7 stop/abnormal-exit policy not established','Ten actual children per method. Source-matched assertions included. Explicit budget-stop amendment and whole-block replacement for IWSQWS session 3.']]
    timing_rows=[['Batch','Beijing start / end','Elapsed','Adopted groups']]
    for i,s in enumerate(data['source_batches']):
        t=s['timing'];seconds=t['host_elapsed_seconds']
        starts=['Nov 20 20:28:04 - 21:02:03','Nov 20 23:19:04 -Nov 21 00:17:52','Nov 21 07:10:39 - 07:19:05']
        timing_rows.append(['B%d'%(i+1),starts[i],'%dm %.2fs'%(int(seconds//60),seconds%60),s['adopted_groups']])
    refs=('Sources: Wen et al., Controlled Concurrency Testing via Periodical Scheduling, ICSE 2022, Sections 4.1/4.4 and Figure 7, https://wcventure.github.io/pdf/ICSE2022_PERIOD.pdf. CS340 Research Paper Replication assignment supplied by the user. Raw verified evidence archives, archived scripts and manifests are indexed by SHA256 in this package.')
    mdtable=lambda rows:'\n'.join(['| '+' | '.join(map(str,rows[0]))+' |','| '+' | '.join('---' for _ in rows[0])+' |']+['| '+' | '.join(map(str,row))+' |' for row in rows[1:]])
    times=[['Program']+methods]+[[c]+['%.6f'%stats[c,m]['time_mean_seconds'] for m in methods] for c in cases]
    md=['# RQ3 runtime comparison: nine-program review draft','', '## Scope and metric','',scope,'',metric,'', '## Results','', 'Table 1. Paired slowdown mean +/- sample SD, n=3 sessions.','',mdtable(table),'',finding,'',assertion,'', '![Figure 1. Runtime slowdown](rq3-nine-programs.png)','', 'Figure 1. Logarithmic axis; categorical program spacing. Error bars are mean +/- sample SD, not confidence intervals.','', 'Table 2. Mean child lifetime (seconds), averaged over three session means.','',mdtable(times),'', '## Setup and deviations','','Table 3. Setup and deviations.','',mdtable(deviations),'','Table 4. Explicit inputs and PCT settings.','',mdtable(environment_rows),'', '## Repair, timing and traceability','',repair,'','Table 5. Formal command durations.','',mdtable(timing_rows),'', 'The sum of the three formal command durations is %.2f seconds (101min13.18s), including setup/export and diagnostic work in the incomplete batch. It is not the sum of only the1,350 timed child lifetimes and excludes earlier environment setup.'%data['formal_batch_elapsed_seconds'],'']
    md.extend(['Each selected measurement maps to a source batch and an archive-relative child log in measurements-1350.csv. Full command lines and per-launch classification are retained in merged-records.json. Source manifests and archive hashes are retained separately.','', '## Paper comparison and claim verdicts','',comparison,'','Table 6. Claim verdicts.','',mdtable([['Claim','Verdict'],['Lower PERIOD runtime cost','Supported descriptively on all 9 selected cases; full claim partially reproduced.'],['Exact Figure 7 values','Inconclusive without matched per-case reference data and timing.'],['More threads reduce slowdown','Not established by the CS subset.'],['Better bug-finding performance','Not tested by this runtime experiment.']]),'',limitations,'','## Remaining assignment work','',remaining,'','## Contribution and AI-use statement (draft)','', 'The operator launched the experiments and supplied console output. Codex assisted script preparation, debugging, raw-log auditing, aggregation, figures and this draft. The team must confirm individual authorship and review the interpretation before integrating the report.','', '## Conclusion','', 'PERIOD has lower observed startup-inclusive runtime cost than IPB, IDB and PCT on the nine selected programs; the broader paper claim is partially reproduced.','',refs,''])
    (OUT/'RQ3-report-draft.md').write_text('\n'.join(md),encoding='utf-8')
    styles=getSampleStyleSheet()
    styles.add(ParagraphStyle(name='BodyRQ',fontName='Helvetica',fontSize=9,leading=12.2,spaceAfter=8))
    styles.add(ParagraphStyle(name='SmallRQ',fontName='Helvetica',fontSize=8,leading=10.5,spaceAfter=6))
    doc=SimpleDocTemplate(str(OUT/'RQ3-report-draft.pdf'),pagesize=A4,leftMargin=38,rightMargin=38,topMargin=36,bottomMargin=38)
    story=[]
    def p(text,style='BodyRQ'):story.append(Paragraph(html.escape(text),styles[style]))
    def heading(text):p(text,'Heading2')
    def tab(rows,widths):
        tbl=Table([[Paragraph(html.escape(str(cell)),styles['SmallRQ']) for cell in row] for row in rows],colWidths=widths,repeatRows=1,hAlign='LEFT')
        tbl.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#DFE8EF')),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5),('LINEBELOW',(0,0),(-1,0),.6,colors.HexColor('#253C53'))]));story.extend([tbl,Spacer(1,9)])
    p('RQ3 runtime comparison','Title');p('Nine-program review draft - 21 November 2026','SmallRQ')
    heading('Scope and measurement');p(scope);p(metric)
    heading('Table 1. Slowdown relative to Native');tab(table,[120,99,99,99,102])
    p('Mean +/- sample SD of three paired session ratios. Each session contains ten actual launches. Native=1.','SmallRQ');p(finding)
    story.append(PageBreak());heading('Figure 1. Runtime slowdown across selected programs')
    drawing.scale(519/940,519/940);drawing.width=519;drawing.height=420*519/940;story.append(drawing)
    p('Error bars are arithmetic mean +/- sample SD plotted on a log scale. Offsets separate methods within each category. No line connects unrelated programs.','SmallRQ')
    heading('Observed child lifetimes')
    times=[['Program']+methods]+[[c]+['%.6f'%stats[c,m]['time_mean_seconds'] for m in methods] for c in cases]
    tab(times,[125,76,80,79,79,80]);p('Table 2. Mean child lifetime in seconds across three session means. These include tool/target startup and are not equal-work throughput comparisons across programs.','SmallRQ');p(assertion)
    story.append(PageBreak());heading('Table 3. Setup and deviations');tab(deviations,[73,141,305])
    heading('Table 4. Inputs, threads and PCT configuration');tab(environment_rows,[138,144,89,148])
    p('PCT steps were checked against the fixed k. The smoke-derived k is not a theoretical worst-case bound. Full commands and binary/source hashes are in environment-manifests.json.','SmallRQ')
    story.append(PageBreak());heading('Repair, audit and elapsed time');p(repair)
    heading('Table 5. Formal command durations');tab(timing_rows,[41,246,108,124])
    p('Formal command time totals 101 min 13.18 s, including setup/export and diagnostic work in the incomplete batch. This excludes earlier environment construction and is not the sum of adopted child lifetimes.')
    p('All 1,350 adopted child logs are covered by the archived audits. The 135 adopted groups passed the coarse timing screen: host elapsed minus child sum > max(30 seconds, 20% of child sum). No tool failures or timeouts remain among adopted groups. This screen is not proof of timing precision.')
    p('Every CSV measurement retains its source batch and archive-relative log. The three source archive SHA256 values are listed in evidence-index.json. Old batches and scripts are preserved. The repair is a new complete paired block, not a relabeling of the old failed batch.')
    heading('Comparison with the paper');p(comparison)
    story.append(PageBreak());heading('Table 6. Claim verdicts and limitations')
    tab([['Claim','Verdict'],['Lower PERIOD overhead','Supported descriptively on 9 selected cases; broader claim partially reproduced.'],['Exact Figure 7 numbers','Inconclusive: exact matched reference/timing unavailable.'],['Thread-count trend','Not established by the four CS points.'],['Bug-finding superiority','Not tested by these runtime averages.']],[142,377]);p(limitations)
    heading('Remaining assignment work');p(remaining)
    heading('Contribution and AI-use statement (draft)');p('The operator launched the experiments and supplied console output. Codex assisted script preparation, debugging, raw-log auditing, aggregation, figures and this draft. The team must confirm individual authorship and review the interpretation before integration.')
    heading('Conclusion');p('PERIOD has lower observed startup-inclusive runtime cost than IPB, IDB and PCT on these nine selected programs; the broader paper claim is partially reproduced.')
    heading('Sources');p(refs,'SmallRQ')
    def footer(canvas,doc):
        canvas.setFont('Helvetica',8);canvas.setFillColor(colors.HexColor('#556677'));canvas.drawString(38,22,'PERIOD RQ3 - review draft');canvas.drawRightString(A4[0]-38,22,str(doc.page))
    doc.build(story,onFirstPage=footer,onLaterPages=footer)
    pages=len(PdfReader(OUT/'RQ3-report-draft.pdf').pages)
    (OUT/'evidence-index.json').write_text(json.dumps(data['source_batches'],indent=2),encoding='utf-8')
    (OUT/'用时记录.json').write_text(json.dumps({'formal_command_seconds_total':data['formal_batch_elapsed_seconds'],
        'includes':'three formal commands, setup/export and incomplete-batch diagnostics; earlier environment work excluded',
        'batches':data['source_batches'],'repair_estimate_minutes':[6,10],'repair_actual_seconds':data['source_batches'][2]['timing']['host_elapsed_seconds']},indent=2,ensure_ascii=False),encoding='utf-8')
    cn=['# 先看这里：九程序 RQ3 结果','', '**本轮补跑已完成并审核；九程序主实验结果已整理，尚未提交 Git。**','',
        '- 补跑实际8分25.98秒，原预估6–10分钟；北京时间2026-11-21 07:10:39至07:19:05。',
        '- 纳入统计：9程序×5方法×3轮×10次＝1,350次，135组、27个完整五方法配对块。覆盖SCTBench的CS、Inspect、Chess、Misc共4/7组、9/36程序。',
        '- 每轮先求10次子进程平均时间，再除以同轮Native均值；最终是三轮配对比值的均值和样本标准差。不是把30次当作30轮。','',
        '## 怎么看成果','',
        '1. 打开 rq3-nine-programs.png 看对比图：横轴九个程序，纵轴是相对Native的倍数，越低越快。纵轴为对数刻度。每个点旁的误差线是三轮的样本标准差。',
        '2. 打开 rq3-results-9-programs.xlsx：Results是数值汇总，Groups是逐轮公式，Samples是1,350条计时和原始日志位置，Environment是逐程序参数、环境与来源。',
        '3. RQ3-report-draft.pdf / .md 是英文RQ3报告草稿，包含方法、结果、偏差、范围限制、补跑过程和剩余任务。','',
        '## 这次得到了什么','',
        '九个程序中PERIOD的测量均值都低于IPB、IDB、PCT。PERIOD相对Native为%.2f–%.2f倍，三种基线为%.2f–%.2f倍。基线最大值超过论文文字的500倍范围，这个差异在报告里明确保留。它不是匹配同一程序参数后得出的精确复现误差。'%(pmin,pmax,bmin,bmax),'',
        '指标包含工具/目标启动和输出收集，不能写成纯稳态开销。保留57次匹配源文件行号的目标断言，这是目标程序结果；不能据此推断某方法找bug更强。','',
        '## 原来的中断怎样处理','',
        '原五程序批次保留14个完整配对块，IWSQWS第三轮采用本次新测的完整五方法块替换。旧第三轮Native 10次及未完成PERIOD 10次仅作诊断保留，不混入统计。原失败批次仍标为不完整。三个批次的来源和哈希均有记录，跨批次采样限制已说明。','',
        '三次正式命令合计101分13.18秒（1小时41分13.18秒），包含命令准备、日志导出和失败轮诊断工作；不含前期搭环境时间，也不是1,350次子进程时间之和。','',
        '## 后面还缺什么','',
        '- SWSQ、boundedBuffer按你的安排暂缓，尚未计入九程序结果。',
        '- 老师要求的单因素扩展实验尚未完成；增加程序覆盖不自动等于完成扩展。',
        '- 精确逐程序Paper vs Ours仍缺匹配的论文原始值和测量边界。',
        '- 需要团队核对贡献/AI使用说明，整合其他RQ，再整理可迁移的仓库运行说明。','',
        '原四程序成果目录哈希保持不变；队友仓库、README、Git提交和推送均未改动。','']
    (OUT/'先看这里.md').write_text('\n'.join(cn),encoding='utf-8')
    print(json.dumps({'report_pages':pages,'PERIOD_range':[pmin,pmax],'baseline_range':[bmin,bmax],
                      'max_baseline':maximum,'source_assertions':data['assertions']},ensure_ascii=False))

if __name__=='__main__':main()

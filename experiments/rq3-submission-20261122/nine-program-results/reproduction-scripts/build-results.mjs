import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';
const base=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const out=path.join(base,'outputs/rq3-expanded-20261121');
const data=JSON.parse(await fs.readFile(path.join(out,'workbook-data.json'),'utf8'));
const {results,groups,samples,environments}=data;
const sourceId=name=>'B'+(1+results.source_batches.findIndex(b=>b.batch===name));
const wb=Workbook.create();
const res=wb.worksheets.add('Results'),grp=wb.worksheets.add('Groups'),raw=wb.worksheets.add('Samples'),env=wb.worksheets.add('Environment');
const font={name:'Arial',size:10,color:'#1D2937'};
for(const [s,r] of [[res,'A1:I54'],[grp,'A1:I139'],[raw,'A1:J1354'],[env,'A1:J30']]){
  s.showGridLines=false;s.getRange(r).format.font=font;s.getRange(r).format.rowHeight=22;
  s.getRange(r).format.verticalAlignment='center';s.getRange(r).format.columnWidth=15;
  s.getRange('A:A').format.columnWidth=27;
}
res.tabColor='#253C53';
const header=(s,r)=>{s.getRange(r).format={fill:'#253C53',font:{...font,bold:true,color:'#FFFFFF'},rowHeight:32,horizontalAlignment:'center',verticalAlignment:'center',wrapText:true};};
const title=(s,text)=>{s.getRange('A2').values=[[text]];s.getRange('A2').format.font={...font,size:15,bold:true};};
title(res,'RQ3 runtime comparison: nine programs');
res.getRange('A4').values=[['Three paired repetitions of 10 actual launches. Mean and sample SD. Startup costs and source-matched assertions are included.']];
res.getRange('A5').values=[['Coverage: 9/36 SCTBench programs, 4/7 families. Independent repetition unit: session, not each launch.']];
res.getRange('A7:I7').values=[['Program','Method','Mean (s)','SD (s)','Slowdown (x)','SD (x)','Assertions / 30','Repetitions','Launches']];header(res,'A7:I7');
res.freezePanes.freezeRows(7);
title(grp,'Per-repetition calculations');
grp.getRange('A4:I4').values=[['Program','Repetition','Method','Mean (s)','Native mean (s)','Slowdown (x)','Assertions','Launches','Source ID']];header(grp,'A4:I4');grp.freezePanes.freezeRows(4);
raw.getRange('A1').values=[['Original observations from verified evidence archives. Source IDs and hashes are listed in Environment.']];
raw.getRange('A2').values=[['One row per measured child. Archive log paths identify the corresponding original output.']];
raw.getRange('A4:J4').values=[['Program','Repetition','Method','Launch in group','Elapsed (s)','Exit code','Target assertion','Source ID','Archived log','Observer index']];header(raw,'A4:J4');raw.freezePanes.freezeRows(4);
raw.getRange('A5:J1354').values=samples.map(s=>[s.case,s.repetition,s.method,s.launch_in_group,s.elapsed_seconds,s.exit_code,s.target_assertion?1:0,sourceId(s.source_batch),s.archive_log,s.observer_index]);
raw.getRange('E5:E1354').setNumberFormat('0.000000');raw.getRange('I:I').format.columnWidth=73;
groups.forEach((g,i)=>{
  const r=i+5,first=i*10+5,last=first+9;
  const native=5+groups.findIndex(n=>n.case===g.case&&n.repetition===g.repetition&&n.method==='Native');
  grp.getRange(`A${r}:C${r}`).values=[[g.case,g.repetition,g.method]];
  grp.getRange(`D${r}:H${r}`).formulas=[[`=AVERAGE(Samples!E${first}:E${last})`,`=D${native}`,`=D${r}/E${r}`,`=SUM(Samples!G${first}:G${last})`,`=COUNT(Samples!E${first}:E${last})`]];
  grp.getRange(`I${r}`).values=[[sourceId(g.source_batch)]];
});
grp.getRange('D5:F139').setNumberFormat('0.000000');
for(const [i,s] of results.statistics.entries()){
  const r=i+8,refs=groups.map((g,j)=>({g,j})).filter(({g})=>g.case===s.case&&g.method===s.method).map(({j})=>j+5);
  const args=col=>refs.map(r=>`Groups!${col}${r}`).join(',');
  res.getRange(`A${r}:B${r}`).values=[[s.case,s.method]];
  res.getRange(`C${r}:I${r}`).formulas=[[`=AVERAGE(${args('D')})`,`=STDEV(${args('D')})`,`=AVERAGE(${args('F')})`,`=STDEV(${args('F')})`,`=SUM(${args('G')})`,`=COUNT(${args('D')})`,`=SUM(${args('H')})`]];
  if(i%10>=5)res.getRange(`A${r}:I${r}`).format.fill='#F1F4F7';
}
res.getRange('C8:D52').setNumberFormat('0.000000');res.getRange('E8:F52').setNumberFormat('0.00');
title(env,'Program inputs and common environment');
env.getRange('A4').values=[['E1: VirtualBox 7.2 / 2 vCPU / 2 GB; Linux 3.16.0-77; Ubuntu 18.04.5 rootfs; Clang 10; PIN 2.12; protobuf 2.5; kvm-clock.']];
env.getRange('A5').values=[['Native and Maple use the same executable. PERIOD uses the separately instrumented build. All methods use the same VM.']];
env.getRange('A7:J7').values=[['Program','Environment','Arguments','Workers','Threads incl main','PCT k','PCT depth','Native SHA256','PERIOD SHA256','Source IDs']];header(env,'A7:J7');
env.getRange('A8:J16').values=environments.map(e=>[e.case,e.environment,e.arguments,e.worker_threads,e.total_threads,e.pct_k,e.pct_d,e.native_binary_sha256,e.period_binary_sha256,e.source_batches.map(sourceId).join(', ')]);
env.getRange('C:C').format.columnWidth=26;env.getRange('H:I').format.columnWidth=69;env.getRange('J:J').format.columnWidth=14;
env.getRange('A18:E18').values=[['Source ID','Batch','Archive SHA256','Elapsed (s)','Adopted groups']];header(env,'A18:E18');
env.getRange('A19:E21').values=results.source_batches.map((b,i)=>['B'+(i+1),b.batch,b.archive_sha256,b.timing.host_elapsed_seconds,b.adopted_groups]);
env.getRange('B:B').format.columnWidth=48;env.getRange('C19:C21').format.font={...font,size:10};
// Source registry uses spacious ordinary cells below the program table.
env.getRange('A23').values=[['B3 replaces all five methods of IWSQWS repetition3. Original B2 Native and partial PERIOD are excluded from the merged statistics.']];
env.getRange('A24').values=[['The original B2 batch remains incomplete. Fourteen complete blocks are retained, plus one replacement block from B3.']];
env.getRange('A25').values=[['Build commands, assertion rules, source hashes and full manifests are retained in environment-manifests.json beside this workbook.']];
env.getRange('A26').values=[['Figures are separate export files. Rebuild them after editing observations; original measured source files remain unchanged.']];
// Show hashes without truncation in a separate compact source registry.
env.getRange('C19:C21').values=results.source_batches.map(b=>[b.archive_sha256]);
env.getRange('C:C').format.columnWidth=69;
for(const s of [res,grp,raw])s.getRange('B:B').format.columnWidth=13;
grp.getRange('B5:B139').format.horizontalAlignment='center';grp.getRange('I5:I139').format.horizontalAlignment='center';
raw.getRange('B5:B1354').format.horizontalAlignment='center';raw.getRange('H5:H1354').format.horizontalAlignment='center';
res.getRange('G:G').format.columnWidth=20;raw.getRange('G:G').format.columnWidth=18;
wb.recalculate();
const expected=results.statistics.map(s=>[s.time_mean_seconds,s.time_sample_sd_seconds,s.slowdown_mean,s.slowdown_sample_sd,s.assertions,3,30]);
const vals=res.getRange('C8:I52').values;
let checked=0;
for(let i=0;i<expected.length;i++)for(let j=0;j<7;j++){
  if(typeof vals[i][j]!=='number'||Math.abs(vals[i][j]-expected[i][j])>1e-8)throw Error(`Formula mismatch ${i}/${j}`);checked++;
}
// Verify dependent recalculation with a disposable change; restore before export.
const old=raw.getRange('E5').values[0][0],before=res.getRange('C8').values[0][0];
raw.getRange('E5').values=[[old*2]];wb.recalculate();
if(Math.abs(res.getRange('C8').values[0][0]-(before+old/30))>1e-9)throw Error('Input propagation failed');
raw.getRange('E5').values=[[old]];wb.recalculate();
if(Math.abs(res.getRange('C8').values[0][0]-before)>1e-10)throw Error('Input restoration failed');
const errors=await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:30},maxChars:2000});
console.log(errors.ndjson);
const review=path.join(base,'work/rq3-expanded-build/previews');await fs.mkdir(review,{recursive:true});
for(const [sheetName,range,name] of [['Results','A1:I24','results-top'],['Results','A25:I53','results-bottom'],['Groups','A1:I17','groups'],['Samples','A3:J14','samples'],['Environment','A1:G17','environment'],['Environment','A18:E26','sources']]){
  const png=await wb.render({sheetName,range,scale:1.3,format:'png'});await fs.writeFile(path.join(review,name+'.png'),new Uint8Array(await png.arrayBuffer()));
}
const file=await SpreadsheetFile.exportXlsx(wb);await file.save(path.join(out,'rq3-results-9-programs.xlsx'));
await fs.writeFile(path.join(out,'workbook-verification.json'),JSON.stringify({summary_values_checked:checked,formula_error_scan:errors.ndjson,input_propagation_and_restoration:'passed',raw_observations:1350,groups:135,native_excel_application_tested:false},null,2));
console.log('Workbook exported:315 summary comparisons, restored input propagation, six range previews.');

"""Independent CSV/XLSX consistency checks and evidence snapshot packaging."""
import csv
import hashlib
import json
from pathlib import Path
import shutil
import statistics
import xml.etree.ElementTree as ET
import zipfile
from pypdf import PdfReader

BASE=Path(__file__).resolve().parents[2]
OUT=BASE/'outputs/rq3-expanded-20261121'
data=json.loads((OUT/'results.json').read_text())
with (OUT/'measurements-1350.csv').open(encoding='utf-8-sig',newline='') as f:samples=list(csv.DictReader(f))
with (OUT/'groups-135.csv').open(encoding='utf-8-sig',newline='') as f:groups=list(csv.DictReader(f))
assert len(samples)==1350 and len(groups)==135
assert len({(s['source_batch'],s['archive_log']) for s in samples})==1350
for g in groups:
    rows=[s for s in samples if (s['case'],s['method'],s['repetition'])==(g['case'],g['method'],g['repetition'])]
    assert len(rows)==10 and {s['source_batch'] for s in rows}=={g['source_batch']}
    assert abs(statistics.mean(float(s['elapsed_seconds']) for s in rows)-float(g['mean_seconds']))<1e-10
    assert sum(s['target_assertion']=='True' for s in rows)==int(g['assertions'])
for s in data['statistics']:
    matched=[g for g in groups if (g['case'],g['method'])==(s['case'],s['method'])]
    ratios=[float(g['slowdown']) for g in matched]
    assert len(ratios)==3
    assert abs(statistics.mean(ratios)-s['slowdown_mean'])<1e-10
    assert abs(statistics.stdev(ratios)-s['slowdown_sample_sd'])<1e-10
ns={'x':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
with zipfile.ZipFile(OUT/'rq3-results-9-programs.xlsx') as z:
    root=ET.fromstring(z.read('xl/worksheets/sheet1.xml'))
    cells={c.get('r'):c for c in root.findall('.//x:c',ns)}
    exported_checks=0
    for i,s in enumerate(data['statistics'],8):
        expected=[s['time_mean_seconds'],s['time_sample_sd_seconds'],s['slowdown_mean'],s['slowdown_sample_sd'],s['assertions'],3,30]
        for col,value in zip('CDEFGHI',expected):
            c=cells[col+str(i)]
            assert c.find('x:f',ns) is not None
            actual=float(c.find('x:v',ns).text)
            assert abs(actual-value)<1e-8
            exported_checks+=1
    for name in [n for n in z.namelist() if n.startswith('xl/worksheets/sheet') and n.endswith('.xml')]:
        sheet=ET.fromstring(z.read(name))
        assert not sheet.findall('.//x:c[@t="e"]',ns)
    assert len(ET.fromstring(z.read('xl/worksheets/sheet3.xml')).findall('.//x:sheetData/x:row',ns))>=1350
pages=PdfReader(OUT/'RQ3-report-draft.pdf').pages
assert len(pages)==5
report='\n'.join(p.extract_text() for p in pages)
for text in ['1,350','623.94','Table 4','Table 5','Table 6','Figure 7','driver_returned']:
    assert text in report,text
old=BASE/'outputs/rq3-final-20261120'
old_hashes=json.loads((old/'file-hashes.json').read_text())
for name,digest in old_hashes.items():assert hashlib.sha256((old/name).read_bytes()).hexdigest()==digest
archive_dir=OUT/'evidence';archive_dir.mkdir(exist_ok=True)
audit_dir=OUT/'audits';audit_dir.mkdir(exist_ok=True)
script_dir=OUT/'reproduction-scripts';script_dir.mkdir(exist_ok=True)
for i,source in enumerate(data['source_batches'],1):
    path=BASE/source['evidence_archive']
    assert hashlib.sha256(path.read_bytes()).hexdigest()==source['archive_sha256']
    shutil.copy2(path,archive_dir/(source['batch']+'.tar.gz'))
    shutil.copy2(BASE/'outputs/rq3-legacy-vm'/('audit-'+source['batch'])/'audit.json',audit_dir/('B%d-audit.json'%i))
for name in ['merge-expanded-results.py','audit-five-extra-formal.py','observe-cross-family.py','cross-family-formal-support.py','run-five-extra-formal.py','run-five-extra-formal.ps1','run-five-extra-formal-guest.sh','five-extra-approved-plan.json','five-extra-budget-amendment.md']:
    shutil.copy2(BASE/'outputs/rq3-legacy-vm'/name,script_dir/name)
for name in ['build-results.mjs','make-report.py','finalize-package.py']:
    shutil.copy2(Path(__file__).parent/name,script_dir/name)
for name in ['run-four-cs-formal.py','run-four-cs-formal.ps1','run-four-cs-formal-guest.sh','observe-executions.py']:
    shutil.copy2(BASE/'outputs/rq3-final-20261120/reproduction-scripts'/name,script_dir/name)
usage=('These files snapshot the scripts used in this workspace. Exact executed versions are also retained in each evidence archive.\n'
       'The current local environment paths are captured, not a portable clean-machine setup package. Repository integration and clean-machine instructions remain pending user review.\n'
       'The analysis source builders were executed from outputs/rq3-legacy-vm (merge/audit) and work/rq3-expanded-build (workbook/report); their relative-root calculation assumes those workspace locations.\n'
       'The spreadsheet uses @oai/artifact-tool; the report/figure use ReportLab and Poppler. Never run old CS or full five-program scripts merely to review these results.\n')
(script_dir/'usage-notes.txt').write_text(usage,encoding='utf-8')
verification={'adopted_measurements':1350,'adopted_groups':135,'paired_blocks':27,'cases':9,'families':4,
              'repetitions_per_case_method':3,'launches_per_repetition':10,'source_assertions':57,
              'adopted_tool_failures':0,'adopted_timeouts':0,'timing_screen_flags':0,
              'csv_group_means_rechecked':135,'exported_xlsx_formula_values_checked':exported_checks,
              'xlsx_formula_error_cells':0,'workbook_input_propagation_and_restore':'passed',
              'report_pages':5,'old_result_files_hash_verified':len(old_hashes),
              'pdf_visual_review':'five final pages reviewed','workbook_visual_review':'all four sheets reviewed',
              'native_excel_application_tested':False,
              'deferred_programs':['Chess.SWSQ','Inspect.boundedBuffer'],
              'assignment_extension_completed':False,'repository_modified':False}
(OUT/'verification.json').write_text(json.dumps(verification,indent=2),encoding='utf-8')
files={str(p.relative_to(OUT)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest()
       for p in OUT.rglob('*') if p.is_file() and p.name!='file-hashes.json' and not p.name.endswith('.inspect.ndjson')}
(OUT/'file-hashes.json').write_text(json.dumps(files,indent=2),encoding='utf-8')
print(json.dumps({'checks':'passed','files_hashed':len(files),'measurements':len(samples),
                  'xlsx_cached_formula_checks':exported_checks,'preserved_original_files':len(old_hashes)}))

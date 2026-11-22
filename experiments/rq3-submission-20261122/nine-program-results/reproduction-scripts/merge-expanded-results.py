"""Merge audited complete paired blocks; retain original and repair provenance."""
import csv
import hashlib
import json
from pathlib import Path
import statistics

BASE = Path(__file__).resolve().parents[2]
OUT = BASE / 'outputs/rq3-expanded-20261121'
OUT.mkdir(exist_ok=True)
METHODS = ['Native', 'PERIOD', 'IPB', 'IDB', 'PCT']
BATCHES = ['four-cs-formal-20261120T122804Z', 'five-extra-formal-20261120T151904Z-b3d307', 'five-extra-repair-20261120T231039Z-b86dea']
EXPECTED_HASHES = ['7e81cecdfed972a3d79a11622c92e09d99a91c1098b3526b30631c377c0485b7',
                   '139fcd474eec08a8b905cbf732b69b9c5d36383602aec7145499f12df600c188',
                   '0e4c7b2c202f052dfe182c533bb58975686e9b68e73f5b69063073f16297377b']
CASES = ['CS.reorder_3_bad','CS.reorder_4_bad','CS.reorder_5_bad','CS.reorder_10_bad',
         'Inspect.qsort_mt','Chess.WSQ','Chess.IWSQ','Chess.IWSQWS','Misc.safestack']

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def write_csv(name, rows):
    with (OUT / name).open('w', newline='', encoding='utf-8-sig') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

def main():
    records, sources, environments, excluded = [], [], {}, []
    for index, (batch, expected) in enumerate(zip(BATCHES, EXPECTED_HASHES)):
        raw = BASE / 'work/rq3-legacy-vm' / ('extracted-' + batch)
        host = BASE / 'work/rq3-legacy-vm' / batch
        assert hashlib.sha256((host / 'evidence.tar.gz').read_bytes()).hexdigest() == expected
        summary = read(raw / 'summary.json')
        audit = read(BASE / 'outputs/rq3-legacy-vm' / ('audit-' + batch) / 'audit.json')
        assert summary['complete'] if index != 1 else summary['batch_finished']
        if index == 0:
            assert not audit['raw_execution_problems'] and not audit['flagged_group_count']
        else:
            assert not audit['problems'] and not audit['timing_flags']
        manifest = read(raw / 'manifest.json')
        timing = read(host / 'run-timing.json')
        sources.append({'batch':batch, 'archive_sha256':expected, 'timing':timing,
                        'original_batch_complete':summary['complete'],
                        'adopted_groups':60 if index == 0 else 70 if index == 1 else 5,
                        'evidence_archive':str((host / 'evidence.tar.gz').relative_to(BASE)).replace('\\','/')})
        environments[batch] = manifest
        guest = summary['records'][0]['method_directory'].split('/rep')[0]
        for record in summary['records']:
            if index == 1 and record['case'] == 'Chess.IWSQWS' and record['repetition'] == 3:
                excluded.append({'source_batch':batch,'case':record['case'],'repetition':3,
                                 'method':record['method'],'actual_children':len(record['samples']),
                                 'reason':'entire original rep3 block replaced with fresh paired repair'})
                continue
            record = dict(record, case=('CS.' + record['case']) if index == 0 else record['case'], source_batch=batch)
            record['archive_method_directory'] = record['method_directory'][len(guest)+1:]
            record['samples'] = [dict(s, archive_log=s['log'][len(guest)+1:]) for s in record['samples']]
            records.append(record)
        if index == 1:
            partial = read(raw / 'rep03/Chess.IWSQWS/PERIOD/samples.json')
            excluded.append({'source_batch':batch,'case':'Chess.IWSQWS','repetition':3,'method':'PERIOD',
                             'actual_children':len(partial['samples']), 'reason':'old incomplete PERIOD group retained for diagnosis only'})
    assert len(records) == 135
    assert len({(r['case'],r['method'],r['repetition']) for r in records}) == 135
    records.sort(key=lambda r:(CASES.index(r['case']),r['repetition'],METHODS.index(r['method'])))
    stats, groups, samples, sensitivity = [], [], [], []
    for record in records:
        assert len(record['samples']) == 10 and all(s['valid'] for s in record['samples'])
        assert abs(statistics.mean(s['elapsed_seconds'] for s in record['samples']) - record['mean_seconds']) < 1e-10
        native = next(r for r in records if r['case'] == record['case'] and r['repetition'] == record['repetition'] and r['method'] == 'Native')
        assert native['source_batch'] == record['source_batch']
        groups.append({'case':record['case'], 'repetition':record['repetition'], 'method':record['method'],
                       'mean_seconds':record['mean_seconds'], 'native_mean_seconds':native['mean_seconds'],
                       'slowdown':record['mean_seconds']/native['mean_seconds'],
                       'assertions':sum(s['target_assertion'] for s in record['samples']),
                       'actual_launches':10,'source_batch':record['source_batch'],
                       'period_completion':record.get('period_completion',{}).get('completion_reason','driver_returned') if record['method']=='PERIOD' else 'n.a.'})
        for ordinal, s in enumerate(record['samples'],1):
            samples.append({'case':record['case'],'repetition':record['repetition'],'method':record['method'],
                            'launch_in_group':ordinal, 'observer_index':s['index'], 'elapsed_seconds':s['elapsed_seconds'],
                            'exit_code':s['exit_code'],'target_assertion':s['target_assertion'],
                            'source_batch':record['source_batch'],'archive_log':s['archive_log'],
                            'pct_steps':json.dumps(s['pct_steps']), 'systematic_bound':s.get('systematic_bound'),
                            'round':s.get('round')})
        good = [s['elapsed_seconds'] for s in record['samples'] if not s['target_assertion']]
        sensitivity.append({'case':record['case'],'repetition':record['repetition'],'method':record['method'],
                            'successes':len(good),'success_only_mean_seconds':statistics.mean(good) if good else None,
                            'primary_fixed_budget_result':False})
    assert len(samples) == len({(s['source_batch'],s['archive_log']) for s in samples}) == 1350
    for case in CASES:
        for method in METHODS:
            values = [g for g in groups if g['case']==case and g['method']==method]
            assert {g['repetition'] for g in values} == {1,2,3}
            ratios = [g['slowdown'] for g in values]
            times = [g['mean_seconds'] for g in values]
            stats.append({'case':case,'family':case.split('.')[0],'method':method,'repetitions':3,'launches_per_repetition':10,
                          'time_mean_seconds':statistics.mean(times),'time_sample_sd_seconds':statistics.stdev(times),
                          'slowdown_mean':statistics.mean(ratios),'slowdown_sample_sd':statistics.stdev(ratios),
                          'assertions':sum(g['assertions'] for g in values), 'repetition_slowdowns':ratios})
    case_env = []
    cs_builds = environments[BATCHES[0]]['builds']
    extras = {c['case']:c for c in environments[BATCHES[1]]['cases']}
    for case in CASES:
        cs = case.startswith('CS.')
        meta = cs_builds[case[3:]] if cs else extras[case]
        native_sample = next(r for r in records if r['case']==case and r['method']=='Native')['samples'][0]
        binary = meta['native_binary']
        arguments = native_sample['command'][native_sample['command'].index(binary)+1:]
        pct = next(r for r in records if r['case']==case and r['method']=='PCT')['samples'][0]['command']
        value = lambda flag:int(pct[pct.index(flag)+1])
        case_env.append({'case':case,'environment':'E1','arguments':' '.join(arguments) or '(none)',
                         'worker_threads':meta['worker_threads'], 'total_threads':value('-pct_n'),
                         'pct_n':value('-pct_n'),'pct_k':value('-pct_k'),'pct_d':value('-pct_d'),
                         'build_directory':str(Path(binary).parent).replace('\\','/'),
                         'native_binary_sha256':meta['native_binary_sha256'],
                         'period_binary_sha256':meta['period_binary_sha256'],
                         'source_batches':sorted({r['source_batch'] for r in records if r['case']==case})})
    result = {'cases':CASES,'methods':METHODS,'families':['CS','Inspect','Chess','Misc'],
              'case_count':9,'sctbench_total':36,'sctbench_families_total':7,
              'adopted_measurements':1350,'adopted_groups':135,'paired_blocks':27,
              'source_batches':sources,'excluded':excluded,'statistics':stats,
              'assertions':sum(g['assertions'] for g in groups),
              'formal_batch_elapsed_seconds':sum(s['timing']['host_elapsed_seconds'] for s in sources),
              'timing':'startup-inclusive CLOCK_MONOTONIC child lifetime; not steady-state overhead',
              'limits':['selected9 of36 SCTBench programs,4 of7 families; no CVE overhead',
                        '3 repeated sessions on one VM; fixed PCT seeds; no statistical significance claim',
                        'separate batches; entire IWSQWS rep3 replaced; cross-batch limitation retained',
                        'controlled one-factor extension and exact paper per-case references still pending']}
    write_csv('summary.csv',[{k:v for k,v in s.items() if k!='repetition_slowdowns'} for s in stats])
    write_csv('groups-135.csv',groups)
    write_csv('measurements-1350.csv',samples)
    write_csv('success-only-sensitivity.csv',sensitivity)
    write_csv('environment-by-program.csv',[dict(e,source_batches='; '.join(e['source_batches'])) for e in case_env])
    for name,data in [('results.json',result),('merged-records.json',records),('environment-manifests.json',environments),
                      ('workbook-data.json',{'results':result,'groups':groups,'samples':samples,'environments':case_env})]:
        (OUT / name).write_text(json.dumps(data,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps({'adopted_groups':135,'measurements':1350,'assertions':result['assertions'],
                      'formal_minutes':result['formal_batch_elapsed_seconds']/60,
                      'PERIOD':[{k:v for k,v in s.items() if k in ('case','slowdown_mean','slowdown_sample_sd')} for s in stats if s['method']=='PERIOD'],
                      'max_baseline_slowdown':max(s['slowdown_mean'] for s in stats if s['method'] in ('IPB','IDB','PCT'))},ensure_ascii=False))

if __name__ == '__main__':
    main()

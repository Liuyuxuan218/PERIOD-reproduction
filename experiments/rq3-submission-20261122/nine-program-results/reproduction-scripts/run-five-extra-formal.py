#!/usr/bin/env python3
"""Five audited programs, same startup-inclusive metric, fresh 3x10 batches."""
import datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import statistics
import sys

KIT = Path(__file__).resolve().parent
PLAN = json.loads((KIT / 'five-extra-approved-plan.json').read_text())
spec = importlib.util.spec_from_file_location('formal_support', KIT / 'cross-family-formal-support.py')
S = importlib.util.module_from_spec(spec)
spec.loader.exec_module(S)
NAMES = ['Inspect.qsort_mt', 'Chess.WSQ', 'Chess.IWSQ', 'Chess.IWSQWS', 'Misc.safestack']
METHODS = ('Native', 'PERIOD', 'IPB', 'IDB', 'PCT')
SELECTION = os.environ.get('RQ3_EXTRA_SELECTION', 'all')
if SELECTION not in ('all', 'repair-iwsqws-rep3'):
    raise ValueError('Invalid extra-program selection')
SELECTED_BLOCKS = [(rep, meta['case']) for rep in range(1, 4) for meta in PLAN['cases']
                   if SELECTION == 'all' or (rep == 3 and meta['case'] == 'Chess.IWSQWS')]
TOTAL_GROUPS = len(SELECTED_BLOCKS) * 5
TOTAL_LAUNCHES = TOTAL_GROUPS * 10


def summarize(records, failures, finished=False):
    blocks = [(rep, case) for rep in range(1, 4) for case in NAMES
              if all(any(r['case'] == case and r['repetition'] == rep and r['method'] == m for r in records) for m in METHODS)]
    groups = []
    for name in [name for name in NAMES if any(case == name for rep, case in SELECTED_BLOCKS)]:
        native = {r['repetition']: r['mean_seconds'] for r in records if r['case'] == name and r['method'] == 'Native'}
        for method in METHODS:
            valid = [r for r in records if r['case'] == name and r['method'] == method and (r['repetition'], name) in blocks]
            ratios = [r['mean_seconds'] / native[r['repetition']] for r in valid]
            groups.append({'case': name, 'method': method, 'valid_paired_repetitions': len(ratios),
                           'slowdown_mean': statistics.mean(ratios) if ratios else None,
                           'slowdown_sample_sd': statistics.stdev(ratios) if len(ratios) > 1 else None})
    result = {'complete': finished and len(records) == TOTAL_GROUPS and not failures,
              'batch_finished': finished, 'failure': str(len(failures)) + ' paired block failures' if failures else None,
              'planned_measurement_groups': TOTAL_GROUPS, 'planned_actual_measurements': TOTAL_LAUNCHES,
              'measurement_groups_completed': len(records),
              'actual_measurements': sum(r['actual_executions'] for r in records),
              'complete_paired_blocks': blocks, 'records': records, 'summary': groups, 'failures': failures,
              'selection': SELECTION, 'selected_blocks': SELECTED_BLOCKS,
              'scope': 'five extra programs from Inspect/Chess/Misc; startup-inclusive runtime; two special cases excluded'}
    S.save(KIT / 'summary.json', result)
    return result


def case_environment(meta):
    env = S.ENV.copy()
    env['RQ3_EXPECTED_THREADS'] = str(meta['worker_threads'] + 1)
    env['RQ3_ASSERTION_RULES'] = json.dumps(meta['assertion_rules'])
    return env


def maple(directory, meta, mode, bound, count, seed):
    env = S.maple_env(meta['worker_threads'], mode, bound, count, seed, meta['pct_k'])
    env.update({key: value for key, value in case_environment(meta).items() if key.startswith('RQ3_')})
    env['RQ3_BUDGET'] = str(count)
    destination = directory / 'samples.json'
    S.logged(['python', str(S.OBSERVER), 'maple', str(destination), '--',
              str(S.MAPLE / 'maple/script/maple/runner.py'), meta['native_binary']] + meta['arguments'],
             directory, directory / 'driver.log', env)
    return S.read_samples(destination)


def preflight():
    if [c['case'] for c in PLAN['cases']] != NAMES:
        raise RuntimeError('Approved program list differs; special cases must remain excluded')
    if S.subprocess.check_output(['uname', '-r']).decode().strip() != '3.16.0-77-generic':
        raise RuntimeError('Unexpected kernel')
    if (KIT / 'runtime-clocksource.txt').read_text().strip() != 'kvm-clock':
        raise RuntimeError('Unexpected VM clocksource')
    for meta in PLAN['cases']:
        for kind in ('native', 'period'):
            if hashlib.sha256(Path(meta[kind + '_binary']).read_bytes()).hexdigest() != meta[kind + '_binary_sha256']:
                raise RuntimeError('Existing binary hash mismatch: ' + meta['case'])
        for rel, expected in meta['source_sha256'].items():
            path = Path(meta['native_binary']).parent / rel
            if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
                raise RuntimeError('Existing copied source changed: ' + str(path))
    actual_commit = S.subprocess.check_output(['git', '--no-optional-locks', '-c', 'safe.directory=' + str(S.PERIOD), '-C', str(S.PERIOD), 'rev-parse', 'HEAD']).decode().strip()
    if actual_commit != 'b6f72a7b06d01ffa7114b640312873ec2578a5ea':
        raise RuntimeError('Unexpected PERIOD source commit')
    # Same observer transport checks as the accepted four-case batch, under both Python versions.
    S.observer_checks()
    manifest = dict(PLAN, started_utc=datetime.datetime.utcnow().isoformat() + 'Z',
                    build_directory=PLAN['source_build_directory'], kernel=S.subprocess.check_output(['uname', '-a']).decode().strip(),
                    guest_clocksource='kvm-clock', os_release=Path('/etc/os-release').read_text(),
                    cpu_model=Path('/proc/cpuinfo').read_text(), cpu_affinity_available_to_experiment=sorted(os.sched_getaffinity(0)),
                    budget=10, repetitions=3, methods=METHODS,
                    selected_blocks=SELECTED_BLOCKS, selection=SELECTION,
                    protocol_amendment='actual-launch-budget-v2; before launch11 stop PERIOD normally after exactly10 valid measured children, including retests; search exhaustion not claimed',
                    repair_provenance=json.loads((KIT / 'repair-provenance.json').read_text()) if SELECTION != 'all' else None,
                    classification_version='cross-family-source-assertions-v1',
                    timing='CLOCK_MONOTONIC child lifetime; sudo/tool/target startup and pipe collection included; preparation, profile, discovery and driver/search generation excluded',
                    pct_k_rule='next power of two >= max(256, 8 * observed smoke PCT steps); fixed before formal run; not proof of worst-case bound',
                    affinity='two VM CPUs available; no CPU0 pinning or FIFO claim',
                    assertion_policy='keep source-file/line-matched target assertions; retain tool failures/timeouts separately; reject unknown abnormal exits')
    S.save(KIT / 'manifest.json', manifest)


def main():
    records, failures = [], []
    protected = {}
    summarize(records, failures)
    try:
        preflight()
        for root in (Path('/workdir/rq3-four-cs-QRUZy7'), Path(PLAN['source_build_directory'])):
            for path in root.rglob('*'):
                if path.is_file():
                    protected[str(path)] = hashlib.sha256(path.read_bytes()).hexdigest()
        S.save(KIT / 'preservation-before.json', protected)
        for rep in range(1, 4):
            for index, meta in enumerate(PLAN['cases']):
                name = meta['case']
                if (rep, name) not in SELECTED_BLOCKS:
                    continue
                directory = KIT / ('rep%02d' % rep) / name
                directory.mkdir(parents=True)
                seed = 20261120 + 1000 * rep + index
                failed_method = 'profile'
                group_number = None
                try:
                    print('FORMAL_PROFILE rep=%d case=%s excluded=1' % (rep, name), flush=True)
                    profile_work = directory / 'profile'
                    profile_work.mkdir()
                    profile_values = maple(profile_work, meta, 'race', 0, 1, seed)
                    if len(profile_values) != 1:
                        raise RuntimeError('Expected exactly one profiling child')
                    profile = directory / 'run_race'
                    if not (profile / 'race.db').is_file() or not (profile / 'sinfo.db').is_file():
                        raise RuntimeError('Missing fresh profiling DB')
                    offset = (rep - 1 + index) % 5
                    order = METHODS[offset:] + METHODS[:offset]
                    S.save(directory / 'order.json', {'method_order': order, 'pct_seed': seed, 'pct_k': meta['pct_k']})
                    for method in order:
                        failed_method = method
                        group_number = SELECTED_BLOCKS.index((rep, name)) * 5 + order.index(method) + 1
                        completion = None
                        print('FORMAL_START group=%d/%d rep=%d case=%s method=%s' % (group_number, TOTAL_GROUPS, rep, name, method), flush=True)
                        work = directory / method
                        work.mkdir()
                        observations = []
                        if method in ('Native', 'PERIOD'):
                            env = case_environment(meta)
                            env['RQ3_BUDGET'] = '10'
                            destination = work / 'samples.json'
                            arguments = [meta['native_binary']] + meta['arguments'] if method == 'Native' else [str(S.PERIOD / 'tool/DBDS/run_PDS.py'), '-y', '-d', '3', '-f', '10', '-t', '60', meta['period_binary']] + meta['arguments']
                            S.logged(['python3', str(S.OBSERVER), 'native' if method == 'Native' else 'period', str(destination), '--'] + arguments,
                                     work, work / 'driver.log', env)
                            observations = S.read_samples(destination)
                            if method == 'PERIOD':
                                driver = (work / 'driver.log').read_text(errors='replace')
                                completion = json.loads(destination.read_text())
                                budget_stop = (completion.get('completion_reason') == 'actual_launch_budget_reached'
                                               and completion.get('actual_budget') == 10
                                               and len(observations) == 10 and all(v['valid'] for v in observations)
                                               and 'PERIOD_ACTUAL_LAUNCH_BUDGET_REACHED count=10' in driver)
                                normal_finish = 'End Testing!' in driver and re.search(r'Total Timeouts Interleavings:\s*0\b', driver)
                                if not ((normal_finish or budget_stop) and not re.search(r'Unknown Exception|Traceback', driver)):
                                    raise RuntimeError('PERIOD driver has incomplete search/error/timeout')
                        else:
                            mode = {'IPB': 'pb', 'IDB': 'db', 'PCT': 'pct'}[method]
                            shutil.copytree(str(profile), str(work / 'run_race'))
                            for bound in ([0] if method == 'PCT' else range(4)):
                                remaining = 10 - len(observations)
                                if not remaining:
                                    break
                                run = work / ('bound%d' % bound)
                                run.mkdir()
                                values = maple(run, meta, mode, bound, remaining, seed)
                                for value in values:
                                    value['systematic_bound'] = bound if method != 'PCT' else None
                                observations.extend(values)
                            if method == 'PCT':
                                for value in observations:
                                    if not value['pct_steps'] and value['target_assertion']:
                                        continue
                                    if len(value['pct_steps']) != 1 or not 0 < value['pct_steps'][0] <= meta['pct_k']:
                                        raise RuntimeError('PCT observed steps missing or exceed fixed k')
                        if len(observations) != 10:
                            raise RuntimeError('Actual count %d differs from fixed budget10; no padding/restarting search' % len(observations))
                        row = {'group_number': group_number, 'case': name, 'worker_threads': meta['worker_threads'],
                               'method': method, 'repetition': rep, 'actual_executions': 10,
                               'mean_seconds': statistics.mean(v['elapsed_seconds'] for v in observations),
                               'assertion_executions': sum(v['target_assertion'] for v in observations),
                               'samples': observations, 'method_directory': str(work), 'pct_k': meta['pct_k']}
                        row['original_group_number'] = (rep - 1) * 25 + index * 5 + order.index(method) + 1
                        if completion is not None:
                            row['period_completion'] = {key: completion.get(key) for key in
                                                        ('completion_reason', 'actual_budget', 'unique_measured_rounds', 'retest_launches')}
                        S.save(work / 'group.json', row)
                        records.append(row)
                        summarize(records, failures)
                        print('FORMAL_DONE group=%d/%d rep=%d case=%s method=%s actual=10 mean_seconds=%.6f assertions=%d' %
                              (group_number, TOTAL_GROUPS, rep, name, method, row['mean_seconds'], row['assertion_executions']), flush=True)
                except Exception as exc:
                    failure = {'case': name, 'repetition': rep, 'method': failed_method, 'group_number': group_number,
                               'reason': str(exc), 'paired_block_excluded': True, 'logs': str(directory)}
                    failures.append(failure)
                    S.save(directory / 'block-failure.json', failure)
                    summarize(records, failures)
                    print('FORMAL_BLOCK_FAILED rep=%d case=%s method=%s reason=%s; continuing other blocks' %
                          (rep, name, failed_method, str(exc)), flush=True)
        changes = [path for path, expected in protected.items()
                   if not Path(path).is_file() or hashlib.sha256(Path(path).read_bytes()).hexdigest() != expected]
        S.save(KIT / 'preservation-after.json', {'checked_files': len(protected), 'changed_files': changes})
        if changes:
            failures.append({'preservation_check': changes})
        result = summarize(records, failures, finished=True)
        print('FORMAL_BATCH_FINISHED completed_groups=%d/%d measured_valid_children=%d/%d failed_blocks=%d' %
              (len(records), TOTAL_GROUPS, result['actual_measurements'], TOTAL_LAUNCHES, len(failures)), flush=True)
        if result['complete']:
            print('FORMAL_MEASUREMENTS_COMPLETED groups=%d actual_measurements=%d' % (TOTAL_GROUPS, TOTAL_LAUNCHES), flush=True)
        return 0 if result['complete'] else 1
    except Exception as exc:
        failures.append({'preflight_or_batch': str(exc)})
        summarize(records, failures)
        print('FORMAL_STOPPED: ' + str(exc), flush=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())

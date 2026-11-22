#!/usr/bin/env python3
"""Four CS workloads, five methods, 10 actual launches x 3 independent runs."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import resource
import shutil
import signal
import statistics
import subprocess
import sys
import time

KIT = Path(__file__).resolve().parent
BUILD = Path(sys.argv[1])
OUT = KIT
PERIOD = Path('/workdir/PERIOD')
MAPLE = Path('/home/vagrant/rq3-maple-smoke-IEO4oK')
OBSERVER = KIT / 'observe-cross-family.py'
WORKERS = (3, 4, 5, 10)
METHODS = ('Native', 'PERIOD', 'IPB', 'IDB', 'PCT')
BUDGET = 10
REPETITIONS = 3
SELECTION = os.environ.get('RQ3_SELECTION', 'all')
ALL_BLOCKS = [(rep, workers) for rep in range(1, REPETITIONS + 1) for workers in WORKERS]
if SELECTION == 'all':
    SELECTED_BLOCKS = ALL_BLOCKS
else:
    SELECTED_BLOCKS = [tuple(int(v) for v in item.split(':')) for item in SELECTION.split(',')]
    if not SELECTED_BLOCKS or len(SELECTED_BLOCKS) != len(set(SELECTED_BLOCKS)) or any(block not in ALL_BLOCKS for block in SELECTED_BLOCKS):
        raise ValueError('Invalid selected paired blocks')
PLANNED_GROUPS = len(SELECTED_BLOCKS) * len(METHODS)
PLANNED_LAUNCHES = PLANNED_GROUPS * BUDGET
ENV = os.environ.copy()
ENV.update(ROOT_DIR=str(PERIOD), ROOT=str(MAPLE), PIN_HOME=str(MAPLE / 'pin'),
           MAPLE_HOME=str(MAPLE / 'maple'), PROTOBUF_HOME='/usr', BUILD_DIR='build-release',
           cluster='0', PYTHONUNBUFFERED='1', RQ3_CHILD_TIMEOUT='60')
ENV['PATH'] = str(MAPLE / 'maple/script') + ':' + str(PERIOD / 'clang+llvm/bin') + ':' + ENV['PATH']
ENV['PYTHONPATH'] = str(MAPLE / 'maple/script') + ':' + ENV.get('PYTHONPATH', '')
resource.setrlimit(resource.RLIMIT_CORE, (0, 0))


def save(path, value):
    temp = Path(str(path) + '.tmp')
    temp.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')
    temp.replace(path)


def logged(command, cwd, path, env, timeout=840):
    with path.open('w') as stream:
        stream.write('COMMAND=' + json.dumps(command) + '\n')
        stream.flush()
        process = subprocess.Popen(command, cwd=str(cwd), env=env, stdout=stream,
                                   stderr=subprocess.STDOUT, start_new_session=True)
        try:
            rc = process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait()
            raise RuntimeError('Whole-method timeout; stop batch. Log=' + str(path))
    if rc:
        print(path.read_text(errors='replace')[-3500:], flush=True)
        raise RuntimeError('Method failed (%d): %s' % (rc, path))


def maple_env(workers, mode, bound, count, seed, k):
    env = ENV.copy()
    env.update(mode=('race' if mode == 'race' else 'pct' if mode == 'pct' else 'chess'),
               check_mem='0', enable_djit='0', sched_race='1', sched_app='1', unit_size='1',
               seal_after_one='0', add_races='0', num_threads=str(workers), pb='1',
               delay_bound=('1' if mode == 'db' else '0'), bound=str(bound), limit=str(count),
               output='', cpu='0', max_threads=str(workers + 1), max_steps=str(k),
               seed=str(seed), start_index='0', bug_depth='3', timeout='600', RQ3_BUDGET=str(count))
    return env


def read_samples(path):
    value = json.loads(path.read_text())
    if not value['driver_complete'] or value['driver_exit_code']:
        raise RuntimeError('Driver did not complete: ' + str(path))
    samples = value['samples']
    if not samples or any(not row['valid'] for row in samples):
        raise RuntimeError('Invalid/missing measured child: ' + str(path))
    return samples


def observer_checks():
    """Exercise wrappers, ignored discovery, Maple status1/77 and failures."""
    checks = OUT / 'observer-checks'
    checks.mkdir()
    pin = checks / 'pin.sh'
    pin.write_text('#!/bin/sh\nprintf "HandleThreadStart 0\\nHandleThreadStart 2\\n"\n'
                   'if [ "${4:-0}" != 1 ]; then printf "HandleThreadExit 2\\nHandleThreadExit 0\\n"; fi\n'
                   'printf "PCT NUM STEPS: 12\\nProgram EXIT\\nSaving race DB\\n"\n'
                   'if [ -n "${5:-}" ]; then printf "%s\\n" "$5"; fi\n'
                   'exit "${3:-77}"\n')
    pin.chmod(0o755)
    fake_maple = checks / 'fake-maple.py'
    # sudo resets arbitrary environment variables. Translate fixture settings
    # into explicit arguments before the observer adds its sudo wrapper.
    fake_maple.write_text('import os, subprocess\nfor i in range(2):\n    subprocess.Popen([' + repr(str(pin)) + ', "-t", "/test/systematic_controller.so", os.environ.get("RQ3_FAKE_EXIT", "77"), os.environ.get("RQ3_FAKE_INCOMPLETE", "0"), os.environ.get("RQ3_FAKE_ERROR", "")]).communicate()\n')
    fake_period = checks / 'fake-period.py'
    fake_period.write_text('import subprocess\nrounds = 0\npattern = [[0], [1]]\ncommand = ["sudo", "DBDS_Run=1", "/bin/true"]\ndef launch():\n    subprocess.Popen(command).communicate()\nlaunch()\nfor rounds in range(1, 3):\n    launch()\nprint("Round 3")\n')
    env = ENV.copy()
    env['RQ3_BUDGET'] = '2'
    for interpreter in ('python', 'python3'):
        for mode, args in [('native', ['/bin/true']), ('maple', [str(fake_maple)]), ('period', [str(fake_period)])]:
            dest = checks / (interpreter + '-' + mode + '.json')
            logged([interpreter, str(OBSERVER), mode, str(dest), '--'] + args,
                   checks, checks / (interpreter + '-' + mode + '.log'), env, 30)
            rows = read_samples(dest)
            if len(rows) != 2 or (mode == 'maple' and any(r['exit_code'] != 77 for r in rows)):
                raise RuntimeError('Observer count/exit77 selfcheck failed')
            if mode == 'period' and [r['round'] for r in rows] != [1, 2]:
                raise RuntimeError('Discovery/footer selfcheck failed')
        continuation_env = env.copy()
        continuation_env['RQ3_FAKE_EXIT'] = '1'
        dest = checks / (interpreter + '-maple-continuation.json')
        logged([interpreter, str(OBSERVER), 'maple', str(dest), '--', str(fake_maple)],
               checks, checks / (interpreter + '-maple-continuation.log'), continuation_env, 30)
        rows = read_samples(dest)
        if len(rows) != 2 or not all(row['maple_normal_continuation'] for row in rows):
            raise RuntimeError('Maple status1 completion regression failed')
        # Status1 also denotes failures. Reject these fixtures on the first
        # child even though they print Program EXIT and use the same status.
        for label, mode, changes, args in [
                ('deadlock', 'maple', {'RQ3_FAKE_ERROR': 'ERROR: [CHESS] program deadlock'}, [str(fake_maple)]),
                ('incomplete', 'maple', {'RQ3_FAKE_INCOMPLETE': '1'}, [str(fake_maple)]),
                ('native-one', 'native', {}, [str(pin), '-t', '/test/systematic_controller.so', '1', '0', ''])]:
            fail_env = continuation_env.copy()
            fail_env.update(changes)
            dest = checks / (interpreter + '-' + label + '.json')
            with (checks / (interpreter + '-' + label + '.log')).open('w') as stream:
                code = subprocess.call([interpreter, str(OBSERVER), mode, str(dest), '--'] + args,
                                       cwd=str(checks), env=fail_env, stdout=stream, stderr=subprocess.STDOUT)
            result = json.loads(dest.read_text())
            if code == 0 or result['driver_complete'] or len(result['samples']) != 1 or result['samples'][0]['valid']:
                raise RuntimeError('Failure/stop-immediately regression failed: ' + label)
    # A retest consumes the remaining actual-launch budget before round2.
    # Exception retry handlers must not swallow the observer's clean stop.
    retry = checks / 'fake-retest.py'
    retry.write_text(fake_period.read_text().split('for rounds in range')[0] +
                     'for rounds in (1, 1, 2):\n    try:\n        launch()\n    except Exception:\n        launch()\n')
    overflow = checks / 'fake-maple-overflow.py'
    overflow.write_text(fake_maple.read_text().replace('range(2)', 'range(3)'))
    invalid = checks / 'fake-period-invalid.py'
    invalid.write_text(retry.read_text().replace('/bin/true', '/bin/false'))
    for interpreter in ('python', 'python3'):
        dest = checks / (interpreter + '-period-budget.json')
        logged([interpreter, str(OBSERVER), 'period', str(dest), '--', str(retry)],
               checks, checks / (interpreter + '-period-budget.log'), env, 30)
        data = json.loads(dest.read_text())
        if (len(read_samples(dest)) != 2 or [v['round'] for v in data['samples']] != [1, 1]
                or data.get('completion_reason') != 'actual_launch_budget_reached'
                or data.get('unique_measured_rounds') != 1 or data.get('retest_launches') != 1):
            raise RuntimeError('PERIOD retest/actual-budget stop selfcheck failed')
        for label, mode, target in [('overflow', 'maple', overflow), ('invalid-period', 'period', invalid)]:
            dest = checks / (interpreter + '-' + label + '.json')
            with (checks / (interpreter + '-' + label + '.log')).open('w') as stream:
                code = subprocess.call([interpreter, str(OBSERVER), mode, str(dest), '--', str(target)],
                                       cwd=str(checks), env=env, stdout=stream, stderr=subprocess.STDOUT)
            data = json.loads(dest.read_text())
            if code == 0 or data['driver_complete'] or len(data['samples']) > 2:
                raise RuntimeError('Budget/error rejection selfcheck failed: ' + label)
            if label == 'invalid-period' and all(v['valid'] for v in data['samples']):
                raise RuntimeError('Invalid PERIOD child incorrectly accepted')
    print('FORMAL_OBSERVER_CHECKS_PASSED (both interpreters, Maple normal status1/77, failure rejection, discovery exclusion, budget guard)', flush=True)


def observe_maple(cwd, native, env, destination):
    logged(['python', str(OBSERVER), 'maple', str(destination), '--',
            str(MAPLE / 'maple/script/maple/runner.py'), str(native)],
           cwd, cwd / 'driver.log', env)
    return read_samples(destination)


def summary(records, completed=False, failure=None):
    groups = []
    for workers in WORKERS:
        case = 'reorder_%d_bad' % workers
        native = {r['repetition']: r['mean_seconds'] for r in records if r['case'] == case and r['method'] == 'Native'}
        for method in METHODS:
            rows = [r for r in records if r['case'] == case and r['method'] == method]
            ratios = [r['mean_seconds'] / native[r['repetition']] for r in rows if r['repetition'] in native]
            groups.append({'case': case, 'method': method, 'valid_repetitions': len(rows),
                           'paired_repetitions': len(ratios),
                           'mean_seconds': statistics.mean([r['mean_seconds'] for r in rows]) if rows else None,
                           'slowdown_mean': statistics.mean(ratios) if ratios else None,
                           'slowdown_sample_sd': statistics.stdev(ratios) if len(ratios) > 1 else None})
    payload = {'complete': completed, 'failure': failure, 'measurement_groups_completed': len(records),
               'actual_measurements': sum(r['actual_executions'] for r in records),
               'planned_measurement_groups': PLANNED_GROUPS, 'planned_actual_measurements': PLANNED_LAUNCHES,
               'selected_blocks': SELECTED_BLOCKS,
               'records': records, 'summary': groups,
               'scope': 'reduced RQ3: four variants from one CS benchmark family; process-lifetime slowdown including startup'}
    save(OUT / 'summary.json', payload)


def main():
    records = []
    try:
        if not json.loads((BUILD / 'status.json').read_text())['complete']:
            raise RuntimeError('Prepared build was not validated')
        if subprocess.check_output(['uname', '-r']).decode().strip() != '3.16.0-77-generic':
            raise RuntimeError('Unexpected kernel')
        # These checks produce no benchmark performance results.
        observer_checks()
        metadata = {}
        for workers in WORKERS:
            name = 'reorder_%d_bad' % workers
            data = json.loads((BUILD / name / 'build-metadata.json').read_text())
            for kind in ('native', 'period'):
                digest = hashlib.sha256(Path(data[kind + '_binary']).read_bytes()).hexdigest()
                if digest != data[kind + '_binary_sha256']:
                    raise RuntimeError('Prepared executable changed: ' + name)
            metadata[name] = data
        actual_period_commit = subprocess.check_output(['git', '--no-optional-locks', '-c', 'safe.directory=' + str(PERIOD), '-C', str(PERIOD), 'rev-parse', 'HEAD']).decode().strip()
        if actual_period_commit != 'b6f72a7b06d01ffa7114b640312873ec2578a5ea':
            raise RuntimeError('Unexpected PERIOD source commit')
        manifest = {'started_utc': datetime.datetime.utcnow().isoformat() + 'Z',
                    'classification_version': 'maple-status1-v2',
                    'selected_blocks': SELECTED_BLOCKS,
                    'replacement_of_host_batch': os.environ.get('RQ3_REPAIR_SOURCE', ''),
                    'build_directory': str(BUILD), 'builds': metadata, 'budget': BUDGET,
                    'repetitions': REPETITIONS, 'methods': METHODS,
                    'kernel': subprocess.check_output(['uname', '-a']).decode().strip(),
                    'guest_clocksource': (KIT / 'runtime-clocksource.txt').read_text().strip(),
                    'cpu_affinity_available_to_experiment': sorted(os.sched_getaffinity(0)),
                    'cpu_model': Path('/proc/cpuinfo').read_text(),
                    'os_release': Path('/etc/os-release').read_text(),
                    'clang': subprocess.check_output(['clang', '--version'], env=ENV).decode(),
                    'maple_upstream_commit': 'd59ab26ddaedcd575ffb6a1f5e9711f7d6d2d9f2',
                    'period_upstream_commit': actual_period_commit,
                    'pct_depth': 3, 'pct_n': 'worker threads + main',
                    'pct_k_rule': '8 * (worker_threads + 1) + 16; conservative configured bound, audited on every observed execution, not a proof over all schedules',
                    'systematic_bounds': [0, 1, 2, 3],
                    'timing': 'CLOCK_MONOTONIC child lifetime including sudo/tool/target startup and pipe collection; excludes compilation, profiling, discovery, driver/search generation and database parsing',
                    'affinity': 'same available VM CPUs for all methods; cpu=0 passed to Maple, but this fork comments out SetAffinity/SetSchedPolicy calls, so no actual CPU0 affinity or FIFO claim',
                    'deviations': ['four related CS workloads only; no CVE workloads', '10 actual child executions per method per repetition',
                                   '2-vCPU VirtualBox VM; same Ubuntu 18.04 userland on Linux 3.16', 'clang 10 O0 non-PIE builds from shared bitcode',
                                   'startup-inclusive runtime metric; paper does not fully specify timing boundary'],
                    'excluded_from_600': 'observer selfchecks and 12 race profiling runs; PERIOD dry/default executions'}
        save(OUT / 'manifest.json', manifest)
        summary(records)
        for rep in range(1, REPETITIONS + 1):
            for case_index, workers in enumerate(WORKERS):
                if (rep, workers) not in SELECTED_BLOCKS:
                    continue
                name = 'reorder_%d_bad' % workers
                meta = metadata[name]
                native = Path(meta['native_binary'])
                controlled = Path(meta['period_binary'])
                k = 8 * (workers + 1) + 16
                seed = 20261118 + 1000 * rep + workers
                directory = OUT / ('rep%02d' % rep) / name
                directory.mkdir(parents=True)
                profile_run = directory / 'profile'
                profile_run.mkdir()
                # Profile once per independent repetition into fresh DB files.
                print('FORMAL_PROFILE rep=%d case=%s (excluded from timing)' % (rep, name), flush=True)
                race = observe_maple(profile_run, native, maple_env(workers, 'race', 0, 1, seed, k), profile_run / 'samples.json')
                if len(race) != 1:
                    raise RuntimeError('Expected one profiling execution')
                profile = directory / 'run_race'
                if not (profile / 'race.db').is_file() or not (profile / 'sinfo.db').is_file():
                    raise RuntimeError('Missing profiling databases')
                offset = (rep - 1 + case_index) % len(METHODS)
                order = METHODS[offset:] + METHODS[:offset]
                save(directory / 'order.json', {'method_order': order, 'pct_seed': seed, 'pct_k': k})
                for method in order:
                    print('FORMAL_START group=%d/%d rep=%d case=%s method=%s' % (len(records) + 1, PLANNED_GROUPS, rep, name, method), flush=True)
                    work = directory / method
                    work.mkdir()
                    observations = []
                    driver_text = ''
                    if method == 'Native':
                        env = ENV.copy()
                        env['RQ3_BUDGET'] = str(BUDGET)
                        dest = work / 'samples.json'
                        logged(['python3', str(OBSERVER), 'native', str(dest), '--', str(native)], work, work / 'driver.log', env)
                        observations = read_samples(dest)
                    elif method == 'PERIOD':
                        env = ENV.copy()
                        env['RQ3_BUDGET'] = str(BUDGET)
                        dest = work / 'samples.json'
                        logged(['python3', str(OBSERVER), 'period', str(dest), '--', str(PERIOD / 'tool/DBDS/run_PDS.py'),
                                '-y', '-d', '3', '-f', str(BUDGET), '-t', '60', str(controlled)], work, work / 'driver.log', env)
                        observations = read_samples(dest)
                        driver_text = (work / 'driver.log').read_text(errors='replace')
                        if 'End Testing!' not in driver_text or not re.search(r'Total Timeouts Interleavings:\s*0\b', driver_text):
                            raise RuntimeError('PERIOD search did not complete without timeouts')
                    else:
                        mode = {'IPB': 'pb', 'IDB': 'db', 'PCT': 'pct'}[method]
                        shutil.copytree(str(profile), str(work / 'run_race'))
                        for bound in ([0] if mode == 'pct' else range(4)):
                            remaining = BUDGET - len(observations)
                            if remaining == 0:
                                break
                            run = work / ('bound%d' % bound)
                            run.mkdir()
                            env = maple_env(workers, mode, bound, remaining, seed, k)
                            values = observe_maple(run, native, env, run / 'samples.json')
                            for value in values:
                                value['systematic_bound'] = bound if mode != 'pct' else None
                            observations.extend(values)
                            # The actual remaining budget is passed at each
                            # bound. Thus DB=1 at bound0 +9 at bound1 totals10.
                        if method == 'PCT':
                            for value in observations:
                                steps = value['pct_steps']
                                # An assertion may terminate before the tool
                                # prints its final step count. Keep that bug
                                # outcome explicit, rather than censoring it.
                                if not steps and value['target_assertion']:
                                    continue
                                if len(steps) != 1 or not 0 < steps[0] <= k:
                                    raise RuntimeError('PCT step count missing or exceeds configured k')
                    if len(observations) != BUDGET:
                        raise RuntimeError('%s actual count=%d, expected10; no partial means accepted' % (method, len(observations)))
                    row = {'case': name, 'worker_threads': workers, 'method': method,
                           'repetition': rep, 'actual_executions': len(observations),
                           'mean_seconds': statistics.mean(v['elapsed_seconds'] for v in observations),
                           'assertion_executions': sum(v['target_assertion'] for v in observations),
                           'samples': observations, 'method_directory': str(work)}
                    save(work / 'group.json', row)
                    records.append(row)
                    summary(records)
                    print('FORMAL_DONE group=%d/%d rep=%d case=%s method=%s actual=10 mean_seconds=%.6f assertions=%d' %
                          (len(records), PLANNED_GROUPS, rep, name, method, row['mean_seconds'], row['assertion_executions']), flush=True)
        if len(records) != PLANNED_GROUPS or sum(r['actual_executions'] for r in records) != PLANNED_LAUNCHES:
            raise RuntimeError('Final count mismatch')
        summary(records, completed=True)
        print('FORMAL_MEASUREMENTS_COMPLETED groups=%d actual_measurements=%d' % (PLANNED_GROUPS, PLANNED_LAUNCHES), flush=True)
        return 0
    except Exception as exc:
        summary(records, failure=str(exc))
        print('FORMAL_STOPPED: ' + str(exc), flush=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())

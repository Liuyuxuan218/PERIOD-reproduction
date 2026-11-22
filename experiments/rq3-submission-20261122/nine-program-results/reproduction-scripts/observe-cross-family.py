#!/usr/bin/env python
"""Python 2.7/3.6 observer of actual children, using CLOCK_MONOTONIC.

Runtime dependencies and scheduling algorithms are not rewritten. All measured
children use sudo, matched environment, null stdin and two captured pipes.
Compilation, driver startup, profiling and PERIOD discovery are excluded.
"""
from __future__ import print_function
import copy
import ctypes
import inspect
import json
import os
import re
import runpy
import signal
import subprocess
import sys


class Timespec(ctypes.Structure):
    _fields_ = [('seconds', ctypes.c_long), ('nanoseconds', ctypes.c_long)]


RT = ctypes.CDLL('librt.so.1', use_errno=True)
RT.clock_gettime.argtypes = [ctypes.c_int, ctypes.POINTER(Timespec)]
RT.clock_gettime.restype = ctypes.c_int


def monotonic():
    value = Timespec()
    if RT.clock_gettime(1, ctypes.byref(value)):
        raise OSError(ctypes.get_errno(), 'CLOCK_MONOTONIC failed')
    return value.seconds + value.nanoseconds * 1e-9


def save(path, data):
    temporary = path + '.tmp'
    with open(temporary, 'w') as stream:
        json.dump(data, stream, indent=2, sort_keys=True)
        stream.write('\n')
    os.rename(temporary, path)


def text(value):
    return (value or b'').decode('utf-8', 'replace')


class ChildTimeout(RuntimeError):
    pass


class ActualBudgetReached(BaseException):
    """Stop PERIOD before another launch; bypass its Exception retry handlers."""
    pass


def classify_child(mode, command, return_code, combined, timed_out, expected_threads=0, assertion_rules=None):
    rules = assertion_rules or []
    assertion = bool(re.search(r'assertion.*failed|assert.*failed', combined, re.I) and
                     any(re.search(re.escape(rule['file']) + ':' + str(rule['line']) + r'\D', combined) for rule in rules))
    infrastructure = re.findall(r'unexpected AUX VEC|out_of_range|vector::_M_range_check|sched_setattr error|Operation not permitted|cannot open shared object|No such file or directory|command not found|Traceback|unable to resolve host|Segmentation fault', combined, re.I)
    normal = return_code == 0
    diagnostics = []
    continuation = False
    maple_assertion = False
    starts, ends = [], []
    if mode == 'maple':
        starts = re.findall(r'^HandleThreadStart\s+(\d+)\s*$', combined, re.M)
        ends = re.findall(r'^HandleThreadExit\s+(\d+)\s*$', combined, re.M)
        controller = any(os.path.basename(arg) == 'systematic_controller.so' for arg in command)
        errors = re.findall(r'^\s*ERROR:[^\r\n]*', combined, re.M | re.I)
        complete_threads = bool(starts and '0' in starts and len(set(starts)) == len(starts)
                                and sorted(starts) == sorted(ends)
                                and (not expected_threads or len(starts) == expected_threads))
        program_exit = bool(re.search(r'^Program EXIT\s*$', combined, re.M))
        saved = bool(re.search(r'^Saving race DB\s*$', combined, re.M))
        exhausted = bool(return_code == 77 and controller and re.search(r'^\[CHESS\] search done\s*$', combined, re.M))
        continuation = bool(return_code == 1 and controller and program_exit and complete_threads and saved and not errors)
        maple_assertion = bool(return_code == 1 and controller and assertion and
                               re.search(r'^\s*ERROR: signal 6\s*!+', combined, re.M))
        diagnostics = [e for e in errors if not (maple_assertion and re.match(r'^\s*ERROR: signal 6\s*!+\s*$', e))]
        normal = bool(program_exit and complete_threads and not errors and
                      ((return_code == 0 and saved) or continuation or (return_code == 77 and (saved or exhausted))))
    expected_assertion = (return_code in (-6, 6, 134) and assertion) or maple_assertion
    return {'exit_code': return_code, 'timed_out': timed_out, 'target_assertion': assertion,
            'maple_normal_continuation': continuation, 'maple_diagnostics': diagnostics,
            'infrastructure_errors': infrastructure,
            'observed_threads_including_main': len(starts) if mode == 'maple' else None,
            'pct_steps': [int(v) for v in re.findall(r'PCT NUM STEPS:\s*(\d+)', combined)],
            'valid': bool((normal or expected_assertion) and not infrastructure and not diagnostics and not timed_out)}


def main():
    mode, destination = sys.argv[1:3]
    assert sys.argv[3] == '--'
    arguments = sys.argv[4:]
    samples = []
    original = subprocess.Popen
    null = open('/dev/null', 'rb')
    budget = int(os.environ.get('RQ3_BUDGET', '10'))
    child_timeout = int(os.environ.get('RQ3_CHILD_TIMEOUT', '60'))
    expected_threads = int(os.environ.get('RQ3_EXPECTED_THREADS', '0'))
    assertion_rules = json.loads(os.environ.get('RQ3_ASSERTION_RULES', '[]'))

    class ObservedPopen(original):
        def __init__(self, command, *args, **kwargs):
            caller = inspect.currentframe().f_back.f_globals
            is_list = isinstance(command, (list, tuple))
            observed = mode == 'native' or (mode == 'maple' and is_list and command[0].endswith('/pin.sh'))
            observed = observed or (mode == 'period' and is_list and 'DBDS_Run=1' in command and caller.get('rounds', 0) > 0)
            self.observation = None
            if observed:
                if len(samples) >= budget:
                    if mode == 'period' and len(samples) == budget and all(row['valid'] for row in samples):
                        raise ActualBudgetReached()
                    raise RuntimeError('Actual execution budget exceeded (including any retests)')
                command = list(command)
                if command[0] != 'sudo':
                    command = ['sudo', 'Dry_Run=0', 'DBDS_Run=0',
                               'ASAN_OPTIONS=abort_on_error=1:detect_leaks=0',
                               'TSAN_OPTIONS=report_bugs=1'] + command
                # sudo normally strips LD_LIBRARY_PATH. Retain the same common
                # libraries and the separate Maple protobuf dependency.
                command.insert(1, 'LD_LIBRARY_PATH=' + os.environ.get('LD_LIBRARY_PATH', ''))
                kwargs.update(stdin=null, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              close_fds=True, preexec_fn=os.setsid)
                self.observation = {'index': len(samples) + 1, 'command': command,
                                    'round': caller.get('rounds'),
                                    'yield_pattern': copy.deepcopy(caller.get('pattern')),
                                    'bound': os.environ.get('bound') if mode == 'maple' else None}
            self.started = monotonic()
            original.__init__(self, command, *args, **kwargs)

        def communicate(self, *args, **kwargs):
            if self.observation is None:
                return original.communicate(self, *args, **kwargs)
            item = self.observation
            self.observation = None
            previous = signal.getsignal(signal.SIGALRM)

            def expire(signum, frame):
                raise ChildTimeout('Measured child exceeded %d seconds' % child_timeout)

            signal.signal(signal.SIGALRM, expire)
            signal.setitimer(signal.ITIMER_REAL, child_timeout)
            # The same blocking pipe wait is used in both Python interpreters.
            kwargs.pop('timeout', None)
            timed_out = False
            output = (b'', b'')
            try:
                output = original.communicate(self, *args, **kwargs)
            except ChildTimeout:
                timed_out = True
                os.killpg(self.pid, signal.SIGKILL)
                output = original.communicate(self)
            finally:
                ended = monotonic()
                signal.setitimer(signal.ITIMER_REAL, 0)
                signal.signal(signal.SIGALRM, previous)
                out, err = text(output[0]), text(output[1])
                log_path = '%s.child-%02d.log' % (destination, item['index'])
                with open(log_path, 'wb') as stream:
                    stream.write((out + '\nSTDERR:\n' + err).encode('utf-8'))
                combined = out + '\n' + err
                item.update(classify_child(mode, item['command'], self.returncode, combined,
                                           timed_out, expected_threads, assertion_rules))
                item.update(elapsed_seconds=ended - self.started, log=log_path)
                item['valid'] = bool(item['valid'] and ended > self.started)
                samples.append(item)
                save(destination, {'mode': mode, 'samples': samples, 'driver_complete': False})
                if mode == 'maple':
                    # Preserve the original runner log, outside the timed span.
                    print(out, end='')
                    print(err, end='')
                    sys.stdout.flush()
            if timed_out:
                raise ChildTimeout('Measured child timed out; stop this batch')
            if not item['valid']:
                raise RuntimeError('Invalid measured child, exit=%s, log=%s' % (self.returncode, log_path))
            return output

    subprocess.Popen = ObservedPopen
    exit_code = 0
    complete = False
    completion_reason = 'driver_returned'
    try:
        if mode == 'native':
            for index in range(budget):
                process = subprocess.Popen(arguments)
                process.communicate()
                if not samples[-1]['valid']:
                    raise RuntimeError('Native child failed validation')
        else:
            target = arguments[0]
            sys.argv = arguments
            sys.path.insert(0, os.path.dirname(target))
            runpy.run_path(target, run_name='__main__')
        complete = True
    except ActualBudgetReached:
        if mode != 'period' or len(samples) != budget or not all(row['valid'] for row in samples):
            exit_code = 1
            raise RuntimeError('Invalid actual-budget completion')
        complete = True
        completion_reason = 'actual_launch_budget_reached'
        print('PERIOD_ACTUAL_LAUNCH_BUDGET_REACHED count=%d; no further child launched; search not exhausted' % budget)
    except SystemExit as error:
        exit_code = error.code if isinstance(error.code, int) else (0 if error.code is None else 1)
        complete = exit_code == 0
    except BaseException:
        exit_code = 1
        raise
    finally:
        subprocess.Popen = original
        null.close()
        save(destination, {'mode': mode, 'samples': samples, 'driver_complete': complete,
                           'driver_exit_code': exit_code,
                           'completion_reason': completion_reason if complete else 'failed',
                           'actual_budget': budget,
                           'unique_measured_rounds': len(set(row['round'] for row in samples)) if mode == 'period' else None,
                           'retest_launches': len(samples) - len(set(row['round'] for row in samples)) if mode == 'period' else None,
                           'classification_version': 'cross-family-source-assertions-v1',
                           'timing': 'CLOCK_MONOTONIC child lifetime: sudo + target/tool startup + execution + pipe collection; excludes driver/preparation'})
    return exit_code


if __name__ == '__main__':
    sys.exit(main())

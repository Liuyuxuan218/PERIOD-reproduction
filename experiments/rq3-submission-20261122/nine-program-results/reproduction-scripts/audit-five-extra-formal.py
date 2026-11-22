"""Audit raw saved measurements, pairing, settings and transfer integrity offline."""
import ast
import csv
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import statistics
import sys
import tarfile

BASE = Path(__file__).resolve().parents[2]
NAME = sys.argv[1] if len(sys.argv) > 1 else 'five-extra-formal-20261120T151904Z-b3d307'
assert re.fullmatch(r'five-extra-(?:formal|repair)-\d{8}T\d{6}Z-[a-f0-9]{6}', NAME)
BATCH = BASE / 'work/rq3-legacy-vm' / NAME
OUT = BASE / 'outputs/rq3-legacy-vm' / ('audit-' + NAME)
OUT.mkdir(exist_ok=True)
RAW = BASE / 'work/rq3-legacy-vm' / ('extracted-' + NAME)
RAW.mkdir(exist_ok=True)


def main():
    evidence = (BATCH / 'formal-evidence.txt').read_bytes()
    evidence = evidence.decode('utf-16') if evidence[:2] in (b'\xff\xfe', b'\xfe\xff') else evidence.decode('utf-8-sig')
    expected = re.search(r'^FORMAL_ARCHIVE_SHA256=([a-f0-9]{64})\s*$', evidence, re.M).group(1)
    guest = re.search(r'^FORMAL_DIRECTORY=(/workdir/rq3-five-extra-formal-[a-zA-Z0-9]+)\s*$', evidence, re.M).group(1)
    archive = BATCH / 'evidence.tar.gz'
    assert hashlib.sha256(archive.read_bytes()).hexdigest() == expected
    with tarfile.open(archive) as stream:
        total = 0
        for member in stream:
            rel = PurePosixPath(member.name.removeprefix('./'))
            assert not rel.is_absolute() and '..' not in rel.parts and ':' not in str(rel)
            if member.isdir():
                continue
            assert member.isfile() and member.size < 100 * 1024 * 1024
            total += member.size
            assert total < 500 * 1024 * 1024
            path = RAW / Path(*rel.parts)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(stream.extractfile(member).read())
    summary = json.loads((RAW / 'summary.json').read_text())
    manifest = json.loads((RAW / 'manifest.json').read_text())
    preservation = json.loads((RAW / 'preservation-after.json').read_text())
    assert not preservation['changed_files']
    plan = {r['case']: r for r in manifest['cases']}
    tree = ast.parse((RAW / 'observe-cross-family.py').read_text())
    classifier = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'classify_child')
    scope = {'re': re, 'os': os}
    exec(compile(ast.Module(body=[classifier], type_ignores=[]), '<archived-classifier>', 'exec'), scope)
    progress = [json.loads(line.lstrip('\ufeff')) for line in (BATCH / 'host-progress.jsonl').read_text(encoding='utf-8-sig').splitlines() if line.strip()]
    quality, assertions, groups, samples_out, issues = [], [], [], [], []
    raw_count = 0
    for record in summary['records']:
        assert len(record['samples']) == record['actual_executions'] == 10
        meta = plan[record['case']]
        for sample in record['samples']:
            assert sample['log'].startswith(guest + '/')
            relative = sample['log'][len(guest) + 1:]
            text = (RAW / relative).read_text(errors='replace')
            mode = 'native' if record['method'] == 'Native' else 'period' if record['method'] == 'PERIOD' else 'maple'
            checked = scope['classify_child'](mode, sample['command'], sample['exit_code'], text,
                                             sample['timed_out'], meta['pct_n'], meta['assertion_rules'])
            assert sample['valid'] and checked['valid'] and sample['elapsed_seconds'] > 0, relative
            assert checked['target_assertion'] == sample['target_assertion']
            binary = meta['period_binary'] if mode == 'period' else meta['native_binary']
            assert binary in sample['command']
            binary_index = sample['command'].index(binary)
            assert sample['command'][binary_index + 1:] == meta['arguments']
            if record['method'] == 'PCT':
                for flag, value in [('-pct_n', meta['pct_n']), ('-pct_k', meta['pct_k']), ('-pct_d', 3)]:
                    assert int(sample['command'][sample['command'].index(flag) + 1]) == value
                steps = checked['pct_steps']
                assert (not steps and checked['target_assertion']) or (len(steps) == 1 and 0 < steps[0] <= meta['pct_k'])
            if record['method'] in ('IPB', 'IDB'):
                assert sample['systematic_bound'] in (0, 1, 2, 3)
                for flag, value in [('-pb_limit', sample['systematic_bound']), ('-delay_bound', int(record['method'] == 'IDB'))]:
                    assert int(sample['command'][sample['command'].index(flag) + 1]) == value
            raw_count += 1
            row = {'case': record['case'], 'repetition': record['repetition'], 'method': record['method'],
                   'index': sample['index'], 'elapsed_seconds': sample['elapsed_seconds'],
                   'target_assertion': sample['target_assertion'], 'exit_code': sample['exit_code'],
                   'log': relative, 'source_batch': NAME}
            samples_out.append(row)
            if sample['target_assertion']:
                assertions.append(row)
        mean = statistics.mean(s['elapsed_seconds'] for s in record['samples'])
        assert abs(mean - record['mean_seconds']) < 1e-10
        assert sum(s['target_assertion'] for s in record['samples']) == record['assertion_executions']
        if record['method'] == 'PERIOD' and record.get('period_completion', {}).get('completion_reason') == 'actual_launch_budget_reached':
            folder = RAW / record['method_directory'][len(guest) + 1:]
            completion = json.loads((folder / 'samples.json').read_text())
            assert completion['driver_complete'] and completion['driver_exit_code'] == 0
            assert completion['completion_reason'] == 'actual_launch_budget_reached' and completion['actual_budget'] == 10
            rounds = {s['round'] for s in record['samples']}
            assert completion['unique_measured_rounds'] == len(rounds)
            assert completion['retest_launches'] == 10 - len(rounds)
            log = (folder / 'driver.log').read_text(errors='replace')
            assert 'PERIOD_ACTUAL_LAUNCH_BUDGET_REACHED count=10' in log
            assert not re.search(r'Unknown Exception|Traceback', log)
        group_number = record['group_number']
        starts = [r for r in progress if re.match(r'^FORMAL_START group=%d/' % group_number, r['line'])]
        ends = [r for r in progress if re.match(r'^FORMAL_DONE group=%d/' % group_number, r['line'])]
        assert len(starts) == len(ends) == 1
        host = ends[0]['host_elapsed_seconds'] - starts[0]['host_elapsed_seconds']
        children = sum(s['elapsed_seconds'] for s in record['samples'])
        quality.append({'group': group_number, 'case': record['case'], 'repetition': record['repetition'],
                        'method': record['method'], 'host_seconds': host, 'child_seconds': children,
                        'flagged': host - children > max(30, .2 * children)})
        groups.append({k: record[k] for k in ('case', 'method', 'repetition', 'mean_seconds', 'assertion_executions')})
    extra = []
    # Read all profile/partial-group raw logs as well; do not silently adopt them as complete groups.
    covered = {r['log'] for r in samples_out}
    for path in RAW.rglob('*.child-*.log'):
        relative = path.relative_to(RAW).as_posix()
        if relative not in covered:
            content = path.read_text(errors='replace')
            category = 'observer_selfcheck' if relative.startswith('observer-checks/') else 'profiling' if '/profile/' in relative else 'partial_group'
            extra.append({'log': relative, 'bytes': len(content), 'category': category})
    extra_counts = {kind: sum(r['category'] == kind for r in extra) for kind in ('profiling', 'partial_group', 'observer_selfcheck')}
    partial = RAW / 'rep03/Chess.IWSQWS/PERIOD/samples.json'
    partial_info = None
    if partial.is_file() and not any(g['case'] == 'Chess.IWSQWS' and g['repetition'] == 3 and g['method'] == 'PERIOD' for g in groups):
        values = json.loads(partial.read_text())
        for child in values['samples']:
            relative = child['log'][len(guest) + 1:]
            text = (RAW / relative).read_text(errors='replace')
            meta = plan['Chess.IWSQWS']
            checked = scope['classify_child']('period', child['command'], child['exit_code'], text,
                                             child['timed_out'], meta['pct_n'], meta['assertion_rules'])
            assert child['valid'] and checked['valid'] and child['elapsed_seconds'] > 0
            assert meta['period_binary'] in child['command']
            assert child['command'][child['command'].index(meta['period_binary']) + 1:] == meta['arguments']
        partial_info = {'actual_children': len(values['samples']), 'driver_complete': values['driver_complete'],
                        'driver_exit_code': values['driver_exit_code'],
                        'all_children_valid': all(r['valid'] for r in values['samples']),
                        'rounds': [r['round'] for r in values['samples']], 'not_adopted_as_complete_group': True}
        assert partial_info['actual_children'] == 10 and partial_info['all_children_valid']
    methods = ['Native', 'PERIOD', 'IPB', 'IDB', 'PCT']
    paired = [(rep, case) for rep in range(1, 4) for case in plan
              if all(any(g['case'] == case and g['repetition'] == rep and g['method'] == m for g in groups) for m in methods)]
    stats = []
    for case in plan:
        for method in methods:
            matched = [g for g in groups if g['case'] == case and g['method'] == method and (g['repetition'], case) in paired]
            ratios = [g['mean_seconds'] / next(n['mean_seconds'] for n in groups if n['case'] == case and n['repetition'] == g['repetition'] and n['method'] == 'Native') for g in matched]
            stats.append({'case': case, 'method': method, 'paired_repetitions': len(ratios),
                          'slowdown_mean': statistics.mean(ratios) if ratios else None,
                          'slowdown_sample_sd': statistics.stdev(ratios) if len(ratios) > 1 else None})
    for filename, rows in [('summary.csv', stats), ('groups.csv', groups), ('measurements.csv', samples_out)]:
        with (OUT / filename).open('w', newline='', encoding='utf-8-sig') as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    original = BASE / 'outputs/rq3-final-20261120'
    hashes = json.loads((original / 'file-hashes.json').read_text())
    for filename, sha in hashes.items():
        assert hashlib.sha256((original / filename).read_bytes()).hexdigest() == sha
    result = {'source_batch': NAME, 'archive_sha256': expected, 'raw_logs_of_completed_groups_read': raw_count,
              'additional_raw_logs_read': len(extra), 'additional_log_categories': extra_counts, 'completed_groups': len(groups),
              'complete_paired_blocks': len(paired), 'complete_paired_children': 50 * len(paired),
              'target_assertions': assertions, 'timing_flags': [g for g in quality if g['flagged']],
              'quality': quality, 'partial_PERIOD_group': partial_info, 'preservation': preservation,
              'original_deliverable_files_checked': len(hashes), 'problems': issues,
              'stats': stats, 'timing': json.loads((BATCH / 'run-timing.json').read_text(encoding='utf-8-sig')),
              'original_failures': summary['failures'], 'archive_extracted_to': str(RAW)}
    (OUT / 'audit.json').write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding='utf-8')
    if NAME.startswith('five-extra-repair-'):
        assert manifest['selection'] == 'repair-iwsqws-rep3'
        provenance = manifest['repair_provenance']
        assert provenance['original_archive_sha256'] == '139fcd474eec08a8b905cbf732b69b9c5d36383602aec7145499f12df600c188'
        assert hashlib.sha256((RAW / 'five-extra-budget-amendment.md').read_bytes()).hexdigest() == provenance['protocol_amendment_sha256']
        assert all(g['case'] == 'Chess.IWSQWS' and g['repetition'] == 3 for g in groups)
        timing = result['timing']
        lines = ['# IWSQWS 第三轮补跑审核', '',
                 '本批仅包含 IWSQWS 第三轮，原五程序批次其余 14 个完整配对块不变。', '',
                 '完成 %d/5 组，%d/50 次计时；完整配对块 %d 个。实际用时 %.2f 秒。' % (len(groups), raw_count, len(paired), timing['host_elapsed_seconds']), '',
                 '主机开始 UTC：%s；结束 UTC：%s。' % (timing['started_utc'], timing['ended_utc']), '',
                 '原始输出按源文件行号与异常规则重新分类；计时筛查标记 %d 个。旧成果 27 个文件及原构建目录校验通过。' % len(result['timing_flags']), '',
                 '仅在五组均完成且审核通过后，用此完整配对块替换旧第三轮；不可把新旧同轮 Native/PERIOD 混在一起。原批次与补跑跨时段采样，须保留该限制。', '']
        (OUT / '审核结果与补跑说明.md').write_text('\n'.join(lines), encoding='utf-8')
        print(json.dumps({'repair_complete': summary['complete'], 'completed_groups': len(groups), 'raw_logs_read': raw_count,
                          'timing_flags': len(result['timing_flags']), 'elapsed_seconds': timing['host_elapsed_seconds']}))
        return
    lines = ['# 五程序正式批次审核', '',
             '实际时间：北京时间 2026-11-20 23:19:04 至 2026-11-21 00:17:52，58 分 48.06 秒。此前预估 50–90 分钟。', '',
             '已完成 71/75 组，即 710 次组内计时；其中 14 个完整五方法配对块共 700 次可用于完整块统计，另有 IWSQWS 第三轮 Native 10 次待配对。PERIOD 第三轮还保留了 10 次有效子进程，但驱动预算保护退出，原协议下不自动认定为完整组。15 次预分析另计。', '',
             '4 个程序（qsort_mt、WSQ、IWSQ、SafeStack）各完成 3 轮；IWSQWS 完成 2 轮，第三轮待补。不必重跑整个五程序批次。', '',
             '失败原因：IWSQWS 第三轮 PERIOD 在第 9 个调度模式自动重试一次，9 个模式已经产生 10 次实际启动。当驱动请求第 11 次时，固定实际预算保护抛异常。归档 10 次子进程均有效，无超时；它是预算停止处理问题，不能称为目标程序/环境故障。', '',
             '统计为每轮 10 次均值/同轮 Native 均值，再对配对轮求均值和样本标准差。IWSQWS 仅两轮，不能标作达到三轮要求。下表仍属于阶段结果。', '',
             '| 程序 | 完整配对轮数 | PERIOD 相对 Native（均值 ± 样本 SD） |', '|---|---:|---|']
    for case in plan:
        s = next(r for r in stats if r['case'] == case and r['method'] == 'PERIOD')
        lines.append('| %s | %d | %.2f ± %.2f 倍 |' % (case, s['paired_repetitions'], s['slowdown_mean'], s['slowdown_sample_sd']))
    lines.extend(['', '读取并审核 %d 个完整组原始日志；另读取 %d 个预分析日志、%d 个部分组日志、%d 个观察器自检日志。部分 PERIOD 的 10 个子进程另行按原始输出独立复核有效。源文件行号匹配的目标断言共 %d 次，按既定协议保留，不作为工具错误、不据此推断错误发现优越性。完成组大幅主机/子进程计时差异筛查标记 %d 个。' % (raw_count, extra_counts['profiling'], extra_counts['partial_group'], extra_counts['observer_selfcheck'], len(assertions), len(result['timing_flags'])), '',
                  '原四程序/初步验证目录文件校验 %d 个无变化；原成果目录 27 个文件哈希未变。' % preservation['checked_files'], '',
                  '补跑方案：明确 PERIOD 实际启动达到 10 次时为预算正常停止；记录该原因和模式数，禁止第 11 次启动。使用相同二进制、计时、种子、方法顺序、PCT 参数，只替换 IWSQWS 第三轮完整五方法块（50 次），保存原失败批次并说明跨批次限制。其他结果不改。该预算终止规则在补跑前公开记录，不能冒称原批次驱动正常完成。', ''])
    (OUT / '审核结果与补跑说明.md').write_text('\n'.join(lines), encoding='utf-8')
    print(json.dumps({'completed_groups': len(groups), 'paired_blocks': len(paired),
                      'raw_logs_read': raw_count + len(extra), 'assertions': len(assertions),
                      'timing_flags': len(result['timing_flags']), 'partial': partial_info,
                      'period_results': [r for r in stats if r['method'] == 'PERIOD']}, ensure_ascii=False))


if __name__ == '__main__':
    main()

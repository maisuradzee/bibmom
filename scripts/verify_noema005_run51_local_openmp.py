from __future__ import annotations
import base64, gzip, hashlib, json, statistics
from pathlib import Path
from typing import Any
from jsonschema import Draft202012Validator, FormatChecker
ROOT=Path(__file__).resolve().parents[1]
REPORT=ROOT/'data/noema-005/run51-local-openmp-report-2026-11-28.json'
SCHEMA=ROOT/'data/noema-005/run51-local-openmp-report.schema.json'
RAW_B64=ROOT/'data/noema-005/raw/run51-local-openmp-2026-11-28.jsonl.gz.b64'
SOURCE=ROOT/'scripts/noema005_run51_openmp.c'

def verify_report(report_path: Path=REPORT)->dict[str,Any]:
    report=json.loads(report_path.read_text(encoding='utf-8'))
    schema=json.loads(SCHEMA.read_text(encoding='utf-8'))
    Draft202012Validator.check_schema(schema)
    errors=list(Draft202012Validator(schema,format_checker=FormatChecker()).iter_errors(report))
    if errors: raise ValueError('Run 51 report schema validation failed: '+'; '.join(e.message for e in errors))
    source_sha=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    if source_sha!=report['build']['source_sha256']: raise ValueError('Run 51 C source SHA-256 mismatch')
    compressed=base64.b64decode(RAW_B64.read_text(encoding='ascii').strip(),validate=True)
    if hashlib.sha256(compressed).hexdigest()!=report['build']['raw_gzip_sha256']: raise ValueError('Run 51 compressed raw artifact SHA-256 mismatch')
    raw=gzip.decompress(compressed)
    if hashlib.sha256(raw).hexdigest()!=report['build']['raw_stdout_sha256']: raise ValueError('Run 51 raw stdout SHA-256 mismatch')
    raw_layouts=[json.loads(line) for line in raw.decode('utf-8').splitlines() if line]
    if len(raw_layouts)!=2 or [x['layout'] for x in raw_layouts]!=['triplet','grouped']: raise ValueError('Run 51 raw layouts mismatch')
    for raw_layout,summary in zip(raw_layouts,report['results'],strict=True):
        for field in ('layout','repeats','input_elements','input_bytes','peak_rss_kib','warmups','repetitions','long_double_mant_dig'):
            if raw_layout[field]!=summary[field]: raise ValueError(f'Run 51 metadata mismatch: {field}')
        if len(raw_layout['cases'])!=24 or len(summary['accuracy'])!=24 or len(summary['neumaier_runtime'])!=5: raise ValueError('Run 51 case counts mismatch')
        for raw_case,acc in zip(raw_layout['cases'],summary['accuracy'],strict=True):
            for field in ('method','requested_workers','actual_threads_min','actual_threads_max','correct_runs'):
                if raw_case[field]!=acc[field]: raise ValueError(f'Run 51 accuracy mismatch: {field}')
            if statistics.median(raw_case['wall_samples_ns'])!=raw_case['median_wall_ns']: raise ValueError('Run 51 wall median mismatch')
            if statistics.median(raw_case['process_cpu_samples_ns'])!=raw_case['median_process_cpu_ns']: raise ValueError('Run 51 CPU median mismatch')
            if raw_case['correct_runs']>raw_layout['repetitions']: raise ValueError('Run 51 correctness count exceeds repetitions')
        neumaier=[c for c in raw_layout['cases'] if c['method']=='openmp_neumaier_full_state']
        for raw_case,summary_case in zip(neumaier,summary['neumaier_runtime'],strict=True):
            for field in ('requested_workers','actual_threads_min','actual_threads_max','median_wall_ns','median_process_cpu_ns','speedup_vs_serial_method','median_effective_input_gib_s'):
                if raw_case[field]!=summary_case[field]: raise ValueError(f'Run 51 Neumaier runtime mismatch: {field}')
    return {'valid':True,'layouts':2,'cases':48,'source_sha256':source_sha,'raw_stdout_sha256':report['build']['raw_stdout_sha256']}

if __name__=='__main__': print(json.dumps(verify_report(),ensure_ascii=False,sort_keys=True))

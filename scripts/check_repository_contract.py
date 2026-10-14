"""Read-only checks for README navigation, measurement indexes and repository hygiene.

This checks repository structure, not scientific validity or release authority.
"""
from pathlib import Path
import csv
import re
import subprocess
import sys
from urllib.parse import unquote

HEADINGS = [
    'Operational problem', 'Users and decisions', 'What currently works',
    'Measured results and conditions', 'Qualification gaps and next work',
    'Run a demonstration or inspect the implementation', 'Engineering documentation',
]


def validate_contract(root):
    root = Path(root).resolve()
    errors = []
    try:
        names = subprocess.run(
            ['git', '-C', str(root), 'ls-files', '-z', '--cached', '--others', '--exclude-standard'],
            check=True, capture_output=True).stdout.decode().split('\0')
        paths = [Path(name) for name in names if name]
    except (OSError, subprocess.CalledProcessError, UnicodeDecodeError):
        excluded = {'.git', '.venv', 'node_modules', '__pycache__', 'outputs'}
        paths = [p.relative_to(root) for p in root.rglob('*')
                 if p.is_file() and not excluded.intersection(p.relative_to(root).parts)]
    for path in paths:
        parts = path.parts
        skill_dir = any(parts[i] in {'.agents', '.codex'} and parts[i+1] == 'skills'
                        for i in range(len(parts)-1))
        if path.name.lower() == 'skill.md' or skill_dir or path.as_posix() == '.agents/skills-manifest.json':
            errors.append(f'Reusable skill copy in project: {path}')

    try:
        readme = (root/'README.md').read_text(encoding='utf-8')
        headings = re.findall(r'^## (.+)$', readme, re.M)
        expected = list(HEADINGS)
        if 'Run checks or inspect the implementation' in headings:
            expected[5] = 'Run checks or inspect the implementation'
        if headings != expected:
            errors.append('Root README must retain the seven project review sections in order')
        measurement_section = readme.split('## Measured results and conditions\n', 1)[-1].split('\n## ', 1)[0]
        if not re.search(r'\]\(governance/measurements/[^)]+\)', measurement_section):
            errors.append('README results need measurement-record links')
        dictionary = (root/'docs/appendix-a-kpi-dictionary.md').read_text(encoding='utf-8')
        with (root/'governance/measurements/index.csv').open(newline='',encoding='utf-8') as f:
            rows = list(csv.DictReader(f))
        if not rows:
            errors.append('Measurement index is empty')
        seen = set()
        allowed = {
            'measurement_status': {'not measured', 'measured', 'inconclusive'},
            'criterion_result': {'not evaluated', 'pass', 'fail', 'inconclusive'},
            'acceptance_disposition': {'pending review', 'accepted', 'accepted with conditions', 'rejected'},
        }
        for row in rows:
            mid = row['measurement_id']
            if not mid or mid in seen:
                errors.append(f'Missing or duplicate measurement ID: {mid}')
            seen.add(mid)
            for field, values in allowed.items():
                if row[field] not in values:
                    errors.append(f'Invalid {field}: {mid}')
            if row['measurement_status'] == 'not measured' and row['criterion_result'] == 'pass':
                errors.append(f'Unmeasured record cannot pass a measured criterion: {mid}')
            if row['kpi_id'] not in dictionary:
                errors.append(f'Unknown KPI definition: {mid}')
            record_path, _, anchor = row['record'].partition('#')
            record = root/'governance/measurements'/record_path
            if root not in record.resolve().parents or not record.is_file():
                errors.append(f'Missing or out-of-project measurement record: {mid}')
                continue
            content = record.read_text(encoding='utf-8')
            if mid not in content or row['kpi_id'] not in content:
                errors.append(f'Record identity mismatch: {mid}')
            if anchor and f'## {mid}'.lower() not in content.lower():
                errors.append(f'Missing plan heading: {mid}')

        docs = [root/'README.md', root/'docs/appendix-a-kpi-dictionary.md']
        docs += list((root/'governance/measurements').glob('*.md'))
        docs += [root/'docs/demo.md', root/'docs/code-walkthrough.md', root/'docs/results.md', root/'notebooks/README.md']
        for path in docs:
            for target in re.findall(r'\]\(([^)]+)\)', path.read_text(encoding='utf-8')):
                if target.startswith(('https:', 'http:', 'mailto:', '#')):
                    continue
                local = unquote(target.split('#',1)[0])
                if local and not (path.parent/local).resolve().exists():
                    errors.append(f'Broken project link: {path.relative_to(root)} -> {target}')
    except (OSError, KeyError, ValueError) as exc:
        errors.append(f'Cannot inspect repository contract: {exc}')
    return errors


if __name__ == '__main__':
    failures = validate_contract(Path(__file__).resolve().parents[1])
    for failure in failures:
        print(f'ERROR: {failure}')
    if not failures:
        print('PASS: README order, measurement index/links and repository hygiene')
    sys.exit(bool(failures))


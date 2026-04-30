import sys, os, io, time, datetime, traceback, unittest

for p in (
    r'O:/Cloud/Code/_scripts',
    r'O:/Cloud/Code/_scripts/pythontk',
    r'O:/Cloud/Code/_scripts/uitk',
    r'O:/Cloud/Code/_scripts/mayatk',
    r'O:/Cloud/Code/_scripts/tentacle',
    r'O:/Cloud/Code/_scripts/tentacle/test',
    r'O:/Cloud/Code/_scripts/tentacle/test/slots',
):
    if p not in sys.path:
        sys.path.insert(0, p)

import __main__ as _main
_main._tentacle_test_complete = False
_main._tentacle_test_passed = False
_main._tentacle_test_summary = ''

try:
    buf = io.StringIO()

    class _Tee:
        def __init__(self, *streams): self._s = streams
        def write(self, t):
            for s in self._s:
                try: s.write(t)
                except Exception: pass
        def flush(self):
            for s in self._s:
                try: s.flush()
                except Exception: pass

    stream = _Tee(sys.__stdout__, buf)
    ts = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    stream.write('\n' + '='*70 + '\n')
    stream.write('Tentacle Test Suite (in Maya GUI)\n')
    stream.write('='*70 + '\n')
    stream.write(f'Started: {ts}\n')
    stream.write('='*70 + '\n')

    loader = unittest.TestLoader()
    suite = loader.discover(
        start_dir=r'O:/Cloud/Code/_scripts/tentacle/test',
        pattern='test_*.py',
        top_level_dir=r'O:/Cloud/Code/_scripts/tentacle/test',
    )
    slot_suite = loader.discover(
        start_dir=r'O:/Cloud/Code/_scripts/tentacle/test/slots',
        pattern='test_*.py',
        top_level_dir=r'O:/Cloud/Code/_scripts/tentacle/test/slots',
    )
    suite.addTests(slot_suite)

    t0 = time.perf_counter()
    runner = unittest.TextTestRunner(stream=stream, verbosity=1)
    result = runner.run(suite)
    duration = time.perf_counter() - t0

    tests_run = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    skipped = len(result.skipped)
    passed = tests_run - failures - errors - skipped
    success = failures == 0 and errors == 0
    status = 'PASSED' if success else 'FAILED'
    summary = (
        f'{status}: {tests_run} tests, {passed} passed, '
        f'{failures} failed, {errors} errors, '
        f'{skipped} skipped ({duration:.2f}s)'
    )

    stream.write('\n' + '='*70 + '\n')
    stream.write(summary + '\n')
    stream.write('='*70 + '\n')

    if result.failures or result.errors:
        stream.write('\nDETAILED FAILURES AND ERRORS:\n')
        stream.write('-'*70 + '\n')
        for t, tb in result.failures:
            stream.write(f'\nFAILED: {t}\n{tb}\n')
        for t, tb in result.errors:
            stream.write(f'\nERROR: {t}\n{tb}\n')

    with open(r'O:/Cloud/Code/_scripts/tentacle/test/temp_tests/_in_maya_results.txt', 'w', encoding='utf-8') as f:
        f.write(buf.getvalue())
        f.write('\n--- METRICS ---\n')
        f.write(f'tests={tests_run}\nfailures={failures}\n'
                f'errors={errors}\nskipped={skipped}\n'
                f'passed={passed}\n')

    _main._tentacle_test_summary = summary
    _main._tentacle_test_passed = success
except Exception:
    tb = traceback.format_exc()
    try:
        with open(r'O:/Cloud/Code/_scripts/tentacle/test/temp_tests/_in_maya_results.txt', 'w', encoding='utf-8') as f:
            f.write('UNHANDLED ERROR IN TEST DISPATCHER\n')
            f.write(tb)
    except Exception:
        pass
    sys.__stderr__.write(tb)
finally:
    _main._tentacle_test_complete = True
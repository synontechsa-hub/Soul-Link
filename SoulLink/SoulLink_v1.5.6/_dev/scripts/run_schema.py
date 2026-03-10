import traceback
import runpy

try:
    runpy.run_path(
        r'd:\Coding\SynonTech\SoulLink\SoulLink_v1.5.6\_dev\scripts\create_schema_v156.py')
except Exception as e:
    with open('pytest_error.log', 'w', encoding='utf-8') as f:
        traceback.print_exc(file=f)

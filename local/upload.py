import os
import sys
import requests

if len(sys.argv) < 3:
	print('Usage: python upload.py <file_path> <app_url>')
	print('Example: python upload.py data/phd_isr_res_filtered.json https://your-app.herokuapp.com')
	sys.exit(1)

file_path = sys.argv[1]
app_url = sys.argv[2].rstrip('/')
admin_key = os.environ.get('ADMIN_KEY', '')

if not admin_key:
	print('Error: ADMIN_KEY environment variable not set')
	sys.exit(1)

if not os.path.exists(file_path):
	print(f'File not found: {file_path}')
	sys.exit(1)

dest = '/app/data/phd_isr_res_filtered.json'
with open(file_path, 'rb') as src:
	with open(dest, 'wb') as dst:
		dst.write(src.read())
print(f'Copied to {dest}')

response = requests.post(
	f'{app_url}/api/admin/reload',
	headers={'x-admin-key': admin_key},
	timeout=30,
)
print(f'Reload response ({response.status_code}): {response.json()}')

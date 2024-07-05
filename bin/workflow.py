#!/usr/bin/env python3

import asyncio
import os
import signal
import subprocess

import env



def get_run_name(workflow):
	return 'workflow-%s-%04d' % (workflow['_id'], workflow['n_attempts'])



def run_workflow(workflow, attempt, output_dir, resume):
	# save current directory
	prev_dir = os.getcwd()

	# change to workflow directory
	os.chdir(output_dir)

	# prepare command line arguments
	run_name = get_run_name(workflow)

	if env.NXF_EXECUTOR == 'k8s':
		args = [
			'nextflow',
			'-log', os.path.join(output_dir, 'nextflow.log'),
			'kuberun',
			workflow['pipeline'],
			'-ansi-log', 'false',
			'-latest',
			'-name', run_name,
			'-profile', workflow['profiles'],
			'-revision', workflow['revision'],
			'-volume-mount', env.PVC_NAME
		]

	elif env.NXF_EXECUTOR == 'pbspro':
		args = [
			'nextflow',
			'-log', os.path.join(output_dir, 'nextflow.log'),
			'run',
			workflow['pipeline'],
			'-ansi-log', 'false',
			'-latest',
			'-name', run_name,
			'-profile', workflow['profiles'],
			'-revision', workflow['revision']
		]

	elif env.NXF_EXECUTOR == 'local':
		args = [
			'nextflow',
			'-log', os.path.join(output_dir, 'nextflow.log'),
			'run',
			workflow['pipeline'],
			'-revision', workflow['revision'],
			'-latest',
			'-name', run_name,
			'-profile', workflow['profiles'],
			'-ansi-log', 'false'
		]

	# add params
	for param in attempt['inputs']:
		pname = param['name']
		if param['type'] == 'directory-path' or param['type'] == 'file-path':
			pval = os.path.join( env.DATASETS_DIR, param['value'])
		else:
			pval = param['value']
		args += [pname, pval]

	# add the output directory
	args += ['--outdir', output_dir]

	# add resume option if specified
	if resume:
		args += ['-resume']

	# launch workflow asynchronously
	proc = subprocess.Popen(
		args,
		stdout=open('.workflow.log', 'w'),
		stderr=subprocess.STDOUT
	)

	# return to original directory
	os.chdir(prev_dir)

	return proc



def save_output(workflow, attempt, output_dir):
	cmd = os.path.join( os.getcwd(), 'scripts/kube-save.sh')
	return subprocess.Popen(
		[cmd, str(workflow['_id']), str(attempt['id']), output_dir],
		stdout=subprocess.PIPE,
		stderr=subprocess.STDOUT
	)



async def set_property(db, workflow, key, value):
	workflow[key] = value
	# get last attempt because has to be the running one
	n_attempt = int(workflow['n_attempts'] - 1)
	if key in workflow['attempts'][n_attempt]:
		workflow['attempts'][n_attempt][key] = value
	await db.workflow_update(workflow['_id'], workflow)



async def launch_async(db, workflow, attempt, output_dir, resume):
	# re-initialize database backend
	db.initialize()

	# start workflow
	proc = run_workflow(workflow, attempt, output_dir, resume)
	proc_pid = proc.pid
	
	print('%d: saving workflow pid...' % (proc_pid))

	# save workflow pid
	await set_property(db, workflow, 'pid', proc.pid)

	print('%d: waiting for workflow to finish...' % (proc_pid))

	# wait for workflow to complete
	if proc.wait() == 0:
		print('%d: workflow completed' % (proc_pid))
		await set_property(db, workflow, 'status', 'completed') # re-updated the previous updating in the "server.py" methods
	else:
		print('%d: workflow failed' % (proc_pid))
		await set_property(db, workflow, 'status', 'failed') # re-updated the previous updating in the "server.py" methods
		return # return to don't save the data

	print('%d: saving output data...' % (proc_pid))

	# save output data
	proc = save_output(workflow, attempt, output_dir)

	proc_out, _ = proc.communicate()
	print(proc_out.decode('utf-8'))

	if proc.wait() == 0:
		print('%d: save output data completed' % (proc_pid))
	else:
		print('%d: save output data failed' % (proc_pid))



def launch(db, workflow, attempt, output_dir, resume):
	asyncio.run(launch_async(db, workflow, attempt, output_dir, resume))



def cancel(workflow):
	# terminate child process
	if workflow['pid'] != -1:
		try:
			os.kill(workflow['pid'], signal.SIGINT)
		except ProcessLookupError:
			pass

	# delete pods if relevant
	if env.NXF_EXECUTOR == 'k8s':
		proc = subprocess.Popen(
			['scripts/kube-cancel.sh', get_run_name(workflow)],
			stdout=subprocess.PIPE,
			stderr=subprocess.STDOUT
		)
		proc_out, _ = proc.communicate()
		print(proc_out.decode('utf-8'))

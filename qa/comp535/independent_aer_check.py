"""Independent Qiskit Aer validation of BB84 with classical basis sifting."""
import json
from math import sqrt
import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error

def one_block(n, e, mode, p, rng):
    a = rng.integers(0, 2, size=n)
    alpha = rng.integers(0, 2, size=n)
    beta = rng.integers(0, 2, size=n)
    attacked = np.zeros(n, dtype=bool)
    eb = np.zeros(n, dtype=int)
    if mode in ('random', 'fixedZ'):
        attacked = rng.random(n) < p
    elif mode == 'burst':
        length = int(round(n*p))
        start = int(rng.integers(0, n-length+1)) if length < n else 0
        attacked[start:start+length] = True
    elif mode != 'none':
        raise ValueError(mode)
    if mode in ('random', 'burst'):
        eb = rng.integers(0, 2, size=n)
    q = QuantumRegister(n, 'q')
    eve = ClassicalRegister(n, 'eve')
    bob = ClassicalRegister(n, 'bob')
    qc = QuantumCircuit(q, eve, bob)
    for i in range(n):
        if a[i]: qc.x(q[i])
        if alpha[i]: qc.h(q[i])
        qc.id(q[i])
        if attacked[i]:
            if eb[i]: qc.h(q[i])
            qc.measure(q[i], eve[i])
            qc.reset(q[i])
            with qc.if_test((eve[i], 1)): qc.x(q[i])
            if eb[i]: qc.h(q[i])
        if beta[i]: qc.h(q[i])
        qc.measure(q[i], bob[i])
    noise = NoiseModel()
    if e: noise.add_all_qubit_quantum_error(depolarizing_error(2*e, 1), ['id'])
    sim = AerSimulator(method='stabilizer', noise_model=noise if e else None, max_parallel_threads=1)
    result = sim.run(qc, shots=1, seed_simulator=int(rng.integers(1,2**31))).result()
    assert result.success, repr(result)
    bitstr = next(iter(result.get_counts(qc))).split()
    assert len(bitstr) == 2, bitstr
    measured = np.fromiter((int(x) for x in bitstr[0][::-1]), dtype=int)
    good = alpha==beta
    err = (a[good] != measured[good]).astype(int)
    return err, alpha[good], np.flatnonzero(good)

def summary(mode, e, p, seed, blocks=35, n=256):
    rng=np.random.default_rng(seed)
    k=bits=kz=nz=kx=nx=0
    ds=[]
    for _ in range(blocks):
        err,b,idx=one_block(n,e,mode,p,rng)
        k+=int(err.sum());bits+=len(err)
        kz+=int(err[b==0].sum());nz+=int((b==0).sum())
        kx+=int(err[b==1].sum());nx+=int((b==1).sum())
        rate=float(err.mean())
        j=np.minimum(7,idx*8//n)
        c=np.bincount(j,weights=err,minlength=8)
        v=np.bincount(j,minlength=8)
        mask=v>0
        if mask.sum()>1 and 0<rate<1:
            ds.append(float((((c[mask]-v[mask]*rate)**2)/(v[mask]*rate*(1-rate))).sum()/(mask.sum()-1)))
    return dict(mode=mode,e=e,p=p,n=n,blocks=blocks,bits=bits,Q=k/bits,QZ=kz/nz,QX=kx/nx,D=float(np.mean(ds)) if ds else 0.0)

def main():
    import qiskit,qiskit_aer
    conditions=[('none',0.,0.,111),('none',.05,0.,112),
      ('random',0.,1.,113),('random',0.,.4,114),
      ('fixedZ',0.,.4,115),('burst',0.,.4,116),
      ('random',.03,.4,117)]
    expected=[0.,.05,.25,.1,.1,.1,.03+(.4/4)*(1-2*.03)]
    rows=[summary(*cond) for cond in conditions]
    for r,mu in zip(rows,expected):
        se=sqrt(max(mu*(1-mu),.001)/r['bits'])
        assert abs(r['Q']-mu)<max(.018,5*se),(r,mu,se)
    assert rows[0]['Q']==0,rows[0]
    assert rows[4]['QZ']==0 and abs(rows[4]['QX']-.2)<.035,rows[4]
    assert rows[5]['D']>1.35*rows[3]['D'],(rows[5],rows[3])
    result=dict(success=True,qiskit=qiskit.__version__,qiskit_aer=qiskit_aer.__version__,rows=rows)
    print('INDEPENDENT AER CHECK PASSED')
    print(json.dumps(result,indent=2))
    with open('independent_aer_results.json','w') as fh: json.dump(result,fh,indent=2)
if __name__=='__main__':main()

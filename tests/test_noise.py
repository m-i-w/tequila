from tequila.circuit import gates
from tequila.objective import ExpectationValue
from tequila.objective.objective import Variable
from tequila.hamiltonian import paulis
from tequila import simulate
import tequila
from tequila.circuit.noise import BitFlip,PhaseDamp,PhaseFlip,AmplitudeDamp,PhaseAmplitudeDamp,DepolarizingError
import numpy
import pytest
import tequila.simulators.simulator_api

@pytest.mark.parametrize("simulator", [tequila.simulators.simulator_api.pick_backend('qiskit')])
@pytest.mark.parametrize("p", numpy.random.uniform(0.,1.,1))
def test_bit_flip(simulator, p):


    qubit = 0
    H = paulis.Qm(qubit)
    U = gates.X(target=qubit)
    O = ExpectationValue(U=U, H=H)
    NM=BitFlip(p,['x'])
    E = simulate(O,backend=simulator,samples=100000,noise_model=NM)
    assert (numpy.isclose(E, 1.0-p, atol=1.e-2))



@pytest.mark.parametrize("simulator", [tequila.simulators.simulator_api.pick_backend('qiskit')])
@pytest.mark.parametrize("p", numpy.random.uniform(0.,1.,1))
def test_phase_flip(simulator, p):


    qubit = 0
    H = paulis.Qm(qubit)
    U = gates.Y(target=qubit)
    O = ExpectationValue(U=U, H=H)
    NM=PhaseFlip(p,['y'])
    E = simulate(O,backend=simulator,samples=100000,noise_model=NM)
    assert (numpy.isclose(E, 1.0-p, atol=1.e-2))


@pytest.mark.parametrize("simulator", [tequila.simulators.simulator_api.pick_backend('qiskit')])
@pytest.mark.parametrize("p", numpy.random.uniform(0.,1.,1))
def test_phase_damp(simulator, p):


    qubit = 0
    H = paulis.Qm(qubit)
    U = gates.H(target=qubit)
    O = ExpectationValue(U=U, H=H)
    NM=PhaseDamp(p,['h'])
    E = simulate(O,backend=simulator,samples=100000,noise_model=NM)
    assert (numpy.isclose(E, 0.5, atol=1.e-2))


@pytest.mark.parametrize("simulator", [tequila.simulators.simulator_api.pick_backend('qiskit')])
@pytest.mark.parametrize("p", numpy.random.uniform(0.,1.,1))
def test_amp_damp(simulator, p):


    qubit = 0
    H = (0.5)*(paulis.I(0)-paulis.Z(0))
    U = gates.X(target=qubit)
    O = ExpectationValue(U=U, H=H)
    NM=AmplitudeDamp(p,['x'])
    E = simulate(O,backend=simulator,samples=100000,noise_model=NM)
    assert (numpy.isclose(E, 1-p, atol=1.e-2))


@pytest.mark.parametrize("simulator", [tequila.simulators.simulator_api.pick_backend('qiskit')])
@pytest.mark.parametrize("p", numpy.random.uniform(0.,1.,1))
def test_phase_amp_damp(simulator, p):


    qubit = 0
    H = paulis.Z(0)
    U = gates.X(target=qubit)
    O = ExpectationValue(U=U, H=H)
    NM=PhaseAmplitudeDamp(p,1-p,['x'])
    E = simulate(O,backend=simulator,samples=100000,noise_model=NM)
    assert (numpy.isclose(E, -1+2*p, atol=1.e-2))

@pytest.mark.parametrize("simulator", [tequila.simulators.simulator_api.pick_backend('qiskit')])
@pytest.mark.parametrize("p", numpy.random.uniform(0.,1.,1))
@pytest.mark.parametrize('controlled',[False,True])
def test_depolarizing_error(simulator, p,controlled):

    cq=1

    qubit = 0
    H = paulis.Z(0)
    if controlled:
        U = gates.X(target=cq)+gates.X(target=qubit,control=cq)
        NM = DepolarizingError(p, ['cx'])
    else:
        U= gates.X(target=qubit)
        NM = DepolarizingError(p, ['x'])
    O = ExpectationValue(U=U, H=H)

    E = simulate(O,backend=simulator,samples=100000,noise_model=NM)
    assert (numpy.isclose(E, -1+p, atol=1.e-2))
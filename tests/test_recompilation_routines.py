from openvqe.circuit import gates
from openvqe.circuit.compiler import compile_controlled_rotation, change_basis
from numpy.random import uniform, randint
from numpy import pi, isclose
from openvqe.simulator.simulator_cirq import SimulatorCirq
from openvqe.hamiltonian import paulis
from openvqe.objective import Objective
import openvqe.simulator as simulator
import pytest
import numpy

PX = paulis.X
PY = paulis.Y
PZ = paulis.Z

def get_all_wfn_simulators():
    simulators = []
    if simulator.has_cirq:
        simulators.append(simulator.SimulatorCirq)
    if simulator.has_pyquil:
        simulators.append(simulator.SimulatorPyquil)
    if simulator.has_qulacs:
        simulators.append(simulator.SimulatorQulacs)
    return simulators

@pytest.mark.parametrize('simulator', get_all_wfn_simulators())
@pytest.mark.parametrize('angle', numpy.random.uniform(0,2*numpy.pi,3))
@pytest.mark.parametrize('axis', ['X', 'Y', 'Z'])
def test_exponential_pauli_wfn(simulator, angle, axis):

    U1 = gates.RotationGate(axis=axis, angle=angle, target=0)
    U2 = gates.ExpPauli(paulistring=axis+"(0)", angle=angle)

    wfn1 = simulator().simulate_wavefunction(U1).wavefunction
    wfn2 = simulator().simulate_wavefunction(U2).wavefunction

    assert(wfn1==wfn2)



def test_controlled_rotations():
    angles = uniform(0, 2 * pi, 5)
    gs = [gates.Rx, gates.Ry, gates.Rz]
    for angle in angles:
        for gate in gs:
            qubit = randint(0, 1)
            control = randint(2, 3)
            U = gates.X(target=control) * gate(target=qubit, control=control, angle=angle)
            RCU = compile_controlled_rotation(gate=U)
            wfn1 = SimulatorCirq().simulate_wavefunction(abstract_circuit=U, initial_state=0).wavefunction
            wfn2 = SimulatorCirq().simulate_wavefunction(abstract_circuit=RCU, initial_state=0).wavefunction
            assert (wfn1 == wfn2)


def test_basis_change():
    for angle in list(uniform(0, 2 * pi, 5)):
        EX = SimulatorCirq().simulate_objective(
            objective=Objective(unitaries=[gates.Rx(target=0, angle=angle)], observable=PX(0)))
        EY = SimulatorCirq().simulate_objective(
            objective=Objective(unitaries=[gates.Rx(target=0, angle=angle)], observable=PY(0)))
        EZ = SimulatorCirq().simulate_objective(
            objective=Objective(unitaries=[gates.Rx(target=0, angle=angle)], observable=PZ(0)))

        EXX = SimulatorCirq().simulate_objective(
            objective=Objective(unitaries=[gates.Rx(target=0, angle=angle) * change_basis(target=0, axis=0)],
                                observable=PZ(0)))
        EYY = SimulatorCirq().simulate_objective(
            objective=Objective(unitaries=[gates.Rx(target=0, angle=angle) * change_basis(target=0, axis=1)],
                                observable=PZ(0)))
        EZZ = SimulatorCirq().simulate_objective(
            objective=Objective(unitaries=[gates.Rx(target=0, angle=angle) * change_basis(target=0, axis=2)],
                                observable=PZ(0)))

        assert (isclose(EX, EXX, atol=1.e-4))
        assert (isclose(EY, EYY, atol=1.e-4))
        assert (isclose(EZ, EZZ, atol=1.e-4))

    for i,gate in enumerate([gates.Rx, gates.Ry, gates.Rz]):
        angle = uniform(0, 2*pi)
        U1 = gate(target=0, angle=angle)
        U2 = change_basis(target=0, axis=i)*gates.Rz(target=0, angle=angle)*change_basis(target=0, axis=i, daggered=True)
        wfn1 = SimulatorCirq().simulate_wavefunction(abstract_circuit=U1)
        wfn2 = SimulatorCirq().simulate_wavefunction(abstract_circuit=U2)
        assert(wfn1.wavefunction == wfn2.wavefunction)
        wfn1 = SimulatorCirq().simulate_wavefunction(abstract_circuit=U1, initial_state=1)
        wfn2 = SimulatorCirq().simulate_wavefunction(abstract_circuit=U2, initial_state=1)
        assert(wfn1.wavefunction == wfn2.wavefunction)


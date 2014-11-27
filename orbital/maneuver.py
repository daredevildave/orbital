from copy import copy

from scipy.constants import pi
from orbital.utilities import (
    elements_for_apsides, saved_state, mean_anomaly_from_true,
    mean_anomaly_from_eccentric)
import orbital.utilities as ou

__all__ = [
    'SetApocenterRadiusTo',
    'SetPericenterRadiusTo',
    'SetApocenterAltitudeTo',
    'SetPericenterAltitudeTo',
    'ChangeApocenterBy',
    'ChangePericenterBy',
    'SetPericenterHere',
    'Maneuver']


class Operation:
    """Base class for orbital operations.

    Maneuvers are used by the user to construct operations, because operations
    contain assumptions about when they can be used. For example, it would not
    make sense to apply an operation to raise the apocenter, if the anomaly was
    not currently at the pericenter.

    Subclasses can implement an __apply__ method as a shortcut method, rather
    than applying a velocity change directly, for example.
    """


class ImpulseOperation(Operation):
    def velocity_delta(self):
        raise NotImplementedError(
            'Subclasses of {}.{} must implement {}'
            .format(__name__, __class__.__name__, self.velocity_delta.__name__))


class TimeOperation(Operation):
    def time_delta(self, orbit):
        """Return the time delta to propagate the orbit by.

        :param orbit: Orbit
        :type orbit: :py:class:`orbital.elements.KeplerianElements`
        """
        raise NotImplementedError(
            'Subclasses of {}.{} must implement {}'
            .format(__name__, __class__.__name__, self.time_delta.__name__))


class SetApocenterRadiusTo(ImpulseOperation):
    def __init__(self, apocenter_radius):
        self.apocenter_radius = apocenter_radius

    def __apply__(self, orbit):
        """This operation can be applied directly without using velocity delta."""
        a, e = elements_for_apsides(self.apocenter_radius,
                                    orbit.pericenter_radius)
        orbit.a = a
        orbit.e = e

    def velocity_delta(self, orbit):
        with saved_state(orbit):
            # get velocity at pericenter
            orbit.M = 0
            old_velocity = orbit.v

            a, e = elements_for_apsides(self.apocenter_radius,
                                        orbit.pericenter_radius)
            orbit.a = a
            orbit.e = e

            new_velocity = orbit.v

        return new_velocity - old_velocity

    def __repr__(self):
        return '{}({!r})'.format(__class__.__name__, self.apocenter_radius)


class SetApocenterAltitudeTo(ImpulseOperation):
    def __init__(self, apocenter_altitude):
        self.apocenter_altitude = apocenter_altitude

    def __apply__(self, orbit):
        """This operation can be applied directly without using velocity delta."""
        apocenter_radius = orbit.body.mean_radius + self.apocenter_altitude
        a, e = elements_for_apsides(apocenter_radius,
                                    orbit.pericenter_radius)
        orbit.a = a
        orbit.e = e

    def velocity_delta(self, orbit):
        with saved_state(orbit):
            # get velocity at pericenter
            orbit.M = 0
            old_velocity = orbit.v

            apocenter_radius = orbit.body.mean_radius + self.apocenter_altitude
            a, e = elements_for_apsides(apocenter_radius,
                                        orbit.pericenter_radius)
            orbit.a = a
            orbit.e = e

            new_velocity = orbit.v

        return new_velocity - old_velocity

    def __repr__(self):
        return '{}({!r})'.format(__class__.__name__, self.apocenter_altitude)


class ChangeApocenterBy(ImpulseOperation):
    def __init__(self, delta):
        self.delta = delta

    def __apply__(self, orbit):
        """This operation can be applied directly without using velocity delta."""
        a, e = elements_for_apsides(orbit.apocenter_radius + self.delta,
                                    orbit.pericenter_radius)
        orbit.a = a
        orbit.e = e

    def velocity_delta(self, orbit):
        with saved_state(orbit):
            # get velocity at pericenter
            orbit.M = 0
            old_velocity = orbit.v

            a, e = elements_for_apsides(orbit.apocenter_radius + self.delta,
                                        orbit.pericenter_radius)
            orbit.a = a
            orbit.e = e

            new_velocity = orbit.v

        return new_velocity - old_velocity

    def __repr__(self):
        return '{}({!r})'.format(__class__.__name__, self.delta)


class SetPericenterRadiusTo(ImpulseOperation):
    def __init__(self, pericenter_radius):
        self.pericenter_radius = pericenter_radius

    def __apply__(self, orbit):
        """This operation can be applied directly without using velocity delta."""
        a, e = elements_for_apsides(orbit.apocenter_radius,
                                    self.pericenter_radius)
        orbit.a = a
        orbit.e = e

    def velocity_delta(self, orbit):
        with saved_state(orbit):
            # get velocity at apocenter
            orbit.M = pi
            old_velocity = orbit.v

            a, e = elements_for_apsides(orbit.apocenter_radius,
                                        self.pericenter_radius)
            orbit.a = a
            orbit.e = e

            new_velocity = orbit.v

        return new_velocity - old_velocity

    def __repr__(self):
        return '{}({!r})'.format(__class__.__name__, self.pericenter_radius)


class SetPericenterAltitudeTo(ImpulseOperation):
    def __init__(self, pericenter_altitude):
        self.pericenter_altitude = pericenter_altitude

    def __apply__(self, orbit):
        """This operation can be applied directly without using velocity delta."""
        pericenter_radius = orbit.body.mean_radius + self.pericenter_altitude
        a, e = elements_for_apsides(orbit.apocenter_radius,
                                    pericenter_radius)
        orbit.a = a
        orbit.e = e

    def velocity_delta(self, orbit):
        with saved_state(orbit):
            # get velocity at apocenter
            orbit.M = pi
            old_velocity = orbit.v

            pericenter_radius = orbit.body.mean_radius + self.pericenter_altitude
            a, e = elements_for_apsides(orbit.apocenter_radius,
                                        pericenter_radius)
            orbit.a = a
            orbit.e = e

            new_velocity = orbit.v

        return new_velocity - old_velocity

    def __repr__(self):
        return '{}({!r})'.format(__class__.__name__, self.pericenter_altitude)


class ChangePericenterBy(ImpulseOperation):
    def __init__(self, delta):
        self.delta = delta

    def __apply__(self, orbit):
        """This operation can be applied directly without using velocity delta."""
        a, e = elements_for_apsides(orbit.apocenter_radius,
                                    orbit.pericenter_radius + self.delta)
        orbit.a = a
        orbit.e = e

    def velocity_delta(self, orbit):
        with saved_state(orbit):
            # get velocity at apocenter
            orbit.M = pi
            old_velocity = orbit.v

            a, e = elements_for_apsides(orbit.apocenter_radius,
                                        orbit.pericenter_radius + self.delta)
            orbit.a = a
            orbit.e = e

            new_velocity = orbit.v

        return new_velocity - old_velocity

    def __repr__(self):
        return '{}({!r})'.format(__class__.__name__, self.delta)


class PropagateAnomalyTo(TimeOperation):
    """Operation for propagating to time in future where anomaly is equal to
    value passed in.

    One (and only one) of these parameters must be passed in:

    :param float M: Mean anomaly
    :param float E: Eccentric anomaly
    :param float f: True anomaly
    """
    def __init__(self, **kwargs):
        # The defaults
        valid_args = set(['M', 'E', 'f'])

        extra_args = set(kwargs.keys()) - valid_args

        # Check for invalid keywords
        if extra_args:
            raise TypeError('Invalid kwargs: ' + ', '.join(list(extra_args)))

        # Ensure a valid keyword was passed
        if not kwargs:
            raise TypeError('Required argument missing.')

        # Ensure only one keyword was passed, but allow other 2 anomaly
        # parameters to be None.
        if sum(1 for x in kwargs.values() if x is not None) > 1:
            raise ValueError('Only one anomaly parameter can be propagated.')

        # Now remove the superfluous None values.
        kwargs = {key: value for key, value in kwargs.items() if value is not None}

        self.key, self.anomaly = kwargs.popitem()

    def time_delta(self, orbit):

        if self.key == 'f':
            M = mean_anomaly_from_true(orbit.e, self.anomaly)
        elif self.key == 'E':
            M = mean_anomaly_from_eccentric(orbit.e, self.anomaly)
        elif self.key == 'M':
            M = self.anomaly

        # Propagate one orbit if destination is 'behind' current state.
        if M < orbit.M:
            M += 2 * pi

        return (M - orbit.M) / orbit.n

    def __repr__(self):
        return '{}({key}={anomaly!r})'.format(__class__.__name__, key=self.key,
                                              anomaly=self.anomaly)


class PropagateAnomalyBy(TimeOperation):
    """Operation for propagating anomaly by a given amount.

    One (and only one) of these parameters must be passed in:

    :param float M: Mean anomaly
    :param float E: Eccentric anomaly
    :param float f: True anomaly
    """
    def __init__(self, **kwargs):
        # The defaults
        valid_args = set(['M', 'E', 'f'])

        extra_args = set(kwargs.keys()) - valid_args

        # Check for invalid keywords
        if extra_args:
            raise TypeError('Invalid kwargs: ' + ', '.join(list(extra_args)))

        # Ensure a valid keyword was passed
        if not kwargs:
            raise TypeError('Required argument missing.')

        # Ensure only one keyword was passed, but allow other 2 anomaly
        # parameters to be None.
        if sum(1 for x in kwargs.values() if x is not None) > 1:
            raise ValueError('Only one anomaly parameter can be propagated.')

        # Now remove the superfluous None values.
        kwargs = {key: value for key, value in kwargs.items() if value is not None}

        self.key, self.anomaly = kwargs.popitem()

    def time_delta(self, orbit):

        if self.key == 'f':
            orbits, f = ou.divmod(self.anomaly, 2 * pi)
            M = mean_anomaly_from_true(orbit.e, f)
            return orbits * orbit.T + M / orbit.n
        elif self.key == 'E':
            orbits, E = ou.divmod(self.anomaly, 2 * pi)
            M = mean_anomaly_from_eccentric(orbit.e, E)
            return orbits * orbit.T + M / orbit.n
        elif self.key == 'M':
            return self.anomaly / orbit.n

    def __repr__(self):
        return '{}({key}={anomaly!r})'.format(__class__.__name__, key=self.key,
                                              anomaly=self.anomaly)


class Circularise(ImpulseOperation):
    """Circularise an orbit."""
    def __init__(self, raise_pericenter=True):
        """Assumptions: anomaly is at the correct apside."""
        self.raise_pericenter = raise_pericenter

    def __apply__(self, orbit):
        if self.raise_pericenter:
            radius = orbit.apocenter_radius
        else:
            radius = orbit.pericenter_radius

        a, e = elements_for_apsides(radius, radius)
        orbit.a = a
        orbit.e = e

    def velocity_delta(self, orbit):
        with saved_state(orbit):
            if self.raise_pericenter:
                orbit.M = pi
                radius = orbit.apocenter_radius
            else:
                orbit.M = 0
                radius = orbit.pericenter_radius

            old_velocity = orbit.v

            a, e = elements_for_apsides(radius, radius)
            orbit.a = a
            orbit.e = e

            new_velocity = orbit.v

            return new_velocity - old_velocity

    def __repr__(self):
        return '{}(raise_pericenter={!r})'.format(__class__.__name__,
                                                  self.raise_pericenter)


class SetPericenterHere(Operation):
    """For a circular orbit, set the pericenter position (in preparation for
        a maneuver to an elliptical orbit.
    """
    def __apply__(self, orbit):
        """Assumptions: orbit is circular"""
        orbit.arg_pe = orbit.f
        orbit.f = 0

    def __repr__(self):
        return '{}()'.format(__class__.__name__)


class Maneuver:
    """Todo: Each maneuver will contain a list of operations, which are therefore
    independent of orbit and calculated at the time the maneuver is applied.
    """
    def __init__(self, operations):
        if not isinstance(operations, list):
            operations = [operations]

        self.operations = operations

    @classmethod
    def set_apocenter_radius_to(cls, apocenter_radius):
        operations = [
            PropagateAnomalyTo(M=0),
            SetApocenterRadiusTo(apocenter_radius)]
        return cls(operations)

    @classmethod
    def set_pericenter_radius_to(cls, pericenter_radius):
        operations = [
            PropagateAnomalyTo(M=pi),
            SetPericenterRadiusTo(pericenter_radius)]
        return cls(operations)

    @classmethod
    def set_apocenter_altitude_to(cls, apocenter_altitude):
        operations = [
            PropagateAnomalyTo(M=0),
            SetApocenterAltitudeTo(apocenter_altitude)]
        return cls(operations)

    @classmethod
    def set_pericenter_altitude_to(cls, pericenter_altitude):
        operations = [
            PropagateAnomalyTo(M=pi),
            SetPericenterAltitudeTo(pericenter_altitude)]
        return cls(operations)

    @classmethod
    def change_apocenter_by(cls, delta):
        operations = [
            PropagateAnomalyTo(M=0),
            ChangeApocenterBy(delta)]
        return cls(operations)

    @classmethod
    def change_pericenter_by(cls, delta):
        operations = [
            PropagateAnomalyTo(M=pi),
            ChangePericenterBy(delta)]
        return cls(operations)

    @classmethod
    def hohmann_transfer_to(cls, orbit):
        operations = [
            SetPericenterHere(),
            SetApocenterRadiusTo(orbit.apocenter_radius),
            PropagateAnomalyTo(M=pi),
            Circularise()]
        return cls(operations)

    @classmethod
    def bielliptic_transfer(cls):
        raise NotImplementedError

    def __apply__(self, orbit):
        for operation in self.operations:
            if hasattr(operation, '__apply__') and callable(getattr(operation, '__apply__')):
                operation.__apply__(orbit)
            elif isinstance(operation, ImpulseOperation):
                orbit.v += operation.velocity_delta(orbit)
            elif isinstance(operation, TimeOperation):
                orbit.t += operation.time_delta(orbit)

    def __repr__(self):
        return '{}({!r})'.format(__class__.__name__, self.operations)

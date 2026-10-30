"""
Unit tests for FIFO DirectionQueue and IntersectionQueueManager.
"""
import pytest
from src.models import Direction, Vehicle, VehicleType
from src.queue_manager import DirectionQueue, IntersectionQueueManager


def test_enqueue_and_fifo_order():
    """Verify vehicles are enqueued and dequeued strictly in FIFO order."""
    dq = DirectionQueue(Direction.NORTH)
    assert len(dq) == 0
    assert dq.is_empty()

    v1 = Vehicle(id="V1", direction=Direction.NORTH, arrival_time=10.0)
    v2 = Vehicle(id="V2", direction=Direction.NORTH, arrival_time=15.0)
    v3 = Vehicle(id="V3", direction=Direction.NORTH, arrival_time=20.0)

    dq.enqueue(v1)
    dq.enqueue(v2)
    dq.enqueue(v3)

    assert len(dq) == 3
    assert not dq.is_empty()
    assert dq.peek().id == "V1"

    # Dequeue first
    out1 = dq.dequeue(current_time=25.0)
    assert out1 is not None
    assert out1.id == "V1"
    assert out1.wait_time == 15.0  # 25 - 10
    assert len(dq) == 2

    # Dequeue second
    out2 = dq.dequeue(current_time=30.0)
    assert out2 is not None
    assert out2.id == "V2"
    assert out2.wait_time == 15.0  # 30 - 15

    # Dequeue third
    out3 = dq.dequeue(current_time=35.0)
    assert out3 is not None
    assert out3.id == "V3"
    assert out3.wait_time == 15.0  # 35 - 20

    # Dequeue from empty
    out4 = dq.dequeue(current_time=40.0)
    assert out4 is None
    assert len(dq) == 0


def test_queue_length_nonnegative():
    """Verify queue lengths never become negative under repeated dequeues."""
    dq = DirectionQueue(Direction.SOUTH)
    for _ in range(5):
        assert dq.dequeue(current_time=10.0) is None
        assert len(dq) >= 0

    batch = dq.dequeue_batch(10, current_time=10.0)
    assert batch == []
    assert len(dq) == 0


def test_batch_dequeue():
    """Verify batch dequeue correctly handles partial and full capacity."""
    dq = DirectionQueue(Direction.EAST)
    for i in range(5):
        dq.enqueue(Vehicle(id=f"V-{i}", direction=Direction.EAST, arrival_time=0.0))

    # Request batch of 3
    served_batch = dq.dequeue_batch(3, current_time=10.0)
    assert len(served_batch) == 3
    assert [v.id for v in served_batch] == ["V-0", "V-1", "V-2"]
    assert len(dq) == 2

    # Request batch larger than remaining
    served_batch2 = dq.dequeue_batch(5, current_time=20.0)
    assert len(served_batch2) == 2
    assert [v.id for v in served_batch2] == ["V-3", "V-4"]
    assert len(dq) == 0


def test_emergency_flag_detection():
    """Verify queue correctly detects presence and count of emergency vehicles."""
    dq = DirectionQueue(Direction.WEST)
    assert not dq.has_emergency()
    assert dq.emergency_count() == 0

    dq.enqueue(Vehicle(id="C1", direction=Direction.WEST, arrival_time=0.0, is_emergency=False))
    assert not dq.has_emergency()

    dq.enqueue(Vehicle(id="EMG1", direction=Direction.WEST, arrival_time=5.0, is_emergency=True, vehicle_type=VehicleType.EMERGENCY))
    assert dq.has_emergency()
    assert dq.emergency_count() == 1

    # Dequeue normal car
    dq.dequeue(current_time=10.0)
    assert dq.has_emergency()

    # Dequeue emergency vehicle
    dq.dequeue(current_time=15.0)
    assert not dq.has_emergency()
    assert dq.emergency_count() == 0


def test_intersection_queue_manager_dispatch():
    """Verify vehicles are routed to their respective directional approach queue."""
    iqm = IntersectionQueueManager()
    iqm.enqueue_vehicle(Vehicle(id="N1", direction=Direction.NORTH, arrival_time=0.0))
    iqm.enqueue_vehicle(Vehicle(id="E1", direction=Direction.EAST, arrival_time=0.0))
    iqm.enqueue_vehicle(Vehicle(id="S1", direction=Direction.SOUTH, arrival_time=0.0))
    iqm.enqueue_vehicle(Vehicle(id="W1", direction=Direction.WEST, arrival_time=0.0))

    assert len(iqm.get_queue(Direction.NORTH)) == 1
    assert len(iqm.get_queue(Direction.EAST)) == 1
    assert len(iqm.get_queue(Direction.SOUTH)) == 1
    assert len(iqm.get_queue(Direction.WEST)) == 1
    assert iqm.total_waiting_vehicles() == 4
    assert iqm.max_queue_length() == 1

    lengths = iqm.get_all_queue_lengths()
    assert lengths == {"North": 1, "East": 1, "South": 1, "West": 1}

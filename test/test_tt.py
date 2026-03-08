import cocotb
from cocotb.triggers import ClockCycles, FallingEdge, RisingEdge

from cocotbext.uart import UartSink, UartSource

from .common import read_exact, start_clock_and_reset

@cocotb.test(timeout_time=10, timeout_unit="ms")
async def test_project_echo(dut):
    dut._log.info("Start")

    await start_clock_and_reset(dut)

    dut._log.info("Test project echo")

    uart_source = UartSource(dut.uart_rx, baud=115200, bits=8)
    uart_sink = UartSink(dut.uart_tx, baud=115200, bits=8)

    # Unrecognized command bytes will be echoed back
    for x in range(0x10, 0x20):
        await uart_source.write(bytes([x]))
        await uart_source.wait()

        data = await uart_sink.read()
        assert data == bytes([x]), f"Expected {x:#02x}, got {data[0]:#02x}"

@cocotb.test(timeout_time=10, timeout_unit="ms")
async def test_project_hello(dut):
    dut._log.info("Start")

    await start_clock_and_reset(dut)

    dut._log.info("Test project hello")

    uart_source = UartSource(dut.uart_rx, baud=115200, bits=8)
    uart_sink = UartSink(dut.uart_tx, baud=115200, bits=8)

    await uart_source.write(b'h')
    await uart_source.wait()

    data = await read_exact(uart_sink, 5)
    assert data == b"Erika", f"Expected 'Erika', got {data}"

@cocotb.test(timeout_time=10, timeout_unit="ms")
async def test_project_full_glitch_sequence_without_reset(dut):
    dut._log.info("Start")

    await start_clock_and_reset(dut)

    dut._log.info("Test project full glitch sequence without reset")

    uart_source = UartSource(dut.uart_rx, baud=115200, bits=8, stop_bits=1)

    await uart_source.write(b'd\x00\x12') # Set delay
    await uart_source.write(b'w\x01')     # Set width
    await uart_source.write(b'n\x02')     # Set num pulses
    await uart_source.write(b's\x00\x03') # Set pulse spacing
    await uart_source.write(b't')         # Trigger pulse

    await RisingEdge(dut.pulse_en)
    await ClockCycles(dut.clk, 1)

    for _ in range(0x12): # Delay
        await ClockCycles(dut.clk, 1)
        assert dut.pulse_out.value == 0, "Expected pulse_out to be 0"

    for _ in range(0x01): # Width
        await ClockCycles(dut.clk, 1)
        assert dut.pulse_out.value == 1, "Expected pulse_out to be 1"

    for _ in range(0x03): # Spacing
        await ClockCycles(dut.clk, 1)
        assert dut.pulse_out.value == 0, "Expected pulse_out to be 0"

    for _ in range(0x01): # Width
        await ClockCycles(dut.clk, 1)
        assert dut.pulse_out.value == 1, "Expected pulse_out to be 1"

    await ClockCycles(dut.clk, 1)
    assert dut.pulse_out.value == 0, "Expected pulse_out to be 0"

@cocotb.test(timeout_time=10, timeout_unit="ms")
async def test_project_full_glitch_sequence_with_reset(dut):
    dut._log.info("Start")

    await start_clock_and_reset(dut)

    dut._log.info("Test project full glitch sequence with reset")

    uart_source = UartSource(dut.uart_rx, baud=115200, bits=8)

    await uart_source.write(b'd\x00\x12') # Set delay
    await uart_source.write(b'w\x01')     # Set width
    await uart_source.write(b'n\x02')     # Set num pulses
    await uart_source.write(b's\x00\x03') # Set pulse spacing
    await uart_source.write(b'r\x00\x50') # Set reset length
    await uart_source.write(b'p')         # Reset target and then pulse

    await RisingEdge(dut.target_reset)

    for x in range(0x50): # Reset
        await ClockCycles(dut.clk, 1)
        assert dut.pulse_out.value == 1, "Expected pulse_out to be 1" # The pulse should also be high during the reset
        assert dut.target_reset.value == 1, "Expected target_reset to be 1"
        assert dut.uo_out.value[6] == 0, "Expected pulse_out (inverted) to be 0 during reset"
        assert dut.uo_out.value[7] == 0, "Expected target_reset (inverted) to be 0 during reset"

    for _ in range(0x12): # Delay
        await ClockCycles(dut.clk, 1)
        assert dut.pulse_out.value == 0, "Expected pulse_out to be 0 during delay"
        assert dut.target_reset.value == 0, "Expected target_reset to be 0 during delay"
        assert dut.uo_out.value[6] == 1, "Expected pulse_out (inverted) to be 1 during delay"
        assert dut.uo_out.value[7] == 1, "Expected target_reset (inverted) to be 1 during delay"

    for _ in range(0x01): # Width
        await ClockCycles(dut.clk, 1)
        assert dut.pulse_out.value == 1, "Expected pulse_out to be 1"
        assert dut.target_reset.value == 0, "Expected target_reset to be 0"
        assert dut.uo_out.value[6] == 0, "Expected pulse_out (inverted) to be 0"
        assert dut.uo_out.value[7] == 1, "Expected target_reset (inverted) to be 1"

    for _ in range(0x03): # Spacing
        await ClockCycles(dut.clk, 1)
        assert dut.pulse_out.value == 0, "Expected pulse_out to be 0"
        assert dut.target_reset.value == 0, "Expected target_reset to be 0"
        assert dut.uo_out.value[6] == 1, "Expected pulse_out (inverted) to be 1"
        assert dut.uo_out.value[7] == 1, "Expected target_reset (inverted) to be 1"

    for _ in range(0x01): # Width
        await ClockCycles(dut.clk, 1)
        assert dut.pulse_out.value == 1, "Expected pulse_out to be 1"
        assert dut.target_reset.value == 0, "Expected target_reset to be 0"
        assert dut.uo_out.value[6] == 0, "Expected pulse_out (inverted) to be 0"
        assert dut.uo_out.value[7] == 1, "Expected target_reset (inverted) to be 1"

    await ClockCycles(dut.clk, 1)
    assert dut.pulse_out.value == 0, "Expected pulse_out to be 0"
    assert dut.target_reset.value == 0, "Expected target_reset to be 0"
    assert dut.uo_out.value[6] == 1, "Expected pulse_out (inverted) to be 1"
    assert dut.uo_out.value[7] == 1, "Expected target_reset (inverted) to be 1"

@cocotb.test(timeout_time=10, timeout_unit="ms")
async def test_project_trigger(dut):
    dut._log.info("Start")

    await start_clock_and_reset(dut)

    dut._log.info("Test project full glitch sequence")

    uart_source = UartSource(dut.uart_rx, baud=115200, bits=8, stop_bits=1)

    await uart_source.write(b'd\x00\x12') # Set delay
    await uart_source.write(b'w\x01')     # Set width
    await uart_source.write(b'n\x02')     # Set num pulses
    await uart_source.write(b's\x00\x03') # Set pulse spacing
    await uart_source.write(b'a')         # Arm
    await uart_source.wait()

    await ClockCycles(dut.clk, 1)

    dut.trigger_in.value = 1
    await ClockCycles(dut.clk, 1)
    dut.trigger_in.value = 0

    for _ in range(0x12): # Delay
        await ClockCycles(dut.clk, 1)
        assert dut.pulse_out.value == 0, "Expected pulse_out to be 0"

    for _ in range(0x01): # Width
        await ClockCycles(dut.clk, 1)
        assert dut.pulse_out.value == 1, "Expected pulse_out to be 1"

    for _ in range(0x03): # Spacing
        await ClockCycles(dut.clk, 1)
        assert dut.pulse_out.value == 0, "Expected pulse_out to be 0"

    for _ in range(0x01): # Width
        await ClockCycles(dut.clk, 1)
        assert dut.pulse_out.value == 1, "Expected pulse_out to be 1"

    await ClockCycles(dut.clk, 1)
    assert dut.pulse_out.value == 0, "Expected pulse_out to be 0"

@cocotb.test(timeout_time=10, timeout_unit="ms")
async def test_project_target_reset_only(dut):
    dut._log.info("Start")

    await start_clock_and_reset(dut)

    dut._log.info("Test project target reset only")

    uart_source = UartSource(dut.uart_rx, baud=115200, bits=8)
    await uart_source.write(b'y')         # Reset mode 'none' (reset only)
    await uart_source.write(b'r\x12\x34') # Set reset length
    await uart_source.write(b'p')         # Power cycle (reset) target

    await RisingEdge(dut.target_reset)

    for _ in range(0x1234): # Reset
        await ClockCycles(dut.clk, 1)
        assert dut.pulse_out.value == 1, "Expected pulse_out to be 1" # The pulse should also be high during the reset
        assert dut.target_reset.value == 1, "Expected target_reset to be 1"

    await ClockCycles(dut.clk, 1)
    assert dut.pulse_out.value == 0, "Expected pulse_out to be 0"
    assert dut.target_reset.value == 0, "Expected target_reset to be 0"


@cocotb.test(timeout_time=10, timeout_unit="ms")
async def test_project_reset_arm_trigger(dut):
    dut._log.info("Start")

    await start_clock_and_reset(dut)

    dut._log.info("Test project reset, arm and trigger")

    uart_source = UartSource(dut.uart_rx, baud=115200, bits=8)
    await uart_source.write(b'i')         # Reset mode 'arm'
    await uart_source.write(b'd\x00\x12') # Set delay
    await uart_source.write(b'w\x01')     # Set width
    await uart_source.write(b'r\x00\x80') # Set reset length
    await uart_source.write(b'p')         # Power cycle (reset) target

    await RisingEdge(dut.target_reset)

    for _ in range(0x80): # Reset
        await ClockCycles(dut.clk, 1)
        assert dut.pulse_out.value == 1, "Expected pulse_out to be 1" # The pulse should also be high during the reset
        assert dut.target_reset.value == 1, "Expected target_reset to be 1"
        assert dut.armed.value == 0, "Expected armed to be 0"

    await ClockCycles(dut.clk, 1)
    assert dut.pulse_out.value == 0, "Expected pulse_out to be 0"
    assert dut.target_reset.value == 0, "Expected target_reset to be 0"

    # Trigger should now be armed
    assert dut.armed.value == 1, "Expected armed to be 1"

    await ClockCycles(dut.clk, 1)
    dut.trigger_in.value = 1
    await ClockCycles(dut.clk, 1)
    dut.trigger_in.value = 0

    for _ in range(0x12): # Delay
        await ClockCycles(dut.clk, 1)
        assert dut.pulse_out.value == 0, "Expected pulse_out to be 0"
        assert dut.armed.value == 0, "Expected armed to be 0"

    for _ in range(0x01): # Width
        await ClockCycles(dut.clk, 1)
        assert dut.pulse_out.value == 1, "Expected pulse_out to be 1"
        assert dut.armed.value == 0, "Expected armed to be 0"

    await ClockCycles(dut.clk, 1)
    assert dut.pulse_out.value == 0, "Expected pulse_out to be 0"
    assert dut.armed.value == 0, "Expected armed to be 0"


@cocotb.test(timeout_time=10, timeout_unit="ms")
async def test_project_num_pulses_zero_no_pulse(dut):
    dut._log.info("Start")

    await start_clock_and_reset(dut)

    dut._log.info("Test num_pulses=0 yields no pulse")

    uart_source = UartSource(dut.uart_rx, baud=115200, bits=8)

    await uart_source.write(b'd\x00\x02') # Set delay
    await uart_source.write(b'w\x01')     # Set width
    await uart_source.write(b'n\x00')     # Set num pulses = 0
    await uart_source.write(b's\x00\x01') # Set pulse spacing
    await uart_source.write(b't')         # Trigger pulse

    await RisingEdge(dut.pulse_en)

    for _ in range(0x02):
        await ClockCycles(dut.clk, 1)
        assert dut.pulse_out.value == 0, "Expected pulse_out to be 0"

    for _ in range(4):
        await ClockCycles(dut.clk, 1)
        assert dut.pulse_out.value == 0, "Expected pulse_out to stay 0"


@cocotb.test(timeout_time=10, timeout_unit="ms")
async def test_project_num_pulses_one_no_spacing(dut):
    dut._log.info("Start")

    await start_clock_and_reset(dut)

    dut._log.info("Test num_pulses=1 no spacing phase")

    uart_source = UartSource(dut.uart_rx, baud=115200, bits=8)

    await uart_source.write(b'd\x00\x01') # Set delay
    await uart_source.write(b'w\x02')     # Set width
    await uart_source.write(b'n\x01')     # Set num pulses = 1
    await uart_source.write(b's\x00\x03') # Set pulse spacing
    await uart_source.write(b't')         # Trigger pulse

    await RisingEdge(dut.pulse_en)
    await ClockCycles(dut.clk, 1)

    await ClockCycles(dut.clk, 1)
    assert dut.pulse_out.value == 0, "Expected pulse_out to be 0 during delay"
    assert dut.busy.value == 1, "Expected busy to be 1 during delay"

    for _ in range(0x02):
        await ClockCycles(dut.clk, 1)
        assert dut.pulse_out.value == 1, "Expected pulse_out to be 1"
        assert dut.busy.value == 1, "Expected busy to be 1 during pulse"

    await ClockCycles(dut.clk, 1)
    assert dut.pulse_out.value == 0, "Expected pulse_out to be 0 after pulse"
    assert dut.busy.value == 0, "Expected busy to be 0 after pulse"


@cocotb.test(timeout_time=10, timeout_unit="ms")
async def test_project_zero_delay_immediate_pulse(dut):
    dut._log.info("Start")

    await start_clock_and_reset(dut)

    dut._log.info("Test zero delay starts pulse immediately")

    uart_source = UartSource(dut.uart_rx, baud=115200, bits=8)

    await uart_source.write(b'd\x00\x00') # Set delay = 0
    await uart_source.write(b'w\x01')     # Set width = 1
    await uart_source.write(b'n\x01')     # Set num pulses = 1
    await uart_source.write(b't')         # Trigger pulse

    await RisingEdge(dut.pulse_en)
    await ClockCycles(dut.clk, 1) # Settle after pulse_en goes high

    await ClockCycles(dut.clk, 1)
    assert dut.pulse_out.value == 0, "Expected one delay cycle even with zero delay"

    await ClockCycles(dut.clk, 1)
    assert dut.pulse_out.value == 1, "Expected pulse_out to be 1"

    await ClockCycles(dut.clk, 1)
    assert dut.pulse_out.value == 0, "Expected pulse_out to return low"


@cocotb.test(timeout_time=10, timeout_unit="ms")
async def test_project_zero_width_one_cycle(dut):
    dut._log.info("Start")

    await start_clock_and_reset(dut)

    dut._log.info("Test zero width is one cycle")

    uart_source = UartSource(dut.uart_rx, baud=115200, bits=8)

    await uart_source.write(b'd\x00\x01') # Set delay
    await uart_source.write(b'w\x00')     # Set width = 0
    await uart_source.write(b'n\x01')     # Set num pulses = 1
    await uart_source.write(b't')         # Trigger pulse

    await RisingEdge(dut.pulse_en)
    await ClockCycles(dut.clk, 1) # Settle

    await ClockCycles(dut.clk, 1)
    assert dut.pulse_out.value == 0, "Expected pulse_out to be 0 during delay"

    await ClockCycles(dut.clk, 1)
    assert dut.pulse_out.value == 1, "Expected pulse_out high for one cycle"

    await ClockCycles(dut.clk, 1)
    assert dut.pulse_out.value == 0, "Expected pulse_out to return low"


@cocotb.test(timeout_time=10, timeout_unit="ms")
async def test_project_zero_spacing_one_low_cycle(dut):
    dut._log.info("Start")

    await start_clock_and_reset(dut)

    dut._log.info("Test zero spacing yields single low cycle")

    uart_source = UartSource(dut.uart_rx, baud=115200, bits=8)

    await uart_source.write(b'd\x00\x01') # Set delay = 1
    await uart_source.write(b'w\x01')     # Set width = 1
    await uart_source.write(b'n\x02')     # Set num pulses = 2
    await uart_source.write(b's\x00\x00') # Set spacing = 0
    await uart_source.write(b't')         # Trigger pulse

    await RisingEdge(dut.pulse_en)
    await ClockCycles(dut.clk, 1)

    await ClockCycles(dut.clk, 1)
    assert dut.pulse_out.value == 0, "Expected pulse_out to be 0 during delay"

    await ClockCycles(dut.clk, 1)
    assert dut.pulse_out.value == 1, "Expected first pulse high"

    await ClockCycles(dut.clk, 1)
    assert dut.pulse_out.value == 0, "Expected single low cycle spacing"

    await ClockCycles(dut.clk, 1)
    assert dut.pulse_out.value == 1, "Expected second pulse high"

    await ClockCycles(dut.clk, 1)
    assert dut.pulse_out.value == 0, "Expected pulse_out to return low"


@cocotb.test(timeout_time=10, timeout_unit="ms")
async def test_project_trigger_ignored_when_not_armed(dut):
    dut._log.info("Start")

    await start_clock_and_reset(dut)

    dut._log.info("Test trigger ignored when not armed")

    uart_source = UartSource(dut.uart_rx, baud=115200, bits=8)

    await uart_source.write(b'd\x00\x01') # Set delay = 1
    await uart_source.write(b'w\x01')     # Set width = 1
    await uart_source.write(b'n\x01')     # Set num pulses = 1

    await ClockCycles(dut.clk, 1)
    assert dut.armed.value == 0, "Expected armed to be 0"

    dut.trigger_in.value = 1
    await ClockCycles(dut.clk, 1)
    dut.trigger_in.value = 0

    for _ in range(6):
        await ClockCycles(dut.clk, 1)
        assert dut.pulse_out.value == 0, "Expected pulse_out to stay low"
        assert dut.busy.value == 0, "Expected busy to stay low"


@cocotb.test(timeout_time=10, timeout_unit="ms")
async def test_project_arm_toggle_disarms(dut):
    dut._log.info("Start")

    await start_clock_and_reset(dut)

    dut._log.info("Test arm toggle disarms")

    uart_source = UartSource(dut.uart_rx, baud=115200, bits=8)

    await uart_source.write(b'd\x00\x01') # Set delay = 1
    await uart_source.write(b'w\x01')     # Set width = 1
    await uart_source.write(b'n\x01')     # Set num pulses = 1
    await uart_source.write(b'a')         # Arm
    await uart_source.wait()

    await ClockCycles(dut.clk, 1)
    assert dut.armed.value == 1, "Expected armed to be 1"

    await uart_source.write(b'a')         # Toggle arm off
    await uart_source.wait()

    await ClockCycles(dut.clk, 1)
    assert dut.armed.value == 0, "Expected armed to be 0"

    dut.trigger_in.value = 1
    await ClockCycles(dut.clk, 1)
    dut.trigger_in.value = 0

    for _ in range(6):
        await ClockCycles(dut.clk, 1)
        assert dut.pulse_out.value == 0, "Expected pulse_out to stay low"
        assert dut.busy.value == 0, "Expected busy to stay low"


@cocotb.test(timeout_time=10, timeout_unit="ms")
async def test_project_armed_clears_on_trigger(dut):
    dut._log.info("Start")

    await start_clock_and_reset(dut)

    dut._log.info("Test armed clears when trigger fires")

    uart_source = UartSource(dut.uart_rx, baud=115200, bits=8)

    await uart_source.write(b'd\x00\x02') # Set delay = 2
    await uart_source.write(b'w\x01')     # Set width = 1
    await uart_source.write(b'n\x01')     # Set num pulses = 1
    await uart_source.write(b'a')         # Arm
    await uart_source.wait()

    await ClockCycles(dut.clk, 1)
    assert dut.armed.value == 1, "Expected armed to be 1"

    dut.trigger_in.value = 1
    await ClockCycles(dut.clk, 1)
    dut.trigger_in.value = 0

    for _ in range(0x02):
        await ClockCycles(dut.clk, 1)
        assert dut.armed.value == 0, "Expected armed to be 0 after trigger"
        assert dut.busy.value == 1, "Expected busy to be 1 during delay"

    await ClockCycles(dut.clk, 1)
    assert dut.pulse_out.value == 1, "Expected pulse_out to be 1"

    await ClockCycles(dut.clk, 1)
    assert dut.pulse_out.value == 0, "Expected pulse_out to be 0"
    assert dut.busy.value == 0, "Expected busy to be 0 after pulse"


@cocotb.test(timeout_time=10, timeout_unit="ms")
async def test_project_busy_during_reset_and_pulse(dut):
    dut._log.info("Start")

    await start_clock_and_reset(dut)

    dut._log.info("Test busy high during reset and pulse sequence")

    uart_source = UartSource(dut.uart_rx, baud=115200, bits=8)

    await uart_source.write(b'd\x00\x02') # Set delay = 2
    await uart_source.write(b'w\x01')     # Set width = 1
    await uart_source.write(b'n\x01')     # Set num pulses = 1
    await uart_source.write(b'r\x00\x03') # Set reset length
    await uart_source.write(b'p')         # Reset and then pulse

    await RisingEdge(dut.target_reset)
    await FallingEdge(dut.clk) # Settle

    assert dut.busy.value == 1, "Expected busy to be 1 during reset"

    for _ in range(0x03):
        await ClockCycles(dut.clk, 1)
        assert dut.busy.value == 1, "Expected busy to stay 1 during reset"

    await ClockCycles(dut.clk, 1)
    assert dut.busy.value == 1, "Expected busy to stay 1 during delay"

    await ClockCycles(dut.clk, 1)
    assert dut.pulse_out.value == 0, "Expected pulse_out low during delay"

    await ClockCycles(dut.clk, 1)
    assert dut.pulse_out.value == 1, "Expected pulse_out high during pulse"
    assert dut.busy.value == 1, "Expected busy high during pulse"

    await ClockCycles(dut.clk, 1)
    assert dut.pulse_out.value == 0, "Expected pulse_out low after pulse"
    assert dut.busy.value == 0, "Expected busy low after sequence"


@cocotb.test(timeout_time=10, timeout_unit="ms")
async def test_project_ignore_trigger_while_busy(dut):
    dut._log.info("Start")

    await start_clock_and_reset(dut)

    dut._log.info("Test trigger ignored while busy")

    uart_source = UartSource(dut.uart_rx, baud=115200, bits=8)

    await uart_source.write(b'd\x00\x10') # Set delay
    await uart_source.write(b'w\x01')     # Set width
    await uart_source.write(b'n\x01')     # Set num pulses = 1
    await uart_source.write(b't')         # Trigger pulse

    await RisingEdge(dut.pulse_en)
    await ClockCycles(dut.clk, 1) # Settle

    await ClockCycles(dut.clk, 1)
    assert dut.busy.value == 1, "Expected busy to be 1 during delay"
    assert dut.pulse_out.value == 0, "Expected pulse_out to be 0 during delay"

    await uart_source.write(b't') # Trigger again while busy

    for _ in range(0x10 - 1): # Remaining delay cycles
        await ClockCycles(dut.clk, 1)
        assert dut.pulse_out.value == 0, "Expected pulse_out to be 0 during delay"

    await ClockCycles(dut.clk, 1)
    assert dut.pulse_out.value == 1, "Expected single pulse"

    await ClockCycles(dut.clk, 1)
    assert dut.pulse_out.value == 0, "Expected pulse_out to return low"
    assert dut.busy.value == 0, "Expected busy to return low"

    for _ in range(4):
        await ClockCycles(dut.clk, 1)
        assert dut.pulse_out.value == 0, "Expected no extra pulses"


@cocotb.test(timeout_time=10, timeout_unit="ms")
async def test_project_ignore_external_trigger_while_busy(dut):
    dut._log.info("Start")

    await start_clock_and_reset(dut)

    dut._log.info("Test external trigger ignored while busy")

    uart_source = UartSource(dut.uart_rx, baud=115200, bits=8)

    await uart_source.write(b'd\x00\x10') # Set delay
    await uart_source.write(b'w\x01')     # Set width
    await uart_source.write(b'n\x01')     # Set num pulses = 1
    await uart_source.write(b'a')         # Arm
    await uart_source.wait()

    await ClockCycles(dut.clk, 1)
    assert dut.armed.value == 1, "Expected armed to be 1"

    dut.trigger_in.value = 1
    await ClockCycles(dut.clk, 1)
    dut.trigger_in.value = 0

    await ClockCycles(dut.clk, 1)
    assert dut.busy.value == 1, "Expected busy to be 1 during delay"

    dut.trigger_in.value = 1
    await ClockCycles(dut.clk, 1)
    dut.trigger_in.value = 0

    for _ in range(0x10 - 2): # Remaining delay cycles
        await ClockCycles(dut.clk, 1)
        assert dut.pulse_out.value == 0, "Expected pulse_out to be 0 during delay"

    await ClockCycles(dut.clk, 1)
    assert dut.pulse_out.value == 1, "Expected single pulse"

    await ClockCycles(dut.clk, 1)
    assert dut.pulse_out.value == 0, "Expected pulse_out to return low"
    assert dut.busy.value == 0, "Expected busy to return low"

    for _ in range(4):
        await ClockCycles(dut.clk, 1)
        assert dut.pulse_out.value == 0, "Expected no extra pulses"


@cocotb.test(timeout_time=10, timeout_unit="ms")
async def test_project_no_pulse_en_on_reset_only(dut):
    dut._log.info("Start")

    await start_clock_and_reset(dut)

    dut._log.info("Test pulse_en stays low for reset-only")

    uart_source = UartSource(dut.uart_rx, baud=115200, bits=8)

    await uart_source.write(b'y')         # Reset mode 'none'
    await uart_source.write(b'r\x00\x03') # Set reset length = 3
    await uart_source.write(b'p')         # Reset target only

    for _ in range(6):
        await ClockCycles(dut.clk, 1)
        assert dut.pulse_en.value == 0, "Expected pulse_en to stay low"


@cocotb.test(timeout_time=10, timeout_unit="ms")
async def test_project_armed_clears_on_uart_trigger(dut):
    dut._log.info("Start")

    await start_clock_and_reset(dut)

    dut._log.info("Test armed clears on UART trigger")

    uart_source = UartSource(dut.uart_rx, baud=115200, bits=8)

    await uart_source.write(b'd\x00\x01') # Set delay
    await uart_source.write(b'w\x01')     # Set width
    await uart_source.write(b'n\x01')     # Set num pulses = 1
    await uart_source.write(b'a')         # Arm
    await uart_source.wait()

    await ClockCycles(dut.clk, 1)
    assert dut.armed.value == 1, "Expected armed to be 1"

    await uart_source.write(b't')         # Trigger via UART

    await RisingEdge(dut.pulse_en)
    await ClockCycles(dut.clk, 1) # Settle

    await ClockCycles(dut.clk, 1)
    assert dut.armed.value == 0, "Expected armed to clear"


@cocotb.test(timeout_time=10, timeout_unit="ms")
async def test_project_defaults_uart_trigger(dut):
    dut._log.info("Start")

    await start_clock_and_reset(dut)

    dut._log.info("Test defaults: UART trigger without configuration")

    uart_source = UartSource(dut.uart_rx, baud=115200, bits=8)

    await uart_source.write(b't')  # Trigger pulse with defaults

    await RisingEdge(dut.pulse_en)
    await ClockCycles(dut.clk, 1) # Settle after pulse_en goes high

    highs = 0
    for _ in range(6):
        await ClockCycles(dut.clk, 1)
        if dut.pulse_out.value == 1:
            highs += 1

    assert highs == 1, f"Expected one pulse with defaults, got {highs}"


@cocotb.test(timeout_time=10, timeout_unit="ms")
async def test_project_defaults_reset_then_pulse(dut):
    dut._log.info("Start")

    await start_clock_and_reset(dut)

    dut._log.info("Test defaults: reset then pulse")

    uart_source = UartSource(dut.uart_rx, baud=115200, bits=8)

    await uart_source.write(b'p') # Reset target, then pulse (default)

    await RisingEdge(dut.target_reset)

    await ClockCycles(dut.clk, 1)
    assert dut.target_reset.value == 1, "Expected reset asserted"
    assert dut.pulse_out.value == 1, "Expected pulse_out high during reset"

    highs = 0
    for _ in range(6):
        await ClockCycles(dut.clk, 1)
        if dut.pulse_out.value == 1 and dut.target_reset.value == 0:
            highs += 1

    assert highs == 1, f"Expected one pulse after reset, got {highs}"

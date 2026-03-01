import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, RisingEdge

from cocotbext.uart import UartSink, UartSource

@cocotb.test(timeout_time=10, timeout_unit="ms")
async def test_uart_handler_echo(dut):
    dut._log.info("Start")

    # Set the clock period to 20 ns (50 MHz)
    clock = Clock(dut.clk, 20, unit="ns")
    cocotb.start_soon(clock.start())

    # Reset
    dut._log.info("Reset")
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)

    dut._log.info("Test UART handler echo")

    uart_source = UartSource(dut.uart_rx, baud=115200, bits=8)
    uart_sink = UartSink(dut.uart_tx, baud=115200, bits=8)

    # Unrecognized command bytes will be echoed back
    for x in range(0x10, 0x20):
        await uart_source.write(bytes([x]))
        await uart_source.wait()

        data = await uart_sink.read()
        assert data == bytes([x]), f"Expected {x:#02x}, got {data[0]:#02x}"

@cocotb.test(timeout_time=10, timeout_unit="ms")
async def test_uart_handler_hello(dut):
    dut._log.info("Start")

    # Set the clock period to 20 ns (50 MHz)
    clock = Clock(dut.clk, 20, unit="ns")
    cocotb.start_soon(clock.start())

    # Reset
    dut._log.info("Reset")
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)

    dut._log.info("Test UART handler hello")

    uart_source = UartSource(dut.uart_rx, baud=115200, bits=8)
    uart_sink = UartSink(dut.uart_tx, baud=115200, bits=8)

    await uart_source.write(b'h')
    await uart_source.wait()

    # uart_sink.read(5) should return b'Erika', but it only waits for the first byte
    # and then throws an exception because the queue is empty.
    # Let's just read one byte at a time instead.
    data = await uart_sink.read()
    assert data == b'E', f"Expected 'E', got {data}"
    data = await uart_sink.read()
    assert data == b'r', f"Expected 'r', got {data}"
    data = await uart_sink.read()
    assert data == b'i', f"Expected 'i', got {data}"
    data = await uart_sink.read()
    assert data == b'k', f"Expected 'k', got {data}"
    data = await uart_sink.read()
    assert data == b'a', f"Expected 'a', got {data}"

@cocotb.test(timeout_time=10, timeout_unit="ms")
async def test_uart_handler_set_delay(dut):
    dut._log.info("Start")

    # Set the clock period to 20 ns (50 MHz)
    clock = Clock(dut.clk, 20, unit="ns")
    cocotb.start_soon(clock.start())

    # Reset
    dut._log.info("Reset")
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)

    dut._log.info("Test UART handler set delay")

    uart_source = UartSource(dut.uart_rx, baud=115200, bits=8)

    await uart_source.write(b'd\x12\x34') # Set delay command (d, 0x64), high byte of delay (0x12), low byte of delay (0x34)
    await uart_source.wait()
    assert dut.pulse_delay.value == 0x1234, f"Expected pulse_delay to be 0x1234, got {dut.pulse_delay.value}"

    await uart_source.write(b'd\x00\x00') # Set delay command (d, 0x64), high byte of delay (0x00), low byte of delay (0x00)
    await uart_source.wait()
    assert dut.pulse_delay.value == 0x0000, f"Expected pulse_delay to be 0x0000, got {dut.pulse_delay.value}"

    await uart_source.write(b'd\xff\xff') # Set delay command (d, 0x64), high byte of delay (0xff), low byte of delay (0xff)
    await uart_source.wait()
    assert dut.pulse_delay.value == 0xffff, f"Expected pulse_delay to be 0xffff, got {dut.pulse_delay.value}"

@cocotb.test(timeout_time=10, timeout_unit="ms")
async def test_uart_handler_set_width(dut):
    dut._log.info("Start")

    # Set the clock period to 20 ns (50 MHz)
    clock = Clock(dut.clk, 20, unit="ns")
    cocotb.start_soon(clock.start())

    # Reset
    dut._log.info("Reset")
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)

    dut._log.info("Test UART handler set width")

    uart_source = UartSource(dut.uart_rx, baud=115200, bits=8)

    await uart_source.write(b'w\x12') # Set width command (w, 0x77), width (0x12)
    await uart_source.wait()
    assert dut.pulse_width.value == 0x12, f"Expected pulse_width to be 0x12, got {dut.pulse_width.value}"

    await uart_source.write(b'w\x00') # Set width command (w, 0x77), width (0x00)
    await uart_source.wait()
    assert dut.pulse_width.value == 0x00, f"Expected pulse_width to be 0x00, got {dut.pulse_width.value}"

    await uart_source.write(b'w\xff') # Set width command (w, 0x77), width (0xff)
    await uart_source.wait()
    assert dut.pulse_width.value == 0xff, f"Expected pulse_width to be 0xff, got {dut.pulse_width.value}"

@cocotb.test(timeout_time=10, timeout_unit="ms")
async def test_uart_handler_set_num_pulses(dut):
    dut._log.info("Start")

    # Set the clock period to 20 ns (50 MHz)
    clock = Clock(dut.clk, 20, unit="ns")
    cocotb.start_soon(clock.start())

    # Reset
    dut._log.info("Reset")
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)

    dut._log.info("Test UART handler set num pulses")

    uart_source = UartSource(dut.uart_rx, baud=115200, bits=8)

    await uart_source.write(b'n\x12') # Set num pulses command (n, 0x6e), num pulses (0x12)
    await uart_source.wait()
    assert dut.num_pulses.value == 0x12, f"Expected num_pulses to be 0x12, got {dut.num_pulses.value}"

    await uart_source.write(b'n\x00') # Set num pulses command (n, 0x6e), num pulses (0x00)
    await uart_source.wait()
    assert dut.num_pulses.value == 0x00, f"Expected num_pulses to be 0x00, got {dut.num_pulses.value}"

    await uart_source.write(b'n\xff') # Set num pulses command (n, 0x6e), num pulses (0xff)
    await uart_source.wait()
    assert dut.num_pulses.value == 0xff, f"Expected num_pulses to be 0xff, got {dut.num_pulses.value}"

@cocotb.test(timeout_time=10, timeout_unit="ms")
async def test_uart_handler_set_pulse_spacing(dut):
    dut._log.info("Start")

    # Set the clock period to 20 ns (50 MHz)
    clock = Clock(dut.clk, 20, unit="ns")
    cocotb.start_soon(clock.start())

    # Reset
    dut._log.info("Reset")
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)

    dut._log.info("Test UART handler set pulse spacing")

    uart_source = UartSource(dut.uart_rx, baud=115200, bits=8)

    await uart_source.write(b's\x12\x34') # Set pulse spacing command (s, 0x73), pulse spacing (0x1234)
    await uart_source.wait()
    assert dut.pulse_spacing.value == 0x1234, f"Expected pulse spacing to be 0x1234, got {dut.pulse_spacing.value}"

    await uart_source.write(b's\x00\x00') # Set pulse spacing command (s, 0x73), pulse spacing (0x0000)
    await uart_source.wait()
    assert dut.pulse_spacing.value == 0x0000, f"Expected pulse spacing to be 0x0000, got {dut.pulse_spacing.value}"

    await uart_source.write(b's\xff\xff') # Set pulse spacing command (s, 0x73), pulse spacing (0xffff)
    await uart_source.wait()
    assert dut.pulse_spacing.value == 0xffff, f"Expected pulse spacing to be 0xffff, got {dut.pulse_spacing.value}"

@cocotb.test(timeout_time=10, timeout_unit="ms")
async def test_uart_handler_trigger_pulse(dut):
    dut._log.info("Start")

    # Set the clock period to 20 ns (50 MHz)
    clock = Clock(dut.clk, 20, unit="ns")
    cocotb.start_soon(clock.start())

    # Reset
    dut._log.info("Reset")
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)

    dut._log.info("Test UART handler trigger pulse")

    uart_source = UartSource(dut.uart_rx, baud=115200, bits=8)

    assert dut.pulse_en.value == 0, "Expected pulse_en to be 0"

    await uart_source.write(b't') # Trigger pulse command (t, 0x74)

    await RisingEdge(dut.pulse_en)
    await ClockCycles(dut.clk, 1)
    assert dut.pulse_en.value == 1, "Expected pulse_en to be 1"
    await ClockCycles(dut.clk, 1)
    assert dut.pulse_en.value == 0, "Expected pulse_en to be 0"

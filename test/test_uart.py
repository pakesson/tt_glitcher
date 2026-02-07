import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, FallingEdge, RisingEdge

from cocotbext.uart import UartSink, UartSource

@cocotb.test()
async def test_uart_tx_a(dut):
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

    dut._log.info("Test UART TX A")

    uart_sink = UartSink(dut.uart_tx, baud=115200, bits=8)

    dut.uart_tx_data.value = ord('A')
    dut.uart_tx_en.value = 1
    await ClockCycles(dut.clk, 1)
    dut.uart_tx_en.value = 0

    data = await uart_sink.read()
    assert data == b'A', f"Expected 'A', got {data}"

    await FallingEdge(dut.uart_tx_busy)
    await ClockCycles(dut.clk, 1)
    assert dut.uart_tx_busy.value == 0, "Expected uart_tx_busy to be 0"

@cocotb.test()
async def test_uart_tx_more(dut):
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

    dut._log.info("Test UART TX, bytes 0x00 to 0x39")

    uart_sink = UartSink(dut.uart_tx, baud=115200, bits=8)

    for x in range(0x0, 0x3a):
        dut.uart_tx_data.value = x
        dut.uart_tx_en.value = 1
        await ClockCycles(dut.clk, 1)
        dut.uart_tx_en.value = 0

        data = await uart_sink.read()
        assert data == bytes([x]), f"Expected {x:02x}, got {data.hex()}"

        await FallingEdge(dut.uart_tx_busy)
        await ClockCycles(dut.clk, 1)
        assert dut.uart_tx_busy.value == 0, "Expected uart_tx_busy to be 0"

@cocotb.test()
async def test_uart_rx_a(dut):
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

    dut._log.info("Test UART RX A")

    uart_source = UartSource(dut.uart_rx, baud=115200, bits=8)

    await uart_source.write(b'A')

    await RisingEdge(dut.uart_rx_valid)

    assert dut.uart_rx_data.value == ord('A'), f"Expected uart_rx_data to be 'A' (0x41), got {dut.uart_rx_data.value:02x}"

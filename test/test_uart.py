import cocotb
from cocotb.triggers import ClockCycles, FallingEdge, RisingEdge

from cocotbext.uart import UartSink, UartSource

from .common import start_clock_and_reset

async def send_uart_tx_byte(dut, value):
    while dut.uart_tx_busy.value:
        await ClockCycles(dut.clk, 1)
    dut.uart_tx_data.value = value
    dut.uart_tx_en.value = 1
    await ClockCycles(dut.clk, 1)
    dut.uart_tx_en.value = 0

@cocotb.test(timeout_time=10, timeout_unit="ms")
async def test_uart_tx_a(dut):
    dut._log.info("Start")

    await start_clock_and_reset(dut)

    dut._log.info("Test UART TX A")

    uart_sink = UartSink(dut.uart_tx, baud=115200, bits=8)

    await send_uart_tx_byte(dut, ord('A'))

    data = await uart_sink.read()
    assert data == b'A', f"Expected 'A', got {data}"

    await FallingEdge(dut.uart_tx_busy)
    await ClockCycles(dut.clk, 1)
    assert dut.uart_tx_busy.value == 0, "Expected uart_tx_busy to be 0"

@cocotb.test(timeout_time=10, timeout_unit="ms")
async def test_uart_tx_more(dut):
    dut._log.info("Start")

    await start_clock_and_reset(dut)

    dut._log.info("Test UART TX, bytes 0x00 to 0x0f")

    uart_sink = UartSink(dut.uart_tx, baud=115200, bits=8)

    for x in range(0x0, 0x10):
        await send_uart_tx_byte(dut, x)

        data = await uart_sink.read()
        assert data == bytes([x]), f"Expected {x:02x}, got {data.hex()}"

        await FallingEdge(dut.uart_tx_busy)
        await ClockCycles(dut.clk, 1)
        assert dut.uart_tx_busy.value == 0, "Expected uart_tx_busy to be 0"

@cocotb.test(timeout_time=10, timeout_unit="ms")
async def test_uart_rx_a(dut):
    dut._log.info("Start")

    await start_clock_and_reset(dut)

    dut._log.info("Test UART RX A")

    uart_source = UartSource(dut.uart_rx, baud=115200, bits=8)

    await uart_source.write(b'A')

    await RisingEdge(dut.uart_rx_valid)

    assert dut.uart_rx_data.value == ord('A'), f"Expected uart_rx_data to be 'A' (0x41), got {dut.uart_rx_data.value:02x}"

@cocotb.test(timeout_time=10, timeout_unit="ms")
async def test_uart_tx_ignores_enable_while_busy(dut):
    dut._log.info("Start")

    await start_clock_and_reset(dut)

    dut._log.info("Test UART TX ignores uart_tx_en while busy")

    uart_sink = UartSink(dut.uart_tx, baud=115200, bits=8)

    dut.uart_tx_data.value = 0x12
    dut.uart_tx_en.value = 1
    await ClockCycles(dut.clk, 1)
    dut.uart_tx_en.value = 0

    await ClockCycles(dut.clk, 5)

    # Assert uart_tx_en with different data while previous transfer is still active.
    # uart_tx should ignore this strobe and continue the current frame.
    dut.uart_tx_data.value = 0xA5
    dut.uart_tx_en.value = 1
    await ClockCycles(dut.clk, 1)
    dut.uart_tx_en.value = 0

    first = await uart_sink.read()
    assert first == b'\x12', f"Expected first byte 0x12, got {first.hex()}"

    await FallingEdge(dut.uart_tx_busy)
    await ClockCycles(dut.clk, 1)
    assert dut.uart_tx_busy.value == 0, "Expected uart_tx_busy to be 0 after first frame"

    await send_uart_tx_byte(dut, 0xA5)
    second = await uart_sink.read()
    assert second == b'\xA5', f"Expected second byte 0xA5, got {second.hex()}"

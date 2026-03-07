import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles


async def start_clock_and_reset(dut, *, clk_period_ns=20, reset_cycles=5):
    cocotb.start_soon(Clock(dut.clk, clk_period_ns, unit="ns").start())

    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, reset_cycles)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)


async def read_exact(uart_sink, length):
    # uart_sink.read(n) should return n bytes, but it only waits for the first byte
    # and then throws an exception because the queue is empty.
    # Let's just read one byte at a time instead.
    data = bytearray()
    for _ in range(length):
        data += await uart_sink.read()
    return bytes(data)

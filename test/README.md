# Tests

## How to run

### Python

Tests can be run either directly with `python`:
```sh
python test.py            # Run all tests with cocotb runners
```
or using `pytest` for more control:
```sh
pytest test.py                              # Run all tests through pytest
pytest test.py -s                           # Show details
pytest test.py -k "uart_handler_runner"     # Only run matching tests
pytest test.py -k "uart_handler_runner" -s  # Only run matching tests w/ details
```

To run gatelevel simulation, first harden the project and copy `../ runs/wokwi/final/nl/tt_um_pakesson_glitcher.nl.v` to `gate_level_netlist.v`.
Then run
```sh
GATES=yes pytest test.py  # Gate level tests, only runs (top level) project tests
```
or
```sh
GATES=yes python test.py  # Gate level tests, only runs (top level) project tests
```

### Makefile

It is also possible to run top-level tests using the provided makefile.

To run the RTL simulation:

```sh
make -B
```

To run gatelevel simulation, first harden the project and copy `../ runs/wokwi/final/nl/tt_um_pakesson_glitcher.nl.v` to `gate_level_netlist.v`.

Then run:

```sh
make -B GATES=yes
```

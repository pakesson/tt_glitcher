<!---

This file is used to generate your project datasheet. Please fill in the information below and delete any unused
sections.

You can also include images in this folder and reference them in the markdown. Each image must be less than
512 kb in size, and the combined size of all images must be less than 1 MB.
-->

## How it works

This project is a pulse generator with configurable parameters, intended for use in voltage or electromagnetic fault injection attacks.

The pulse generator can be configured and controlled over UART (115200 8N1).

Pulses can be triggered either over UART or using the trigger input signal.

**Commands**

All parameter values are either 16-bit or 8-bit unsigned integers.
Timing-related values are specified in number of clock cycles.

- Set delay: 0x64 (`d`) followed by the high byte and the low byte of the 16-bit delay value
- Set width: 0x77 (`w`) followed by the 8-bit width value
- Set number of pulses: 0x6e (`n`) followed by the 8-bit number of pulses
- Set pulse spacing: 0x73 (`s`) followed by the high byte and the low byte of the 16-bit pulse spacing value
- Trigger pulse: 0x74 (`t`)
    - Triggers a pulse immediately (after the configured delay)
- Hello: 0x68 (`h`)
    - Transmits `Hello\n` over UART

Unhandled command bytes are echoed back over UART.

## How to test

TODO: Explain how to use the project

## External hardware

The pulse output can be used with a MOSFET or analog multiplexer/switch for voltage fault injection, or connected to a ChipSHOUTER for EMFI.

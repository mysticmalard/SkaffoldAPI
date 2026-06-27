# SPDX-License-Identifier: GPL-3.0-only
# Copyright (c) 2026 MysticMalard

from skaffold import *

@pattern
def green():
    color = Color(0, 255, 0)

    for row in SCREEN:
        for pixel in row:
            pixel.setColor(color)
    SCREEN.render()

@pattern
def display():
    ySize = len(SCREEN)
    xSize = len(SCREEN[0])
    frameSize = ySize * xSize * 3
    while True:
        cmd = listen(frameSize)
        for y in range(ySize):
            for x in range(xSize):
                i = ySize * y + xSize * x
                j = i + 3
                c = Color(*cmd[i:j])
                SCREEN[y][x].setColor(c)
        sys_call()

@pattern
def vitals():
    top, bottom = bisect(SCREEN, 1, HORIZONTAL)
    dischargeGrad = Gradient(
        (RED, 0.00),
        (ORANGE, 0.25),
        (YELLOW, 0.30),
        (LIME, 0.40),
        (GREEN, 0.50),
        (GREEN, 0.75),
        (WHITE, 0.80),
        (WHITE, 1.00),
    )
    chargeRateGrad = Gradient(
        (RED, 0.00),
        (YELLOW, 0.25),
        (BLACK, 0.50),
        (GREEN, 0.75),
        (BLUE, 1.00),
    )
    chargeRateBar = Bar(top, 3, chargeRateGrad, True)
    dischargeBar = Bar(top, 1, dischargeGrad)
    a, b, c, d = partition(bottom, 4, VERTICAL)
    tempGrad = Gradient(
        (PURPLE, 0),
        (BLUE, 0.25),
        (GREEN, 0.30),
        (ORANGE, 0.50),
        (YELLOW, 0.70),
        (RED, 0.90),
        (RED, 0.95),
        (WHITE, 1.00),
    )
    CPUtempBar = Bar(a, 0, tempGrad)
    GPUtempBar = Bar(b, 0, tempGrad)
    memUsageBar = Bar(c, 0, tempGrad)
    fanSpeedBar = Bar(d, 0, tempGrad)
    while True:
        cmd = listen(6)
        chargeRateBar.setAlpha(cmd[0])
        dischargeBar.setAlpha(cmd[1])
        CPUtempBar.setAlpha(cmd[2])
        GPUtempBar.setAlpha(cmd[3])
        memUsageBar.setAlpha(cmd[4])
        fanSpeedBar.setAlpha(cmd[5])
        SCREEN.render()
        sys_call()


macropad = get_macropad()
macropad.setup(green, display, vitals)
macropad.build()

output = open('macropad.ska', 'w+')
print('\n'.join(macropad.asm), end='', file=output)
output.close()
print('hello world')
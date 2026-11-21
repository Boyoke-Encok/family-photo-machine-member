#!/usr/bin/env python3
"""The Family Photo With One Machine Member (make.fun).

Draws one 1024x1024 PNG: a candid family afternoon at home.
Living room + kitchen edge, warm window light. Mother on the sofa with
a mug, father at the counter chopping, a child playing with blocks on
the rug, and one small household robot rolling across the floor
mid-task with a tray. Particular details: half-peeled carrot on the
board, a dog bowl by the rug, laundry on the radiator, mismatched
chairs stacked by the wall. No text anywhere in the image.

Own code, written fresh. Deterministic: fixed geometry, seeded grain.
"""
import os
import random
from PIL import Image, ImageDraw, ImageFilter

W, H = 1024, 1024
OUT = "/output/entry.png"

# ---- palette ----
WALL_TOP = (233, 220, 196)
WALL_BOT = (214, 194, 164)
FLOOR_A = (176, 138, 96)
FLOOR_B = (158, 122, 82)
RUG = (150, 92, 74)
RUG_EDGE = (124, 74, 58)
SOFA = (96, 122, 108)
SOFA_DARK = (78, 100, 88)
SOFA_CUSHION = (112, 138, 122)
COUNTER = (120, 96, 72)
COUNTER_TOP = (206, 186, 158)
SKIN_A = (214, 164, 128)
SKIN_B = (196, 144, 108)
SKIN_C = (232, 186, 148)
HAIR_DARK = (58, 40, 28)
HAIR_GREY = (150, 140, 128)
SWEATER = (198, 142, 52)
JEANS = (70, 88, 118)
APRON = (168, 178, 172)
SHIRT_KID = (186, 84, 66)
ROBOT_BODY = (232, 226, 212)
ROBOT_TEAL = (64, 128, 122)
ROBOT_DARK = (52, 54, 58)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def vgrad(img, top, bottom, y0=0, y1=None):
    y1 = H if y1 is None else y1
    d = ImageDraw.Draw(img)
    for y in range(y0, y1):
        d.line([(0, y), (W, y)], fill=lerp(top, bottom, (y - y0) / max(1, y1 - y0)))
    return img


def rr(d, box, r, fill, outline=None, width=1):
    d.rounded_rectangle([int(v) for v in box], radius=int(r), fill=fill,
                        outline=outline, width=int(width))


def limb(d, x0, y0, x1, y1, w, color):
    w = int(w)
    x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
    d.ellipse([x0 - w // 2, y0 - w // 2, x0 + w // 2, y0 + w // 2], fill=color)
    d.ellipse([x1 - w // 2, y1 - w // 2, x1 + w // 2, y1 + w // 2], fill=color)


def person(d, x, y, s, skin, hair, shirt, pants, pose):
    """Simple flat figure, s = scale (head radius ~ 26*s). Anchor (x, y)
    is the centre of the head. pose in {'sit_sofa','stand_counter','sit_floor'}."""
    hr = 26 * s
    # head
    d.ellipse([x - hr, y - hr, x + hr, y + hr], fill=skin)
    if pose == "sit_sofa":
        # hair: cap + bun
        d.pieslice([x - hr, y - hr, x + hr, y + hr], start=180, end=360, fill=hair)
        d.ellipse([x + hr * 0.55, y - hr * 1.35, x + hr * 1.25, y - hr * 0.55], fill=hair)
        # torso: seated, leaning slightly
        rr(d, [x - 34 * s, y + hr * 0.8, x + 36 * s, y + hr * 0.8 + 92 * s], 18 * s, shirt)
        # legs: thighs forward over the seat edge, calves down, feet on the floor
        limb(d, x - 6 * s, y + hr * 0.8 + 82 * s, x + 46 * s, y + hr * 0.8 + 104 * s, 24 * s, pants)
        limb(d, x + 46 * s, y + hr * 0.8 + 104 * s, x + 50 * s, y + hr * 0.8 + 156 * s, 22 * s, pants)
        limb(d, x + 2 * s, y + hr * 0.8 + 86 * s, x + 22 * s, y + hr * 0.8 + 110 * s, 24 * s, pants)
        limb(d, x + 22 * s, y + hr * 0.8 + 110 * s, x + 24 * s, y + hr * 0.8 + 158 * s, 22 * s, pants)
        # shoes: small rounded rects at the feet
        rr(d, [x + 34 * s, y + hr * 0.8 + 152 * s, x + 66 * s, y + hr * 0.8 + 168 * s], 8 * s, (60, 48, 40))
        rr(d, [x + 8 * s, y + hr * 0.8 + 154 * s, x + 40 * s, y + hr * 0.8 + 170 * s], 8 * s, (60, 48, 40))
        # arm resting on sofa back
        limb(d, x - 28 * s, y + hr * 0.8 + 18 * s, x - 58 * s, y + hr * 0.8 + 34 * s, 22 * s, shirt)
        limb(d, x - 58 * s, y + hr * 0.8 + 34 * s, x - 66 * s, y + hr * 0.8 + 66 * s, 20 * s, skin)
        # arm holding mug to chest
        limb(d, x + 26 * s, y + hr * 0.8 + 16 * s, x + 52 * s, y + hr * 0.8 + 44 * s, 22 * s, shirt)
        limb(d, x + 52 * s, y + hr * 0.8 + 44 * s, x + 34 * s, y + hr * 0.8 + 58 * s, 20 * s, skin)
        return (x + 30 * s, y + hr * 0.8 + 52 * s)  # mug hand pos
    if pose == "stand_counter":
        # hair: short, grey at temples
        d.pieslice([x - hr, y - hr, x + hr, y + hr], start=180, end=360, fill=hair)
        d.pieslice([x - hr, y - hr * 0.4, x + hr, y + hr * 0.5], start=180, end=360, fill=HAIR_GREY)
        # torso + apron (only upper body shows above the counter)
        rr(d, [x - 40 * s, y + hr * 0.8, x + 40 * s, y + hr * 0.8 + 110 * s], 20 * s, shirt)
        rr(d, [x - 30 * s, y + hr * 0.8 + 26 * s, x + 30 * s, y + hr * 0.8 + 110 * s], 10 * s, APRON)
        # arms reaching down-forward to the board
        limb(d, x - 34 * s, y + hr * 0.8 + 22 * s, x - 66 * s, y + hr * 0.8 + 78 * s, 22 * s, shirt)
        limb(d, x - 66 * s, y + hr * 0.8 + 78 * s, x - 52 * s, y + hr * 0.8 + 104 * s, 20 * s, skin)
        limb(d, x + 34 * s, y + hr * 0.8 + 22 * s, x + 58 * s, y + hr * 0.8 + 74 * s, 22 * s, shirt)
        limb(d, x + 58 * s, y + hr * 0.8 + 74 * s, x + 40 * s, y + hr * 0.8 + 100 * s, 20 * s, skin)
        return (x - 52 * s, y + hr * 0.8 + 104 * s)
    # sit_floor: child, cross-legged, reaching for blocks
    d.pieslice([x - hr, y - hr, x + hr, y + hr], start=180, end=360, fill=hair)
    d.ellipse([x - 6 * s, y - hr * 1.35, x + 8 * s, y - hr * 0.75], fill=hair)  # tuft
    rr(d, [x - 26 * s, y + hr * 0.8, x + 26 * s, y + hr * 0.8 + 62 * s], 14 * s, shirt)
    d.line([(x - 20 * s, y + hr * 0.8 + 34 * s), (x + 20 * s, y + hr * 0.8 + 34 * s)],
           fill=(240, 236, 220), width=int(6 * s))  # stripe
    # crossed legs
    limb(d, x - 14 * s, y + hr * 0.8 + 56 * s, x - 52 * s, y + hr * 0.8 + 82 * s, 20 * s, pants)
    limb(d, x + 14 * s, y + hr * 0.8 + 56 * s, x + 52 * s, y + hr * 0.8 + 82 * s, 20 * s, pants)
    # arms reaching forward-down to the blocks
    limb(d, x - 22 * s, y + hr * 0.8 + 14 * s, x - 44 * s, y + hr * 0.8 + 52 * s, 16 * s, shirt)
    limb(d, x - 44 * s, y + hr * 0.8 + 52 * s, x - 56 * s, y + hr * 0.8 + 74 * s, 14 * s, skin)
    limb(d, x + 22 * s, y + hr * 0.8 + 14 * s, x + 46 * s, y + hr * 0.8 + 48 * s, 16 * s, shirt)
    limb(d, x + 46 * s, y + hr * 0.8 + 48 * s, x + 58 * s, y + hr * 0.8 + 70 * s, 14 * s, skin)
    return (x - 56 * s, y + hr * 0.8 + 74 * s)


def draw():
    img = Image.new("RGB", (W, H))
    vgrad(img, WALL_TOP, WALL_BOT, 0, 700)
    d = ImageDraw.Draw(img)

    # ---- floor (wood planks, perspective-ish) ----
    d.rectangle([0, 700, W, H], fill=FLOOR_A)
    for i, y in enumerate(range(700, H, 46)):
        d.rectangle([0, y, W, y + 3], fill=FLOOR_B)
        d.line([(0, y), (W, y)], fill=(140, 106, 70), width=1)
    for x in (180, 420, 700, 900):
        d.line([(x, 700), (x - 60, H)], fill=(140, 106, 70), width=2)

    # ---- window, left, with warm light ----
    d.rectangle([56, 64, 348, 452], fill=(120, 96, 70))  # frame shadow
    d.rectangle([66, 74, 338, 442], fill=(250, 226, 176))  # bright pane
    d.rectangle([66, 74, 338, 442], outline=(255, 244, 214), width=4)
    d.line([(202, 74), (202, 442)], fill=(120, 96, 70), width=8)
    d.line([(66, 258), (338, 258)], fill=(120, 96, 70), width=8)
    # distant rooftops + tree seen through the glass
    d.polygon([(66, 442), (66, 380), (150, 330), (240, 392), (338, 350), (338, 442)],
              fill=(168, 150, 118))
    d.ellipse([250, 300, 330, 372], fill=(110, 140, 90))
    d.rectangle([120, 330, 128, 442], fill=(120, 96, 70))
    # sheer curtain, right half of the window
    for i in range(6):
        x = 268 + i * 12
        d.line([(x, 74), (x - 14, 452)], fill=(255, 250, 238), width=5)

    # ---- radiator + laundry under the window ----
    d.rectangle([80, 470, 330, 560], fill=(196, 188, 172))
    for x in range(96, 326, 22):
        d.rounded_rectangle([x, 482, x + 12, 548], radius=6, fill=(176, 168, 152))
    # laundry: a striped towel + a small sock draped over the top
    d.polygon([(100, 470), (210, 470), (206, 540), (104, 540)], fill=(214, 96, 84))
    d.line([(100, 500), (208, 500)], fill=(240, 236, 220), width=6)
    d.line([(102, 522), (207, 522)], fill=(240, 236, 220), width=6)
    d.polygon([(222, 470), (268, 470), (264, 516), (226, 516)], fill=(96, 128, 160))
    d.ellipse([286, 470, 316, 506], fill=(240, 236, 220))  # sock
    d.rectangle([286, 500, 316, 512], fill=(214, 96, 84))

    # ---- framed pictures on the wall ----
    d.rectangle([420, 90, 560, 210], fill=(90, 74, 58))
    d.rectangle([432, 102, 548, 198], fill=(222, 200, 168))
    d.polygon([(440, 198), (470, 140), (500, 175), (520, 130), (548, 198)], fill=(120, 150, 110))
    d.ellipse([516, 112, 540, 136], fill=(240, 200, 110))
    d.rectangle([600, 130, 690, 200], fill=(90, 74, 58))
    d.rectangle([610, 140, 680, 190], fill=(190, 150, 120))
    d.ellipse([628, 150, 662, 184], fill=(232, 186, 148))
    d.rectangle([628, 184, 662, 190], fill=(70, 88, 118))

    # ---- rug ----
    d.ellipse([300, 760, 780, 990], fill=RUG)
    d.ellipse([330, 782, 750, 968], outline=RUG_EDGE, width=6)
    d.ellipse([380, 810, 700, 940], outline=(186, 130, 100), width=4)

    # ---- sofa, left-center ----
    rr(d, [70, 640, 520, 900], 26, SOFA)
    rr(d, [70, 640, 520, 760], 26, SOFA_DARK)  # backrest
    rr(d, [92, 700, 300, 800], 18, SOFA_CUSHION)
    rr(d, [310, 700, 498, 800], 18, SOFA_CUSHION)
    rr(d, [92, 790, 498, 862], 18, (104, 130, 116))  # seat
    rr(d, [70, 760, 110, 880], 14, SOFA_DARK)  # armrest
    rr(d, [480, 760, 520, 880], 14, SOFA_DARK)
    # cushion + throw blanket over the arm
    rr(d, [110, 712, 190, 786], 14, (196, 120, 84))
    d.polygon([(470, 760), (520, 760), (520, 880), (486, 880), (470, 830)], fill=(214, 96, 84))

    # ---- mother on the sofa ----
    mug_hand = person(d, 250, 600, 1.0, SKIN_A, HAIR_DARK, SWEATER, JEANS, "sit_sofa")
    # mug in her hand
    mx, my = mug_hand
    d.rounded_rectangle([mx - 4, my - 16, mx + 22, my + 8], radius=4, fill=(196, 84, 66))
    d.arc([mx + 20, my - 10, mx + 34, my + 4], start=270, end=90, fill=(196, 84, 66), width=4)
    # book left open on the sofa beside her
    d.polygon([(360, 800), (420, 792), (420, 818), (360, 824)], fill=(240, 236, 220))
    d.polygon([(420, 792), (478, 800), (478, 824), (420, 818)], fill=(226, 220, 202))
    d.line([(420, 792), (420, 818)], fill=(120, 110, 96), width=2)

    # ---- kitchen counter, right ----
    d.rectangle([660, 560, W, H], fill=COUNTER)
    d.rectangle([660, 560, W, 596], fill=COUNTER_TOP)
    d.line([(660, 596), (W, 596)], fill=(150, 128, 100), width=3)
    d.rectangle([700, 640, 790, 700], outline=(90, 70, 52), width=3)  # cabinet door
    d.rectangle([820, 640, 910, 700], outline=(90, 70, 52), width=3)
    d.ellipse([742, 664, 752, 674], fill=(90, 70, 52))
    d.ellipse([862, 664, 872, 674], fill=(90, 70, 52))
    # shelf with jars above the counter
    d.rectangle([700, 300, 980, 318], fill=(120, 96, 70))
    for jx, jc in ((720, (214, 180, 120)), (790, (150, 120, 90)), (860, (196, 150, 110))):
        rr(d, [jx, 240, jx + 44, 300], 8, jc)
        rr(d, [jx + 4, 232, jx + 40, 244], 4, (90, 70, 52))
    # hanging plant, top right
    d.line([(950, 60), (950, 120)], fill=(120, 96, 70), width=3)
    d.polygon([(920, 120), (980, 120), (968, 160), (932, 160)], fill=(168, 96, 66))
    for ang in (-50, -20, 10, 40):
        x1 = 950 + int(34 * __import__("math").sin(__import__("math").radians(ang)))
        y1 = 120 - int(30 * abs(__import__("math").cos(__import__("math").radians(ang))))
        d.line([(950, 118), (x1, y1)], fill=(90, 130, 80), width=4)

    # ---- father behind the counter ----
    person(d, 800, 470, 1.0, SKIN_B, HAIR_DARK, (120, 140, 150), JEANS, "stand_counter")
    # chopping board + half-peeled carrot on the counter top
    d.rounded_rectangle([690, 536, 890, 562], radius=6, fill=(196, 150, 100))
    # carrot: orange body, peeled pale half, green top
    d.polygon([(722, 544), (800, 544), (814, 558), (722, 558)], fill=(232, 122, 40))
    d.polygon([(800, 544), (860, 544), (868, 558), (800, 558)], fill=(244, 200, 130))
    d.polygon([(718, 544), (734, 530), (750, 544)], fill=(90, 140, 70))
    # peel strips beside it
    d.polygon([(828, 552), (850, 544), (860, 554), (838, 562)], fill=(232, 122, 40))
    d.polygon([(810, 558), (826, 550), (834, 560), (818, 562)], fill=(244, 200, 130))
    # knife in his hand
    d.line([(738, 538), (774, 516)], fill=(220, 224, 228), width=7)
    d.line([(738, 538), (724, 548)], fill=(60, 48, 40), width=8)
    # mug on the counter
    d.rounded_rectangle([920, 532, 952, 560], radius=4, fill=(96, 128, 160))

    # ---- mismatched chairs stacked by the wall (right of counter) ----
    # chair 1 (wooden, upside down on top of chair 2)
    d.rectangle([952, 620, 960, 700], fill=(140, 100, 60))
    d.rectangle([1000, 620, 1008, 700], fill=(140, 100, 60))
    d.rectangle([948, 700, 1012, 716], fill=(150, 108, 64))
    d.rectangle([952, 716, 960, 790], fill=(140, 100, 60))
    d.rectangle([1000, 716, 1008, 790], fill=(140, 100, 60))
    # chair 2 (painted blue, seat visible)
    d.rectangle([946, 800, 1014, 816], fill=(90, 120, 150))
    d.rectangle([950, 816, 958, 880], fill=(80, 108, 138))
    d.rectangle([1002, 816, 1010, 880], fill=(80, 108, 138))

    # ---- wall clock + floor lamp fill the middle wall ----
    d.ellipse([566, 186, 634, 254], fill=(240, 236, 220), outline=(90, 74, 58), width=4)
    d.line([(600, 220), (600, 196)], fill=(60, 48, 40), width=3)
    d.line([(600, 220), (618, 228)], fill=(60, 48, 40), width=3)
    d.ellipse([596, 216, 604, 224], fill=(60, 48, 40))
    # floor lamp between sofa and counter
    d.ellipse([540, 828, 592, 842], fill=(90, 74, 58))
    d.line([(566, 832), (566, 620)], fill=(90, 74, 58), width=5)
    d.polygon([(536, 620), (596, 620), (586, 566), (546, 566)], fill=(240, 200, 110))
    d.polygon([(536, 620), (596, 620), (586, 566), (546, 566)], outline=(200, 160, 80), width=2)

    # ---- child on the rug with blocks ----
    person(d, 470, 800, 0.72, SKIN_C, HAIR_DARK, SHIRT_KID, (90, 110, 140), "sit_floor")
    # wooden blocks: a small tower + scattered ones
    for bx, by, bc in ((524, 876, (214, 160, 80)), (560, 876, (150, 110, 70)),
                       (524, 840, (150, 110, 70)), (596, 882, (196, 120, 84)),
                       (420, 888, (120, 150, 110))):
        d.rectangle([bx, by, bx + 36, by + 36], fill=bc, outline=(90, 70, 52), width=2)
    d.rectangle([524, 840, 560, 876], fill=(214, 160, 80), outline=(90, 70, 52), width=2)

    # ---- the machine member: small household robot, mid-task with a tray ----
    rx, ry = 640, 880  # body centre
    # soft shadow
    d.ellipse([rx - 66, ry + 62, rx + 66, ry + 82], fill=(120, 96, 70))
    # wheels
    d.ellipse([rx - 58, ry + 28, rx - 14, ry + 72], fill=ROBOT_DARK)
    d.ellipse([rx + 14, ry + 28, rx + 58, ry + 72], fill=ROBOT_DARK)
    d.ellipse([rx - 44, ry + 42, rx - 28, ry + 58], fill=(120, 122, 126))
    d.ellipse([rx + 28, ry + 42, rx + 44, ry + 58], fill=(120, 122, 126))
    # body: rounded, slightly scuffed cream with teal band
    rr(d, [rx - 52, ry - 52, rx + 52, ry + 40], 24, ROBOT_BODY, outline=(190, 182, 166), width=2)
    d.rectangle([rx - 52, ry - 6, rx + 52, ry + 14], fill=ROBOT_TEAL)
    d.rectangle([rx - 30, ry + 2, rx - 14, ry + 8], fill=(232, 226, 212))
    d.rectangle([rx + 2, ry + 2, rx + 18, ry + 8], fill=(232, 226, 212))
    # scuff marks
    d.arc([rx - 40, ry - 44, rx - 8, ry - 20], start=200, end=340, fill=(170, 162, 148), width=3)
    d.line([(rx + 30, ry - 40), (rx + 42, ry - 28)], fill=(170, 162, 148), width=3)
    # head mast + eye
    d.rectangle([rx - 8, ry - 78, rx + 8, ry - 50], fill=ROBOT_TEAL)
    rr(d, [rx - 26, ry - 104, rx + 26, ry - 70], 12, ROBOT_BODY, outline=(190, 182, 166), width=2)
    d.ellipse([rx - 12, ry - 94, rx + 12, ry - 76], fill=(40, 44, 50))
    d.ellipse([rx - 5, ry - 89, rx + 3, ry - 81], fill=(150, 220, 210))
    d.ellipse([rx + 30, ry - 100, rx + 38, ry - 92], fill=(120, 200, 110))  # status light
    # arm holding a tray with a cup, reaching toward the sofa
    limb(d, rx - 44, ry - 20, rx - 78, ry - 52, 14, ROBOT_TEAL)
    limb(d, rx - 78, ry - 52, rx - 96, ry - 84, 12, ROBOT_TEAL)
    d.ellipse([rx - 104, ry - 92, rx - 88, ry - 76], fill=ROBOT_DARK)
    # tray
    d.polygon([(rx - 128, ry - 96), (rx - 66, ry - 96), (rx - 72, ry - 84), (rx - 122, ry - 84)],
              fill=(190, 182, 166))
    # cup on the tray
    d.rounded_rectangle([rx - 112, ry - 116, rx - 90, ry - 96], radius=3, fill=(240, 236, 220))
    d.arc([rx - 92, ry - 112, rx - 80, ry - 100], start=270, end=90, fill=(240, 236, 220), width=3)
    # faint motion ticks behind the wheels
    for i, mx in enumerate((rx + 66, rx + 78, rx + 90)):
        d.line([(mx, ry + 58), (mx + 10, ry + 58)], fill=(150, 128, 100), width=3)

    # ---- dog bowl by the rug ----
    d.ellipse([120, 930, 210, 962], fill=(70, 110, 150))
    d.ellipse([132, 934, 198, 952], fill=(50, 88, 126))
    for kx, ky in ((150, 940), (168, 944), (184, 940), (160, 948), (178, 948)):
        d.ellipse([kx, ky, kx + 7, ky + 6], fill=(150, 110, 70))
    # a slipper kicked off nearby
    d.ellipse([250, 950, 300, 968], fill=(186, 84, 66))
    d.ellipse([252, 946, 282, 958], fill=(214, 120, 96))

    # ---- warm light wash + photo finish (overlay, then grain + vignette) ----
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.polygon([(66, 74), (348, 74), (560, 1024), (120, 1024)], fill=(255, 214, 140, 26))
    od.polygon([(66, 442), (348, 442), (620, 1024), (200, 1024)], fill=(255, 200, 120, 18))
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")

    # vignette
    vig = Image.new("L", (W, H), 0)
    vd = ImageDraw.Draw(vig)
    vd.ellipse([-220, -220, W + 220, H + 220], fill=255)
    vig = vig.filter(ImageFilter.GaussianBlur(180))
    black = Image.new("RGB", (W, H), (24, 18, 12))
    img = Image.composite(img, black, vig.point(lambda p: 255 - int((255 - p) * 0.55)))

    # film grain (seeded, deterministic)
    rnd = random.Random(42)
    px = img.load()
    for _ in range(9000):
        x, y = rnd.randrange(W), rnd.randrange(H)
        v = rnd.randint(-14, 14)
        r, g, b = px[x, y]
        px[x, y] = (max(0, min(255, r + v)), max(0, min(255, g + v)), max(0, min(255, b + v)))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    img.save(OUT, "PNG", optimize=True)
    print(f"wrote {OUT} {os.path.getsize(OUT)} bytes")


if __name__ == "__main__":
    draw()

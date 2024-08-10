from typing import List, Tuple, Optional

from msodumper.number_format import format_number_according_to_MSONFC

class LFO:
    lsid: int

class LSTF:
    lsid: int
    fSimpleList: int

class LFOLVL:
    iLvl: int
    fFormatting: int
    lvl: int

class LFOData:
    rgLfoLvl: List[LFOLVL]

class PlfLfo:
    rgLfo: List[LFO]
    rgLfoData: List[LFOData]

class PlfLst:
    rgLstf: List[LSTF]


from typing import List, Tuple, Optional

class LVLF:
    nfc: int
    rgbxchNums: List[int]
    fLegal: int

class LVL:
    xst: List[int]
    lvlf: LVLF

def get_paragraph_number_text(
    lvl: LVL,
    iLvlCur: int,
    previous_paragraph_levels: List[int]
) -> Optional[List[int]]:
    """
    根据给定的参数，使用python实现获取段落编号文本的函数。

    Args:
        lvl: LVL 对象。
        iLvlCur: 段落的 iLvl 属性。
        previous_paragraph_levels: 之前段落的 iLvl 属性列表。

    Returns:
        如果段落是列表的一部分，则返回一个列表，包含段落编号文本的字符数组。
        如果段落不是列表的一部分，则返回 None。
    """

    # 复制 lvl.xst 到 xstNumberText。
    xstNumberText = lvl.xst.copy()

    # 如果 lvl.lvlf.nfc 不等于 0x17，则跳到步骤 4。
    if lvl.lvlf.nfc != 0x17:
        return None

    # 获取 xchBullet 变量。
    xchBullet = xstNumberText[0]

    # 如果 xchBullet & 0xF000 不为零，则将 xstNumberText[0] 设置为 xchBullet & 0x0FFF。
    if xchBullet & 0xF000 != 0:
        xstNumberText[0] = xchBullet & 0x0FFF

    # 遍历 lvl.lvlf.rgbxchNums 中的所有条目。
    for j, iLvlTemp_index in enumerate(lvl.lvlf.rgbxchNums):
        # 如果 lvl.lvlf.rgbxchNums[j] 为零，则跳过当前循环。
        if iLvlTemp_index == 0:
            continue

        # 获取 iLvlTemp 变量。
        iLvlTemp = lvl.xst[iLvlTemp_index - 1]

        # 如果 iLvlTemp 等于 iLvlCur，则将 xstNumberText 中的 iLvlTemp 占位符替换为当前段落的级别编号。
        if iLvlTemp == iLvlCur:
            xstNumberText[iLvlTemp_index - 1] = iLvlCur

        # 如果 iLvlTemp 小于 iLvlCur，则将 xstNumberText 中的 iLvlTemp 占位符替换为之前段落中最近的级别编号，该级别编号等于 iLvlTemp。
        elif iLvlTemp < iLvlCur:
            # 找到之前段落中最近的级别编号，该级别编号等于 iLvlTemp。
            closest_previous_level = next((level for level in reversed(previous_paragraph_levels) if level == iLvlTemp), None)

            # 如果找到了 closest_previous_level，则将 xstNumberText 中的 iLvlTemp 占位符替换为 closest_previous_level。
            if closest_previous_level is not None:
                xstNumberText[iLvlTemp_index - 1] = closest_previous_level
            else:
                return None

        # 如果 iLvlTemp 大于 iLvlCur，则文件无效，算法结束。
        elif iLvlTemp > iLvlCur:
            return None

        # 如果 lvl.lvlf.fLegal 不为零，则根据 LVLF 中的 fLegal 字段描述重新格式化每个级别编号，然后再替换其相应的占位符。
        if lvl.lvlf.fLegal != 0:
            # TODO: 根据 LVLF 中的 fLegal 字段描述重新格式化每个级别编号。
            pass

    return xstNumberText

class LSTF:
    rgistdPara: List[int]

class LVL:
    lvlf: LVLF
    grpprlChpx: List[int]
    grpprlPapx: List[int]

class LVLF:
    ixchFollow: int
    jc: int

def format_paragraph_and_number_text(
    lstf: LSTF,
    lvl: LVL,
    xstNumberText: List[int],
    paragraph: object,  # 假设 paragraph 是一个可以应用样式的对象
):
    """
    根据给定的参数，使用python实现格式化段落和编号文本的函数。

    Args:
        lstf: LSTF 对象。
        lvl: LVL 对象。
        xstNumberText: 编号文本的字符数组。
        paragraph: 段落对象。

    Returns:
        None
    """

    # 如果 lstf.rgistdPara[iLvlCur] 不等于 0x0FFF，则将 lstf.rgistdPara[iLvlCur] 指定的样式应用于段落和 xstNumberText。
    if lstf.rgistdPara[iLvlCur] != 0x0FFF:
        # TODO: 将 lstf.rgistdPara[iLvlCur] 指定的样式应用于段落和 xstNumberText。
        pass

    # 将 lvl.grpprlChpx 指定的字符属性应用于 xstNumberText。
    # TODO: 将 lvl.grpprlChpx 指定的字符属性应用于 xstNumberText。
    pass

    # 将 lvl.lvlf.ixchFollow 指定的字符追加到 xstNumberText。
    xstNumberText.append(lvl.lvlf.ixchFollow)

    # 将 lvl.grpprlPapx 指定的段落属性应用于段落，包括 xstNumberText。
    # TODO: 将 lvl.grpprlPapx 指定的段落属性应用于段落，包括 xstNumberText。
    pass

    # 根据 lvl.lvlf.jc 指定的对齐方式，仅对 xstNumberText 进行对齐。
    # TODO: 根据 lvl.lvlf.jc 指定的对齐方式，仅对 xstNumberText 进行对齐。
    pass

class Paragraph:
    iLfo: int
    iLvl: int
    char_position: int

def get_paragraph_level_number(
    PlfLfo: PlfLfo,
    PlfLst: PlfLst,
    FibRgFcLcb97: List[int],
    paragraphs: List[Paragraph]
) -> Optional[str]:
    """
    根据给定的参数，使用python实现获取段落级别编号的函数。

    Args:
        cp: 当前段落对象。
        PlfLfo: PlfLfo 对象。
        PlfLst: PlfLst 对象。
        FibRgFcLcb97: FibRgFcLcb97 数组。
        paragraphs: 所有段落对象的列表。

    Returns:
        如果段落是列表的一部分，则返回一个字符串，包含段落的级别编号。
        如果段落不是列表的一部分，则返回 None。
    """

    # 步骤 1-10：获取 iLvlCur 和 lvl。
    iLfoCur, iLvlCur, lvl = get_paragraph_properties(cp.iLfo, cp.iLvl, PlfLfo, PlfLst, FibRgFcLcb97)

    # 如果没有找到 iLvlCur 和 lvl，则返回 None。
    if iLvlCur is None or lvl is None:
        return None

    # 获取 lsidCur。
    lsidCur = PlfLfo.rgLfo[cp.iLfo - 1].lsid

    # 获取 nfcCur。
    nfcCur = lvl.lvlf.nfc

    # 如果 nfcCur 等于 0xFF 或 0x17，则该级别没有编号序列，段落的级别编号为空字符串。
    if nfcCur == 0xFF or nfcCur == 0x17:
        return ""

    # 获取 iStartAt。
    iStartAt = lvl.lvlf.iStartAt

    # 获取 iLvlRestartLim。
    if lvl.lvlf.fNoRestart != 0:
        iLvlRestartLim = lvl.lvlf.iLvlRestartLim
    else:
        iLvlRestartLim = iLvlCur

    # 初始化 numCur。
    numCur = iStartAt

    # 遍历所有段落。
    for p in paragraphs:
        # 如果段落的 iLfo 属性为零，则跳过当前循环。
        if p.iLfo == 0:
            continue

        # 如果段落不在与 cp 相同的有效选择范围内，则跳过当前循环。
        if p.char_position >= cp.char_position:
            continue

        # 步骤 1-6：获取 lfo.lsid 和 lfolvl。
        lfo_lsid, _, _ = get_paragraph_properties(p.iLfo, p.iLvl, PlfLfo, PlfLst, FibRgFcLcb97)

        # 如果 lfo.lsid 不等于 lsidCur，则跳过当前循环。
        if lfo_lsid != lsidCur:
            continue

        # 如果段落的 iLvl 属性小于 iLvlRestartLim，则将 numCur 设置为 iStartAt。
        if p.iLvl < iLvlRestartLim:
            numCur = iStartAt

        # 如果段落的 iLvl 属性不等于 iLvlCur，则跳过当前循环。
        if p.iLvl != iLvlCur:
            continue

        # 获取 lfolvl。
        lfolvl = PlfLfo.rgLfoData[p.iLfo - 1].rgLfoLvl[p.iLvl]

        # 如果段落的 iLfo 属性之前没有遇到过，并且 lfolvl.fStartAt 不为零，则将 numCur 设置为 lfolvl.iStartAt。
        if p.iLfo not in [p_.iLfo for p_ in paragraphs if p_.char_position < p.char_position] and lfolvl.fStartAt != 0:
            numCur = lfolvl.iStartAt

        # 将 numCur 加 1。
        numCur += 1

        # 如果段落 p 不包含 cp，则返回步骤 6。
        if p != cp:
            continue

        # 获取段落的级别编号。
        xsLevelNumber = format_number_according_to_MSONFC(numCur, nfcCur)

        # 返回段落的级别编号。
        return xsLevelNumber

    # 如果没有找到段落的级别编号，则返回 None。
    return None

def get_paragraph_properties(
    iLfoCur: int,
    iLvlCur: int,
    PlfLfo: PlfLfo,
    PlfLst: PlfLst,
    FibRgFcLcb97: List[int]
) -> Optional[Tuple[int, int, LVL]]:
    """
    根据给定的参数，使用python实现获取段落属性的函数。

    Args:
        iLfoCur: 段落的 iLfo 属性。
        iLvlCur: 段落的 iLvl 属性。
        PlfLfo: PlfLfo 对象。
        PlfLst: PlfLst 对象。
        FibRgFcLcb97: FibRgFcLcb97 数组。

    Returns:
        如果段落是列表的一部分，则返回一个元组，包含段落的 iLvlCur、lvl 和 fFormatting 属性。
        如果段落不是列表的一部分，则返回 None。
    """

    # 如果 iLfoCur 为零，则段落不是列表的一部分，算法结束。
    if iLfoCur == 0:
        return None

    # 获取 LFO 对象。
    lfo = PlfLfo.rgLfo[iLfoCur - 1]

    # 检查 LFO 对象是否存在。
    if lfo is None:
        return None

    # 获取 LSTF 对象。
    lstf = next((lstf for lstf in PlfLst.rgLstf if lstf.lsid == lfo.lsid), None)

    # 检查 LSTF 对象是否存在。
    if lstf is None:
        return None

    # 获取 LFOData 对象。
    lfodata = PlfLfo.rgLfoData[iLfoCur - 1]

    # 获取 LFOLVL 对象。
    lfolvl = next((lfolvl for lfolvl in lfodata.rgLfoLvl if lfolvl.iLvl == iLvlCur), None)

    # 如果没有找到 LFOLVL 对象，则跳到步骤 8。
    if lfolvl is None:
        return None

    # 如果 lfolvl.fFormatting 不为零，则获取 lvl 属性并跳到步骤 2。
    if lfolvl.fFormatting != 0:
        lvl = lfolvl.lvl
        return iLvlCur, lvl, lfolvl.fFormatting

    # 初始化 i 变量。
    i = 0

    # 遍历 PlfLst.rgLstf 中的所有 LSTF 对象。
    for lstf_ in PlfLst.rgLstf:
        # 如果 LSTF.fSimpleList 为零，则 i 加 9。
        if lstf_.fSimpleList == 0:
            i += 9
        # 如果 LSTF.fSimpleList 不为零，则 i 加 1。
        else:
            i += 1

    # 将 i 加上 iLvlCur。
    i += iLvlCur

    # 获取 lvl 属性。
    lvl = LVL(lvlf=LVLF(nfc=FibRgFcLcb97[i], iStartAt=FibRgFcLcb97[i + 1], fNoRestart=FibRgFcLcb97[i + 2], iLvlRestartLim=FibRgFcLcb97[i + 3]))

    return iLvlCur, lvl, 0
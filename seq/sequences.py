import seq.rare_new as rare
# import seq.haste as haste
# import seq.gre as gre

class RARE(rare.RARE):
    def __init__(self): super(RARE, self).__init__()

# class HASTE(haste.HASTE):
#     def __init__(self): super(HASTE, self).__init__()
#
# class GRE(gre.GRE):
#     def __init__(self): super(GRE, self).__init__()

"""
Definition of default sequences
"""
defaultsequences={
    'RARE': RARE(),
    # 'HASTE': HASTE(),
    # 'GRE3D': GRE3D(),
    }
def get_raw_test_cases():
	return {
		"tabnav_move_cursor_start": {
			"markdown": {
				"markdown01_unformatted_table.md":
				[
					{
						"id": "MSR5",
						"description": "Single cursor in first cell",
						"initial_selections": [(6, 6)],
						"expected_selections": [(1, 1)]
					},
					{
						"id": "FQ3N",
						"description": "Single cursor in last cell of row",
						"initial_selections": [(138, 138)],
						"expected_selections": [(132, 132)]
					},
					{
						"id": "MZ66",
						"description": "Single cursor in line separator cell",
						"initial_selections": [(56, 56)],
						"expected_selections": [(51, 51)]
					},
					{
						"id": "NTGM",
						"description": "Single cursor already at start of first cell of row",
						"initial_selections": [(101, 101)],
						"expected_selections": [(101, 101)]
					},
					{
						"id": "TFBP",
						"description": "Single cursor already at start of cell",
						"initial_selections": [(112, 112)],
						"expected_selections": [(112, 112)]
					},
					{
						"id": "KLJL",
						"description": "Single cursor in empty cell",
						"initial_selections": [(206, 206)],
						"expected_selections": [(206, 206)]
					},
					{
						"id": "ZFVU",
						"description": "Single cursor after last pipe (not in table)",
						"initial_selections": [(280, 280)],
						"expected_selections": [(280, 280)]
					},
					{
						"id": "QRBV",
						"description": "Single cursor before first pipe (not in table)",
						"initial_selections": [(100, 100)],
						"expected_selections": [(100, 100)]
					},
					{
						"id": "E5R2",
						"description": "Multiple cursors single cell",
						"initial_selections": [(152, 152), (158, 158), (163, 163), (170, 170), (177, 177), (184, 184)],
						"expected_selections": [(149, 149)]
					},
					{
						"id": "I4DY",
						"description": "Cell selected forward",
						"initial_selections": [(192, 205)],
						"expected_selections": [(192, 192)]
					},
					{
						"id": "EP4Y",
						"description": "Cell selected reverse",
						"initial_selections": [(247, 243)],
						"expected_selections": [(243, 243)]
					},
					{
						"id": "HFP5",
						"description": "Region spans a cell plus pipes on either end (3 cells)",
						"initial_selections": [(111, 120)],
						"expected_selections": [(101, 101), (112, 112), (120, 120)]
					},
					{
						"id": "N6WP",
						"description": "Region spans three body rows",
						"initial_selections": [(123, 244)],
						"expected_selections": [(120, 120), (132, 132), (149, 149), (192, 192), (206, 206), (207, 207), (227, 227), (243, 243)]
					},
					{
						"id": "X7DY",
						"description": "Region spans body and separator row, separators excluded",
						"initial_selections": [(14, 128)],
						"expected_selections": [(13, 13), (25, 25), (37, 37), (101, 101), (112, 112), (120, 120)],
						"settings": {"tabnav.include_separators": False}
					},
					{
						"id": "WTGF",
						"description": "Region spans body and separator row, separators included",
						"initial_selections": [(14, 128)],
						"expected_selections": [(13, 13), (25, 25), (37, 37), (51, 51), (63, 63), (75, 75), (87, 87), (101, 101), (112, 112), (120, 120)],
						"settings": {"tabnav.include_separators": True}
					}
				],
				"markdown02_multiple_tables.md":
				[
					{
						"id": "3AWG",
						"description": "Multiple cursors in multiple tables",
						"initial_selections": [(280, 280), (763, 763), (1395, 1395), (1922, 1922), (2338, 2338)],
						"expected_selections": [(265, 265), (759, 759), (1384, 1384), (1922, 1922), (2326, 2326)]
					},
					{
						"id": "7EN6",
						"description": "Cursor in empty line between tables (not in table)",
						"initial_selections": [(1860, 1860)],
						"expected_selections": [(1860, 1860)]
					},
					{
						"id": "ZP7L",
						"description": "Single region spans multiple tables (no change)",
						"initial_selections": [(1537, 2001)],
						"expected_selections": [(1537, 2001)]
					},
					{
						"id": "3SGX",
						"description": "Multiple cursors in multiple line separator rows",
						"initial_selections": [(212, 212), (1913, 1913)],
						"expected_selections": [(208, 208), (1906, 1906)]
					}
				],
				"markdown03_borderless.md":
				[
					{
						"id": "FJL7",
						"description": "Cursor in first column",
						"initial_selections": [(75, 75)],
						"expected_selections": [(68, 68)]
					},
					{
						"id": "IJF6",
						"description": "Cursor in last column",
						"initial_selections": [(98, 98)],
						"expected_selections": [(91, 91)]
					},
					{
						"id": "DKGB",
						"description": "Cursor at start of first column",
						"initial_selections": [(136, 136)],
						"expected_selections": [(136, 136)]
					},
					{
						"id": "KG6S",
						"description": "Cursor in first column of separator",
						"initial_selections": [(39, 39)],
						"expected_selections": [(34, 34)]
					},
					{
						"id": "EQ44",
						"description": "Cursor in last column of separator",
						"initial_selections": [(62, 62)],
						"expected_selections": [(57, 57)]
					},
					{
						"id": "J42R",
						"description": "Selection spans separator row",
						"initial_selections": [(18, 86)],
						"expected_selections": [(11, 11), (23, 23), (68, 68), (79, 79)]
					}
				]
			}
		},
		"tabnav_move_cursor_end": {
			"markdown": {
				"markdown01_unformatted_table.md":
				[
					{
						"id": "RKGZ",
						"description": "Single cursor in first cell",
						"initial_selections": [(6, 6)],
						"expected_selections": [(12, 12)]
					},
					{
						"id": "7STJ",
						"description": "Single cursor in last cell of row",
						"initial_selections": [(138, 138)],
						"expected_selections": [(146, 146)]
					},
					{
						"id": "TEMV",
						"description": "Single cursor in line separator cell",
						"initial_selections": [(56, 56)],
						"expected_selections": [(62, 62)]
					},
					{
						"id": "KXHP",
						"description": "Single cursor already at end of cell",
						"initial_selections": [(111, 111)],
						"expected_selections": [(111, 111)]
					},
					{
						"id": "65KK",
						"description": "Single cursor already at end of last cell of row",
						"initial_selections": [(146, 146)],
						"expected_selections": [(146, 146)]
					},
					{
						"id": "3W7Q",
						"description": "Single cursor in empty cell",
						"initial_selections": [(206, 206)],
						"expected_selections": [(206, 206)]
					},
					{
						"id": "FSUM",
						"description": "Single cursor after last pipe (not in table)",
						"initial_selections": [(280, 280)],
						"expected_selections": [(280, 280)]
					},
					{
						"id": "P67M",
						"description": "Single cursor before first pipe (not in table)",
						"initial_selections": [(100, 100)],
						"expected_selections": [(100, 100)]
					},
					{
						"id": "LYSY",
						"description": "Multiple cursors single cell",
						"initial_selections": [(152, 152), (158, 158), (163, 163), (170, 170), (177, 177), (184, 184)],
						"expected_selections": [(191, 191)]
					},
					{
						"id": "7UAV",
						"description": "Cell selected forward",
						"initial_selections": [(192, 205)],
						"expected_selections": [(205, 205)]
					},
					{
						"id": "OOXZ",
						"description": "Cell selected reverse",
						"initial_selections": [(247, 243)],
						"expected_selections": [(247, 247)]
					},
					{
						"id": "6GRX",
						"description": "Region spans a cell plus pipes on either end (3 cells)",
						"initial_selections": [(111, 120)],
						"expected_selections": [(111, 111), (119, 119), (131, 131)]
					},
					{
						"id": "HICB",
						"description": "Region spans three body rows",
						"initial_selections": [(123, 244)],
						"expected_selections": [(131, 131), (146, 146), (191, 191), (205, 205), (206, 206), (224, 224), (242, 242), (247, 247)]
					},
					{
						"id": "PTUN",
						"description": "Region spans body and separator row, separators excluded",
						"initial_selections": [(14, 128)],
						"expected_selections": [(24, 24), (36, 36), (48, 48), (111, 111), (119, 119), (131, 131)],
						"settings": {"tabnav.include_separators": False}
					},
					{
						"id": "NPWG",
						"description": "Region spans body and separator row, separators included",
						"initial_selections": [(14, 128)],
						"expected_selections": [(24, 24), (36, 36), (48, 48), (62, 62), (74, 74), (86, 86), (98, 98), (111, 111), (119, 119), (131, 131)],
						"settings": {"tabnav.include_separators": True}
					}
				],
				"markdown02_multiple_tables.md":
				[
					{
						"id": "2UF4",
						"description": "Multiple cursors in multiple tables",
						"initial_selections": [(280, 280), (763, 763), (1395, 1395), (1922, 1922), (2338, 2338)],
						"expected_selections": [(284, 284), (766, 766), (1402, 1402), (1935, 1935), (2339, 2339)]
					},
					{
						"id": "XKMY",
						"description": "Cursor in empty line between tables (not in table)",
						"initial_selections": [(1860, 1860)],
						"expected_selections": [(1860, 1860)]
					},
					{
						"id": "VDEY",
						"description": "Single region spans multiple tables (no change)",
						"initial_selections": [(1537, 2001)],
						"expected_selections": [(1537, 2001)]
					},
					{
						"id": "BGP3",
						"description": "Multiple cursors in multiple line separator rows",
						"initial_selections": [(212, 212), (1913, 1913)],
						"expected_selections": [(226, 226), (1919, 1919)]
					}
				],
				"markdown03_borderless.md":
				[
					{
						"id": "L5EO",
						"description": "Cursor in first column",
						"initial_selections": [(75, 75)],
						"expected_selections": [(78, 78)]
					},
					{
						"id": "4MHS",
						"description": "Cursor in last column",
						"initial_selections": [(98, 98)],
						"expected_selections": [(101, 101)]
					},
					{
						"id": "3JFE",
						"description": "Cursor at start of first column",
						"initial_selections": [(136, 136)],
						"expected_selections": [(146, 146)]
					},
					{
						"id": "67MF",
						"description": "Cursor in first column of separator",
						"initial_selections": [(39, 39)],
						"expected_selections": [(44, 44)]
					},
					{
						"id": "RQJE",
						"description": "Cursor in last column of separator",
						"initial_selections": [(62, 62)],
						"expected_selections": [(67, 67)]
					},
					{
						"id": "RAFL",
						"description": "Selection spans separator row",
						"initial_selections": [(18, 86)],
						"expected_selections": [(22, 22), (33, 33), (78, 78), (90, 90)]
					}
				]
			}
		},
		"tabnav_move_cursor_left": {
			"markdown": {
				"markdown01_unformatted_table.md":
				[
					{
						"id": "24UC",
						"description": "Single cursor in first cell",
						"initial_selections": [(6, 6)],
						"expected_selections": [(1, 1)]
					},
					{
						"id": "SPKB",
						"description": "Single cursor in last cell of row",
						"initial_selections": [(138, 138)],
						"expected_selections": [(132, 132)]
					},
					{
						"id": "NQGK",
						"description": "Single cursor at start of cell in line separator cell",
						"initial_selections": [(75, 75)],
						"expected_selections": [(63, 63)]
					},
					{
						"id": "KSM7",
						"description": "Single cursor already at start of first cell of row",
						"initial_selections": [(101, 101)],
						"expected_selections": [(101, 101)]
					},
					{
						"id": "BEIC",
						"description": "Single cursor already at start of cell",
						"initial_selections": [(112, 112)],
						"expected_selections": [(101, 101)]
					},
					{
						"id": "O4EV",
						"description": "Single cursor in empty cell",
						"initial_selections": [(206, 206)],
						"expected_selections": [(192, 192)]
					},
					{
						"id": "47XD",
						"description": "Target cell is an empty cell",
						"initial_selections": [(207, 207),],
						"expected_selections": [(206, 206)]
					},
					{
						"id": "NXW6",
						"description": "Single cursor after last pipe (not in table)",
						"initial_selections": [(280, 280)],
						"expected_selections": [(280, 280)]
					},
					{
						"id": "RPP2",
						"description": "Single cursor before first pipe (not in table)",
						"initial_selections": [(100, 100)],
						"expected_selections": [(100, 100)]
					},
					{
						"id": "5Z6J",
						"description": "Multiple cursors, some at start of cell, some not",
						"initial_selections": [(19, 19), (112, 112), (180, 180), (248, 248)],
						"expected_selections": [(13, 13), (112, 112), (149, 149), (248, 248)]
					},
					{
						"id": "3DGS",
						"description": "Multiple cursors, all at the start of their respective cells",
						"initial_selections": [(37, 37), (132, 132), (248, 248), (347, 347)],
						"expected_selections": [(25, 25), (120, 120), (243, 243), (312, 312)]
					},
					{
						"id": "EHXK",
						"description": "Multiple cursors, some at start of first column",
						"initial_selections": [(1, 1), (120, 120), (227, 227), (347, 347)],
						"expected_selections": [(1, 1), (112, 112), (227, 227), (312, 312)]
					},
					{
						"id": "5XC2",
						"description": "Two cursors merging to one at start of first cell of colum",
						"initial_selections": [(227, 227), (243, 243)],
						"expected_selections": [(227, 227)]
					},
					{
						"id": "JKG6",
						"description": "Multiple cursors same row, one cursor is the target for another",
						"initial_selections": [(112, 112), (120, 120)],
						"expected_selections": [(101, 101), (112, 112)]
					}
				],
				"markdown02_multiple_tables.md":
				[
					{
						"id": "HH5L",
						"description": "Multiple cursors at start of cells in multiple tables",
						"initial_selections": [(97, 97), (285, 285), (712, 712), (1067, 1067), (1417, 1417), (1683, 1683), (1996, 1996), (2162, 2162)],
						"expected_selections": [(97, 97), (265, 265), (705, 705), (1048, 1048), (1403, 1403), (1669, 1669), (1982, 1982), (2162, 2162)]
					},
					{
						"id": "OH6Z",
						"description": "Multiple cursors in multiple line separator rows",
						"initial_selections": [(208, 208), (1906, 1906)],
						"expected_selections": [(201, 201), (1892, 1892)]
					}
				],
				"markdown03_borderless.md":
				[
					{
						"id": "DRII",
						"description": "Cursors at start of each column",
						"initial_selections": [(0, 0), (79, 79), (125, 125)],
						"expected_selections": [(0, 0), (68, 68), (113, 113)]
					}
				],
			}
		},
		"tabnav_move_cursor_right": {
			"markdown": {
				"markdown01_unformatted_table.md":
				[
					{
						"id": "SGRB",
						"description": "Single cursor in first cell",
						"initial_selections": [(6, 6)],
						"expected_selections": [(12, 12)]
					},
					{
						"id": "72AV",
						"description": "Single cursor in last cell of row",
						"initial_selections": [(138, 138)],
						"expected_selections": [(146, 146)]
					},
					{
						"id": "TFIU",
						"description": "Single cursor at end of cell in line separator cell",
						"initial_selections": [(74, 74)],
						"expected_selections": [(86, 86)]
					},
					{
						"id": "J3S7",
						"description": "Single cursor already at end of last cell of row",
						"initial_selections": [(146, 146)],
						"expected_selections": [(146, 146)]
					},
					{
						"id": "ZII7",
						"description": "Single cursor already at end of cell",
						"initial_selections": [(191, 191)],
						"expected_selections": [(205, 205)]
					},
					{
						"id": "ELLF",
						"description": "Single cursor in empty cell",
						"initial_selections": [(206, 206)],
						"expected_selections": [(224, 224)]
					},
					{
						"id": "P7EM",
						"description": "Target cell is an empty cell",
						"initial_selections": [(205, 205)],
						"expected_selections": [(206, 206)]
					},
					{
						"id": "JEPY",
						"description": "Single cursor after last pipe (not in table)",
						"initial_selections": [(280, 280)],
						"expected_selections": [(280, 280)]
					},
					{
						"id": "L5ZP",
						"description": "Single cursor before first pipe (not in table)",
						"initial_selections": [(100, 100)],
						"expected_selections": [(100, 100)]
					},
					{
						"id": "JZGG",
						"description": "Multiple cursors, some at end of cell, some not",
						"initial_selections": [(12, 12), (114, 114), (191, 191), (295, 295)],
						"expected_selections": [(12, 12), (119, 119), (191, 191), (307, 307)]
					},
					{
						"id": "C4OR",
						"description": "Multiple cursors, all at the end of their respective cells",
						"initial_selections": [(12, 12), (119, 119), (191, 191), (307, 307)],
						"expected_selections": [(24, 24), (131, 131), (205, 205), (311, 311)]
					},
					{
						"id": "JTBR",
						"description": "Multiple cursors, some at end of last column",
						"initial_selections": [(36, 36), (146, 146), (206, 206), (279, 279), (346, 346)],
						"expected_selections": [(48, 48), (146, 146), (224, 224), (279, 279), (354, 354)]
					},
					{
						"id": "F5I5",
						"description": "Two cursors merging to one at end of last cell of colum",
						"initial_selections": [(131, 131), (146, 146)],
						"expected_selections": [(146, 146)]
					},
					{
						"id": "KDS6",
						"description": "Multiple cursors same row, one cursor is the target for another",
						"initial_selections": [(111, 111), (119, 119)],
						"expected_selections": [(119, 119), (131, 131)]
					}
				],
				"markdown02_multiple_tables.md":
				[
					{
						"id": "GOEZ",
						"description": "Multiple cursors at end of cells in multiple tables",
						"initial_selections": [(478, 478), (704, 704), (996, 996), (1522, 1522), (2055, 2055), (2279, 2279)],
						"expected_selections": [(492, 492), (711, 711), (1010, 1010), (1522, 1522), (2069, 2069), (2279, 2279)]
					},
					{
						"id": "4WIC",
						"description": "Multiple cursors in multiple line separator rows",
						"initial_selections": [(207, 207), (1905, 1905)],
						"expected_selections": [(226, 226), (1919, 1919)]
					}
				],
				"markdown03_borderless.md":
				[
					{
						"id": "FQXF",
						"description": "Cursors at end of each column",
						"initial_selections": [(10, 10), (124, 124), (203, 203)],
						"expected_selections": [(22, 22), (135, 135), (203, 203)]
					}
				]
			}
		},
		"tabnav_move_cursor_up": {
			"markdown": {
				"markdown01_unformatted_table.md":
				[
					{
						"id": "Q5PE",
						"description": "Cursor in top row of file doesn't move",
						"initial_selections": [(6, 6)],
						"expected_selections": [(6, 6)]
					},
					{
						"id": "42LX",
						"description": "Single cursor in first cell of row",
						"initial_selections": [(231, 231)],
						"expected_selections": [(153, 153)]
					},
					{
						"id": "FFIL",
						"description": "Single cursor in last cell of row",
						"initial_selections": [(215, 215)],
						"expected_selections": [(140, 140)]
					},
					{
						"id": "NDMD",
						"description": "Separators excluded - separator row jumped",
						"initial_selections": [(140, 140)],
						"expected_selections": [(45, 45)],
						"settings": {"tabnav.include_separators": False}
					},
					{
						"id": "HSCM",
						"description": "Separators excluded - multiple cursros, separator only jumped as applicable",
						"initial_selections": [(106, 106), (245, 245)],
						"expected_selections": [(6, 6), (194, 194)],
						"settings": {"tabnav.include_separators": False}
					},
					{
						"id": "CAVZ",
						"description": "Cursor in line separator row moves out",
						"initial_selections": [(69, 69)],
						"expected_selections": [(19, 19)],
						"settings": {"tabnav.include_separators": False}
					},
					{
						"id": "AEZM",
						"description": "Separators included - moves to separator row",
						"initial_selections": [(140, 140)],
						"expected_selections": [(95, 95)],
						"settings": {"tabnav.include_separators": True}
					},
					{
						"id": "JOQO",
						"description": "Move to shorter cell, go to end of cell",
						"initial_selections": [(186, 186)],
						"expected_selections": [(111, 111)]
					},
					{
						"id": "7KPM",
						"description": "Single cursor in empty cell",
						"initial_selections": [(206, 206)],
						"expected_selections": [(120, 120)]
					},
					{
						"id": "FPKG",
						"description": "Target cell is an empty cell",
						"initial_selections": [(264, 264)],
						"expected_selections": [(206, 206)]
					},
					{
						"id": "Y2QP",
						"description": "Relatively aligned cursors, one in top row - merged",
						"initial_selections": [(40, 40), (135, 135)],
						"expected_selections": [(40, 40)]
					},
					{
						"id": "CIOA",
						"description": "Multiple cursors in a single cell - all move",
						"initial_selections": [(230, 230), (236, 236)],
						"expected_selections": [(152, 152), (158, 158)]
					},
					{
						"id": "HBX2",
						"description": "Target row has insufficient columns - cursor doesn't move",
						"initial_selections": [(352, 352)],
						"expected_selections": [(352, 352)]
					},
					{
						"id": "BZIA",
						"description": "Multiple cursors, some move some don't",
						"initial_selections": [(119, 119), (191, 191), (339, 339), (352, 352)],
						"expected_selections": [(20, 20), (111, 111), (275, 275), (352, 352)]
					},
					{
						"id": "T3JT",
						"description": "Target location already selected by another cursor",
						"initial_selections": [(152, 152), (230, 230)],
						"expected_selections": [(104, 104), (152, 152)]
					}
				],
				"markdown02_multiple_tables.md":
				[
					{
						"id": "BMGX",
						"description": "Cursors in top rows of multiple tables",
						"initial_selections": [(129, 129), (1878, 1878)],
						"expected_selections": [(129, 129), (1878, 1878)]
					},
					{
						"id": "SGZN",
						"description": "Multiple cursors in multiple tables",
						"initial_selections": [(148, 148), (247, 247), (613, 613), (720, 720), (1869, 1869), (2192, 2192), (2213, 2213)],
						"expected_selections": [(148, 148), (163, 163), (529, 529), (636, 636), (1869, 1869), (2162, 2162), (2183, 2183)]
					}
				],
				"markdown03_borderless.md":
				[
					{
						"id": "I5EB",
						"description": "Cursors in borderless table",
						"initial_selections": [(102, 102), (151, 151), (203, 203)],
						"expected_selections": [(68, 68), (117, 117), (169, 169)]
					}
				]
			}
		},
		"tabnav_move_cursor_down": {
			"markdown": {
				"markdown01_unformatted_table.md":
				[
					{
						"id": "27UB",
						"description": "Cursor in bottom row of file doesn't move",
						"initial_selections": [(291, 291)],
						"expected_selections": [(291, 291)]
					},
					{
						"id": "7Y36",
						"description": "Single cursor in first cell of row",
						"initial_selections": [(231, 231)],
						"expected_selections": [(286, 286)]
					},
					{
						"id": "ZB5C",
						"description": "Single cursor in last cell of row",
						"initial_selections": [(136, 136)],
						"expected_selections": [(211, 211)]
					},
					{
						"id": "4ZGQ",
						"description": "Separators excluded - separator row jumped",
						"initial_selections": [(45, 45)],
						"expected_selections": [(140, 140)],
						"settings": {"tabnav.include_separators": False}
					},
					{
						"id": "TB3O",
						"description": "Separators excluded - multiple cursros, separator only jumped as applicable",
						"initial_selections": [(6, 6), (116, 116)],
						"expected_selections": [(106, 106), (196, 196)],
						"settings": {"tabnav.include_separators": False}
					},
					{
						"id": "FLUF",
						"description": "Cursor in line separator row moves out",
						"initial_selections": [(69, 69)],
						"expected_selections": [(118, 118)],
						"settings": {"tabnav.include_separators": False}
					},
					{
						"id": "E4DJ",
						"description": "Separators included - moves to separator row",
						"initial_selections": [(29, 29)],
						"expected_selections": [(79, 79)],
						"settings": {"tabnav.include_separators": True}
					},
					{
						"id": "7V7C",
						"description": "Move to shorter cell, go to end of cell",
						"initial_selections": [(186, 186)],
						"expected_selections": [(242, 242)]
					},
					{
						"id": "EH2O",
						"description": "Single cursor in empty cell",
						"initial_selections": [(206, 206)],
						"expected_selections": [(248, 248)]
					},
					{
						"id": "BZER",
						"description": "Target cell is an empty cell",
						"initial_selections": [(123, 123)],
						"expected_selections": [(206, 206)]
					},
					{
						"id": "YUX4",
						"description": "Relatively aligned cursors, one in bottom row - merged",
						"initial_selections": [(245, 245), (310, 310)],
						"expected_selections": [(310, 310)]
					},
					{
						"id": "RI6N",
						"description": "Multiple cursors in a single cell - all move",
						"initial_selections": [(253, 253), (261, 261), (272, 272)],
						"expected_selections": [(317, 317), (325, 325), (336, 336)]
					},
					{
						"id": "4UFD",
						"description": "Target row has insufficient columns - cursor doesn't move",
						"initial_selections": [(217, 217)],
						"expected_selections": [(217, 217)]
					},
					{
						"id": "OKQL",
						"description": "Multiple cursors, some move some don't",
						"initial_selections": [(108, 108), (195, 195), (217, 217), (310, 310)],
						"expected_selections": [(156, 156), (217, 217), (246, 246), (310, 310)]
					},
					{
						"id": "V5PR",
						"description": "Target location already selected by another cursor",
						"initial_selections": [(152, 152), (230, 230)],
						"expected_selections": [(230, 230), (285, 285)]
					}
				],
				"markdown02_multiple_tables.md":
				[
					{
						"id": "442Z",
						"description": "Cursors in bottom rows of multiple tables",
						"initial_selections": [(1817, 1817), (2812, 2812)],
						"expected_selections": [(1817, 1817), (2812, 2812)]
					},
					{
						"id": "EIBD",
						"description": "Multiple cursors in multiple tables",
						"initial_selections": [(777, 777), (1309, 1309), (1832, 1832), (2123, 2123)],
						"expected_selections": [(861, 861), (1393, 1393), (1832, 1832), (2153, 2153)]
					}
				],
				"markdown03_borderless.md":
				[
					{
						"id": "BQ2C",
						"description": "Cursors in borderless table",
						"initial_selections": [(68, 68), (117, 117), (169, 169)],
						"expected_selections": [(102, 102), (151, 151), (203, 203)]
					}
				]
			}
		},
		"tabnav_select_current": {
			"markdown": {
				"markdown01_unformatted_table.md":
				[
					{
						"id": "TF4W",
						"description": "Single cursor in first cell",
						"initial_selections": [(6, 6)],
						"expected_selections": [(1, 12)]
					},
					{
						"id": "PK62",
						"description": "Single cursor in last cell of row",
						"initial_selections": [(138, 138)],
						"expected_selections": [(132, 146)]
					},
					{
						"id": "GCZL",
						"description": "Single cursor in line separator cell",
						"initial_selections": [(56, 56)],
						"expected_selections": [(51, 62)]
					},
					{
						"id": "7TXP",
						"description": "Single cursor at start of cell",
						"initial_selections": [(112, 112)],
						"expected_selections": [(112, 119)]
					},
					{
						"id": "NLQS",
						"description": "Single cursor at end of cell",
						"initial_selections": [(191, 191)],
						"expected_selections": [(149, 191)]
					},
					{
						"id": "CUYU",
						"description": "Single cursor in empty cell",
						"initial_selections": [(206, 206)],
						"expected_selections": [(206, 206)]
					},
					{
						"id": "TICE",
						"description": "Single cursor after last pipe (not in table)",
						"initial_selections": [(280, 280)],
						"expected_selections": [(280, 280)]
					},
					{
						"id": "2Q6Z",
						"description": "Single cursor before first pipe (not in table)",
						"initial_selections": [(100, 100)],
						"expected_selections": [(100, 100)]
					},
					{
						"id": "F4MU",
						"description": "Multiple cursors single cell",
						"initial_selections": [(152, 152), (158, 158), (163, 163), (170, 170), (177, 177), (184, 184)],
						"expected_selections": [(149, 191)]
					},
					{
						"id": "CZ3T",
						"description": "Cell already selected, forward",
						"initial_selections": [(192, 205)],
						"expected_selections": [(192, 205)]
					},
					{
						"id": "UHHL",
						"description": "Cell already selected, reverse",
						"initial_selections": [(205, 192)],
						"expected_selections": [(205, 192)]
					},
					{
						"id": "USRZ",
						"description": "Region spans a cell plus pipes on either end (3 cells)",
						"initial_selections": [(111, 120)],
						"expected_selections": [(101, 111), (112, 119), (120, 131)]
					},
					{
						"id": "WM7K",
						"description": "Region spans three body rows",
						"initial_selections": [(123, 244)],
						"expected_selections": [(120, 131), (132, 146), (149, 191), (192, 205), (206, 206), (207, 224), (227, 242), (243, 247)]
					},
					{
						"id": "WQYH",
						"description": "Region spans body and separator row, separators excluded",
						"initial_selections": [(14, 128)],
						"expected_selections": [(13, 24), (25, 36), (37, 48), (101, 111), (112, 119), (120, 131)],
						"settings": {"tabnav.include_separators": False}
					},
					{
						"id": "4ZRW",
						"description": "Region spans body and separator row, separators included",
						"initial_selections": [(14, 128)],
						"expected_selections": [(13, 24), (25, 36), (37, 48), (51, 62), (63, 74), (75, 86), (87, 98), (101, 111), (112, 119), (120, 131)],
						"settings": {"tabnav.include_separators": True}
					},
					{
						"id": "MNIB",
						"description": "Subset of a cell selected",
						"initial_selections": [(162, 171)],
						"expected_selections": [(149, 191)]
					}
				],
				"markdown02_multiple_tables.md":
				[
					{
						"id": "5QGC",
						"description": "Multiple cursors in multiple tables",
						"initial_selections": [(280, 280), (763, 763), (1395, 1395), (1922, 1922), (2338, 2338)],
						"expected_selections": [(265, 284), (759, 766), (1384, 1402), (1922, 1935), (2326, 2339)]
					},
					{
						"id": "LSVE",
						"description": "Cursor in empty line between tables (not in table)",
						"initial_selections": [(1860, 1860)],
						"expected_selections": [(1860, 1860)]
					},
					{
						"id": "YKR2",
						"description": "Single region spans multiple tables (no change)",
						"initial_selections": [(1537, 2001)],
						"expected_selections": [(1537, 2001)]
					},
					{
						"id": "UOFD",
						"description": "Multiple cursors in multiple line separator rows",
						"initial_selections": [(212, 212), (1913, 1913)],
						"expected_selections": [(208, 226), (1906, 1919)]
					}
				],
				"markdown03_borderless.md":
				[
					{
						"id": "QPLW",
						"description": "Cursor at start of first column",
						"initial_selections": [(68, 68)],
						"expected_selections": [(68, 78)]
					},
					{
						"id": "6JYN",
						"description": "Cursor at end of last column",
						"initial_selections": [(135, 135)],
						"expected_selections": [(125, 135)]
					},
					{
						"id": "GXZP",
						"description": "Cursor at start of first column of separator",
						"initial_selections": [(34, 34)],
						"expected_selections": [(34, 44)]
					},
					{
						"id": "7SKV",
						"description": "Cursor at end of last column of separator",
						"initial_selections": [(67, 67)],
						"expected_selections": [(57, 67)]
					},
					{
						"id": "XOHX",
						"description": "Selection spans separator row",
						"initial_selections": [(18, 86)],
						"expected_selections": [(11, 22), (23, 33), (68, 78), (79, 90)]
					}
				]
			}
		},
		"tabnav_select_left": {
			"markdown": {
				"markdown01_unformatted_table.md":
				[
					{
						"id": "L3VA",
						"description": "Single cursor in first cell",
						"initial_selections": [(6, 6)],
						"expected_selections": [(12, 1)]
					},
					{
						"id": "CFIY",
						"description": "Single cursor in last cell of row",
						"initial_selections": [(138, 138)],
						"expected_selections": [(146, 132)]
					},
					{
						"id": "24XH",
						"description": "Cell in line separator row already selected",
						"initial_selections": [(74, 63)],
						"expected_selections": [(62, 51)]
					},
					{
						"id": "IG6N",
						"description": "First cell of row already selected, reverse",
						"initial_selections": [(111, 101)],
						"expected_selections": [(111, 101)]
					},
					{
						"id": "V5XE",
						"description": "First cell of row already selected, forward",
						"initial_selections": [(101, 111)],
						"expected_selections": [(111, 101)]
					},
					{
						"id": "XAJK",
						"description": "Cell already selected, reverse",
						"initial_selections": [(205, 192)],
						"expected_selections": [(191, 149)]
					},
					{
						"id": "L5OL",
						"description": "Cell already selected, forward",
						"initial_selections": [(192, 205)],
						"expected_selections": [(191, 149)]
					},
					{
						"id": "MYPK",
						"description": "Single cursor in empty cell",
						"initial_selections": [(206, 206)],
						"expected_selections": [(205, 192)]
					},
					{
						"id": "ABKN",
						"description": "Target cell is an empty cell",
						"initial_selections": [(224, 207)],
						"expected_selections": [(206, 206)]
					},
					{
						"id": "DRBR",
						"description": "Single cursor after last pipe (not in table)",
						"initial_selections": [(280, 280)],
						"expected_selections": [(280, 280)]
					},
					{
						"id": "SG2F",
						"description": "Single cursor before first pipe (not in table)",
						"initial_selections": [(100, 100)],
						"expected_selections": [(100, 100)]
					},
					{
						"id": "AFR7",
						"description": "Multiple regions, some cells selected, some not",
						"initial_selections": [(101, 111), (205, 192), (245, 245)],
						"expected_selections": [(111, 101), (205, 192), (247, 243)]
					},
					{
						"id": "7QCS",
						"description": "Multiple cells selected",
						"initial_selections": [(131, 120), (205, 192), (247, 243)],
						"expected_selections": [(119, 112), (191, 149), (242, 227)]
					},
					{
						"id": "V4JF",
						"description": "Multiple cells selected, some in first column",
						"initial_selections": [(131, 120), (224, 207), (242, 227), (307, 282)],
						"expected_selections": [(119, 112), (206, 206), (242, 227), (307, 282)]
					},
					{
						"id": "CWSW",
						"description": "Two regions merging to one at in first column",
						"initial_selections": [(111, 101), (119, 112)],
						"expected_selections": [(111, 101)]
					},
					{
						"id": "HYS5",
						"description": "Multiple adjacent cells same row",
						"initial_selections": [(119, 112), (131, 120), (146, 132)],
						"expected_selections": [(111, 101), (119, 112), (131, 120)]
					}
				],
				"markdown02_multiple_tables.md":
				[
					{
						"id": "5AZ6",
						"description": "Multiple cells in multiple tables",
						"initial_selections": [(394, 376), (1131, 1125), (1995, 1982), (2339, 2326)],
						"expected_selections": [(375, 369), (1124, 1105), (1995, 1982), (2325, 2312)]
					},
					{
						"id": "VRXT",
						"description": "Multiple cells in multiple line separator rows",
						"initial_selections": [(226, 208), (254, 241), (1919, 1906)],
						"expected_selections": [(207, 201), (240, 227), (1905, 1892)]
					}
				],
				"markdown03_borderless.md":
				[
					{
						"id": "5J5U",
						"description": "Cells at selected in each column",
						"initial_selections": [(78, 68), (124, 113), (169, 159)],
						"expected_selections": [(78, 68), (112, 102), (158, 147)]
					}
				],
			}
		},
		"tabnav_select_right": {
			"markdown": {
				"markdown01_unformatted_table.md":
				[
					{
						"id": "U5HP",
						"description": "Single cursor in first cell",
						"initial_selections": [(6, 6)],
						"expected_selections": [(1, 12)]
					},
					{
						"id": "BP6J",
						"description": "Single cursor in last cell of row",
						"initial_selections": [(138, 138)],
						"expected_selections": [(132, 146)]
					},
					{
						"id": "HAYY",
						"description": "Cell in line separator row already selected",
						"initial_selections": [(63, 74)],
						"expected_selections": [(75, 86)]
					},
					{
						"id": "XCK2",
						"description": "Last cell of row already selected, reverse",
						"initial_selections": [(146, 132)],
						"expected_selections": [(132, 146)]
					},
					{
						"id": "TUPB",
						"description": "Last cell of row already selected, forward",
						"initial_selections": [(132, 146)],
						"expected_selections": [(132, 146)]
					},
					{
						"id": "ZOBX",
						"description": "Cell already selected, reverse",
						"initial_selections": [(247, 243)],
						"expected_selections": [(248, 279)]
					},
					{
						"id": "P4KF",
						"description": "Cell already selected, forward",
						"initial_selections": [(243, 247)],
						"expected_selections": [(248, 279)]
					},
					{
						"id": "XHRS",
						"description": "Single cursor in empty cell",
						"initial_selections": [(206, 206)],
						"expected_selections": [(207, 224)]
					},
					{
						"id": "CN6I",
						"description": "Target cell is an empty cell",
						"initial_selections": [(192, 205)],
						"expected_selections": [(206, 206)]
					},
					{
						"id": "HWWK",
						"description": "Single cursor after last pipe (not in table)",
						"initial_selections": [(280, 280)],
						"expected_selections": [(280, 280)]
					},
					{
						"id": "YVVG",
						"description": "Single cursor before first pipe (not in table)",
						"initial_selections": [(100, 100)],
						"expected_selections": [(100, 100)]
					},
					{
						"id": "PNMG",
						"description": "Multiple regions, some cells selected, some not",
						"initial_selections": [(101, 111), (205, 192), (245, 245)],
						"expected_selections": [(101, 111), (192, 205), (243, 247)]
					},
					{
						"id": "Y4GI",
						"description": "Multiple cells selected",
						"initial_selections": [(120, 131), (243, 247), (282, 307)],
						"expected_selections": [(132, 146), (248, 279), (308, 311)]
					},
					{
						"id": "VZUJ",
						"description": "Multiple cells selected, some in last column",
						"initial_selections": [(132, 146), (248, 279), (308, 311)],
						"expected_selections": [(132, 146), (248, 279), (312, 346)]
					},
					{
						"id": "RE7A",
						"description": "Two regions merging to one at in last column",
						"initial_selections": [(120, 131), (132, 146)],
						"expected_selections": [(132, 146)]
					},
					{
						"id": "URCP",
						"description": "Multiple adjacent cells same row",
						"initial_selections": [(101, 111), (112, 119), (120, 131)],
						"expected_selections": [(112, 119), (120, 131), (132, 146)]
					}
				],
				"markdown02_multiple_tables.md":
				[
					{
						"id": "GFPR",
						"description": "Multiple cells in multiple tables",
						"initial_selections": [(376, 394), (1125, 1131), (1982, 1995), (2326, 2339)],
						"expected_selections": [(395, 408), (1132, 1150), (1996, 2009), (2326, 2339)]
					},
					{
						"id": "JFZW",
						"description": "Multiple cells in multiple line separator rows",
						"initial_selections": [(201, 207), (227, 240), (1892, 1905)],
						"expected_selections": [(208, 226), (241, 254), (1906, 1919)]
					}
				],
				"markdown03_borderless.md":
				[
					{
						"id": "LHVP",
						"description": "Cells at selected in each column",
						"initial_selections": [(68, 78), (113, 124), (159, 169)],
						"expected_selections": [(79, 90), (125, 135), (159, 169)]
					}
				],
			}
		},
		"tabnav_select_up": {
			"markdown": {
				"markdown01_unformatted_table.md":
				[
					{
						"id": "D3XU",
						"description": "Cell in top row of file doesn't move",
						"initial_selections": [(12, 1)],
						"expected_selections": [(12, 1)]
					},
					{
						"id": "RJBV",
						"description": "First cell of row",
						"initial_selections": [(191, 149)],
						"expected_selections": [(111, 101)]
					},
					{
						"id": "CRRK",
						"description": "Last cell of row",
						"initial_selections": [(224, 207)],
						"expected_selections": [(146, 132)]
					},
					{
						"id": "XC2B",
						"description": "Separators excluded - separator row jumped",
						"initial_selections": [(146, 132)],
						"expected_selections": [(48, 37)],
						"settings": {"tabnav.include_separators": False}
					},
					{
						"id": "WX5P",
						"description": "Separators excluded - multiple cells, separator only jumped as applicable",
						"initial_selections": [(146, 132), (242, 227)],
						"expected_selections": [(48, 37), (191, 149)],
						"settings": {"tabnav.include_separators": False}
					},
					{
						"id": "KLLS",
						"description": "Cell in line separator row moves out",
						"initial_selections": [(74, 63)],
						"expected_selections": [(24, 13)],
						"settings": {"tabnav.include_separators": False}
					},
					{
						"id": "EB7Z",
						"description": "Separators included - moves to separator row",
						"initial_selections": [(146, 132)],
						"expected_selections": [(98, 87)],
						"settings": {"tabnav.include_separators": True}
					},
					{
						"id": "7FXN",
						"description": "Single cursor in empty cell",
						"initial_selections": [(206, 206)],
						"expected_selections": [(131, 120)]
					},
					{
						"id": "CPXV",
						"description": "Target cell is an empty cell",
						"initial_selections": [(279, 248)],
						"expected_selections": [(206, 206)]
					},
					{
						"id": "ZKX7",
						"description": "Sequential cells in a column, one in top row merged",
						"initial_selections": [(24, 13), (119, 112)],
						"expected_selections": [(24, 13)]
					},
					{
						"id": "U2XO",
						"description": "Target row has insufficient columns - cell doesn't move",
						"initial_selections": [(354, 347)],
						"expected_selections": [(354, 347)]
					},
					{
						"id": "CO3J",
						"description": "Multiple cells, some move some don't",
						"initial_selections": [(36, 25), (242, 227), (354, 347)],
						"expected_selections": [(36, 25), (191, 149), (354, 347)]
					},
					{
						"id": "APIB",
						"description": "Multiple sequential cells in a column",
						"initial_selections": [(191, 149), (242, 227), (307, 282)],
						"expected_selections": [(111, 101), (191, 149), (242, 227)]
					}
				],
				"markdown02_multiple_tables.md":
				[
					{
						"id": "2MVT",
						"description": "Cells in top rows of multiple tables",
						"initial_selections": [(142, 124), (1889, 1876)],
						"expected_selections": [(142, 124), (1889, 1876)]
					},
					{
						"id": "53LW",
						"description": "Multiple cells in multiple tables",
						"initial_selections": [(368, 349), (646, 628), (1514, 1501), (2129, 2116), (2265, 2252)],
						"expected_selections": [(284, 265), (562, 544), (1430, 1417), (2099, 2086), (2235, 2222)]
					}
				],
				"markdown03_borderless.md":
				[
					{
						"id": "WVHY",
						"description": "Cells in borderless table",
						"initial_selections": [(112, 102), (158, 147), (203, 193)],
						"expected_selections": [(78, 68), (124, 113), (169, 159)]
					}
				]
			}
		},
		"tabnav_select_down": {
			"markdown": {
				"markdown01_unformatted_table.md":
				[
					{
						"id": "CXWI",
						"description": "Cell in bottom row of file doesn't move",
						"initial_selections": [(311, 308)],
						"expected_selections": [(311, 308)]
					},
					{
						"id": "AHR4",
						"description": "First cell of row",
						"initial_selections": [(111, 101)],
						"expected_selections": [(191, 149)]
					},
					{
						"id": "NHTA",
						"description": "Last cell of row",
						"initial_selections": [(146, 132)],
						"expected_selections": [(224, 207)]
					},
					{
						"id": "3DHK",
						"description": "Separators excluded - separator row jumped",
						"initial_selections": [(24, 13)],
						"expected_selections": [(119, 112)],
						"settings": {"tabnav.include_separators": False}
					},
					{
						"id": "YUUF",
						"description": "Separators excluded - multiple cursros, separator only jumped as applicable",
						"initial_selections": [(36, 25), (119, 112)],
						"expected_selections": [(131, 120), (205, 192)],
						"settings": {"tabnav.include_separators": False}
					},
					{
						"id": "SZZW",
						"description": "Cell in line separator row moves out",
						"initial_selections": [(74, 63)],
						"expected_selections": [(119, 112)],
						"settings": {"tabnav.include_separators": False}
					},
					{
						"id": "SY5V",
						"description": "Separators included - moves to separator row",
						"initial_selections": [(24, 13)],
						"expected_selections": [(74, 63)],
						"settings": {"tabnav.include_separators": True}
					},
					{
						"id": "TXOK",
						"description": "Single cursor in empty cell",
						"initial_selections": [(206, 206)],
						"expected_selections": [(279, 248)]
					},
					{
						"id": "W7CY",
						"description": "Target cell is an empty cell",
						"initial_selections": [(131, 120)],
						"expected_selections": [(206, 206)]
					},
					{
						"id": "TCTI",
						"description": "Sequential cells in a column, one in bottom row - merged",
						"initial_selections": [(247, 243), (311, 308)],
						"expected_selections": [(311, 308)]
					},
					{
						"id": "ORBP",
						"description": "Target row has insufficient columns - cell doesn't move",
						"initial_selections": [(224, 207)],
						"expected_selections": [(224, 207)]
					},
					{
						"id": "XH2O",
						"description": "Multiple cells, some move some don't",
						"initial_selections": [(111, 101), (224, 207), (311, 308)],
						"expected_selections": [(191, 149), (224, 207), (311, 308)]
					},
					{
						"id": "K4TA",
						"description": "Sequential cells in the same column",
						"initial_selections": [(119, 112), (205, 192), (247, 243)],
						"expected_selections": [(205, 192), (247, 243), (311, 308)]
					}
				],
				"markdown02_multiple_tables.md":
				[
					{
						"id": "UPU7",
						"description": "Cells in bottom rows of multiple tables",
						"initial_selections": [(1822, 1804), (2819, 2806)],
						"expected_selections": [(1822, 1804), (2819, 2806)]
					},
					{
						"id": "36JP",
						"description": "Multiple cursors in multiple tables",
						"initial_selections": [(536, 517), (982, 964), (1500, 1487), (2099, 2086), (2235, 2222)],
						"expected_selections": [(620, 601), (1066, 1048), (1584, 1571), (2129, 2116), (2265, 2252)]
					}
				],
				"markdown03_borderless.md":
				[
					{
						"id": "VSL4",
						"description": "Cells in borderless table",
						"initial_selections": [(78, 68), (124, 113), (169, 159)],
						"expected_selections": [(112, 102), (158, 147), (203, 193)]
					}
				]
			}
		},
		# The _add_ and _extend_ commands share logic with the _move_ and _select_ commands,
		# respectively. They just don't clear the initial selections. So only limited additional
		# testing is required
		"tabnav_add_cursor_left": {
			"markdown": {
				"markdown01_unformatted_table.md":
				[
					{
						"id": "XBNN",
						"description": "Region split into one cursor per cell",
						"initial_selections": [(125, 245)],
						"expected_selections": [(120, 120), (132, 132), (149, 149), (192, 192), (206, 206), (207, 207), (227, 227), (243, 243)]
					},
					{
						"id": "HPT7",
						"description": "Multiple cursors, some added, some not",
						"initial_selections": [(7, 7), (130, 130), (217, 217), (243, 243)],
						"expected_selections": [(7, 7), (119, 119), (130, 130), (206, 206), (217, 217), (227, 227), (243, 243)]
					}
				]
			}
		},
		"tabnav_add_cursor_right": {
			"markdown": {
				"markdown01_unformatted_table.md":
				[
					{
						"id": "52HQ",
						"description": "Region split into one cursor per cell",
						"initial_selections": [(125, 245)],
						"expected_selections": [(131, 131), (146, 146), (191, 191), (205, 205), (206, 206), (224, 224), (242, 242), (247, 247)]
					},
					{
						"id": "G4VI",
						"description": "Multiple cursors, some added, some not",
						"initial_selections": [(18, 18), (139, 139), (197, 197), (227, 227), (310, 310)],
						"expected_selections": [(18, 18), (30, 30), (139, 139), (197, 197), (206, 206), (227, 227), (243, 243), (310, 310), (314, 314)]
					}
				]
			}
		},
		"tabnav_add_cursor_up": {
			"markdown": {
				"markdown01_unformatted_table.md":
				[
					{
						"id": "HIFZ",
						"description": "Region split into one cursor per cell",
						"initial_selections": [(125, 245)],
						"expected_selections": [(120, 120), (132, 132), (149, 149), (192, 192), (206, 206), (207, 207), (227, 227), (243, 243)]
					},
					{
						"id": "5AI3",
						"description": "Multiple cursors, some added, some not",
						"initial_selections": [(19, 19), (126, 126), (227, 227), (264, 264), (351, 351)],
						"expected_selections": [(19, 19), (31, 31), (126, 126), (149, 149), (206, 206), (227, 227), (264, 264), (351, 351)]
					}
				]
			}
		},
		"tabnav_add_cursor_down": {
			"markdown": {
				"markdown01_unformatted_table.md":
				[
					{
						"id": "R3DS",
						"description": "Multiple cursors, some added, some not",
						"initial_selections": [(20, 20), (126, 126), (218, 218), (227, 227), (325, 325)],
						"expected_selections": [(20, 20), (119, 119), (126, 126), (206, 206), (218, 218), (227, 227), (282, 282), (325, 325)]
					}
				]
			}
		},
		"tabnav_extend_selection_left": {
			"markdown": {
				"markdown01_unformatted_table.md":
				[
					{
						"id": "S7K2",
						"description": "Region split into cells",
						"initial_selections": [(125, 245)],
						"expected_selections": [(131, 120), (146, 132), (191, 149), (205, 192), (206, 206), (224, 207), (242, 227), (247, 243)]
					},
					{
						"id": "PUOM",
						"description": "Multiple cells, some added, some not",
						"initial_selections": [(12, 1), (131, 120), (146, 132), (224, 207), (247, 243)],
						"expected_selections": [(12, 1), (119, 112), (131, 120), (146, 132), (206, 206), (224, 207), (242, 227), (247, 243)]
					}
				]
			}
		},
		"tabnav_extend_selection_right": {
			"markdown": {
				"markdown01_unformatted_table.md":
				[
					{
						"id": "XJDJ",
						"description": "Region split into cells",
						"initial_selections": [(125, 245)],
						"expected_selections": [(120, 131), (132, 146), (149, 191), (192, 205), (206, 206), (207, 224), (227, 242), (243, 247)]
					},
					{
						"id": "RY2I",
						"description": "Multiple cells, some added, some not",
						"initial_selections": [(13, 24), (132, 146), (192, 205), (227, 242), (282, 307), (308, 311)],
						"expected_selections": [(13, 24), (25, 36), (132, 146), (192, 205), (206, 206), (227, 242), (243, 247), (282, 307), (308, 311), (312, 346)]
					}
				]
			}
		},
		"tabnav_extend_selection_up": {
			"markdown": {
				"markdown01_unformatted_table.md":
				[
					{
						"id": "XE26",
						"description": "Region split into cells",
						"initial_selections": [(125, 245)],
						"expected_selections": [(131, 120), (146, 132), (191, 149), (205, 192), (206, 206), (224, 207), (242, 227), (247, 243)]
					},
					{
						"id": "JMBK",
						"description": "Multiple cells, some added, some not",
						"initial_selections": [(24, 13), (131, 120), (242, 227), (279, 248), (307, 282), (354, 347)],
						"expected_selections": [(24, 13), (36, 25), (131, 120), (191, 149), (206, 206), (242, 227), (279, 248), (307, 282), (354, 347)]
					}
				]
			}
		},
		"tabnav_extend_selection_down": {
			"markdown": {
				"markdown01_unformatted_table.md":
				[
					{
						"id": "GJ5T",
						"description": "Region split into cells",
						"initial_selections": [(125, 245)],
						"expected_selections": [(131, 120), (146, 132), (191, 149), (205, 192), (206, 206), (224, 207), (242, 227), (247, 243)]
					},
					{
						"id": "BOCR",
						"description": "Multiple cells, some added, some not",
						"initial_selections": [(24, 13), (131, 120), (191, 149), (224, 207), (242, 227), (346, 312)],
						"expected_selections": [(24, 13), (119, 112), (131, 120), (191, 149), (206, 206), (224, 207), (242, 227), (307, 282), (346, 312)]
					}
				]
			}
		},
		"tabnav_select_row": {
			"markdown": {
				"markdown01_unformatted_table.md":
				[
					{
						"id": "6F5F",
						"description": "First cell of row",
						"initial_selections": [(6, 6)],
						"expected_selections": [(1, 12), (13, 24), (25, 36), (37, 48)]
					},
					{
						"id": "2SXL",
						"description": "Last cell of row",
						"initial_selections": [(137, 143)],
						"expected_selections": [(101, 111), (112, 119), (120, 131), (132, 146)]
					},
					{
						"id": "A45Z",
						"description": "Multiple disjoint selections",
						"initial_selections": [(115, 115), (125, 125), (318, 318)],
						"expected_selections": [(101, 111), (112, 119), (120, 131), (132, 146), (282, 307), (308, 311), (312, 346), (347, 354)]
					},
					{
						"id": "KQ2A",
						"description": "Separators excluded - region spanning separator row",
						"initial_selections": [(19, 123)],
						"expected_selections": [(1, 12), (13, 24), (25, 36), (37, 48), (101, 111), (112, 119), (120, 131), (132, 146)],
						"settings": {"tabnav.include_separators": False}
					},
					{
						"id": "LXN5",
						"description": "Separators excluded - only separator row selected",
						"initial_selections": [(66, 66)],
						"expected_selections": [(51, 62), (63, 74), (75, 86), (87, 98)],
						"settings": {"tabnav.include_separators": False}
					},
					{
						"id": "6DLQ",
						"description": "Separators included - region spanning separator row",
						"initial_selections": [(20, 124)],
						"expected_selections": [(1, 12), (13, 24), (25, 36), (37, 48), (51, 62), (63, 74), (75, 86), (87, 98), (101, 111), (112, 119), (120, 131), (132, 146)],
						"settings": {"tabnav.include_separators": True}
					},
					{
						"id": "PTG5",
						"description": "Rows with different numbers of cells",
						"initial_selections": [(157, 157), (235, 235)],
						"expected_selections": [(149, 191), (192, 205), (206, 206), (207, 224), (227, 242), (243, 247), (248, 279)]
					},
					{
						"id": "L4WI",
						"description": "Row already selected",
						"initial_selections": [(149, 191), (192, 205), (206, 206), (207, 224)],
						"expected_selections": [(149, 191), (192, 205), (206, 206), (207, 224)]
					}
				],
				"markdown02_multiple_tables.md":
				[
					{
						"id": "ELIM",
						"description": "Selections in multiple tables",
						"initial_selections": [(614, 785), (2167, 2167), (2376, 2376)],
						"expected_selections": [(601, 620), (621, 627), (628, 646), (647, 660), (661, 674), (675, 682), (685, 704), (705, 711), (712, 730), (731, 744), (745, 758), (759, 766), (769, 788), (789, 795), (796, 814), (815, 828), (829, 842), (843, 850), (2162, 2175), (2176, 2189), (2372, 2385), (2386, 2399)]
					}
				],
				"markdown03_borderless.md":
				[
					{
						"id": "H3BK",
						"description": "Select row in borderless table",
						"initial_selections": [(83, 152)],
						"expected_selections": [(68, 78), (79, 90), (91, 101), (102, 112), (113, 124), (125, 135), (136, 146), (147, 158), (159, 169)]
					}
				]
			}
		},
		"tabnav_select_column": {
			"markdown": {
				"markdown01_unformatted_table.md":
				[
					{
						"id": "KVRJ",
						"description": "First column",
						"initial_selections": [(7, 7)],
						"expected_selections": [(1, 12), (101, 111), (149, 191), (227, 242), (282, 307)]
					},
					{
						"id": "HIBD",
						"description": "Region spanning multiple columns",
						"initial_selections": [(105, 116)],
						"expected_selections": [(1, 12), (13, 24), (101, 111), (112, 119), (149, 191), (192, 205), (227, 242), (243, 247), (282, 307), (308, 311)]
					},
					{
						"id": "YQEP",
						"description": "Multiple disjoint selections",
						"initial_selections": [(106, 106), (255, 268)],
						"expected_selections": [(1, 12), (25, 36), (101, 111), (120, 131), (149, 191), (206, 206), (227, 242), (248, 279), (282, 307), (312, 346)]
					},
					{
						"id": "4QEY",
						"description": "Multiple selections, one in separator row",
						"initial_selections": [(69, 69), (106, 106)],
						"expected_selections": [(1, 12), (13, 24), (101, 111), (112, 119), (149, 191), (192, 205), (227, 242), (243, 247), (282, 307), (308, 311)],
					},
					{
						"id": "4QEY",
						"description": "Only selection in separator row",
						"initial_selections": [(68, 68)],
						"expected_selections": [(13, 24), (112, 119), (192, 205), (243, 247), (308, 311)],
					},
					{
						"id": "4VY3",
						"description": "Separators included",
						"initial_selections": [(198, 198)],
						"expected_selections": [(13, 24), (63, 74), (112, 119), (192, 205), (243, 247), (308, 311)],
						"settings": {"tabnav.include_separators": True}
					},
					{
						"id": "POFJ",
						"description": "Column with missing cell",
						"initial_selections": [(221, 221)],
						"expected_selections": [(37, 48), (132, 146), (207, 224), (347, 354)]
					},
					{
						"id": "LZZL",
						"description": "Column already selected",
						"initial_selections": [(13, 24), (112, 119), (192, 205), (243, 247), (308, 311)],
						"expected_selections": [(13, 24), (112, 119), (192, 205), (243, 247), (308, 311)]
					}
				],
				"markdown02_multiple_tables.md":
				[
					{
						"id": "F7OQ",
						"description": "Last column",
						"initial_selections": [(848, 848)],
						"expected_selections": [(171, 178), (339, 346), (423, 430), (507, 514), (591, 598), (675, 682), (759, 766), (843, 850), (927, 934), (1011, 1018), (1095, 1102), (1179, 1186), (1263, 1270), (1347, 1354), (1431, 1438), (1515, 1522), (1599, 1606), (1683, 1690), (1767, 1774), (1851, 1858)]
					},
					{
						"id": "B3GS",
						"description": "Non-overlapping columns in multiple tables",
						"initial_selections": [(687, 693), (1069, 1076), (2091, 2095)],
						"expected_selections": [(97, 116), (143, 156), (265, 284), (311, 324), (349, 368), (395, 408), (433, 452), (479, 492), (517, 536), (563, 576), (601, 620), (647, 660), (685, 704), (731, 744), (769, 788), (815, 828), (853, 872), (899, 912), (937, 956), (983, 996), (1021, 1040), (1067, 1080), (1105, 1124), (1151, 1164), (1189, 1208), (1235, 1248), (1273, 1292), (1319, 1332), (1357, 1376), (1403, 1416), (1441, 1460), (1487, 1500), (1525, 1544), (1571, 1584), (1609, 1628), (1655, 1668), (1693, 1712), (1739, 1752), (1777, 1796), (1823, 1836), (1876, 1889), (1936, 1949), (1966, 1979), (1996, 2009), (2026, 2039), (2056, 2069), (2086, 2099), (2116, 2129), (2146, 2159), (2176, 2189), (2206, 2219), (2236, 2249), (2266, 2279), (2296, 2309), (2326, 2339), (2356, 2369), (2386, 2399), (2416, 2429), (2446, 2459), (2476, 2489), (2506, 2519), (2536, 2549), (2566, 2579), (2596, 2609), (2626, 2639), (2656, 2669), (2686, 2699), (2716, 2729), (2746, 2759), (2776, 2789), (2806, 2819)]
					}
				],
				"markdown03_borderless.md":
				[
					{
						"id": "K5YV",
						"description": "Select columns in borderless table",
						"initial_selections": [(73, 75), (95, 97)],
						"expected_selections": [(0, 10), (23, 33), (68, 78), (91, 101), (102, 112), (125, 135), (136, 146), (159, 169), (170, 180), (193, 203), (204, 214), (227, 237)]
					}
				]
			}
		},
		"tabnav_select_all": {
			"markdown": {
				"markdown01_unformatted_table.md":
				[
					{
						"id": "LNSZ",
						"description": "First column",
						"initial_selections": [(7, 7)],
						"expected_selections": [(1, 12), (13, 24), (25, 36), (37, 48), (101, 111), (112, 119), (120, 131), (132, 146), (149, 191), (192, 205), (206, 206), (207, 224), (227, 242), (243, 247), (248, 279), (282, 307), (308, 311), (312, 346), (347, 354)]
					},
					{
						"id": "Y77A",
						"description": "Region spanning multiple columns",
						"initial_selections": [(105, 116)],
						"expected_selections": [(1, 12), (13, 24), (25, 36), (37, 48), (101, 111), (112, 119), (120, 131), (132, 146), (149, 191), (192, 205), (206, 206), (207, 224), (227, 242), (243, 247), (248, 279), (282, 307), (308, 311), (312, 346), (347, 354)]
					},
					{
						"id": "YWRX",
						"description": "Multiple disjoint selections",
						"initial_selections": [(106, 106), (255, 268)],
						"expected_selections": [(1, 12), (13, 24), (25, 36), (37, 48), (101, 111), (112, 119), (120, 131), (132, 146), (149, 191), (192, 205), (206, 206), (207, 224), (227, 242), (243, 247), (248, 279), (282, 307), (308, 311), (312, 346), (347, 354)]
					},
					{
						"id": "TCDQ",
						"description": "Separators excluded - multiple selections, one in separator row",
						"initial_selections": [(69, 69), (106, 106)],
						"expected_selections": [(1, 12), (13, 24), (25, 36), (37, 48), (101, 111), (112, 119), (120, 131), (132, 146), (149, 191), (192, 205), (206, 206), (207, 224), (227, 242), (243, 247), (248, 279), (282, 307), (308, 311), (312, 346), (347, 354)]
					},
					{
						"id": "YLQ6",
						"description": "Separators excluded - only selection in separator row",
						"initial_selections": [(68, 68)],
						"expected_selections": [(1, 12), (13, 24), (25, 36), (37, 48), (101, 111), (112, 119), (120, 131), (132, 146), (149, 191), (192, 205), (206, 206), (207, 224), (227, 242), (243, 247), (248, 279), (282, 307), (308, 311), (312, 346), (347, 354)]
					},
					{
						"id": "VXTP",
						"description": "Separators included",
						"initial_selections": [(198, 198)],
						"expected_selections": [(1, 12), (13, 24), (25, 36), (37, 48), (51, 62), (63, 74), (75, 86), (87, 98), (101, 111), (112, 119), (120, 131), (132, 146), (149, 191), (192, 205), (206, 206), (207, 224), (227, 242), (243, 247), (248, 279), (282, 307), (308, 311), (312, 346), (347, 354)],
						"settings": {"tabnav.include_separators": True}
					},
					{
						"id": "R5VH",
						"description": "Selection in column with missing cell",
						"initial_selections": [(221, 221)],
						"expected_selections": [(1, 12), (13, 24), (25, 36), (37, 48), (101, 111), (112, 119), (120, 131), (132, 146), (149, 191), (192, 205), (206, 206), (207, 224), (227, 242), (243, 247), (248, 279), (282, 307), (308, 311), (312, 346), (347, 354)]
					},
					{
						"id": "UJSH",
						"description": "Table already selected",
						"initial_selections": [(1, 12), (13, 24), (25, 36), (37, 48), (101, 111), (112, 119), (120, 131), (132, 146), (149, 191), (192, 205), (206, 206), (207, 224), (227, 242), (243, 247), (248, 279), (282, 307), (308, 311), (312, 346), (347, 354)],
						"expected_selections": [(1, 12), (13, 24), (25, 36), (37, 48), (101, 111), (112, 119), (120, 131), (132, 146), (149, 191), (192, 205), (206, 206), (207, 224), (227, 242), (243, 247), (248, 279), (282, 307), (308, 311), (312, 346), (347, 354)]
					}
				],
				"markdown02_multiple_tables.md":
				[
					{
						"id": "2EHI",
						"description": "Select multiple tables",
						"initial_selections": [(687, 693), (1069, 1076), (2091, 2095)],
						"expected_selections": [(97, 116), (117, 123), (124, 142), (143, 156), (157, 170), (171, 178), (265, 284), (285, 291), (292, 310), (311, 324), (325, 338), (339, 346), (349, 368), (369, 375), (376, 394), (395, 408), (409, 422), (423, 430), (433, 452), (453, 459), (460, 478), (479, 492), (493, 506), (507, 514), (517, 536), (537, 543), (544, 562), (563, 576), (577, 590), (591, 598), (601, 620), (621, 627), (628, 646), (647, 660), (661, 674), (675, 682), (685, 704), (705, 711), (712, 730), (731, 744), (745, 758), (759, 766), (769, 788), (789, 795), (796, 814), (815, 828), (829, 842), (843, 850), (853, 872), (873, 879), (880, 898), (899, 912), (913, 926), (927, 934), (937, 956), (957, 963), (964, 982), (983, 996), (997, 1010), (1011, 1018), (1021, 1040), (1041, 1047), (1048, 1066), (1067, 1080), (1081, 1094), (1095, 1102), (1105, 1124), (1125, 1131), (1132, 1150), (1151, 1164), (1165, 1178), (1179, 1186), (1189, 1208), (1209, 1215), (1216, 1234), (1235, 1248), (1249, 1262), (1263, 1270), (1273, 1292), (1293, 1299), (1300, 1318), (1319, 1332), (1333, 1346), (1347, 1354), (1357, 1376), (1377, 1383), (1384, 1402), (1403, 1416), (1417, 1430), (1431, 1438), (1441, 1460), (1461, 1467), (1468, 1486), (1487, 1500), (1501, 1514), (1515, 1522), (1525, 1544), (1545, 1551), (1552, 1570), (1571, 1584), (1585, 1598), (1599, 1606), (1609, 1628), (1629, 1635), (1636, 1654), (1655, 1668), (1669, 1682), (1683, 1690), (1693, 1712), (1713, 1719), (1720, 1738), (1739, 1752), (1753, 1766), (1767, 1774), (1777, 1796), (1797, 1803), (1804, 1822), (1823, 1836), (1837, 1850), (1851, 1858), (1862, 1875), (1876, 1889), (1922, 1935), (1936, 1949), (1952, 1965), (1966, 1979), (1982, 1995), (1996, 2009), (2012, 2025), (2026, 2039), (2042, 2055), (2056, 2069), (2072, 2085), (2086, 2099), (2102, 2115), (2116, 2129), (2132, 2145), (2146, 2159), (2162, 2175), (2176, 2189), (2192, 2205), (2206, 2219), (2222, 2235), (2236, 2249), (2252, 2265), (2266, 2279), (2282, 2295), (2296, 2309), (2312, 2325), (2326, 2339), (2342, 2355), (2356, 2369), (2372, 2385), (2386, 2399), (2402, 2415), (2416, 2429), (2432, 2445), (2446, 2459), (2462, 2475), (2476, 2489), (2492, 2505), (2506, 2519), (2522, 2535), (2536, 2549), (2552, 2565), (2566, 2579), (2582, 2595), (2596, 2609), (2612, 2625), (2626, 2639), (2642, 2655), (2656, 2669), (2672, 2685), (2686, 2699), (2702, 2715), (2716, 2729), (2732, 2745), (2746, 2759), (2762, 2775), (2776, 2789), (2792, 2805), (2806, 2819)]
					}
				],
				"markdown03_borderless.md":
				[
					{
						"id": "QDJB",
						"description": "Select borderless table",
						"initial_selections": [(73, 75)],
						"expected_selections": [(0, 10), (11, 22), (23, 33), (68, 78), (79, 90), (91, 101), (102, 112), (113, 124), (125, 135), (136, 146), (147, 158), (159, 169), (170, 180), (181, 192), (193, 203), (204, 214), (215, 226), (227, 237)]
					}
				]
			}
		},
	}
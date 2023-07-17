from collections import OrderedDict

lines_color = ["BL", "BR", "G", "LG", "O1", "O2", "R", "LR", "Y"]

line_colorcode = [
    'BL', 'BL+Y', 'BL+G', 'BL+R', 'BL+O', 'BL+BR', 
    'BR', 'BR+R', 'BR+G', 
    'G', 'G+Y', 'G+O', 'G+R', 
    'O', 'O+Y', 'O+R', 
    'R', 
    'Y',
]

line_colorhex = [
    "#0070bd", "#0070bd", "#0070bd", "#0070bd", "#0070bd", "#0070bd", # BL
    "#c48c31", "#c48c31", "#c48c31", # BR
    "#008659", "#008659", "#008659", "#008659", # G
    "#f8b61c", "#f8b61c", "#f8b61c",  # O
    "#e3002c", # R
    "#ffdb00", # Y
]

linename_map={'BL':'BL', 'BR':'BR', 'G':'G', 'LG':'G', 'O':'O', 'O1':'O', 'O2':'O', 'R':'R', 'LR':'R', 'Y':'Y'}

color_map = OrderedDict(
    BL="#0070bd",
    BR="#c48c31",
    G="#008659",
    LG="#cfdb00",
    O="#f8b61c",
    O1="#f8b61c",
    O2="#f8b61c",
    R="#e3002c",
    LR="#fd92a3",
    Y="#ffdb00",
)

lineStationDict = {
    "BL":['頂埔', '永寧', '土城', '海山', '亞東醫院', '府中', '板橋', '新埔', '江子翠', '龍山寺', '西門', '台北車站', '善導寺', '忠孝新生', '忠孝復興', '忠孝敦化', '國父紀念館', '市政府', '永春', '後山埤', '昆陽', '南港', '南港展覽館'],
    "BR":['動物園', '木柵', '萬芳社區', '萬芳醫院', '辛亥', '麟光', '六張犁', '科技大樓', '大安', '忠孝復興', '南京復興', '中山國中', '松山機場', '大直', '劍南路', '西湖', '港墘', '文德', '內湖', '大湖公園', '葫洲', '東湖', '南港軟體園區', '南港展覽館'],
    "Y":['大坪林', '十四張', '秀朗橋', '景平', '景安', '中和', '橋和', '中原', '板新', '板橋', '新埔民生', '頭前庄', '幸福', '新北產業園區'],
    "G":['新店', '新店區公所', '七張', '小碧潭', '大坪林', '景美', '萬隆', '公館', '台電大樓', '古亭', '中正紀念堂', '小南門', '西門', '北門', '中山', '松江南京', '南京復興', '台北小巨蛋', '南京三民', '松山'],
    "R":['象山', '台北101/世貿', '信義安和', '大安', '大安森林公園', '東門', '中正紀念堂', '台大醫院', '台北車站', '中山', '雙連', '民權西路', '圓山', '劍潭', '士林', '芝山', '明德', '石牌', '唭哩岸', '奇岩', '新北投', '北投', '復興崗', '忠義', '關渡', '竹圍', '紅樹林', '淡水'],
    "O":['南勢角', '景安', '永安市場', '頂溪', '古亭', '東門', '忠孝新生', '松江南京', '行天宮', '中山國小', '民權西路', '大橋頭', '台北橋', '菜寮', '三重', '先嗇宮', '頭前庄', '新莊', '輔大', '丹鳳', '迴龍', '三重國小', '三和國中', '徐匯中學', '三民高中', '蘆洲']
}

if __name__ == "__main__":
    pass
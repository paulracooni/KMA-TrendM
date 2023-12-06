import lxml.html
from pathlib import Path
from ..tm_driver import TMDriver

PATH_TEMPALTE = Path(__file__).parent.parent / "template" / "231206.html"

color_map = {
    "enhancement" : "rgb(253, 228, 228)", #FDE4E4
    "tech-centric": "rgb(253, 228, 228)", #FDE4E4
    "culture"     : "rgb(253, 228, 228)", #FDE4E4
    "type"        : "rgb(253, 228, 228)", #FDE4E4

    "expansion": "rgb(245, 244, 217)", #F5F4D9
    "sense"    : "rgb(245, 244, 217)", #F5F4D9
    "space"    : "rgb(245, 244, 217)", #F5F4D9
    "ecosystem": "rgb(245, 244, 217)", #F5F4D9

    "connectivity": "rgb(253, 241, 217)", #FDF1D9
    "experience"  : "rgb(253, 241, 217)", #FDF1D9
    "co-creation" : "rgb(253, 241, 217)", #FDF1D9
    "community"   : "rgb(253, 241, 217)", #FDF1D9

    "reversal"       : "rgb(208, 244, 241)", #D0F4F1
    "personalization": "rgb(208, 244, 241)", #D0F4F1
    "originality"    : "rgb(208, 244, 241)", #D0F4F1
    "luxury"         : "rgb(208, 244, 241)", #D0F4F1

    "reduction"  : "rgb(227, 227, 251)", #D0F4F1
    "environment": "rgb(227, 227, 251)", #D0F4F1
    "time"       : "rgb(227, 227, 251)", #D0F4F1
    "curation"   : "rgb(227, 227, 251)", #D0F4F1

    "disruption"   : "rgb(218, 244, 253)", #DAF4FD
    "diversity"    : "rgb(218, 244, 253)", #DAF4FD
    "subculture"   : "rgb(218, 244, 253)", #DAF4FD
    "human-centric": "rgb(218, 244, 253)", #DAF4FD
}

def render_template(article):

    
    dom = lxml.html.fromstring(
        PATH_TEMPALTE.open("r", encoding='UTF-8').read())

    # iamge
    e_img = dom.cssselect("#block-image > img")[0]
    e_img.attrib['src'] = article.image.url
    e_img.attrib['alt'] = article.image.description

    # id="block-trend"
    e_trend = dom.cssselect("#block-trend")[0]
    e_trend.text = f" {article.data['summary']}"

    # id="block-insight"
    e_insight = dom.cssselect("#block-insight")[0]
    for child in e_insight.getchildren():
        e_insight.remove(child)

    for insight in article.data['insights']:
        e_insight.insert(0, lxml.html.fromstring(
            "<li style=\"text-align: justify; margin-right: 20px; font-size: 12px;\">"
                f"{insight}"
            "</li>"))

    # id="block-keyword"
    e_keywords = dom.cssselect("#block-keywords")[0]
    e_keywords.text = ", ".join(article.data['keywords'])
        
    # id="block-reference"
    e_ref = dom.cssselect("#block-reference > span > a")[0]
    e_ref.attrib['href'] = article.news.url_origin
    e_ref.text = f"[원문기사/이미지] {article.news.title}"

    classify = extr_valid_classify(article.data)
    # id="pattern-{trend}", 
    for key in extr_keys(article.data, "probsOfTrendPattern"):
        style = style_t_pattern.format(color_map[key.lower()]) \
            if classify['trend'] in key else style_f_pattern
        e_pattern = dom.cssselect(f"#pattern-{key.lower()}")[0]
        e_pattern.attrib['style'] = style
    # id="issue-{issue}"
    for key in extr_keys(article.data, "probsOfIssue"):
        style = style_t_issue.format(color_map[key.lower()])\
            if classify['issue'] in key else style_f_issue
        e_issue = dom.cssselect(f"#issue-{key.lower()}")[0]
        e_issue.attrib['style'] = style
    # id="sector-{section}"
    for key in extr_keys(article.data, "probsOfSector"):
        style = style_t_sector if classify['sector'] in key else style_f_sector
        e_sector = dom.cssselect(f"#sector-{key.lower()}")[0]
        e_sector.attrib['style'] = style

    return lxml.html.tostring(dom)


def extr_valid_classify(article_data):
    return dict(
        trend  = _extr_valid_key(article_data, 'trendPattern', 'probsOfTrendPattern'),
        issue  = _extr_valid_key(article_data, 'issue', 'probsOfIssue'),
        sector = _extr_valid_key(article_data, 'sector', 'probsOfSector'))
    

def _extr_valid_key(article_data, key_pred, key_probs):
    if article_data[key_pred] in list(article_data[key_probs].keys()):
        return article_data[key_pred]

    try:
        key = _get_key_of_max_val(article_data[key_probs])
    except ValueError:
        key = article_data[key_pred]
    return key


def _get_key_of_max_val(data):
    max_val = 0
    for key, val in data.items():
        if max_val <= float(val):
            max_val = float(val)

    ret_key = None
    for key, val in data.items():
        if max_val == float(val):
            ret_key = key
            break
    return ret_key

def extr_keys(article_data, key_probs):
    return list(article_data[key_probs].keys())


style_t_pattern = """width: 16.6667%;
text-align: right;
background-color: {};"""

style_f_pattern = """width: 16.6667%;
text-align: center;
background-color: rgb(255, 255, 255);"""


style_t_issue = """width: 16.6667%;
text-align: center;
background-color: {};
"""
style_f_issue = """
width: 16.6667%;
text-align: center;
background-color: rgb(255, 255, 255);
"""

style_t_sector = """box-sizing: border-box;
--tw-border-spacing-x: 0;
--tw-border-spacing-y: 0;
--tw-translate-x: 0;
--tw-translate-y: 0;
--tw-rotate: 0;
--tw-skew-x: 0;
--tw-skew-y: 0;
--tw-scale-x: 1;
--tw-scale-y: 1;
--tw-pan-x: ;
--tw-pan-y: ;
--tw-pinch-zoom: ;
--tw-scroll-snap-strictness: proximity;
--tw-ordinal: ;
--tw-slashed-zero: ;
--tw-numeric-figure: ;
--tw-numeric-spacing: ;
--tw-numeric-fraction: ;
--tw-ring-inset: ;
--tw-ring-offset-width: 0px;
--tw-ring-offset-color: #fff;
--tw-ring-color: rgb(59 130 246 / 0.5);
--tw-ring-offset-shadow: 0 0 #0000;
--tw-ring-shadow: 0 0 #0000;
--tw-shadow: 0 0 #0000;
--tw-shadow-colored: 0 0 #0000;
--tw-blur: ;
--tw-brightness: ;
--tw-contrast: ;
--tw-grayscale: ;
--tw-hue-rotate: ;
--tw-invert: ;
--tw-saturate: ;
--tw-sepia: ;
--tw-drop-shadow: ;
--tw-backdrop-blur: ;
--tw-backdrop-brightness: ;
--tw-backdrop-contrast: ;
--tw-backdrop-grayscale: ;
--tw-backdrop-hue-rotate: ;
--tw-backdrop-invert: ;
--tw-backdrop-opacity: ;
--tw-backdrop-saturate: ;
--tw-backdrop-sepia: ;
padding: 8px;
border: 1px solid rgb(236, 236, 236);
user-select: text;
min-width: 5px;
width: 126.766px;
text-align: center;
background-color: rgb(255, 242, 204);
"""

style_f_sector = """box-sizing: border-box;
--tw-border-spacing-x: 0;
--tw-border-spacing-y: 0;
--tw-translate-x: 0;
--tw-translate-y: 0;
--tw-rotate: 0;
--tw-skew-x: 0;
--tw-skew-y: 0;
--tw-scale-x: 1;
--tw-scale-y: 1;
--tw-pan-x: ;
--tw-pan-y: ;
--tw-pinch-zoom: ;
--tw-scroll-snap-strictness: proximity;
--tw-ordinal: ;
--tw-slashed-zero: ;
--tw-numeric-figure: ;
--tw-numeric-spacing: ;
--tw-numeric-fraction: ;
--tw-ring-inset: ;
--tw-ring-offset-width: 0px;
--tw-ring-offset-color: #fff;
--tw-ring-color: rgb(59 130 246 / 0.5);
--tw-ring-offset-shadow: 0 0 #0000;
--tw-ring-shadow: 0 0 #0000;
--tw-shadow: 0 0 #0000;
--tw-shadow-colored: 0 0 #0000;
--tw-blur: ;
--tw-brightness: ;
--tw-contrast: ;
--tw-grayscale: ;
--tw-hue-rotate: ;
--tw-invert: ;
--tw-saturate: ;
--tw-sepia: ;
--tw-drop-shadow: ;
--tw-backdrop-blur: ;
--tw-backdrop-brightness: ;
--tw-backdrop-contrast: ;
--tw-backdrop-grayscale: ;
--tw-backdrop-hue-rotate: ;
--tw-backdrop-invert: ;
--tw-backdrop-opacity: ;
--tw-backdrop-saturate: ;
--tw-backdrop-sepia: ;
padding: 8px;
border: 1px solid rgb(236, 236, 236);
user-select: text;
min-width: 5px;
width: 126.766px;
text-align: center;
background-color: rgb(255, 255, 255);
"""
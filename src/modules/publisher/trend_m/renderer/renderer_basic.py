import lxml.html

from ..tm_driver import TMDriver

def render_template(summary):

    dom = lxml.html.fromstring(TMDriver.TEMPLATE)

    # iamge
    e_img = dom.cssselect("#block-image > img")[0]
    e_img.attrib['src'] = summary.image.url
    e_img.attrib['alt'] = summary.image.description

    # image description
    e_fig_cap = dom.cssselect("#block-image > figcaption")[0]
    e_fig_cap.text = summary.image.description

    # id="block-trend"
    e_trend = dom.cssselect("#block-trend")[0]
    e_trend.text = f" {summary.summary}"

    # id="block-insight"
    e_insight = dom.cssselect("#block-insight")[0]
    for child in e_insight.getchildren():
        e_insight.remove(child)

    for insight in summary.insight.split('\n'):
        e_insight.insert(0, lxml.html.fromstring(
            "<li style=\"text-align: justify; margin-right: 20px\">"
                f"{insight}"
            "</li>"))

    # id="block-keyword"
    e_keywords = dom.cssselect("#block-keywords")[0]
    e_keywords.text = ", ".join(summary.keywords)

    # id="block-reference"
    e_ref = dom.cssselect("#block-reference > span > a")[0]
    e_ref.attrib['href'] = summary.news.url_origin
    e_ref.text = f"[원문기사/이미지] {summary.title}"

    classify = extr_valid_classify(summary)
    # id="pattern-{trend}", 
    for key in extr_keys(summary, "ProbsOfTrendPattern"):
        style = style_t_pattern if classify['trend'] in key else style_f_pattern
        e_pattern = dom.cssselect(f"#pattern-{key.lower()}")[0]
        e_pattern.attrib['style'] = style
    # id="issue-{issue}"
    for key in extr_keys(summary, "ProbsOfSubgroup"):
        style = style_t_issue if classify['issue'] in key else style_f_issue
        e_issue = dom.cssselect(f"#issue-{key.lower()}")[0]
        e_issue.attrib['style'] = style
    # id="sector-{section}"
    for key in extr_keys(summary, "ProbsOfSections"):
        style = style_t_issue if classify['section'] in key else style_f_issue
        e_sector = dom.cssselect(f"#sector-{key.lower()}")[0]
        e_sector.attrib['style'] = style

    return lxml.html.tostring(dom)


def extr_valid_classify(summary):
    return dict(
        trend  = _extr_valid_key(summary.classifiy, 'trendPattern', 'probsOfTrendPattern'),
        issue  = _extr_valid_key(summary.classifiy, 'issue', 'probsOfIssue'),
        sector = _extr_valid_key(summary.classifiy, 'sector', 'probsOfSector'))
    

def _extr_valid_key(classifiy, key_pred, key_probs):
    if classifiy[key_pred] in list(classifiy[key_probs].keys()):
        return classifiy[key_pred]
    return _get_key_of_max_val(classifiy[key_probs])


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

def extr_keys(summary, key_probs):
    return list(summary.classifiy[key_probs].keys())


style_t_pattern = """width: 16.6667%;
text-align: right;
background-color: rgb(255, 242, 204);"""

style_f_pattern = """width: 16.6667%;
text-align: center;
background-color: rgb(255, 255, 255);"""


style_t_issue = """width: 16.6667%;
text-align: center;
background-color: rgb(255, 242, 204);
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

style_f_sector = """
box-sizing: border-box;
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
width: 126.828px;
text-align: center;
background-color: rgb(255, 255, 255);
"""
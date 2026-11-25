#!/usr/bin/env python3
"""
Generates the Elementor import files for the FSI (Fulton Science Innovations) website.

Outputs (written to ../):
  fsi-global-kit.zip        -> Elementor > Tools > Import/Export Kit (Site Settings only)
  fsi-header.json           -> Templates > Saved Templates > Import (Theme Builder header)
  fsi-footer.json           -> Templates > Saved Templates > Import (Theme Builder footer)
  fsi-homepage.json         -> Templates > Saved Templates > Import (page template)

Every color and font in the templates points at an Elementor Global Color / Global Font,
so the whole site can be restyled from Site Settings.

Run:  python3 build.py
"""
import json
import os
import random
import zipfile
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)
random.seed(20261124)

# ---------------------------------------------------------------------------
# Design tokens (picked from the client design)
# ---------------------------------------------------------------------------
SYSTEM_COLORS = [
    ("primary", "Primary – FSI Navy", "#0A3D80"),
    ("secondary", "Secondary – FSI Gold", "#F9BE1A"),
    ("text", "Text – Body", "#33425E"),
    ("accent", "Accent – Bright Blue", "#0068BE"),
]
CUSTOM_COLORS = [
    ("fsideep", "Deep Navy", "#03234F"),
    ("fsihead", "Heading Dark", "#0C1A3A"),
    ("fsigold", "Gold Dark (hover)", "#E5A500"),
    ("fsiltbl", "Light Blue Card", "#DFECFC"),
    ("fsiltgd", "Light Gold Card", "#FFF4D6"),
    ("fsiltpu", "Light Purple Card", "#ECE6FC"),
    ("fsibggr", "Section Background", "#F5F8FC"),
    ("fsibord", "Border", "#DCE4F0"),
    ("fsiwhit", "White", "#FFFFFF"),
    ("fsimute", "Muted Text", "#5B6B85"),
    ("fsigren", "Success Green", "#1E9E5A"),
]

HEAD_FONT = "Poppins"   # bold geometric sans – closest Google match to the design headings
BODY_FONT = "Inter"     # clean UI sans for body copy


def px(v, unit="px"):
    return {"unit": unit, "size": v, "sizes": []}


def em(v):
    return {"unit": "em", "size": v, "sizes": []}


def typo(family, weight, size, lh=None, size_t=None, size_m=None, transform=None, ls=None, style=None):
    d = {
        "typography_typography": "custom",
        "typography_font_family": family,
        "typography_font_weight": str(weight),
        "typography_font_size": px(size),
    }
    if size_t:
        d["typography_font_size_tablet"] = px(size_t)
    if size_m:
        d["typography_font_size_mobile"] = px(size_m)
    if lh:
        d["typography_line_height"] = em(lh)
    if transform:
        d["typography_text_transform"] = transform
    if ls is not None:
        d["typography_letter_spacing"] = px(ls)
    if style:
        d["typography_font_style"] = style
    return d


SYSTEM_TYPO = [
    ("primary", "Primary – Headings", typo(HEAD_FONT, 700, 34, 1.2, 30, 26)),
    ("secondary", "Secondary – Subheadings", typo(HEAD_FONT, 600, 18, 1.35, 17, 16)),
    ("text", "Text – Body", typo(BODY_FONT, 400, 16, 1.6, 16, 15)),
    ("accent", "Accent – Buttons", typo(HEAD_FONT, 600, 15, 1.2, 15, 14)),
]
CUSTOM_TYPO = [
    ("fsidisp", "Display – Hero Title", typo(HEAD_FONT, 800, 48, 1.1, 40, 32)),
    ("fsih3cd", "Card Title", typo(HEAD_FONT, 700, 20, 1.3, 19, 18)),
    ("fsih4sm", "Small Title", typo(HEAD_FONT, 600, 16, 1.3, 16, 15)),
    ("fsieyeb", "Eyebrow", typo(HEAD_FONT, 700, 14, 1.3, 13, 12, transform="uppercase", ls=2.5)),
    ("fsibdlg", "Body Large", typo(BODY_FONT, 400, 18, 1.55, 17, 16)),
    ("fsibdsm", "Body Small", typo(BODY_FONT, 400, 14, 1.55, 14, 14)),
    ("fsicapt", "Caption", typo(BODY_FONT, 500, 12, 1.4, 12, 12)),
    ("fsinavi", "Navigation", typo(HEAD_FONT, 500, 14, 1.2)),
    ("fsistat", "Statistic", typo(HEAD_FONT, 800, 28, 1.1, 26, 24)),
    ("fsiquot", "Quote", typo(BODY_FONT, 600, 15, 1.5, 15, 14)),
    ("fsilabl", "Feature Label", typo(HEAD_FONT, 600, 14, 1.3, 14, 14)),
]

CUSTOM_CSS = r"""/* ===== FSI helper classes (used by the imported templates) ===== */
/* Adds a trailing arrow to buttons that already have a leading icon */
.fsi-btn-arrow .elementor-button-text::after{content:"\2192";margin-left:10px;display:inline-block;transition:transform .2s}
.fsi-btn-arrow .elementor-button:hover .elementor-button-text::after{transform:translateX(3px)}
/* ===== Gold swoosh underline (add class "fsi-swoosh" to a Heading widget) =====
   Sized in em, so it scales with the heading's font size on every breakpoint. */
.fsi-swoosh .elementor-heading-title{
  position:relative;
  display:inline-block;
  padding-bottom:.45em;
}
.fsi-swoosh .elementor-heading-title::after{
  content:"";
  position:absolute;
  left:0;
  bottom:0;
  width:var(--fsi-swoosh-width,2.4em);
  height:.36em;
  background-color:var(--fsi-swoosh-color,var(--e-global-color-secondary));
  -webkit-mask:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 120 16' preserveAspectRatio='none'%3E%3Cpath d='M1 12C30 4.5 70 1 118 2C120.5 2.2 120.5 6 118 6.4C72 8.5 36 11.5 5 15.6C1.5 16 -0.5 13 1 12Z'/%3E%3C/svg%3E") no-repeat 0 0/100% 100%;
          mask:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 120 16' preserveAspectRatio='none'%3E%3Cpath d='M1 12C30 4.5 70 1 118 2C120.5 2.2 120.5 6 118 6.4C72 8.5 36 11.5 5 15.6C1.5 16 -0.5 13 1 12Z'/%3E%3C/svg%3E") no-repeat 0 0/100% 100%;
}
/* Centered headings */
.fsi-swoosh--center .elementor-heading-title::after{left:50%;transform:translateX(-50%)}
/* Right-aligned headings */
.fsi-swoosh--right .elementor-heading-title::after{left:auto;right:0}
/* Width options */
.fsi-swoosh--short{--fsi-swoosh-width:1.6em}
.fsi-swoosh--long{--fsi-swoosh-width:4em}
.fsi-swoosh--full{--fsi-swoosh-width:100%}
/* Colour options */
.fsi-swoosh--white{--fsi-swoosh-color:#fff}
.fsi-swoosh--navy{--fsi-swoosh-color:var(--e-global-color-primary)}
/* Vertical axis title on the results chart */
.fsi-rotate .elementor-heading-title{writing-mode:vertical-rl;transform:rotate(180deg);white-space:nowrap}
/* Card hover lift */
.fsi-card{transition:transform .25s ease, box-shadow .25s ease}
.fsi-card:hover{transform:translateY(-4px);box-shadow:0 14px 30px rgba(10,61,128,.14)}
/* Header menu pill */
.fsi-nav .elementor-nav-menu--main .elementor-item{border-radius:6px}
/* Form selects */
.fsi-form .elementor-field-group .elementor-select-wrapper select{font-size:14px}
.fsi-form .elementor-field-label{font-size:12px;font-weight:500}
/* Footer link lists */
.fsi-footer-links .elementor-icon-list-item a:hover .elementor-icon-list-text{color:var(--e-global-color-accent)}
/* Chart bars */
.fsi-bar{border-radius:3px 3px 0 0}
"""

# ---------------------------------------------------------------------------
# Element helpers
# ---------------------------------------------------------------------------
_used = set()


def eid():
    while True:
        s = "%07x" % random.getrandbits(28)
        if s not in _used:
            _used.add(s)
            return s


def C(cid):
    return "globals/colors?id=%s" % cid


def T(tid):
    return "globals/typography?id=%s" % tid


def box(t, r=None, b=None, l=None, unit="px"):
    if r is None:
        r = b = l = t
    elif b is None:
        b, l = t, r
    elif l is None:
        l = r
    return {"unit": unit, "top": str(t), "right": str(r), "bottom": str(b), "left": str(l),
            "isLinked": t == r == b == l}


def gap(v):
    return {"column": str(v), "row": str(v), "isLinked": True, "unit": "px", "size": v}


def icon(value):
    lib = {"fas": "fa-solid", "far": "fa-regular", "fab": "fa-brands"}[value.split()[0]]
    return {"value": value, "library": lib}


def link(url="#"):
    return {"url": url, "is_external": "", "nofollow": "", "custom_attributes": ""}


def merge(*dicts):
    out = {}
    g = {}
    for d in dicts:
        if not d:
            continue
        d = dict(d)
        g.update(d.pop("__globals__", {}))
        out.update(d)
    if g:
        out["__globals__"] = g
    return out


def con(elements, **s):
    return {"id": eid(), "elType": "container", "settings": merge(s), "elements": elements, "isInner": False}


def row(elements, **s):
    base = {"content_width": "full", "flex_direction": "row", "flex_gap": gap(20),
            "padding": box(0)}
    base.update(s)
    return con(elements, **base)


def col(elements, **s):
    base = {"content_width": "full", "flex_direction": "column", "flex_gap": gap(12),
            "padding": box(0)}
    base.update(s)
    return con(elements, **base)


def section(elements, bg=None, pad=(70, 20, 70, 20), pad_m=(48, 16, 48, 16), **s):
    """Top-level boxed section."""
    base = {
        "content_width": "boxed",
        "boxed_width": px(1240),
        "flex_direction": "column",
        "flex_gap": gap(32),
        "padding": box(*pad),
        "padding_mobile": box(*pad_m),
    }
    if bg:
        base["background_background"] = "classic"
        base["__globals__"] = {"background_color": C(bg)}
    base.update(s)
    return con(elements, **base)


def w(widget_type, **s):
    return {"id": eid(), "elType": "widget", "settings": merge(s), "elements": [], "widgetType": widget_type}


def width(desktop, tablet=None, mobile=100):
    d = {"width": px(desktop, "%")}
    if tablet is not None:
        d["width_tablet"] = px(tablet, "%")
    if mobile is not None:
        d["width_mobile"] = px(mobile, "%")
    return d


def wwidth(desktop, tablet=None, mobile=100):
    """Custom width for a widget inside a flex container."""
    d = {"_element_width": "initial", "_element_custom_width": px(desktop, "%")}
    if tablet is not None:
        d["_element_width_tablet"] = "initial"
        d["_element_custom_width_tablet"] = px(tablet, "%")
    if mobile is not None:
        d["_element_width_mobile"] = "initial"
        d["_element_custom_width_mobile"] = px(mobile, "%")
    return d


def heading(text, tag="h2", color="fsihead", font="primary", align=None, align_m=None, **s):
    d = {"title": text, "header_size": tag, "__globals__": {"title_color": C(color), "typography_typography": T(font)}}
    if align:
        d["align"] = align
    if align_m:
        d["align_mobile"] = align_m
    return w("heading", **merge(d, s))


def text(html, color="text", font="text", align=None, **s):
    d = {"editor": html, "__globals__": {"text_color": C(color), "typography_typography": T(font)}}
    if align:
        d["align"] = align
    return w("text-editor", **merge(d, s))


def button(label, url="#", ic="fas fa-arrow-right", style="gold", icon_pos="right", size="md", css="", **s):
    d = {
        "text": label,
        "link": link(url),
        "size": size,
        "icon_align": icon_pos,
        "icon_indent": px(10),
        "text_padding": box(14, 24) if size == "md" else box(11, 18),
        "border_radius": box(6),
        "__globals__": {"typography_typography": T("accent")},
    }
    if ic:
        d["selected_icon"] = icon(ic)
    if css:
        d["_css_classes"] = css
    if style == "gold":
        d["background_background"] = "classic"
        d["button_background_hover_background"] = "classic"
        d["__globals__"].update({
            "button_text_color": C("fsihead"),
            "background_color": C("secondary"),
            "hover_color": C("fsihead"),
            "button_background_hover_color": C("fsigold"),
        })
    elif style == "outline-white":
        d["background_background"] = "classic"
        d["background_color"] = "rgba(255,255,255,0)"
        d["button_background_hover_background"] = "classic"
        d["border_border"] = "solid"
        d["border_width"] = box(2)
        d["__globals__"].update({
            "button_text_color": C("fsiwhit"),
            "border_color": C("fsiwhit"),
            "hover_color": C("primary"),
            "button_background_hover_color": C("fsiwhit"),
        })
    elif style == "navy":
        d["background_background"] = "classic"
        d["button_background_hover_background"] = "classic"
        d["__globals__"].update({
            "button_text_color": C("fsiwhit"),
            "background_color": C("primary"),
            "hover_color": C("fsiwhit"),
            "button_background_hover_color": C("accent"),
        })
    return w("button", **merge(d, s))


def ico(value, color="primary", size=28, url=None, **s):
    d = {"selected_icon": icon(value), "view": "default", "icon_size": px(size),
         "__globals__": {"primary_color": C(color)}}
    if url:
        d["link"] = link(url)
    return w("icon", **merge(d, s))


def image(alt="", height=None, radius=0, **s):
    # No URL on purpose -> Elementor shows its placeholder; swap in the real image after import.
    d = {"image_size": "full", "width": px(100, "%"), "image_border_radius": box(radius)}
    if height:
        d["height"] = px(height)
        d["object-fit"] = "cover"
    return w("image", **merge(d, s))


def icon_list(items, ic="fas fa-check-circle", icon_color="secondary", text_color="fsiwhit", font="fsibdsm",
              gap_px=6, icon_size=16, **s):
    d = {
        "icon_list": [{"_id": eid(), "text": t, "selected_icon": icon(ic), "link": link("")} for t in items],
        "space_between": px(gap_px),
        "icon_size": px(icon_size),
        "text_indent": px(8),
        "icon_self_align": "left",
        "__globals__": {"icon_color": C(icon_color), "text_color": C(text_color),
                        "icon_typography_typography": T(font)},
    }
    return w("icon-list", **merge(d, s))


def card_style(bg="fsiwhit", radius=10, border=True, shadow=True, pad=(20, 20, 20, 20)):
    d = {
        "background_background": "classic",
        "border_radius": box(radius),
        "padding": box(*pad),
        "__globals__": {"background_color": C(bg)},
    }
    if border:
        d["border_border"] = "solid"
        d["border_width"] = box(1)
        d["__globals__"]["border_color"] = C("fsibord")
    if shadow:
        d["box_shadow_box_shadow_type"] = "yes"
        d["box_shadow_box_shadow"] = {"horizontal": 0, "vertical": 6, "blur": 20, "spread": 0,
                                      "color": "rgba(10,61,128,0.08)"}
    return d


# ---------------------------------------------------------------------------
# HEADER
# ---------------------------------------------------------------------------
def build_header():
    menu = w(
        "nav-menu",
        menu="",
        layout="horizontal",
        align_items="center",
        pointer="background",
        animation_background="fade",
        submenu_icon=icon("fas fa-chevron-down"),
        dropdown="tablet",
        toggle="burger",
        full_width="",
        padding_horizontal_menu_item=px(12),
        padding_vertical_menu_item=px(9),
        menu_space_between=px(2),
        _css_classes="fsi-nav",
        _flex_size="grow",
        __globals__={
            "menu_typography_typography": T("fsinavi"),
            "color_menu_item": C("fsihead"),
            "color_menu_item_hover": C("primary"),
            "pointer_color_menu_item_hover": C("fsiltbl"),
            "color_menu_item_active": C("fsiwhit"),
            "pointer_color_menu_item_active": C("primary"),
            "color_dropdown_item": C("fsihead"),
            "background_color_dropdown_item": C("fsiwhit"),
            "color_dropdown_item_hover": C("fsiwhit"),
            "background_color_dropdown_item_hover": C("primary"),
            "toggle_color": C("primary"),
        },
    )
    search = w("search-form", skin="full_screen", toggle_size=px(34), toggle_align="center",
               __globals__={"toggle_color": C("fsihead")})
    logo = w("theme-site-logo", width=px(190), width_mobile=px(150), align="left",
             **wwidth(16, 30, 50))
    cta = button("Request a Demo", "#request-demo", size="sm")
    header = con(
        [logo, menu, search, cta],
        content_width="boxed",
        boxed_width=px(1240),
        flex_direction="row",
        flex_align_items="center",
        flex_justify_content="space-between",
        flex_gap=gap(16),
        padding=box(14, 20),
        padding_mobile=box(12, 16),
        background_background="classic",
        border_border="solid",
        border_width=box(0, 0, 1, 0),
        __globals__={"background_color": C("fsiwhit"), "border_color": C("fsibord")},
        html_tag="header",
    )
    return [header]


# ---------------------------------------------------------------------------
# FOOTER
# ---------------------------------------------------------------------------
def build_footer():
    def links_col(title, items):
        return col([
            heading(title, "h6", "fsihead", "fsih4sm"),
            w("icon-list", icon_list=[{"_id": eid(), "text": t, "selected_icon": {"value": "", "library": ""},
                                       "link": link("#")} for t in items],
              space_between=px(4), _css_classes="fsi-footer-links",
              __globals__={"text_color": C("text"), "icon_typography_typography": T("fsibdsm")}),
        ], flex_gap=gap(8), **width(18, 30, 100))

    social = w(
        "social-icons",
        social_icon_list=[
            {"_id": eid(), "social_icon": icon("fab fa-youtube"), "link": link("#"), "item_icon_color": "default"},
            {"_id": eid(), "social_icon": icon("fab fa-facebook-f"), "link": link("#"), "item_icon_color": "default"},
            {"_id": eid(), "social_icon": icon("fab fa-linkedin-in"), "link": link("#"), "item_icon_color": "default"},
        ],
        shape="rounded",
        align="left",
        icon_color="custom",
        icon_size=px(16),
        icon_padding=em(0.6),
        icon_spacing=px(10),
        border_radius=box(6),
        __globals__={"icon_primary_color": C("primary"), "icon_secondary_color": C("fsiwhit")},
    )
    logo_col = col([w("theme-site-logo", width=px(200), align="left")],
                   flex_justify_content="center",
                   border_border="solid", border_width=box(0, 1, 0, 0),
                   border_width_mobile=box(0),
                   padding=box(0, 30, 0, 0), padding_mobile=box(0),
                   __globals__={"border_color": C("fsibord")},
                   **width(26, 100, 100))
    connect = col([heading("Connect With Us", "h6", "fsihead", "fsih4sm"), social],
                  border_border="solid", border_width=box(0, 0, 0, 1), border_width_mobile=box(0),
                  padding=box(0, 0, 0, 30), padding_mobile=box(0),
                  __globals__={"border_color": C("fsibord")}, **width(20, 30, 100))
    main = con(
        [
            logo_col,
            links_col("Solutions", ["FSI Courses", "The FSI Way", "Professional Learning", "FSI Publishing"]),
            links_col("Implementation", ["School Plans", "District Plans", "Success Stories"]),
            links_col("About FSI", ["Our Mission", "Our Team", "Contact"]),
            connect,
        ],
        content_width="boxed",
        boxed_width=px(1240),
        flex_direction="row",
        flex_wrap="wrap",
        flex_justify_content="space-between",
        flex_gap=gap(24),
        padding=box(36, 20),
        padding_mobile=box(32, 16),
        background_background="classic",
        __globals__={"background_color": C("fsiwhit")},
        html_tag="footer",
    )
    copyright_bar = con(
        [text("<p>© 2026 Fulton Science Innovations. All rights reserved.</p>", "fsimute", "fsicapt",
              align="center")],
        content_width="boxed", boxed_width=px(1240), padding=box(14, 20),
        background_background="classic", border_border="solid", border_width=box(1, 0, 0, 0),
        __globals__={"background_color": C("fsibggr"), "border_color": C("fsibord")},
    )
    return [main, copyright_bar]


# ---------------------------------------------------------------------------
# HOMEPAGE
# ---------------------------------------------------------------------------
def hero():
    content = col(
        [
            heading("Georgia's Science Instruction Partner", "p", "secondary", "fsieyeb"),
            col([
                heading("Transform Science Teaching.", "h1", "fsiwhit", "fsidisp"),
                heading("Accelerate Student Achievement.", "h2", "secondary", "fsidisp"),
            ], flex_gap=gap(4)),
            text("<p>Georgia-aligned interactive courses, hands-on learning systems, Milestones preparation, "
                 "and teacher coaching—all connected through <strong>The FSI Way</strong>.</p>",
                 "fsiwhit", "fsibdlg"),
            row([
                button("Request District Demo", "#request-demo", ic="far fa-calendar-alt", icon_pos="left",
                       css="fsi-btn-arrow"),
                button("Watch The FSI Way in Action", "#watch", ic="far fa-play-circle", icon_pos="left",
                       style="outline-white"),
            ], flex_wrap="wrap", flex_gap=gap(16), padding=box(10, 0, 0, 0)),
        ],
        flex_gap=gap(18),
        **width(52, 75, 100),
    )
    return con(
        [content],
        content_width="boxed",
        boxed_width=px(1240),
        flex_direction="row",
        flex_align_items="center",
        min_height=px(500),
        min_height_tablet=px(440),
        min_height_mobile=px(0),
        padding=box(70, 20),
        padding_mobile=box(56, 16),
        background_background="classic",
        background_position="center right",
        background_repeat="no-repeat",
        background_size="cover",
        background_overlay_background="gradient",
        background_overlay_color="#03234F",
        background_overlay_color_stop=px(38, "%"),
        background_overlay_color_b="rgba(3,35,79,0)",
        background_overlay_color_b_stop=px(78, "%"),
        background_overlay_gradient_type="linear",
        background_overlay_gradient_angle=px(90, "deg"),
        background_overlay_gradient_angle_mobile=px(180, "deg"),
        __globals__={"background_color": C("fsideep")},
        _element_id="hero",
    )


def feature_strip():
    feats = [
        ("far fa-map", "Georgia-Aligned<br>Instruction"),
        ("fas fa-laptop", "Digital &amp; Hands-On<br>Learning"),
        ("fas fa-user-friends", "Teacher Coaching &amp;<br>Professional Learning"),
        ("far fa-chart-bar", "Milestones<br>Preparation"),
        ("fas fa-layer-group", "Classroom Kits &amp;<br>Publishing"),
    ]
    items = []
    for i, (ic, label) in enumerate(feats):
        last = i == len(feats) - 1
        items.append(w(
            "icon-box",
            selected_icon=icon(ic),
            title_text=label,
            description_text="",
            position="left",
            content_vertical_alignment="middle",
            title_size="h3",
            text_align="left",
            icon_size=px(30),
            icon_space=px(14),
            title_bottom_space=px(0),
            _border_border="" if last else "solid",
            _border_width=box(0, 1, 0, 0),
            _padding=box(4, 14),
            **wwidth(20, 33, 100),
            __globals__={"primary_color": C("primary"), "title_color": C("fsihead"),
                         "title_typography_typography": T("fsilabl"), "_border_color": C("fsibord")},
        ))
    return con(
        items,
        content_width="boxed", boxed_width=px(1240),
        flex_direction="row", flex_wrap="wrap", flex_wrap_mobile="wrap",
        flex_align_items="center", flex_justify_content="space-between",
        flex_gap=gap(0), flex_gap_mobile=gap(14),
        padding=box(22, 20), padding_mobile=box(24, 16),
        background_background="classic",
        border_border="solid", border_width=box(0, 0, 1, 0),
        box_shadow_box_shadow_type="yes",
        box_shadow_box_shadow={"horizontal": 0, "vertical": 4, "blur": 14, "spread": 0,
                               "color": "rgba(10,61,128,0.06)"},
        __globals__={"background_color": C("fsiwhit"), "border_color": C("fsibord")},
    )


def choose_path():
    def path_card(ic, title, desc, bg, url):
        return con(
            [
                ico(ic, "primary", 40, _flex_size="none"),
                col([heading(title, "h3", "fsihead", "fsih3cd"), text("<p>" + desc + "</p>", "text", "fsibdsm")],
                    flex_gap=gap(4), _flex_size="grow"),
                ico("fas fa-chevron-right", "fsihead", 14),
            ],
            content_width="full", flex_direction="row", flex_align_items="center", flex_gap=gap(16),
            html_tag="a", link=link(url), _css_classes="fsi-card",
            **merge(card_style(bg, 10, border=False, shadow=False, pad=(20, 18, 20, 20)), width(26, 100, 100)),
        )

    title = col([heading("Choose Your Path with FSI", "h2", "fsihead", "primary", _css_classes="fsi-swoosh")],
                flex_gap=gap(6), **width(22, 100, 100))
    return section([
        row([
            title,
            path_card("fas fa-city", "District Leaders",
                      "Explore a districtwide solution to improve science achievement.", "fsiltbl", "#district"),
            path_card("fas fa-school", "School Administrators",
                      "Plan implementation and support for your school.", "fsiltgd", "#schools"),
            path_card("fas fa-graduation-cap", "Teachers",
                      "Experience an FSI science lesson and see it in action.", "fsiltpu", "#teachers"),
        ], flex_align_items="center", flex_wrap_tablet="wrap", flex_gap=gap(22)),
    ], bg="fsiwhit", pad=(48, 20, 48, 20))


def solutions():
    def sol_card(ic, title, desc):
        return con(
            [
                image(title, height=180, radius=0),
                col([
                    row([ico(ic, "primary", 22), heading(title, "h3", "fsihead", "fsih3cd")],
                        flex_align_items="center", flex_gap=gap(10)),
                    row([text("<p>" + desc + "</p>", "text", "fsibdsm", _flex_size="grow"),
                         ico("fas fa-chevron-right", "fsihead", 13)],
                        flex_align_items="center", flex_gap=gap(10)),
                ], padding=box(16, 18, 20, 18), flex_gap=gap(8)),
            ],
            content_width="full", flex_direction="column", flex_gap=gap(0),
            html_tag="a", link=link("#"), _css_classes="fsi-card",
            overflow="hidden",
            **merge(card_style("fsiwhit", 10, pad=(0, 0, 0, 0)), width(25, 48, 100)),
        )

    return section([
        col([
            heading("The Complete FSI Solution", "p", "fsihead", "fsieyeb", align="center"),
            heading("A Connected System for Science Success", "h2", "fsihead", "primary", align="center",
                    _css_classes="fsi-swoosh fsi-swoosh--center"),
        ], flex_gap=gap(6), flex_align_items="center"),
        row([
            sol_card("fas fa-laptop", "FSI Courses",
                     "Engaging digital lessons, interactive activities, assessments, and progress dashboards."),
            sol_card("fas fa-chalkboard-teacher", "The FSI Way Boards",
                     "Hands-on, reusable learning systems for labeling, sorting, CER, and scientific modeling."),
            sol_card("fas fa-school", "FSI Professional Learning",
                     "Job-embedded coaching, demonstration lessons, and implementation support for lasting impact."),
            sol_card("fas fa-layer-group", "FSI Publishing",
                     "Workbooks, games, classroom kits, and assessment-preparation products for Georgia science."),
        ], flex_wrap_tablet="wrap", flex_gap=gap(20)),
    ], bg="fsibggr", pad=(56, 20, 56, 20))


def lesson_and_results():
    lesson = con(
        [
            col([
                heading("Experience an FSI Interactive Lesson", "h2", "fsiwhit", "primary"),
                text("<p>See how our interactive content builds understanding, engages students, "
                     "and prepares them for Georgia Milestones.</p>", "fsiwhit", "text"),
                button("Try a Sample Interactive", "#sample"),
            ], flex_gap=gap(16), **width(52, 52, 100)),
            col([image("Interactive lesson on laptop", radius=8)], flex_justify_content="center",
                **width(48, 48, 100)),
        ],
        content_width="full", flex_direction="row", flex_direction_mobile="column",
        flex_align_items="center", flex_gap=gap(20),
        background_background="classic", border_radius=box(12),
        padding=box(32, 28), padding_mobile=box(28, 20),
        __globals__={"background_color": C("primary")},
        **width(48, 100, 100),
    )

    def bar(pct, label, color):
        return col([
            heading(f"{pct}%", "p", "fsihead", "fsistat", align="center"),
            con([], content_width="full", min_height=px(round(pct * 1.9)),
                background_background="classic", _css_classes="fsi-bar", width=px(100, "%"),
                __globals__={"background_color": C(color)}),
        ], flex_justify_content="flex-end", flex_gap=gap(4), width=px(90), width_mobile=px(80))

    axis_labels = col(
        [text(f"<p>{v}%</p>", "fsihead", "fsicapt", align="right") for v in (100, 80, 60, 40, 20, 0)],
        flex_justify_content="space-between", flex_gap=gap(0), min_height=px(200), width=px(40),
        padding=box(0, 0, 0, 0),
    )
    plot = row([bar(62, "Before FSI", "accent"), bar(71, "After FSI", "secondary")],
               flex_align_items="flex-end", flex_justify_content="space-around", flex_gap=gap(24),
               min_height=px(200), border_border="solid", border_width=box(0, 0, 1, 1),
               padding=box(0, 16, 0, 16), _flex_size="grow",
               __globals__={"border_color": C("fsimute")})
    chart = col([
        row([
            col([], width=px(62)),
            con([
                heading("+9", "p", "fsigren", "fsistat", align="center"),
                heading("percentage points", "p", "fsigren", "fsicapt", align="center"),
            ], content_width="full", flex_direction="column", flex_gap=gap(0), padding=box(4, 16),
                border_border="solid", border_width=box(2), border_radius=box(30),
                __globals__={"border_color": C("fsigren")}),
        ], flex_justify_content="center", flex_gap=gap(0)),
        row([
            heading("Georgia Milestones (% Proficient + Distinguished)", "p", "fsihead", "fsicapt",
                    _css_classes="fsi-rotate", _flex_size="none"),
            axis_labels,
            plot,
        ], flex_align_items="center", flex_gap=gap(8)),
        row([col([], width=px(110)),
             row([heading("Before FSI", "p", "fsihead", "fsicapt", align="center", _flex_size="grow"),
                  heading("After FSI", "p", "fsihead", "fsicapt", align="center", _flex_size="grow")],
                 flex_justify_content="space-around", _flex_size="grow")], flex_gap=gap(0)),
    ], flex_gap=gap(10), **width(52, 52, 100))

    testimonial = col([
        w("video", video_type="youtube", youtube_url="https://www.youtube.com/watch?v=XHOmBV4js_E",
          show_image_overlay="yes", image_overlay_size="full", lightbox="", aspect_ratio="169",
          _border_radius=box(8)),
        text("<p>“FSI gave our teachers the tools, the support, and the confidence to make science come "
             "alive for our students.”</p>", "fsihead", "fsiquot"),
        col([
            heading("Dr. Shawanda Williams", "p", "fsihead", "fsih4sm"),
            text("<p>Principal, [Georgia Elementary School]</p>", "fsimute", "fsicapt"),
        ], flex_gap=gap(0)),
    ], flex_gap=gap(12), **width(48, 48, 100))

    results = con(
        [
            heading("Proven Results in Georgia", "h2", "primary", "fsih3cd"),
            text("<p>FSI schools are seeing measurable gains in science achievement.</p>", "text", "fsibdsm"),
            row([chart, testimonial], flex_direction_mobile="column", flex_gap=gap(20)),
        ],
        content_width="full", flex_direction="column", flex_gap=gap(8),
        **merge(card_style("fsiwhit", 12, pad=(24, 24, 24, 24)), {"border_width": box(2)},
                {"__globals__": {"border_color": C("primary")}}, width(52, 100, 100)),
    )
    return section([row([lesson, results], flex_wrap_tablet="wrap", flex_gap=gap(24),
                        flex_align_items="stretch")],
                   bg="fsiwhit", pad=(48, 20, 56, 20))


def professional_learning():
    form = w(
        "form",
        form_name="Request Professional Learning",
        form_fields=[
            {"_id": eid(), "custom_id": "grade", "field_type": "select", "field_label": "Grade or Subject",
             "field_options": "3rd Grade\n4th Grade\n5th Grade\n6th Grade\n7th Grade\n8th Grade\nBiology\nPhysical Science",
             "width": "50", "width_mobile": "100", "required": "true"},
            {"_id": eid(), "custom_id": "month", "field_type": "select", "field_label": "Preferred Month",
             "field_options": "January 2027\nFebruary 2027\nMarch 2027\nApril 2027",
             "width": "50", "width_mobile": "100", "required": "true"},
            {"_id": eid(), "custom_id": "focus", "field_type": "select", "field_label": "Professional Learning Focus",
             "field_options": "Milestones Preparation\nThe FSI Way Implementation\nFSI Courses Onboarding\nOn-site Coaching\nVirtual Professional Learning",
             "width": "100", "required": "true"},
        ],
        show_labels="yes",
        input_size="sm",
        button_text="Check Availability & Request Dates",
        button_size="sm",
        button_width="100",
        selected_button_icon=icon("fas fa-arrow-right"),
        button_icon_align="right",
        button_icon_indent=px(10),
        submit_actions=["email"],
        email_subject="New Professional Learning Request – FSI website",
        success_message="Thanks! The FSI team will confirm availability shortly.",
        column_gap=px(14),
        row_gap=px(12),
        label_spacing=px(4),
        field_border_width=box(1),
        field_border_radius=box(6),
        button_border_radius=box(6),
        _css_classes="fsi-form",
        __globals__={
            "label_color": C("fsihead"),
            "label_typography_typography": T("fsicapt"),
            "field_text_color": C("fsihead"),
            "field_typography_typography": T("fsibdsm"),
            "field_background_color": C("fsiwhit"),
            "field_border_color": C("fsibord"),
            "button_background_color": C("secondary"),
            "button_text_color": C("fsihead"),
            "button_background_hover_color": C("fsigold"),
            "button_hover_color": C("fsihead"),
            "button_typography_typography": T("accent"),
        },
    )
    form_card = col([
        heading("Request Professional Learning", "h3", "fsihead", "fsih3cd"),
        form,
        text('<p style="text-align:center;">Or <a href="#waitlist"><strong>Join the Priority Waitlist</strong></a></p>',
             "fsihead", "fsibdsm"),
    ], flex_gap=gap(10), **merge(card_style("fsiwhit", 10, border=False, pad=(22, 24, 18, 24)),
                                  width(34, 100, 100)))
    middle = col([
        row([
            ico("far fa-calendar-alt", "secondary", 30),
            col([heading("2027 FSI Milestones Prep School Tour", "p", "secondary", "fsih4sm"),
                 text("<p>January – April 2027</p>", "fsiwhit", "fsibdsm")], flex_gap=gap(0)),
        ], flex_align_items="center", flex_gap=gap(12)),
        heading("Bring The FSI Way to Your School", "h2", "fsiwhit", "primary"),
        text("<p>Request professional learning for your science teachers. Choose your preferred grade, focus, "
             "and dates—or join the priority waitlist if your dates are not available.</p>", "fsiwhit", "text"),
        icon_list(["Milestones preparation", "The FSI Way implementation", "On-site or virtual professional learning"],
                  text_color="fsiwhit"),
    ], flex_gap=gap(14), flex_justify_content="center", padding=box(36, 0), padding_mobile=box(0),
        **width(40, 100, 100))
    presenter = col([image("FSI presenter", height=380, radius=0)],
                    flex_justify_content="center", **width(26, 100, 100))
    inner = con(
        [presenter, middle, form_card],
        content_width="boxed", boxed_width=px(1440),
        flex_direction="row", flex_wrap_tablet="wrap", flex_align_items="center", flex_gap=gap(32),
        padding=box(0, 30, 0, 0), padding_tablet=box(40, 24), padding_mobile=box(40, 16),
        background_background="gradient",
        background_color="#03234F",
        background_color_b="#0A3D80",
        background_gradient_type="linear",
        background_gradient_angle=px(90, "deg"),
        __globals__={"background_color": C("fsideep"), "background_color_b": C("primary")},
        _element_id="professional-learning",
    )
    return inner


def implementation_plans():
    def plan(ic, title, items, bg="fsiwhit", badge=False):
        els = [
            row([ico(ic, "primary", 24), heading(title, "h3", "fsihead", "fsih3cd")],
                flex_align_items="center", flex_gap=gap(10)),
            icon_list(items, ic="fas fa-check", icon_color="primary", text_color="fsihead", icon_size=12),
        ]
        if badge:
            els.insert(0, heading("Most Popular", "span", "fsihead", "fsicapt",
                                  _background_background="classic", _padding=box(4, 10), _border_radius=box(4),
                                  _position="absolute", _offset_orientation_h="end", _offset_x_end=px(14),
                                  _offset_y=px(-12), _z_index=2,
                                  __globals__={"_background_color": C("secondary")}))
        return con(els, content_width="full", flex_direction="column", flex_gap=gap(14),
                   **merge(card_style(bg, 10, pad=(22, 22, 24, 22)), width(25, 48, 100)))

    intro = col([
        heading("Implementation Plans for Schools &amp; Districts", "h2", "fsihead", "primary"),
        text("<p><strong>Flexible</strong> options to fit your goals, scale, and <strong>level</strong> of "
             "support—from a single school to a complete district solution.</p>", "text", "fsibdsm"),
    ], flex_gap=gap(12), **width(25, 100, 100))
    return section([
        row([
            intro,
            plan("fas fa-school", "School Essential",
                 ["FSI Courses (selected grades)", "The FSI Way classroom resources", "Implementation launch support"]),
            plan("fas fa-star", "School Plus",
                 ["FSI Courses (all science grades)", "The FSI Way boards and materials",
                  "Professional learning & coaching", "Assessment preparation support"], bg="fsiltgd", badge=True),
            plan("fas fa-users", "District Partnership",
                 ["Districtwide implementation plan", "Full access to FSI solutions",
                  "Ongoing professional learning", "Data reviews and continuous improvement"]),
        ], flex_wrap_tablet="wrap", flex_gap=gap(22), flex_align_items="stretch"),
    ], bg="fsibggr", pad=(56, 20, 40, 20), _element_id="plans")


def publishing():
    def product(title, sub):
        return w("image-box", title_text=title, description_text=sub, title_size="h3",
                 image_space=px(10), text_align="center", title_bottom_space=px(2),
                 image_size=px(100, "%"), link=link("#"),
                 **wwidth(23, 46, 100),
                 __globals__={"title_color": C("fsihead"), "description_color": C("fsimute"),
                              "title_typography_typography": T("fsih4sm"),
                              "description_typography_typography": T("fsicapt")})

    intro = col([
        heading("Explore FSI Publishing", "h2", "fsihead", "primary"),
        text("<p>Classroom-tested resources to build science understanding, reinforce learning, "
             "and prepare for Georgia assessments.</p>", "text", "fsibdsm"),
        row([button("Shop All Products", "#shop", size="sm")]),
    ], flex_gap=gap(14), **width(24, 100, 100))
    products = row([
        product("Science Workbooks", "(Grades 5, 8, Biology)"),
        product("The FSI Way Kits", "(Hands-On Learning Boards)"),
        product("Review &amp; Test Prep", "(Milestones &amp; EOC)"),
        product("Science Games", "(Engaging Practice)"),
    ], flex_wrap="wrap", flex_justify_content="space-between", flex_gap=gap(16), **width(74, 100, 100))
    return section([row([intro, products], flex_wrap_tablet="wrap", flex_align_items="center",
                        flex_gap=gap(28))],
                   bg="fsiwhit", pad=(40, 20, 56, 20), _element_id="publishing")


def cta_band():
    return con(
        [
            col([
                heading("Ready to Transform Science in Your Schools?", "h2", "fsiwhit", "primary"),
                text("<p>Request a district or school demo, explore our solutions, or get in touch with the FSI team.</p>",
                     "fsiwhit", "text"),
            ], flex_gap=gap(6), **width(60, 100, 100)),
            row([
                button("Request a Demo", "#request-demo", ic="far fa-calendar-alt", icon_pos="left",
                       css="fsi-btn-arrow"),
                button("Contact FSI", "#contact", ic="far fa-envelope", icon_pos="left", style="outline-white"),
            ], flex_wrap="wrap", flex_justify_content="flex-end", flex_justify_content_tablet="flex-start",
                flex_gap=gap(16), **width(40, 100, 100)),
        ],
        content_width="boxed", boxed_width=px(1240),
        flex_direction="row", flex_wrap_tablet="wrap", flex_align_items="center", flex_gap=gap(24),
        padding=box(40, 20), padding_mobile=box(44, 16),
        background_background="gradient",
        background_color="#0A3D80",
        background_color_b="#0068BE",
        background_gradient_type="linear",
        background_gradient_angle=px(90, "deg"),
        __globals__={"background_color": C("primary"), "background_color_b": C("accent")},
        _element_id="request-demo",
    )


def build_home():
    return [hero(), feature_strip(), choose_path(), solutions(), lesson_and_results(),
            professional_learning(), implementation_plans(), publishing(), cta_band()]


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------
def fix_text_color_typos(elements):
    # guard against accidental unknown global ids
    valid = {c[0] for c in SYSTEM_COLORS + CUSTOM_COLORS}
    valid_t = {t[0] for t in SYSTEM_TYPO + CUSTOM_TYPO}
    for el in elements:
        g = el["settings"].get("__globals__", {})
        for k, v in g.items():
            kind, _, gid = v.partition("?id=")
            if kind.endswith("colors"):
                assert gid in valid, f"unknown color id {gid} on {k}"
            else:
                assert gid in valid_t, f"unknown typography id {gid} on {k}"
        fix_text_color_typos(el["elements"])


def mark_inner(elements, depth=0):
    for el in elements:
        if el["elType"] == "container":
            el["isInner"] = depth > 0
        mark_inner(el["elements"], depth + 1)


def template(title, ttype, content, page_settings=None):
    mark_inner(content)
    fix_text_color_typos(content)
    return {"content": content, "page_settings": page_settings or [], "version": "0.4",
            "title": title, "type": ttype}


def kit_settings():
    s = {
        "system_colors": [{"_id": i, "title": t, "color": c} for i, t, c in SYSTEM_COLORS],
        "custom_colors": [{"_id": i, "title": t, "color": c} for i, t, c in CUSTOM_COLORS],
        "system_typography": [merge({"_id": i, "title": t}, d) for i, t, d in SYSTEM_TYPO],
        "custom_typography": [merge({"_id": i, "title": t}, d) for i, t, d in CUSTOM_TYPO],
        "default_generic_fonts": "Sans-serif",
        # Layout
        "container_width": px(1240),
        "container_padding": box(0),
        "space_between_widgets": {"column": "20", "row": "20", "isLinked": True, "unit": "px", "size": 20},
        "page_title_selector": "h1.entry-title",
        # Background
        "body_background_background": "classic",
        "body_background_color": "#FFFFFF",
        # Theme style – body & links
        "body_color": "#33425E",
        "body_typography_typography": "custom",
        "body_typography_font_family": BODY_FONT,
        "body_typography_font_size": px(16),
        "body_typography_font_weight": "400",
        "body_typography_line_height": em(1.6),
        "link_normal_color": "#0068BE",
        "link_hover_color": "#0A3D80",
        "paragraph_spacing": px(0),
        # Headings
        "__globals__": {
            "body_color": C("text"),
            "link_normal_color": C("accent"),
            "link_hover_color": C("primary"),
            "h1_color": C("fsihead"), "h2_color": C("fsihead"), "h3_color": C("fsihead"),
            "h4_color": C("fsihead"), "h5_color": C("fsihead"), "h6_color": C("fsihead"),
            "button_text_color": C("fsihead"),
            "button_background_color": C("secondary"),
            "button_hover_text_color": C("fsihead"),
            "button_hover_background_color": C("fsigold"),
            "form_field_text_color": C("fsihead"),
            "form_field_background_color": C("fsiwhit"),
            "form_field_border_color": C("fsibord"),
            "form_label_color": C("fsihead"),
        },
        # Buttons
        "button_typography_typography": "custom",
        "button_typography_font_family": HEAD_FONT,
        "button_typography_font_size": px(15),
        "button_typography_font_weight": "600",
        "button_text_color": "#0C1A3A",
        "button_background_color": "#F9BE1A",
        "button_hover_text_color": "#0C1A3A",
        "button_hover_background_color": "#E5A500",
        "button_border_radius": box(6),
        "button_padding": box(14, 24),
        # Form fields
        "form_field_typography_typography": "custom",
        "form_field_typography_font_family": BODY_FONT,
        "form_field_typography_font_size": px(14),
        "form_field_text_color": "#0C1A3A",
        "form_field_background_color": "#FFFFFF",
        "form_field_border_border": "solid",
        "form_field_border_width": box(1),
        "form_field_border_color": "#DCE4F0",
        "form_field_border_radius": box(6),
        "form_field_padding": box(10, 12),
        "form_label_typography_typography": "custom",
        "form_label_typography_font_family": BODY_FONT,
        "form_label_typography_font_size": px(13),
        "form_label_typography_font_weight": "500",
        "form_label_color": "#0C1A3A",
        # Images
        "image_border_radius": box(8),
        # Custom CSS (Elementor Pro)
        "custom_css": CUSTOM_CSS,
    }
    sizes = {"h1": (48, 40, 32, 800, 1.1), "h2": (34, 30, 26, 700, 1.2), "h3": (22, 20, 19, 700, 1.3),
             "h4": (18, 17, 16, 600, 1.35), "h5": (16, 16, 15, 600, 1.4), "h6": (14, 14, 14, 600, 1.4)}
    for h, (d, t, m, wt, lh) in sizes.items():
        s[f"{h}_color"] = "#0C1A3A"
        s[f"{h}_typography_typography"] = "custom"
        s[f"{h}_typography_font_family"] = HEAD_FONT
        s[f"{h}_typography_font_size"] = px(d)
        s[f"{h}_typography_font_size_tablet"] = px(t)
        s[f"{h}_typography_font_size_mobile"] = px(m)
        s[f"{h}_typography_font_weight"] = str(wt)
        s[f"{h}_typography_line_height"] = em(lh)
    return s


def write_json(name, data):
    path = os.path.join(OUT, name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    return path


def main():
    # Templates
    write_json("fsi-header.json", template("FSI – Header", "header", build_header()))
    write_json("fsi-footer.json", template("FSI – Footer", "footer", build_footer()))
    write_json("src/fsi-homepage.generated.json", template("FSI – Homepage", "page", build_home(),
                                             {"hide_title": "yes", "template": "elementor_header_footer"}))

    # Kit (site settings only)
    kit_dir = os.path.join(OUT, "kit-source")
    os.makedirs(kit_dir, exist_ok=True)
    manifest = {
        "name": "fsi-global-styles",
        "title": "FSI Global Styles",
        "description": "Fulton Science Innovations – global colors, fonts and theme styles.",
        "author": "FSI",
        "version": "2.0",
        "elementor_version": "3.25.0",
        "created": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        "thumbnail": False,
        "site": "",
        "site-settings": ["global-colors", "global-typography", "theme-style-typography", "theme-style-buttons",
                          "theme-style-images", "theme-style-form-fields", "settings-background",
                          "settings-layout", "settings-custom-css"],
        "templates": {},
        "content": {},
        "wp-content": {},
        "plugins": [
            {"name": "Elementor", "plugin": "elementor/elementor", "pluginUri": "https://elementor.com/",
             "version": "3.25.0"},
            {"name": "Elementor Pro", "plugin": "elementor-pro/elementor-pro", "pluginUri": "https://elementor.com/",
             "version": "3.25.0"},
        ],
    }
    site_settings = {"content": [], "settings": kit_settings(), "metadata": []}
    with open(os.path.join(kit_dir, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=1)
    with open(os.path.join(kit_dir, "site-settings.json"), "w") as f:
        json.dump(site_settings, f, indent=1)
    with zipfile.ZipFile(os.path.join(OUT, "fsi-global-kit.zip"), "w", zipfile.ZIP_DEFLATED) as z:
        z.write(os.path.join(kit_dir, "manifest.json"), "manifest.json")
        z.write(os.path.join(kit_dir, "site-settings.json"), "site-settings.json")
    print("done")


if __name__ == "__main__":
    main()

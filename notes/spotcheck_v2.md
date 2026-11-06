# Hand check of v2 positives (2026-11-06)

Every value labelled single / scale event, with the token name(s) that arrived. Judged by name and by where the
variable lives: **system** = a scale or global token (spacing, type size, radius, grid); **component** = a
component variable shared by a few files, or an ambiguous name. Component ones are excluded in the
`system-level positives only` cut of `pooled_v2.py` (COMPONENT). Semantic UI's 23 come from one 2013-14 event
that turned every component into theme variables with generic names (medium, tiny); it is reported with and without.

| System | Value | Kind | Cluster -> token | New token name(s) | Judged |
|---|---|---|---|---|---|
| carbon | 2 px | single | 2016-02 -> 2017-06 | `button-border-width` | component |
| carbon | 32 px | scale event | 2016-02 -> 2018-02 | `spacing-xl` | system |
| carbon | 24 px | scale event | 2016-03 -> 2018-02 | `spacing-lg` | system |
| carbon | 48 px | scale event | 2016-03 -> 2018-02 | `spacing-3xl` | system |
| carbon | 8 px | scale event | 2017-02 -> 2018-02 | `spacing-xs` | system |
| carbon | 4 px | scale event | 2017-04 -> 2018-02 | `spacing-2xs` | system |
| eui | 16 px | scale event | 2017-02 -> 2017-10 | `kuiSize` | system |
| eui | 12 px | single | 2017-02 -> 2017-05 | `globalSubTextFontSize`, `globalFormControlHorizontalPadding` | system |
| eui | 20 px | single | 2017-03 -> 2018-10 | `size` | component |
| eui | 8 px | scale event | 2017-09 -> 2017-10 | `kuiSizeS` | system |
| eui | 48 px | single | 2019-01 -> 2019-02 | `euiHeaderChildSize` | component |
| bootstrap | 6 px | single | 2011-05 -> 2012-12 | `border-radius-large` | system |
| bootstrap | 12 px | scale event | 2011-05 -> 2013-06 | `padding-base-horizontal` | system |
| bootstrap | 16 px | scale event | 2011-05 -> 2013-06 | `padding-large-horizontal` | system |
| bootstrap | 20 px | single | 2011-07 -> 2011-10 | `gridGutterWidth` | system |
| bootstrap | 14 px | single | 2011-07 -> 2012-09 | `baseFontSize` | system |
| bootstrap | 4 px | single | 2011-10 -> 2012-12 | `border-radius-base` | system |
| bootstrap | 8 px | scale event | 2012-02 -> 2013-06 | `padding-base-vertical` | system |
| bootstrap | 3 px | scale event | 2012-02 -> 2012-10 | `borderRadiusSmall` | system |
| bootstrap | 24 px | single | 2017-06 -> 2017-11 | `close-font-size` | component |
| primer-css | 14 px | scale event | 2015-04 -> 2017-07 | `h5-size`, `body-font-size` | system |
| primer-css | 16 px | scale event | 2015-04 -> 2017-07 | `margin`, `h4-size` | system |
| primer-css | 12 px | scale event | 2015-04 -> 2017-07 | `h6-size`, `font-size-small` | system |
| primer-css | 26 px | scale event | 2016-04 -> 2017-07 | `h1-size-mobile` | system |
| primer-css | 1 px | single | 2017-07 -> 2017-12 | `border-width` | system |
| mdc-web | 56 px | scale event | 2016-01 -> 2017-10 | `mdc-toolbar-mobile-row-height` | component |
| mdc-web | 7 px | single | 2017-03 -> 2018-03 | `mdc-chip-vertical-padding` | component |
| ant-design | 2 px | single | 2015-07 -> 2016-12 | `border-radius-sm` | system |
| ant-design | 4 px | single | 2015-07 -> 2016-03 | `border-radius-sm` | system |
| ant-design | 14 px | single | 2015-07 -> 2016-12 | `font-size-lg` | system |
| ant-design | 22 px | single | 2015-08 -> 2016-01 | `input-height-sm` | system |
| ant-design | 40 px | scale event | 2016-02 -> 2017-12 | `btn-height-lg`, `input-height-lg` | component |
| ant-design | 6 px | scale event | 2016-12 -> 2017-12 | `input-padding-vertical-lg` | component |
| govuk-frontend | 1 px | single | 2017-08 -> 2018-01 | `offset` | component |
| uswds | 32 px | scale event | 2015-09 -> 2017-08 | `h3-font-size` | system |
| uswds | 24 px | single | 2015-09 -> 2016-08 | `site-margins-mobile` | system |
| uswds | 8 px | single | 2015-09 -> 2017-10 | `spacing-x-small` | system |
| uswds | 16 px | single | 2016-06 -> 2017-10 | `h6-font-size`, `spacing-small` | system |
| clarity | 8 px | scale event | 2016-11 -> 2017-11 | `clr-table-cellpadding` | component |
| clarity | 24 px | scale event | 2016-11 -> 2017-12 | `clr-button-height`, `clr-alert-min-height`, `clr-subnav-height` | component |
| clarity | 4 px | scale event | 2016-11 -> 2017-12 | `clr-button-vertical-margin`, `clr-table-smallpadding`, `clr-icon-margin-right` | component |
| clarity | 16 px | scale event | 2016-12 -> 2017-12 | `clr-button-height-sm`, `clr-checkbox-radio-label-height`, `clr-modal-content-padding-top` | component |
| clarity | 12 px | scale event | 2017-02 -> 2017-12 | `clr-alert-item-min-height` | component |
| clarity | 10.6667 px | scale event | 2017-11 -> 2017-12 | `clr-icon-dimension-sm`, `clr-checkbox-radio-height`, `clr-form-icon-dim` | component |
| clarity | 240 px | scale event | 2017-11 -> 2017-12 | `clr-sliding-panel-width` | component |
| spectrum-css | 20 px | single | 2018-12 -> 2019-07 | `--spectrum-global-dimension-size-200` | system |
| spectrum-css | 12 px | scale event | 2018-12 -> 2019-11 | `--spectrum-global-dimension-static-size-150`, `--spectrum-alias-body-margin-bottom` | system |
| foundation | 24 px | single | 2015-12 -> 2017-01 | `base-line-height` | system |
| semantic-ui | 16 px | scale event | 2013-06 -> 2013-11 | `medium` | event (generic names) |
| semantic-ui | 24 px | scale event | 2013-06 -> 2013-11 | `horizontalPadding`, `massive` | event (generic names) |
| semantic-ui | 14.4 px | scale event | 2013-06 -> 2014-03 | `h5` | event (generic names) |
| semantic-ui | 14 px | scale event | 2013-06 -> 2013-11 | `tiny`, `small` | event (generic names) |
| semantic-ui | 18 px | scale event | 2013-06 -> 2013-11 | `large` | event (generic names) |
| semantic-ui | 10 px | scale event | 2013-06 -> 2014-05 | `mini` | event (generic names) |
| semantic-ui | 12 px | scale event | 2013-06 -> 2014-02 | `dropdownPointingDistance`, `attachedHorizontalPadding`, `attachedVerticalPadding` | event (generic names) |
| semantic-ui | 20 px | scale event | 2013-06 -> 2013-11 | `big` | event (generic names) |
| semantic-ui | 22 px | scale event | 2013-06 -> 2013-11 | `huge` | event (generic names) |
| semantic-ui | 5 px | scale event | 2013-06 -> 2013-12 | `roundedBorderRadius` | event (generic names) |
| semantic-ui | 11 px | scale event | 2013-06 -> 2014-05 | `tiny` | event (generic names) |
| semantic-ui | 32 px | scale event | 2013-06 -> 2013-12 | `circularSize`, `squareSize`, `avatarSize` | event (generic names) |
| semantic-ui | 8 px | scale event | 2013-06 -> 2013-12 | `directionMargin` | event (generic names) |
| semantic-ui | 3 px | scale event | 2013-06 -> 2014-02 | `secondaryPointingBorderWidth` | event (generic names) |
| semantic-ui | 4 px | scale event | 2013-06 -> 2013-11 | `borderRadius` | event (generic names) |
| semantic-ui | 12.8 px | scale event | 2013-07 -> 2013-11 | `verticalPadding`, `mini` | event (generic names) |
| semantic-ui | 80 px | scale event | 2013-07 -> 2013-12 | `tinyWidth` | event (generic names) |
| semantic-ui | 13 px | scale event | 2013-09 -> 2014-05 | `medium` | event (generic names) |
| semantic-ui | 19.2 px | scale event | 2013-09 -> 2014-03 | `largeFontSize` | event (generic names) |
| semantic-ui | 28 px | scale event | 2013-10 -> 2014-02 | `h2` | event (generic names) |
| semantic-ui | 8000 px | scale event | 2013-10 -> 2013-12 | `circularRadius` | event (generic names) |
| semantic-ui | 250 px | scale event | 2013-10 -> 2014-08 | `maxWidth`, `loadingMinHeight` | event (generic names) |
| semantic-ui | 2 px | scale event | 2013-11 -> 2014-09 | `activeBorderSize` | event (generic names) |
| patternfly | 20 px | single | 2018-08 -> 2019-02 | `fa-fw-width` | component |
| lightning | 32 px | single | 2015-10 -> 2016-02 | `height-banner-badge` | component |

73 positives: 18 component, 23 Semantic UI event, 32 system-level elsewhere.

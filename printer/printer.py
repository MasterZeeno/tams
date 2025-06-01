from itertools import combinations
from pprint import pprint
from typing import Any
from typing import List, Dict, Union

def __GET_FORMAT_COMBO(
    varlist: List[str],
    excluded: Union[List[str], str] = 'none',
    index_ref: List[str] = None
) -> Dict[str, List[str]]:
    if isinstance(excluded, str):
        excluded = [excluded]
    
    index_ref = index_ref if index_ref else varlist
    formats = [f for f in varlist if f not in excluded]
    char_map = {f[0]: f for f in formats}
    chars = sorted(char_map.keys())

    results: Dict[str, List[str]] = {}

    for r in range(len(chars), 0, -1):
        for combo in combinations(chars, r):
            key = ''.join(combo)
            full = '-'.join(char_map[c] for c in combo)
            fmt_indices = ''
            if index_ref:
                fmt_indices = ';'.join(str(index_ref.index(char_map[c])) for c in combo) + ';'
            results[key] = [full, fmt_indices]
    
    return results

ANSI_ESC = '\033['
RESET = f'{ANSI_ESC}0m'

TEXT_CASES = {
    'title': str.title,
    'capitalize': str.capitalize,
    'lower': str.lower,
    'upper': str.upper
}

TEXT_FORMATS = ('none', 'bold', 'dim', 'italic')
TEXT_FORMATS_COMBO = __GET_FORMAT_COMBO(TEXT_FORMATS)
COLOR_THEMES = {'dark': 30, 'light': 90}

PRESET_SETS = {
    'default': '',
    'error': '',
    'success': '',
    'warning': '☢︎',
    'info': '𝒊',
    'text': '»',
    'subtext': '›',
    'dash': '―',
}

DEFAULTS = {
    'preset': 'default',
    'text_case': 'title',
    'text_formats': '',
    'icon': '',
    'color_code': 7,
    'color_theme': 'dark',
    'indent_count': 1
}

COLOR_CODES = {
    DEFAULTS['color_code'] if i == 0 else i: v
    for i, v in enumerate(('white', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan'))
}

PRESET_THEMES_KEYS = tuple(DEFAULTS.keys())[2:6]
PRESET_THEMES = {
    name: dict(zip(tuple(DEFAULTS.keys())[2:6], (f'{TEXT_FORMATS.index('bold')};' if name in tuple(PRESET_SETS.keys())[1:5] else '', icon, DEFAULTS['color_code'] if i == 0 else i, DEFAULTS['color_theme'])))
    for i, (name, icon) in enumerate(PRESET_SETS.items())
}

class Printer:
    def __init__(self, **kwargs: Any) -> None:
        self._style = DEFAULTS.copy()
        self._tfc = TEXT_FORMATS_COMBO.copy()
        self._resolve_style(init=True, **kwargs)

    def __call__(self, messages: str | list[str, ...]) -> None:
        self._print(messages)

    def _print(self, messages: str | list[str, ...], icon: str = '', bold: bool = True, newline: dict[str, int] | list[int, int] | int = 0, **kwargs: Any) -> None:
        self._resolve_style(**kwargs)
        
        newline_prev = 0
        newline_next = 0
        
        if isinstance(newline, int):
            newline_next = newline
        if isinstance(newline, list):
            [newline_prev, newline_next] = newline
        if isinstance(newline, dict):
            for k, v in newline.items():
                if 'prev' in k:
                    newline_prev = v
                elif 'next' in k:
                    newline_next = v
        
        if not isinstance(messages, list):
            messages = [messages]
        
        if newline_prev:
                self._newline(newline_prev)
        
        for index, message in enumerate(messages):
            message = TEXT_CASES.get(self._style['text_case'], lambda x: x)(message)
            textformat = self.text_title if bold else self.text_subtitle
            icon = icon if icon else self._style['icon']
           
            pprint(f'{self.indent}{self.icon_formatted}{icon}{RESET} {"".join([textformat, message, RESET])}')
        
        if newline_next:
            self._newline(newline_next)
            
    def _resolve_style(self, init: bool = False, **kwargs: Any) -> None:
        pkey = 'preset'
        preset = kwargs.get(pkey, None)
        if init:
            preset = preset if preset and preset in PRESET_SETS else DEFAULTS[pkey]
            kwargs.update(PRESET_THEMES[preset])
            kwargs[pkey] = preset
        else:
            if preset:
                del kwargs[pkey]
            kwargs = self._resolve_styles(**kwargs)
        
        for key, value in kwargs.items():
            if key in self._style:
                old_value = self._get(key)
                if value != old_value:
                    self._set(key, value)
                
        self.color_code = self._style['color_code'] + COLOR_THEMES[self._style['color_theme']]
        self._resolve_icon_format()
        self.tf = self._style['text_formats']
        self.icon_formatted: str = f'{self._format_code(self._icon_format)}'
        self.text_title: str = f'{self._format_code(textformats)}'
        self.text_subtitle: str = f'{self._format_code(textformats.replace('1;', '2;'))}'
        self.indent: str = ' ' * min(5, max(0, self._style.get('indent_count', 1)))
            
    def _resolve_icon_format(self, delim: str = ';'):
        icon_format = self._style.get('text_formats', '').replace(self._tfc['i'][1], '')
        self._icon_format = icon_format if icon_format else self._tfc['b'][1])
    
    def _resolve_list(self, varlist: Any, delim: str = ' ') -> list[str, ...]:
        return list(varlist.keys()) if isinstance(varlist, dict) else (str(varlist).split(delim) if not isinstance(varlist, list) else varlist)
    
    def _resolve_substr(self, varlist: Any, val: str, i: int | None = -1) -> str:
        varlist = self._resolve_list(varlist)
        val = val.strip().lower()
        for idx, value in enumerate(varlist):
            if value.startswith(val):
                return value
        return varlist[i] if i else ''
    
    def _resolve_indexes(self, varlist1: Any, varlist2: Any, ret: type = str, i: int | None = 0, delim: str = ';') -> int | str:
        varlist1 = self._resolve_list(varlist1)
        varlist2 = self._resolve_list(varlist2)
        intarr: list[int, ...] = []
        for val in varlist1:
            intarr.append(self._get_index(varlist2, val, i))
        intarr = sorted(set(intarr))
        return delim.join([str(a) for a in intarr]) if ret == str else intarr
            
    def _get_index(self, varlist: Any, idx: int | str = -1, ret: type = int, i: int | None = 0, delim: str = ';') -> int | str: 
        varlist = self._resolve_list(varlist)
        index = varlist.index((varlist[len(varlist) if 0 > idx > len(varlist) else idx]) if isinstance(idx, int) else (self._resolve_substr(varlist, idx, i)))
        return index if ret == int else f'{index}{delim}'
            
    def _resolve_styles(self, **kwargs: Any) -> Any:
        for idx, txt in enumerate(tuple(DEFAULTS.keys())[1:3]):
            txtval: str | int = kwargs.get(txt, '')
            if txt in kwargs and txtval != self._style.get(txt, ''):
                kwargs[txt] = self._resolve_indexes(txtval, TEXT_FORMATS) if idx == 0 else self._resolve_substr(TEXT_CASES, textval)
                            
        for i, c in enumerate(tuple(DEFAULTS.keys())[4:6]):
            cval: int | str = kwargs.get(c, self._style[c])
            cval = (cval if 0 < cval < 10 else DEFAULTS[c]) if isinstance(cval, int) else str(cval).strip().lower()
            kwargs[c] = cval
            
        return kwargs
                    
    def _format_code(self, fmt: str, contents: str = '') -> str:
        return f'{ANSI_ESC}{fmt}{self.color_code}m{contents}'

    def _newline(self, count: int = 1) -> None:
        for c in range(1, count+1):
            pprint()
            
    def _init_idx(self, d: str = '_') -> None:
        self._style = DEFAULTS.copy()
        self._tfc = TEXT_FORMATS_COMBO.copy()
        
        idx_map = {
            ''.join([k[0] for k in key.split('_') if k]): key
            for key in self._style.keys()
        }
        
        for key in self._style.keys():
            sh = ''.join(p[0] for p in key.split(d) if p)
            idx_map[sh] = key
            
    def _get(self, key: str, fallback: str | None = None, i: int = 1) -> Any | None:
        return self._idx[key][i] if key in self._idx else (self._style[key] if key in self._style else fallback)

    def _set(self, key: str, val: Any) -> None:
        key = self._idx[key][0] if key in self._idx else (key if key in self._style else None)
        if key:
            self._style[key] = val
 
    def currentStyle(self) -> None:
        currStyle = self._style.copy()
        opts = {'init': True}
        
        self._print('Current styles:', newline=[1, 1], preset='info', **opts)
        details: list[str, ...] = []
        for k, v in currStyle.items():
            if k.startswith('text_f'):
                v = [TEXT_FORMATS[int(vv)] for vv in v.split(';') if vv] if v else []
            if k.startswith('text_c'):
                v += ' case'
            if k.startswith('color_c'):
                k = 'Theme Color'
                v = f'{self._style["color_theme"]}er {COLOR_CODES[v]}'
            if k.startswith('in'):
                k = k.split('_')[0]
                v = f'{v} {"spaces" if v > 1 else "space"}'
            k = k.replace('_', ' ')
            v = f"'{v}'" if isinstance(v, str) else v
            pair = f'{k}: {v}'
            if not k.startswith('color_t'):
                details.append(f'{k}: {v}')
            
        self._print(details, icon='›', bold=False, preset=currStyle['preset'], indent_count=2, **opts)
        
        # self._print(f'\n{self._style}\n', init=True, preset='info')

    # def defaultStyle(self) -> None:
        # self._print(str(DEFAULTS), init=True, preset='info')
# Hack to make jupyter notebook wider
from IPython.display import display, Markdown, HTML


def showToggleCodeButton(default_hide=False):
    code_show = 'true'
    if not default_hide:
        code_show = 'false'
    display(HTML("<style>.container { width:98% !important; }</style>"))
    display(HTML("<style>.output.output_scroll { height: auto; }</style>"))
    display(HTML('''<script>
       code_show=%s;
       function code_toggle() {
          if (code_show) {
              $('div.input').hide();
              $('div.cell.code_cell:not(:has( .output_wrapper .output_area))').hide();
          } else {
              $('div.input').show();
              $('div.cell.code_cell').show();
          }
          code_show = !code_show
       }
       $( document ).ready(code_toggle);
    </script>
    <form action="javascript:code_toggle()"><input type="submit" class="btn btn-primary" value="Click here to toggle on/off the code."></form>''' % code_show))

def display_mk(mk: str):
	display(Markdown(mk))

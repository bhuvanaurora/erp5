##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import string
from Products.Formulator.DummyField import fields
from Products.Formulator import Widget, Validator
from Products.Formulator.Field import ZMIField
from Products.Formulator.Form import BasicForm
from Products.Formulator.MethodField import BoundMethod
from Selection import Selection
from DateTime import DateTime
from Products.ERP5Type.Utils import getPath

from zLOG import LOG


class MatrixBoxWidget(Widget.Widget):
    """
    An UI widget which displays a matrix

    A MatrixBoxWidget should be called 'matrixbox', if you don't do so, then
    you may have some errors, or some strange problems, you have been Warned !!!!

    Don't forget that you can use tales expressions for every field, so this
    is really usefull if you want to use fonctions instead of predefined variables.

    A function is provided to

    - access a cell

    - modify a cell


    """
    property_names = Widget.Widget.property_names +\
                     ['cell_base_id', 'lines', 'columns', 'tabs',
                      'getter_method' ,
                      'editable_attributes' , 'global_attributes',
                      'update_cell_range'
                       ]

    default = fields.TextAreaField('default',
                                   title='Default',
                                   description=(
        "Default value of the text in the widget."),
                                   default="",
                                   width=20, height=3,
                                   required=0)

    columns = fields.ListTextAreaField('columns',
                                 title="Columns",
                                 description=(
      """This defines columnes of the matrixbox. This should be a list of couples, 
      couple[0] is the variation, and couple[1] is the name displayed to the user.
      For example (('color/bleu','bleu'),('color/red','red')), Required"""),
                                 default=[],
                                 required=1)

    lines = fields.ListTextAreaField('lines',
                                 title="Lines",
                                 description=(
      """This defines lines of the matrixbox. This should be a list of couples, 
      couple[0] is the variation, and couple[1] is the name displayed to the user.
      For example (('size/baby/02','baby/02'),('size/baby/03','baby/03')), Required"""),
                                 default=[],
                                 required=1)

    tabs = fields.ListTextAreaField('tabs',
                                 title="Tabs",
                                 description=(
      """This defines tabs. You can use it with the same way as Lines and Columns,
      This is used only if you have more than 2 kinds of variations. Required"""),
                                 default=[],
                                 required=0)

    getter_method = fields.MethodField('getter_method',
                                 title='Getter method',
                                 description=("""
        You can specify a specific method in order to retrieve cells.
        This field can be empty, if so the MatrixBox will use the default method :
        getCell."""),

                                 default='',
                                 required=0)

    editable_attributes = fields.ListTextAreaField('editable_attributes',
                                 title="Editable Properties",
                                 description=(
        """A list of attributes which are set by hidden fields called matrixbox_attribute_name. This is used
        when we want to specify a value calculated for each cell"""),
                                 default=[],
                                 required=0)

    global_attributes = fields.ListTextAreaField('global_attributes',
                                 title="Global Properties",
                                 description=(
        """An optional list of globals attributes which are set by hidden fields and which are applied to each cell. 
        This is used if we want to set the same value for every cell"""),
                                 default=[],
                                 required=0)

    cell_base_id = fields.StringField('cell_base_id',
                                 title='Base id for cells',
                                 description=("""
        The Base id for cells : this is the name used to store cells, we usually,
        use names like : 'mouvement','path', ...."""),
                                 default='cell',
                                 required=0)

    update_cell_range = fields.CheckBoxField('update_cell_range',
                                  title="Update Cell Range",
                                  description=(
        "The cell range should be updated upon edit."),
                                  default=0)


    def render(self, field, key, value, REQUEST):
        """
          This is where most things happen. This method renders a list
          of items
        """
        # First grasp the variables we may need
        here = REQUEST['here']
        form = field.aq_parent
        field_title = field.get_value('title')
        cell_base_id = field.get_value('cell_base_id')
        lines = field.get_value('lines')
        columns = field.get_value('columns')
        tabs = field.get_value('tabs')
        getter_method_name = field.get_value('getter_method')
        getter_method = getattr(here, getter_method_name, here.getCell)
        editable_attributes = field.get_value('editable_attributes')

        # This is required when we have no tabs
        if len(tabs) == 0: tabs = [(None,None)]

        column_ids = map(lambda x: x[0], columns)
        line_ids = map(lambda x: x[0], lines)
        tab_ids = map(lambda x: x[0], tabs)
        editable_attribute_ids = map(lambda x: x[0], editable_attributes)

        # THIS MUST BE REMOVED - WHY IS THIS BAD ?
        # IT IS BAD BECAUSE TAB_IDS DO NOT DEFINE A RANGE....
        # here.setCellRange(line_ids, column_ids, base_id=cell_base_id)

        url = REQUEST.URL

        list_html = ''
        k = 0
        # Create one table per tab
        for tab in tabs:
          tab_id = tab[0]
          if type(tab_id) is not type(()) and type(tab_id) is not type([]) and tab_id is not None:
            tab_id = [tab_id]

          # Create the header of the table - this should probably become DTML
          header = """\
  <!-- Matrix Content -->
  %s<br>
  <div class="ListContent">
   <table cellpadding="0" cellspacing="0" border="0">
  """ % tab[1]

          # Create the footer. This should be replaced by DTML
          # And work as some kind of parameter
          footer = """\
        </div>
       </td>
      </div>
     </tr>
     <tr >
      <td colspan="%s" width="50" align="center" valign="middle"
          class="DataA">
      </td>
     </tr>
    </table>
   </div>
  """ %  len(columns)

          list_header = """\
  <tr ><td class=\"Data\"></td>
  """

          for cname in columns:
              list_header = list_header + ("<td class=\"Data\">%s</td>\n" %
                  str(cname[1]))
          list_header = list_header + "</tr>"

          # Build Lines
          i = 0
          j = 0
          list_body = ''
          for l in lines:
            if not i % 2:
              td_css = 'DataA'
            else:
              td_css = 'DataB'
            list_body = list_body + '<tr><td class=\"%s\">%s</td>' % (td_css, str(l[1]))
            j = 0
            for c in columns:
              if tab_id is None:
                kw = [l[0], c[0]]
              else:
                kw = [l[0], c[0]] + tab_id
              kwd = {}
              kwd['base_id'] = cell_base_id
              cell = getter_method(*kw, **kwd)
              cell_body = ''
              for attribute_id in editable_attribute_ids:
                my_field_id = '%s_%s' % (field.id, attribute_id)
                if form.has_field(my_field_id):
                  my_field = form.get_field(my_field_id)
                  key = my_field.id + '_cell_%s_%s_%s' % (i,j, k)
                  #LOG("Cell",0,str(cell))
                  #LOG("Cell",0,str(getter_method))
                  #LOG("Cell",0,str(kwd))
                  #LOG("Cell",0,str(kw))
                  attribute_value = my_field.get_value('default', cell = cell,
                                    cell_index = kw, cell_position = (i,j, k))
                  cell_body += str(my_field.render(value = attribute_value, REQUEST = REQUEST, key = key))
              list_body = list_body + \
                    ('<td class=\"%s\">%s</td>' % (td_css, cell_body))
              j += 1
            list_body = list_body + '</tr>'
            i += 1

          list_html += header + list_header + \
                  list_body + footer
          k += 1

        return list_html

MatrixBoxWidgetInstance = MatrixBoxWidget()

class MatrixBoxValidator(Validator.Validator):
    property_names = Validator.Validator.property_names

    def validate(self, field, key, REQUEST):
        form = field.aq_parent
        # We need to know where we get the getter from
        # This is coppied from ERP5 Form
        here = getattr(form, 'aq_parent', REQUEST)
        cell_base_id = field.get_value('cell_base_id')
        lines = field.get_value('lines')
        columns = field.get_value('columns')
        tabs = field.get_value('tabs')
        editable_attributes = field.get_value('editable_attributes')

        getter_method_name = field.get_value('getter_method')
        getter_method = getattr(here, getter_method_name, here.getCell)

        # This is required when we have no tabs
        if len(tabs) == 0: tabs = [(None,None)]

        column_ids = map(lambda x: x[0], columns)
        line_ids = map(lambda x: x[0], lines)
        tab_ids = map(lambda x: x[0], tabs)
        editable_attribute_ids = map(lambda x: x[0], editable_attributes)

        k = 0
        result = {}
        # Create one table per tab
        for tab_id in tab_ids:
          if type(tab_id) is not type(()) and type(tab_id) is not type([]) and tab_id is not None:
            tab_id = [tab_id]

          i = 0
          j = 0
          for l in line_ids:
            j = 0
            for c in column_ids:
              if tab_id is None:
                kw = [l, c]
              else:
                kw = [l, c] + tab_id
              kw = tuple(kw)
              kwd = {}
              kwd['base_id'] = cell_base_id
              cell = getter_method(*kw, **kwd)
              for attribute_id in editable_attribute_ids:
                my_field_id = '%s_%s' % (field.id, attribute_id)
                if form.has_field(my_field_id):
                  my_field = form.get_field(my_field_id)
                  key = 'field_' + my_field.id + '_cell_%s_%s_%s' % (i,j, k)
                  attribute_value = my_field.get_value('default', cell = cell, cell_index = kw,
                                                      cell_position = (i,j, k))
                  value = my_field.validator.validate(my_field, key, REQUEST)
                  if attribute_value != value and not my_field.get_value('hidden'):
                    # Only validate modified values from visible fields
                    if not result.has_key(kw):
                       result[kw] = {}
                    result[kw][attribute_id] = value
                  else:
                    if result.has_key(kw):
                      result[kw][attribute_id] = value
              j += 1
            i += 1
          k += 1

        return result

MatrixBoxValidatorInstance = MatrixBoxValidator()

class MatrixBox(ZMIField):
    meta_type = "MatrixBox"

    widget = MatrixBoxWidgetInstance
    validator = MatrixBoxValidatorInstance


# Psyco
import psyco
psyco.bind(MatrixBoxWidget.render)
psyco.bind(MatrixBoxValidator.validate)


